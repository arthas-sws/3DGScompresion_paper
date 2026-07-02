#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def norm(value: Any) -> str:
    return str(value or "").strip()


def metric_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (norm(item.get("dataset")).lower(), norm(item.get("scene")).lower(), norm(item.get("metric")).lower())


def result_numbers(item: dict[str, Any]) -> tuple[str, str, str]:
    return (norm(item.get("method_value")), norm(item.get("baseline_value")), norm(item.get("difference")))


def collect_review_numbers(review: dict[str, Any]) -> dict[tuple[str, str, str], tuple[str, str, str]]:
    out: dict[tuple[str, str, str], tuple[str, str, str]] = {}
    for table in review.get("experiment_tables", []) if isinstance(review.get("experiment_tables"), list) else []:
        if not isinstance(table, dict):
            continue
        for row in table.get("rows", []) if isinstance(table.get("rows"), list) else []:
            if not isinstance(row, dict):
                continue
            dataset = row.get("Dataset") or row.get("dataset") or table.get("caption", "")
            scene = row.get("Scene") or row.get("scene") or ""
            for key, value in row.items():
                if re.search(r"PSNR|SSIM|LPIPS|FPS|MB|GB|Size|Time", str(key), re.I):
                    out[(norm(dataset).lower(), norm(scene).lower(), norm(key).lower())] = (norm(value), "", "")
    return out


def text_overlap(a: str, b: str, min_len: int = 180) -> bool:
    paras_a = [p.strip() for p in re.split(r"\n\s*\n", a) if len(p.strip()) >= min_len]
    paras_b = {p.strip() for p in re.split(r"\n\s*\n", b) if len(p.strip()) >= min_len}
    return any(p in paras_b for p in paras_a)


def validate(source_pack_path: Path, standard_json_path: Path, innovation_json_path: Path, review_json_path: Path, standard_md_path: Path | None = None, innovation_md_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    source_pack = load_json(source_pack_path)
    standard = load_json(standard_json_path)
    innovation = load_json(innovation_json_path)
    review = load_json(review_json_path)

    sp_paper = source_pack.get("paper", {}) if isinstance(source_pack.get("paper"), dict) else {}
    std_paper = standard.get("paper", {}) if isinstance(standard.get("paper"), dict) else {}
    inv_paper = innovation.get("paper", {}) if isinstance(innovation.get("paper"), dict) else {}
    rev_paper = review.get("paper", {}) if isinstance(review.get("paper"), dict) else {}
    for key in ("id", "title", "arxiv_id", "pdf_hash", "code_commit"):
        values = [norm(x.get(key)) for x in (sp_paper, std_paper, inv_paper, rev_paper) if norm(x.get(key))]
        if values and len(set(values)) > 1:
            errors.append(f"paper.{key} inconsistent across modes: {values}")

    sp_tables = {str(t.get("table_id")) for t in source_pack.get("experiment_tables", []) if isinstance(t, dict)}
    review_tables = {str(t.get("table_id")) for t in review.get("experiment_tables", []) if isinstance(t, dict) and t.get("table_id")}
    missing_tables = sorted(review_tables - sp_tables)
    if missing_tables:
        errors.append(f"review tables missing from Source Pack: {', '.join(missing_tables)}")

    std_results = standard.get("analysis", {}).get("main_results", []) if isinstance(standard.get("analysis"), dict) else []
    inv_results = innovation.get("analysis", {}).get("main_results", []) if isinstance(innovation.get("analysis"), dict) else []
    std_map = {metric_key(item): result_numbers(item) for item in std_results if isinstance(item, dict)}
    inv_map = {metric_key(item): result_numbers(item) for item in inv_results if isinstance(item, dict)}
    for key in sorted(set(std_map) & set(inv_map)):
        if std_map[key] != inv_map[key]:
            errors.append(f"metric numbers inconsistent for {key}: standard={std_map[key]} innovation={inv_map[key]}")

    std_diff = {json.dumps(item, ensure_ascii=False, sort_keys=True) for item in standard.get("analysis", {}).get("code_differences", []) if isinstance(item, dict)}
    inv_diff = {json.dumps(item, ensure_ascii=False, sort_keys=True) for item in innovation.get("analysis", {}).get("code_differences", []) if isinstance(item, dict)}
    if std_diff and inv_diff and std_diff != inv_diff:
        warnings.append("standard and innovation code_differences differ; inspect whether this is intended")

    if standard_md_path and innovation_md_path and standard_md_path.is_file() and innovation_md_path.is_file():
        if text_overlap(standard_md_path.read_text(encoding="utf-8"), innovation_md_path.read_text(encoding="utf-8")):
            errors.append("standard and innovation Markdown share a long identical paragraph")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {"schema_version": "1.0", "status": status, "errors": errors, "warnings": warnings}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate cross-mode consistency for one paper.")
    parser.add_argument("--source-pack", type=Path, required=True)
    parser.add_argument("--standard-json", type=Path, required=True)
    parser.add_argument("--innovation-json", type=Path, required=True)
    parser.add_argument("--review-json", type=Path, required=True)
    parser.add_argument("--standard-md", type=Path)
    parser.add_argument("--innovation-md", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.source_pack, args.standard_json, args.innovation_json, args.review_json, args.standard_md, args.innovation_md)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
