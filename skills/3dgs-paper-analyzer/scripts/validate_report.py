#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

METRIC_RE = re.compile(r"\b(PSNR|SSIM|LPIPS|FPS|MB|GB|ms|dB|ATE|RPE|F-score)\b", re.I)
NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?")
EVIDENCE_RE = re.compile(r"(Table|Fig\.?|Figure|Eq\.?|Sec\.?|论文|补充|代码|未报告|无法核实|待核实)", re.I)
CLAIM_MATRIX_RE = re.compile(r"Claim\s*[—-]\s*Evidence|Claim.*理论推导.*主结果", re.I | re.S)
QUICK_CARD_FIELDS = ["方法类型", "压缩对象", "核心贡献", "最强实验依据", "最大质量风险", "最大工程代价", "论文代码一致性", "复现难度", "是否值得复现", "对综述的价值"]
REQUIRED_SECTIONS = ["快速判断", "论文信息与分析边界", "论文与代码差异", "可复现性结论"]
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
        values: list[str] = []
        for child in value.values():
            values.extend(flatten_values(child))
        return values
    if isinstance(value, list):
        values: list[str] = []
        for child in value:
            values.extend(flatten_values(child))
        return values
    return [str(value)]


def chinese_ratio(text: str) -> float:
    cn = sum("\u4e00" <= c <= "\u9fff" for c in text)
    latin = sum(c.isascii() and c.isalpha() for c in text)
    return cn / max(cn + latin, 1)


def metric_numbers(text: str) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for line in text.splitlines():
        if METRIC_RE.search(line):
            for number in NUMBER_RE.findall(line):
                results.append((number, line.strip()))
    return results


