#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

from batch_common import load_status, repo_root, save_status, set_item_status, write_json


def load_finalizer():
    path = repo_root() / "skills" / "3dgs-paper-analyzer" / "scripts" / "finalize_report.py"
    spec = importlib.util.spec_from_file_location("finalize_report", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load analyzer finalizer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def html_ok(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    text = path.read_text(encoding="utf-8")
    return "<html" in text.lower() or "<!doctype html" in text.lower()


def validate_item(batch_dir: Path, paper_id: str) -> dict[str, Any]:
    md_path = batch_dir / "items" / f"{paper_id}.md"
    json_path = batch_dir / "items" / f"{paper_id}.json"
    source_pack_path = batch_dir / "items" / f"{paper_id}.source-pack.json"
    html_path = batch_dir / "items" / f"{paper_id}.html"
    item_validation_path = batch_dir / "items" / f"{paper_id}.validation.json"
    status = load_status(batch_dir)
    profile = str(status.get("profile") or "standard-analysis")
    finalizer = load_finalizer()
    result = finalizer.finalize(profile, paper_id, batch_dir / "items", strict=(profile == "innovation-review"))
    result["required_files"] = {
        "source_pack": str(source_pack_path),
        "markdown": str(md_path),
        "json": str(json_path),
        "html": str(html_path),
        "validation": str(item_validation_path),
    }
    if profile == "innovation-review":
        result["required_files"]["innovation_review"] = str(batch_dir / "items" / f"{paper_id}.innovation-review.json")
    if result.get("completion_status") in {"COMPLETE", "COMPLETE_WITH_WARNINGS"} and not html_ok(html_path):
        result["completion_status"] = "INCOMPLETE"
        result["status"] = "FAIL"
        result.setdefault("errors", []).append("HTML missing, empty, or invalid")
    if result.get("completion_status") in {"COMPLETE", "COMPLETE_WITH_WARNINGS"} and not item_validation_path.is_file():
        result["completion_status"] = "INCOMPLETE"
        result["status"] = "FAIL"
        result.setdefault("errors", []).append("item validation JSON missing")

    validation_path = batch_dir / "validation" / f"{paper_id}.json"
    write_json(validation_path, result)

    state = "validated" if result.get("completion_status") in {"COMPLETE", "COMPLETE_WITH_WARNINGS"} else "failed_quality_gate"
    set_item_status(
        status,
        paper_id,
        state,
        validation_path=str(validation_path),
        report_path=str(md_path),
        json_path=str(json_path),
        source_pack_path=str(source_pack_path),
        html_path=str(html_path),
        item_validation_path=str(item_validation_path),
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
