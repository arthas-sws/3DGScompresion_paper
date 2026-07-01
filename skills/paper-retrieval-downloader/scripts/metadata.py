#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from fetch import build_id_url, fetch_feed, parse_feed
from retrieval_common import deduplicate_items, normalize_arxiv_id, utc_now_iso, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch arXiv metadata for explicit IDs.")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--arxiv-id", action="append", default=[])
    parser.add_argument("--input-list", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ids: list[str] = []
    for value in args.arxiv_id:
        base, _ = normalize_arxiv_id(value)
        if base:
            ids.append(base)
    if args.input_list:
        for line in args.input_list.read_text(encoding="utf-8").splitlines():
            base, _ = normalize_arxiv_id(line.strip())
            if base:
                ids.append(base)

    ids = sorted(set(ids))
    candidates = parse_feed(fetch_feed(build_id_url(ids), args.timeout)) if ids else []
    write_json(
        args.output,
        {
            "schema_version": "1.0",
            "batch_id": args.batch_id,
            "created_at": utc_now_iso(),
            "query": {"keywords": [], "date_from": None, "date_to": None, "source": "arxiv-id-list"},
            "candidates": deduplicate_items(candidates),
        },
    )
    print(f"wrote metadata for {len(candidates)} papers to {args.output}")


if __name__ == "__main__":
    main()