def load_source_pack_validator():
    path = Path(__file__).resolve().parent / "validate_source_pack.py"
    spec = importlib.util.spec_from_file_location("validate_source_pack", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validate_source_pack.py from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_manifest_paper(manifest: dict[str, Any], paper_id: str) -> dict[str, Any] | None:
    for paper in manifest.get("papers", []):
        if isinstance(paper, dict) and paper.get("id") == paper_id:
            return paper
    return None


def resolve_sibling(path_value: str, base_file: Path) -> Path:
    candidate = Path(path_value)
    return candidate if candidate.is_absolute() else base_file.parent / candidate


def source_pack_path(data: dict[str, Any], json_path: Path) -> Path | None:
    for key in ("source_pack_path", "source_pack"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return resolve_sibling(value, json_path)
    ext = data.get("extensions", {}) if isinstance(data.get("extensions"), dict) else {}
    value = ext.get("source_pack")
    if isinstance(value, str) and value:
        return resolve_sibling(value, json_path)
    return None


def table_count(md_text: str) -> int:
    return sum(1 for line in md_text.splitlines() if re.match(r"^\s*\|.*\|\s*$", line))


def result_reference_exists(result: dict[str, Any], source_pack: dict[str, Any] | None) -> bool:
    if not source_pack:
        return True
    evidence = str(result.get("evidence", ""))
    table_ids = {str(t.get("table_id")) for t in source_pack.get("experiment_tables", []) if isinstance(t, dict)}
    table_sources = {str(t.get("source")) for t in source_pack.get("experiment_tables", []) if isinstance(t, dict)}
    evidence_ids = {str(e.get("evidence_id")) for e in source_pack.get("evidence_ledger", []) if isinstance(e, dict)}
    return evidence in table_ids or evidence in evidence_ids or any(evidence and evidence in source for source in table_sources)


def validate(md_path: Path, json_path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    md_text = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
    if not md_text:
        errors.append(f"Markdown file missing or empty: {md_path}")
    try:
        data = load_json(json_path)
    except FileNotFoundError:
        errors.append(f"JSON file missing: {json_path}")
        data = {}
    except json.JSONDecodeError as exc:
        errors.append(f"JSON decode failed: {exc}")
        data = {}

    paper = data.get("paper", {}) if isinstance(data.get("paper"), dict) else {}
    analysis = data.get("analysis", {}) if isinstance(data.get("analysis"), dict) else {}
    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    paper_id = str(paper.get("id", ""))
    analysis_mode = data.get("analysis_mode", "standard-analysis")

    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if analysis_mode not in ("standard-analysis", "innovation-review"):
        errors.append("analysis_mode must be standard-analysis or innovation-review")
    for key in ("id", "title", "authors", "source_url", "pdf_path"):
        if key not in paper:
            errors.append(f"paper missing required key: {key}")
    for key in REQUIRED_ANALYSIS:
        if key not in analysis:
            errors.append(f"analysis missing required key: {key}")
    if validation.get("language") != "zh-CN":
        errors.append("validation.language must be zh-CN")

    title = str(paper.get("title", "")).strip()
    if paper_id and paper_id not in md_text:
        warnings.append(f"Markdown does not mention paper id {paper_id}")
    if title and title not in md_text:
        errors.append("Markdown title/content does not match JSON paper.title")

    source_pack_data: dict[str, Any] | None = None
    sp_path = source_pack_path(data, json_path)
    if sp_path is None:
        errors.append("standard JSON missing source_pack_path or extensions.source_pack")
    else:
        sp_validator = load_source_pack_validator()
        sp_result = sp_validator.validate(sp_path)
        if sp_result.get("status") == "FAIL":
            errors.extend(f"source pack: {msg}" for msg in sp_result.get("errors", []))
        else:
            warnings.extend(f"source pack: {msg}" for msg in sp_result.get("warnings", []))
        if sp_path.is_file():
            source_pack_data = load_json(sp_path)
            sp_paper = source_pack_data.get("paper", {}) if isinstance(source_pack_data.get("paper"), dict) else {}
            for key in ("id", "title", "arxiv_id", "pdf_hash", "code_commit"):
                base_value = paper.get(key)
                sp_value = sp_paper.get(key)
                if key in ("pdf_hash",) and not base_value:
                    base_value = data.get(key)
                if base_value and sp_value and base_value != sp_value:
                    errors.append(f"standard JSON and Source Pack differ on {key}")

    for section in REQUIRED_SECTIONS:
        if section not in md_text:
            errors.append(f"Markdown missing required standard section/content: {section}")
    for field in QUICK_CARD_FIELDS:
        if field not in md_text:
            errors.append(f"quick judgment card missing field: {field}")
    if analysis_mode == "standard-analysis" and (CLAIM_MATRIX_RE.search(md_text) or "| 作者主张 |" in md_text):
        errors.append("standard-analysis must not contain innovation Claim card or Claim-Evidence matrix structure")
    if analysis_mode == "standard-analysis" and table_count(md_text) > 18:
        errors.append("standard Markdown appears to repeat too many full table rows; keep full tables in Source Pack or appendix")

    main_results = analysis.get("main_results", [])
    if not isinstance(main_results, list):
        errors.append("analysis.main_results must be a list")
    else:
        if analysis_mode == "standard-analysis" and len(main_results) > 10:
            errors.append("standard analysis.main_results should contain representative results only (max 10)")
        for idx, result in enumerate(main_results, start=1):
            if not isinstance(result, dict):
                errors.append(f"main_results[{idx}] is not an object")
                continue
            if not result.get("evidence"):
                errors.append(f"main_results[{idx}] missing evidence")
            if not result.get("comparability"):
                errors.append(f"main_results[{idx}] missing comparability")
            if not result_reference_exists(result, source_pack_data):
                errors.append(f"main_results[{idx}] evidence not found in Source Pack: {result.get('evidence')}")

    mapping_ids = {str(m.get("mapping_id")) for m in (source_pack_data or {}).get("code_map", []) if isinstance(m, dict)}
    for idx, mapping in enumerate(analysis.get("code_mapping", []) if isinstance(analysis.get("code_mapping"), list) else [], start=1):
        if isinstance(mapping, dict) and mapping.get("mapping_id") and str(mapping.get("mapping_id")) not in mapping_ids:
            errors.append(f"code_mapping[{idx}] mapping_id not found in Source Pack: {mapping.get('mapping_id')}")

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
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
