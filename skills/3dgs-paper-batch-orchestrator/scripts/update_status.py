#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from batch_common import load_status, save_status, set_item_status


def main() -> None:
    parser = argparse.ArgumentParser(description="Update one paper status in status.json.")
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--error", action="append", default=[])
    parser.add_argument("--warning", action="append", default=[])
    args = parser.parse_args()

    status = load_status(args.batch_dir)
    set_item_status(status, args.paper_id, args.status, errors=args.error, warnings=args.warning)
    save_status(args.batch_dir, status)
    print(f"{args.paper_id}: {args.status}")


if __name__ == "__main__":
    main()
