#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from batch_common import ensure_batch_dirs, load_manifest, load_status, next_attempt, save_status, set_item_status
from build_task import build_task


def main() -> None:
    parser = argparse.ArgumentParser(description="Create retry prompts for failed analysis or quality gate items.")
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--paper-id")
    args = parser.parse_args()

    ensure_batch_dirs(args.batch_dir)
    status = load_status(args.batch_dir)
    target_ids = [args.paper_id] if args.paper_id else [
        paper_id
        for paper_id, item in status.get("items", {}).items()
        if item.get("status") in {"failed_analysis", "failed_quality_gate"}
    ]
    for paper_id in target_ids:
        item = status["items"].get(paper_id, {})
        validation_path = item.get("validation_path", "")
        details = ""
        if validation_path and Path(validation_path).is_file():
            details = Path(validation_path).read_text(encoding="utf-8")
        task_path = build_task(args.batch_dir, paper_id)
        retry_no = next_attempt(args.batch_dir, paper_id)
        retry_path = args.batch_dir / "retry-prompts" / f"{paper_id}.retry-{retry_no}.md"
        retry_path.write_text(
            f"上一轮未通过质量门槛，请修正并重新输出完整 Markdown 和 JSON。\n\n任务包：{task_path}\n\n校验详情：\n\n```json\n{details}\n```\n",
            encoding="utf-8",
        )
        set_item_status(status, paper_id, "retrying", attempts=retry_no, last_attempt=str(retry_path))
    save_status(args.batch_dir, status)
    print(f"retry prompts: {len(target_ids)}")


if __name__ == "__main__":
    main()
