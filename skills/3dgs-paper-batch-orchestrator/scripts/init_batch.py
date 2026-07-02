#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from batch_common import init_from_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a batch analysis directory from retrieval manifest.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--batch-id")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--profile", choices=["standard-analysis", "innovation-review"], default="standard-analysis")
    args = parser.parse_args()

    batch_id = args.batch_id
    if not batch_id:
        import json

        batch_id = str(json.loads(args.manifest.read_text(encoding="utf-8")).get("batch_id") or args.manifest.parent.name)
    output_dir = args.output_dir or Path("paper-batch-output") / batch_id
    manifest, status = init_from_manifest(args.manifest, output_dir, batch_id, args.profile)
    index = output_dir / "batch-index.md"
    lines = [f"# Batch {manifest['batch_id']}", "", f"- Profile: `{args.profile}`", "", "| ID | Title | Status |", "|---|---|---|"]
    for paper in manifest.get("papers", []):
        item = status["items"].get(paper["id"], {})
        lines.append(f"| {paper['id']} | {paper.get('title', '')} | {item.get('status', '')} |")
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"initialized {output_dir}")


if __name__ == "__main__":
    main()
