#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

from batch_common import load_manifest, load_status, repo_root, save_status, set_item_status, write_json


def load_analyzer_validator():
    path = repo_root() / "skills" / "3dgs-paper-analyzer" / "scripts" / "validate_report.py"
    spec = importlib.util.spec_from_file_location("validate_report", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load analyzer validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_innovation_validator():
    path = repo_root() / "skills" / "3dgs-paper-analyzer" / "scripts" / "validate_innovation_review.py"
    spec = importlib.util.spec_from_file_location("validate_innovation_review", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load innovation validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_source_pack_validator():
    path = repo_root() / "skills" / "3dgs-paper-analyzer" / "scripts" / "validate_source_pack.py"
    spec = importlib.util.spec_from_file_location("validate_source_pack", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load source pack validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_item(batch_dir: Path, paper_id: str) -> dict[str, Any]:
    manifest_path = batch_dir / "manifest.json"
    md_path = batch_dir / "items" / f"{paper_id}.md"
    json_path = batch_dir / "items" / f"{paper_id}.json"
    source_pack_path = batch_dir / "items" / f"{paper_id}.source-pack.json"
    status = load_status(batch_dir)
    profile = str(status.get("profile") or "standard-analysis")
    source_pack_validator = load_source_pack_validator()
    source_pack_result = source_pack_validator.validate(source_pack_path)
    validator = load_analyzer_validator()
    result = validator.validate(md_path, json_path, manifest_path)
    if source_pack_result.get("status") == "FAIL":
        result = {
            "schema_version": "1.0",
            "paper_id": paper_id,
            "status": "FAIL",
            "errors": source_pack_result.get("errors", []) + result.get("errors", []),
            "warnings": source_pack_result.get("warnings", []) + result.get("warnings", []),
            "source_pack_status": source_pack_result.get("status"),
            "standard_report_status": result.get("status"),
        }
    if profile == "innovation-review":
        review_json_path = batch_dir / "items" / f"{paper_id}.innovation-review.json"
        innovation_validator = load_innovation_validator()
        innovation_result = innovation_validator.validate(md_path, json_path, review_json_path, manifest_path)
        result = {
            "schema_version": "1.0",
            "paper_id": paper_id,
            "status": "FAIL" if source_pack_result.get("status") == "FAIL" or result.get("status") == "FAIL" or innovation_result.get("status") == "FAIL" else ("WARN" if source_pack_result.get("status") == "WARN" or result.get("status") == "WARN" or innovation_result.get("status") == "WARN" else "PASS"),
            "errors": source_pack_result.get("errors", []) + result.get("errors", []) + innovation_result.get("errors", []),
            "warnings": source_pack_result.get("warnings", []) + result.get("warnings", []) + innovation_result.get("warnings", []),
            "source_pack_status": source_pack_result.get("status"),
            "standard_report_status": result.get("status"),
            "innovation_review_status": innovation_result.get("status"),
        }
    else:
        result["source_pack_status"] = source_pack_result.get("status")
    validation_path = batch_dir / "validation" / f"{paper_id}.json"
    write_json(validation_path, result)

    state = "validated" if result["status"] in ("PASS", "WARN") else "failed_quality_gate"
    set_item_status(
        status,
        paper_id,
        state,
        validation_path=str(validation_path),
        report_path=str(md_path),
        json_path=str(json_path),
        source_pack_path=str(source_pack_path),
        innovation_review_path=str(batch_dir / "items" / f"{paper_id}.innovation-review.json") if profile == "innovation-review" else "",
        errors=result.get("errors", []),
        warnings=result.get("warnings", []),
    )
    save_status(batch_dir, status)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate one batch item using analyzer quality gate.")
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    args = parser.parse_args()
    result = validate_item(args.batch_dir, args.paper_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
