#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from retrieval_common import read_json


def validate(manifest_path: Path) -> dict[str, object]:
    manifest = read_json(manifest_path)
    root = manifest_path.parent
    errors: list[str] = []
    warnings: list[str] = []
    papers = manifest.get("papers", [])
    if manifest.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if not isinstance(papers, list):
        errors.append("papers must be a list")
        papers = []
    ids = [paper.get("id") for paper in papers if isinstance(paper, dict)]
    if len(ids) != len(set(ids)):
        errors.append("paper IDs are not unique")
    for paper in papers:
        if not isinstance(paper, dict):
            errors.append("paper entry is not an object")
            continue
        for key in ("id", "title", "authors", "source_url", "pdf_url", "local_pdf", "download_status", "metadata_status"):
            if key not in paper:
                errors.append(f"{paper.get('id', '<unknown>')} missing {key}")
        local_pdf = str(paper.get("local_pdf", ""))
        if paper.get("download_status") in {"downloaded", "skipped_existing"} and not (root / local_pdf).is_file():
            errors.append(f"{paper.get('id')} marks PDF available but file is missing: {local_pdf}")
        metadata_path = str(paper.get("metadata_path", ""))
        if metadata_path and not (root / metadata_path).is_file():
            warnings.append(f"{paper.get('id')} metadata file is missing: {metadata_path}")
        dedup = paper.get("deduplication", {})
        if not isinstance(dedup, dict) or not dedup.get("canonical_key"):
            warnings.append(f"{paper.get('id')} has no deduplication canonical key")

    failures_path = root / "failures.json"
    if failures_path.is_file():
        failures = read_json(failures_path).get("failures", [])
        failed_ids = {f.get("id") for f in failures if isinstance(f, dict)}
        for paper in papers:
            if paper.get("download_status") == "failed" and paper.get("id") not in failed_ids:
                errors.append(f"{paper.get('id')} failed download is not recorded in failures.json")
    else:
        warnings.append("failures.json is missing")

    return {
        "status": "FAIL" if errors else ("WARN" if warnings else "PASS"),
        "errors": errors,
        "warnings": warnings,
        "paper_count": len(papers),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate retrieval manifest output.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = validate(args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    raise SystemExit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
