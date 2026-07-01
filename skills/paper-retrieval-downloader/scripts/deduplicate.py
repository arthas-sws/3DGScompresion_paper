#!/usr/bin/env python3
from __future__ import annotations

import argparse

from retrieval_common import deduplicate_items, extract_candidates, read_json, utc_now_iso, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Deduplicate paper candidates.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload = read_json(args.input)
    candidates = extract_candidates(payload)
    deduped = deduplicate_items(candidates)
    write_json(
        args.output,
        {
            "schema_version": "1.0",
            "batch_id": payload.get("batch_id", "deduped"),
            "created_at": utc_now_iso(),
            "query": payload.get("query", {}),
            "candidates": deduped,
        },
    )
    print(f"deduplicated {len(candidates)} candidates to {len(deduped)}")


if __name__ == "__main__":
    main()
