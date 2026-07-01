#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

METRIC_RE = re.compile(r"\b(PSNR|SSIM|LPIPS|FPS|MB|GB|ms|dB|ATE|RPE|F-score)\b", re.I)
NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?")
EVIDENCE_RE = re.compile(r"(Table|Fig\.?|Figure|Eq\.?|Sec\.?|论文|补充材料|代码|未报告|无法核实|待核实)", re.I)
SECTION_PATTERNS = {
    "汇报摘要": r"汇报摘要|核心摘要",
    "结果": r"结果汇报|主要结果|定量结果",
    "效率代价": r"效率|存储|显存|模型大小|训练代价",
    "局限": r"局限|适用边界|未证明",
    "可复现性": r"可复现|复现",
}
REQUIRED_ANALYSIS = [
    "task",
    "core_contribution",
    "method_summary",
    "method_category",
    "datasets",
    "metrics",
    "main_results",
    "efficiency",
    "ablations",
    "code_mapping",
    "limitations",
    "claims",
    "evidence",
    "comparability",
    "reproducibility",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def flatten_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        out: list[str] = []
        for child in value.values():
            out.extend(flatten_values(child))
        return out
    if isinstance(value, list):
        out = []
        for child in value:
            out.extend(flatten_values(child))
        return out
    return [str(value)]


def find_manifest_paper(manifest: dict[str, Any], paper_id: str) -> dict[str, Any] | None:
    for paper in manifest.get("papers", []):
        if isinstance(paper, dict) and paper.get("id") == paper_id:
            return paper
    return None


def metric_numbers(text: str) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for line in text.splitlines():
        if METRIC_RE.search(line):
            for number in NUMBER_RE.findall(line):
                results.append((number, line.strip()))
    return results


def chinese_ratio(text: str) -> float:
    cn = sum("\u4e00" <= c <= "\u9fff" for c in text)
    latin = sum(c.isascii() and c.isalpha() for c in text)
    return cn / max(cn + latin, 1)


def validate(md_path: Path, json_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not md_path.is_file():
        errors.append(f"Markdown file missing: {md_path}")
        md_text = ""
    else:
        md_text = md_path.read_text(encoding="utf-8")
    if not json_path.is_file():
        errors.append(f"JSON file missing: {json_path}")
        data: dict[str, Any] = {}
    else:
        try:
            data = load_json(json_path)
        except json.JSONDecodeError as exc:
            errors.append(f"JSON decode failed: {exc}")
            data = {}

    paper = data.get("paper", {}) if isinstance(data.get("paper"), dict) else {}
    analysis = data.get("analysis", {}) if isinstance(data.get("analysis"), dict) else {}
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    paper_id = str(paper.get("id", ""))

    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    for key in ("id", "title", "authors", "source_url", "pdf_path"):
        if key not in paper:
            errors.append(f"paper missing required key: {key}")
    for key in REQUIRED_ANALYSIS:
        if key not in analysis:
            errors.append(f"analysis missing required key: {key}")
    if validation.get("language") != "zh-CN":
        errors.append("validation.language must be zh-CN")

    if paper_id and paper_id not in md_text:
        warnings.append(f"Markdown does not mention paper id {paper_id}")
    title = str(paper.get("title", "")).strip()
    if title and title not in md_text:
        errors.append("Markdown title/content does not match JSON paper.title")

    for section, pattern in SECTION_PATTERNS.items():
        if md_text and not re.search(pattern, md_text, re.I):
            errors.append(f"Markdown missing section/content: {section}")

    main_results = analysis.get("main_results", [])
    if isinstance(main_results, list):
        for idx, result in enumerate(main_results, start=1):
            if not isinstance(result, dict):
                errors.append(f"main_results[{idx}] is not an object")
                continue
            if not result.get("evidence"):
                errors.append(f"main_results[{idx}] missing evidence")
            if not result.get("comparability"):
                errors.append(f"main_results[{idx}] missing comparability")
    else:
        errors.append("analysis.main_results must be a list")

    json_values = "\n".join(flatten_values(data))
    for number, line in metric_numbers(md_text):
        if number not in json_values:
            errors.append(f"metric number appears in Markdown but not JSON: {number}")
        if not EVIDENCE_RE.search(line):
            errors.append(f"metric line lacks evidence marker: {line[:120]}")

    if chinese_ratio(md_text) < 0.2:
        errors.append("Markdown Chinese ratio is too low")
    english_paragraphs = [p for p in re.split(r"\n\s*\n", md_text) if len(re.findall(r"[A-Za-z]", p)) > 300 and chinese_ratio(p) < 0.1]
    if english_paragraphs:
        warnings.append(f"large English paragraphs detected: {len(english_paragraphs)}")

    if manifest_path and manifest_path.is_file() and paper_id:
        manifest = load_json(manifest_path)
        manifest_paper = find_manifest_paper(manifest, paper_id)
        if not manifest_paper:
            errors.append(f"paper id {paper_id} not found in manifest")
        else:
            manifest_title = str(manifest_paper.get("title", "")).strip()
            if manifest_title and title and manifest_title != title:
                errors.append("JSON title does not match manifest title")
        other_ids = [p.get("id") for p in manifest.get("papers", []) if isinstance(p, dict) and p.get("id") != paper_id]
        mixed = [x for x in other_ids if x and re.search(rf"\b{re.escape(str(x))}\b", md_text + json_values)]
        if mixed:
            errors.append(f"report appears to include other paper IDs: {', '.join(map(str, mixed))}")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "metrics_checked": len(metric_numbers(md_text)),
        "chinese_ratio": round(chinese_ratio(md_text), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a single-paper Markdown + JSON analysis pair.")
    parser.add_argument("--md", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    result = validate(args.md, args.json, args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    raise SystemExit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
