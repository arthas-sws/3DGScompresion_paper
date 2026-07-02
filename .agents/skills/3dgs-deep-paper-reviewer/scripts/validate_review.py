#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = [
    "schema_version",
    "paper",
    "index_card",
    "innovation_claims",
    "experiment_tables",
    "experiment_audit",
    "improvement_ideas",
    "proposed_experiments",
    "related_papers",
    "validation",
]

FORBIDDEN_NOVELTY_PHRASES = [
    "not novel",
    "already covered",
    "novelty rejected",
    "innovation is not new",
    "不新",
    "已经被覆盖",
    "缺乏创新性",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_key(record: dict[str, Any]) -> str:
    paper = record.get("paper", {})
    title = str(paper.get("title") or "").strip().lower()
    arxiv_id = str(paper.get("arxiv_id") or "").strip().lower()
    pdf_hash = str(paper.get("pdf_hash") or "").strip().lower()
    return hashlib.sha256(f"{title}|{arxiv_id}|{pdf_hash}".encode("utf-8")).hexdigest()


def validate(data: dict[str, Any], md_text: str | None = None, index_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"missing top-level field: {key}")

    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")

    paper = data.get("paper", {})
    if not paper.get("title"):
        errors.append("paper.title is required")
    if not paper.get("id"):
        errors.append("paper.id is required")
    if not paper.get("pdf_path"):
        errors.append("paper.pdf_path is required")

    index_card = data.get("index_card", {})
    for key in ["task", "method_tags", "innovation_tags", "one_sentence_takeaway", "report_path", "json_path"]:
        if key not in index_card:
            errors.append(f"index_card.{key} is required")

    claims = data.get("innovation_claims", [])
    if not isinstance(claims, list) or not claims:
        warnings.append("innovation_claims is empty")
    claim_ids = {c.get("claim_id") for c in claims if isinstance(c, dict)}

    for audit in data.get("experiment_audit", []):
        claim_id = audit.get("claim_id")
        if claim_id and claim_id not in claim_ids:
            warnings.append(f"experiment_audit references unknown claim_id: {claim_id}")

    for exp in data.get("proposed_experiments", []):
        claim_id = exp.get("claim_id")
        if claim_id and claim_id != "general" and claim_id not in claim_ids:
            warnings.append(f"proposed_experiments references unknown claim_id: {claim_id}")

    for table in data.get("experiment_tables", []):
        status = table.get("extraction_status")
        entry_method = table.get("entry_method")
        if status == "auto_failed" and entry_method == "automatic":
            errors.append(f"{table.get('table_id', '<unknown>')}: auto_failed cannot have automatic entry_method")
        if entry_method == "manual_transcription" and status not in {"auto_failed", "manual_transcription", "partial"}:
            warnings.append(f"{table.get('table_id', '<unknown>')}: manual transcription should record auto_failed/manual/partial status")
        if not table.get("evidence"):
            errors.append(f"{table.get('table_id', '<unknown>')}: missing evidence")

    combined_text = json.dumps(data, ensure_ascii=False)
    if md_text:
        combined_text += "\n" + md_text
    lowered = combined_text.lower()
    for phrase in FORBIDDEN_NOVELTY_PHRASES:
        if phrase.lower() in lowered:
            errors.append(f"forbidden novelty-rejection phrase found: {phrase}")

    if index_path and index_path.exists():
        this_key = stable_key(data)
        matches = 0
        for line_no, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"index line {line_no} is not valid JSON")
                continue
            if stable_key({"paper": item.get("paper", item)}) == this_key:
                matches += 1
        if matches > 1:
            errors.append("paper-index.jsonl contains duplicate records for title + arxiv_id + pdf_hash")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {"schema_version": "1.0", "status": status, "errors": errors, "warnings": warnings}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a 3DGS deep paper review JSON/Markdown pair.")
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--md", type=Path)
    parser.add_argument("--index", type=Path)
    args = parser.parse_args()

    data = load_json(args.json)
    md_text = args.md.read_text(encoding="utf-8") if args.md and args.md.exists() else None
    result = validate(data, md_text, args.index)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] != "FAIL" else 1)


if __name__ == "__main__":
    main()
