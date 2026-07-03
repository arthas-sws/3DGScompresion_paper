#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from batch_common import load_manifest, load_status, read_json


def validate(batch_dir: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest = load_manifest(batch_dir)
    status = load_status(batch_dir)
    manifest_ids = {p.get("id") for p in manifest.get("papers", []) if isinstance(p, dict)}

    for paper_id, item in status.get("items", {}).items():
        if paper_id not in manifest_ids:
            errors.append(f"status contains unknown paper id: {paper_id}")
        if item.get("status") == "validated":
            if not (batch_dir / "items" / f"{paper_id}.md").is_file():
                errors.append(f"validated item missing Markdown: {paper_id}")
            if not (batch_dir / "items" / f"{paper_id}.json").is_file():
                errors.append(f"validated item missing JSON: {paper_id}")
            html_path = batch_dir / "items" / f"{paper_id}.html"
            if not html_path.is_file() or html_path.stat().st_size == 0:
                errors.append(f"validated item missing or empty HTML: {paper_id}")
            validation_path = batch_dir / "items" / f"{paper_id}.validation.json"
            if not validation_path.is_file():
                errors.append(f"validated item missing validation JSON: {paper_id}")
            elif read_json(validation_path).get("completion_status") not in {"COMPLETE", "COMPLETE_WITH_WARNINGS"}:
                errors.append(f"validated item does not have successful finalization: {paper_id}")

    matrix_path = batch_dir / "result-matrix.json"
    if matrix_path.is_file():
        matrix = read_json(matrix_path)
        matrix_ids = {p.get("id") for p in matrix.get("papers", []) if isinstance(p, dict)}
        result_ids = {r.get("paper_id") for r in matrix.get("results", []) if isinstance(r, dict)}
        validated_ids = {pid for pid, item in status.get("items", {}).items() if item.get("status") == "validated"}
        if not matrix_ids.issubset(validated_ids):
            errors.append("result matrix includes non-validated papers")
        if not result_ids.issubset(validated_ids):
            errors.append("result rows include non-validated papers")
        if not (matrix_ids | result_ids).issubset(manifest_ids):
            errors.append("result matrix contains paper IDs outside manifest")
        for result in matrix.get("results", []):
            if isinstance(result, dict) and not result.get("comparability"):
                errors.append(f"result missing comparability: {result.get('paper_id')}")
            if isinstance(result, dict) and not result.get("evidence"):
                errors.append(f"result missing evidence: {result.get('paper_id')}")
    else:
        warnings.append("result-matrix.json not generated yet")

    failed_path = batch_dir / "failed-items.md"
    failed_status_ids = [pid for pid, item in status.get("items", {}).items() if item.get("status") != "validated"]
    if failed_status_ids and not failed_path.is_file():
        errors.append("failed-items.md missing while failed/waiting items exist")

    return {
        "schema_version": "1.0",
        "batch_id": manifest.get("batch_id", batch_dir.name),
        "status": "FAIL" if errors else ("WARN" if warnings else "PASS"),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate batch aggregation and status consistency.")
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = validate(args.batch_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    raise SystemExit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
