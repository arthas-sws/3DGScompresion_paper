#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(args: argparse.Namespace) -> dict[str, object]:
    pdf_hash = sha256_file(args.pdf_path) if args.pdf_path and args.pdf_path.is_file() else "0" * 64
    return {
        "schema_version": "1.0",
        "paper": {
            "id": args.paper_id,
            "title": args.title,
            "authors": [],
            "arxiv_id": args.arxiv_id or "",
            "source_url": args.source_url or "",
            "pdf_path": str(args.pdf_path or ""),
            "pdf_hash": pdf_hash,
            "paper_version": args.paper_version or "",
            "code_url": args.code_url or "",
            "code_commit": args.code_commit or "",
        },
        "source_boundary": {
            "paper": "stub generated; full paper facts must be filled before final analysis",
            "supplement": "not_checked",
            "project_page": "not_checked",
            "official_code": "not_checked",
            "related_papers": "not_checked",
        },
        "evidence_ledger": [
            {
                "evidence_id": "E001",
                "source_type": "paper",
                "location": "Paper identity",
                "page": None,
                "summary": "Paper identity and PDF path recorded by stub.",
                "verification_status": "partial",
                "source_path_or_url": str(args.pdf_path or args.source_url or ""),
                "source_version": args.paper_version or "",
            }
        ],
        "equations": [],
        "figures": [],
        "experiment_tables": [
            {
                "table_id": "T1",
                "caption": "Placeholder table; replace with verified paper table.",
                "source": "Paper Table pending",
                "source_page": None,
                "columns": ["Item", "Value"],
                "rows": [{"Item": "pending", "Value": "unverified"}],
                "extraction_method": "manual_transcription",
                "verification_status": "unverified",
                "uncertain_cells": ["all"],
                "comparability": "not_checked",
                "evidence_ids": ["E001"],
            }
        ],
        "code_map": [
            {
                "mapping_id": "M1",
                "paper_component": "official implementation",
                "paper_location": ["not_checked"],
                "code_location": [],
                "mapping_level": "not_found",
                "differences": [],
                "evidence_ids": ["E001"],
            }
        ],
        "reported_limitations": [],
        "unverified_items": ["stub generated; replace placeholders before delivery"],
        "provenance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "generator": "create_source_pack_stub.py",
            "pdf_hash": pdf_hash,
            "paper_version": args.paper_version or "",
            "code_commit": args.code_commit or "",
            "stale": False,
            "stale_reasons": [],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Source Pack stub for one paper.")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pdf-path", type=Path)
    parser.add_argument("--arxiv-id")
    parser.add_argument("--source-url")
    parser.add_argument("--paper-version")
    parser.add_argument("--code-url")
    parser.add_argument("--code-commit")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / f"{args.paper_id}.source-pack.json"
    if path.exists():
        raise SystemExit("Refusing to overwrite existing Source Pack.")
    path.write_text(json.dumps(build(args), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created {path}")


if __name__ == "__main__":
    main()
