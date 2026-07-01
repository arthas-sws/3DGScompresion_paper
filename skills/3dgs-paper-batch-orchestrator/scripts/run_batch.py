#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from batch_common import (
    ensure_batch_dirs,
    find_paper,
    init_from_manifest,
    load_manifest,
    load_status,
    save_status,
    set_item_status,
)
from build_task import build_task
from validate_item import validate_item


def run(batch_dir: Path, manifest_path: Path | None = None, max_retries: int = 2) -> None:
    if manifest_path and not (batch_dir / "manifest.json").is_file():
        init_from_manifest(manifest_path, batch_dir)
    ensure_batch_dirs(batch_dir)
    manifest = load_manifest(batch_dir)
    status = load_status(batch_dir)

    for paper in manifest.get("papers", []):
        paper_id = str(paper.get("id", ""))
        item = status.get("items", {}).get(paper_id, {})
        if item.get("status") == "validated":
            continue
        pdf_path = batch_dir / str(paper.get("local_pdf", ""))
        if not pdf_path.is_file():
            set_item_status(status, paper_id, "failed_source", errors=[f"missing PDF: {paper.get('local_pdf', '')}"])
            save_status(batch_dir, status)
            continue
        md_path = batch_dir / "items" / f"{paper_id}.md"
        json_path = batch_dir / "items" / f"{paper_id}.json"
        if md_path.is_file() and json_path.is_file():
            set_item_status(status, paper_id, "validating")
            save_status(batch_dir, status)
            validate_item(batch_dir, paper_id)
            continue
        attempts = int(item.get("attempts", 0))
        if attempts >= max_retries + 1:
            set_item_status(status, paper_id, "failed_analysis", errors=["maximum task attempts reached without output"])
            save_status(batch_dir, status)
            continue
        build_task(batch_dir, paper_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare, resume, and validate a batch. Does not pretend to auto-run Codex agents.")
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--max-retries", type=int, default=2)
    args = parser.parse_args()
    run(args.batch_dir, args.manifest, args.max_retries)
    print(f"batch checked: {args.batch_dir}")


if __name__ == "__main__":
    main()
