#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from batch_common import (
    ensure_batch_dirs,
    find_paper,
    load_manifest,
    load_status,
    locate_analyzer_skill,
    next_attempt,
    save_status,
    set_item_status,
)


def render_template(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def build_task(batch_dir: Path, paper_id: str) -> Path:
    ensure_batch_dirs(batch_dir)
    manifest = load_manifest(batch_dir)
    status = load_status(batch_dir)
    paper = find_paper(manifest, paper_id)
    if not paper:
        raise SystemExit(f"paper id not found in manifest: {paper_id}")
    analyzer = locate_analyzer_skill()
    if not analyzer:
        raise SystemExit("3dgs-paper-analyzer/SKILL.md not found")

    attempt = next_attempt(batch_dir, paper_id)
    template_path = Path(__file__).resolve().parents[1] / "templates" / "item-task-prompt.md"
    template = template_path.read_text(encoding="utf-8")
    profile = str(status.get("profile") or "standard-analysis")
    output_md = batch_dir / "items" / f"{paper_id}.md"
    output_json = batch_dir / "items" / f"{paper_id}.json"
    output_review_json = batch_dir / "items" / f"{paper_id}.innovation-review.json"
    if profile == "innovation-review":
        profile_instructions = (
            "Use `3dgs-paper-analyzer` in `innovation-review` mode. "
            "You must still write the standard Markdown and standard JSON, and additionally write "
            f"`{output_review_json}` following `schemas/innovation-review.schema.json`. "
            "Set standard JSON `extensions.innovation_review` to the extension JSON filename. "
            "Do not download related papers silently; write a retrieval request list if key related PDFs are missing."
        )
    else:
        profile_instructions = "Use `3dgs-paper-analyzer` in default `standard-analysis` mode."
    prompt = render_template(
        template,
        {
            "PROFILE": profile,
            "PROFILE_INSTRUCTIONS": profile_instructions,
            "PAPER_ID": paper_id,
            "TITLE": str(paper.get("title", "")),
            "AUTHORS": ", ".join(paper.get("authors", [])),
            "ARXIV_ID": str(paper.get("arxiv_id", "")),
            "SOURCE_URL": str(paper.get("source_url", "")),
            "PDF_PATH": str((batch_dir / paper.get("local_pdf", "")).resolve()),
            "CODE_URL": str(paper.get("code_url", "")),
            "OUTPUT_MD": str(output_md),
            "OUTPUT_JSON": str(output_json),
            "OUTPUT_REVIEW_JSON": str(output_review_json),
        },
    )
    prompt = f"Analyzer skill: {analyzer}\n\n" + prompt
    prompt_path = batch_dir / "attempts" / f"{paper_id}.attempt-{attempt}.prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    set_item_status(status, paper_id, "waiting_for_agent", attempts=attempt, last_attempt=str(prompt_path), errors=[], warnings=[])
    save_status(batch_dir, status)
    return prompt_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an isolated task prompt for one paper.")
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--paper-id", required=True)
    args = parser.parse_args()
    print(build_task(args.batch_dir, args.paper_id))


if __name__ == "__main__":
    main()
