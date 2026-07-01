#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from retrieval_common import candidate_key, deduplicate_items, extract_candidates, read_json, utc_now_iso, write_json


def load_keys(paths: list[Path]) -> set[str]:
    keys: set[str] = set()
    for path in paths:
        payload = read_json(path)
        for item in extract_candidates(payload):
            key, _ = candidate_key(item)
            keys.add(key)
    return keys


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute candidate difference against existing manifests or candidate JSON files.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--against", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = read_json(args.input)
    candidates = deduplicate_items(extract_candidates(payload))
    existing = load_keys(args.against)
    new_items = []
    duplicates = []
    for item in candidates:
        key, _ = candidate_key(item)
        if key in existing:
            duplicates.append(item)
        else:
            new_items.append(item)
    write_json(
        args.output,
        {
            "schema_version": "1.0",
            "batch_id": payload.get("batch_id", "diff"),
            "created_at": utc_now_iso(),
            "query": payload.get("query", {}),
            "new": new_items,
            "duplicates": duplicates,
        },
    )
    print(f"new={len(new_items)} duplicates={len(duplicates)}")


if __name__ == "__main__":
    main()
