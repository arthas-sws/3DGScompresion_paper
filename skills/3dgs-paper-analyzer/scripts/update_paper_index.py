#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


ARXIV_VERSION_RE = re.compile(r"v\d+$", re.I)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", title.lower())).strip()


def canonical_key(record: dict[str, Any]) -> str:
    arxiv_id = str(record.get("arxiv_id") or "").strip()
    if arxiv_id:
        base = ARXIV_VERSION_RE.sub("", arxiv_id)
        return f"arxiv:{base.lower()}"
    doi = str(record.get("doi") or "").strip()
    if doi:
        return f"doi:{doi.lower()}"
    title = normalize_title(str(record.get("title") or ""))
    if title:
        return f"title:{title}"
    raise ValueError("cannot build canonical key without arxiv_id, doi, or title")


def build_record(review: dict[str, Any]) -> dict[str, Any]:
    paper = review.get("paper", {})
    index_card = review.get("index_card", {})
    return {
        "paper_id": paper.get("id", ""),
        "title": paper.get("title", ""),
        "arxiv_id": paper.get("arxiv_id", "") or "",
        "doi": paper.get("doi", "") or "",
        "pdf_hash": paper.get("pdf_hash", "") or "",
        "method_tags": index_card.get("method_tags", []),
        "innovation_tags": index_card.get("innovation_tags", []),
        "report_path": index_card.get("report_path", ""),
        "analysis_json_path": index_card.get("analysis_json_path", ""),
        "innovation_review_path": index_card.get("innovation_review_path", ""),
    }


def read_index(index_path: Path) -> list[dict[str, Any]]:
    if not index_path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"index line {line_no} is invalid JSON: {exc}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"index line {line_no} is not an object")
        records.append(item)
    return records


def atomic_write_jsonl(index_path: Path, records: list[dict[str, Any]]) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=index_path.name + ".", suffix=".tmp", dir=str(index_path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        os.replace(tmp_path, index_path)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        finally:
            raise


def upsert(index_path: Path, record: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    records = read_index(index_path)
    key = canonical_key(record)
    updated = False
    output: list[dict[str, Any]] = []
    for item in records:
        if canonical_key(item) == key:
            output.append(record)
            updated = True
        else:
            output.append(item)
    if not updated:
        output.append(record)

    if not dry_run:
        atomic_write_jsonl(index_path, output)
    return {
        "index": str(index_path),
        "canonical_key": key,
        "action": "updated" if updated else "inserted",
        "records": len(output),
        "dry_run": dry_run,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Atomically upsert an innovation-review index record.")
    parser.add_argument("--review-json", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    review = load_json(args.review_json)
    record = build_record(review)
    result = upsert(args.index, record, args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
