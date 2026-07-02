#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REQUIRED_SECTIONS = [
    "备案卡片",
    "论文身份",
    "问题定义",
    "方法框架",
    "作者创新主张",
    "创新主张逐项解释",
    "关键实验表格",
    "实验对创新主张的支撑",
    "相似论文",
    "实际差别",
    "改进建议",
    "建议补充实验",
    "复现风险",
    "结论边界",
]

NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?")


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "schemas").is_dir() and (parent / "skills").is_dir():
            return parent
    return Path.cwd()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_validate_report():
    path = Path(__file__).resolve().parent / "validate_report.py"
    spec = importlib.util.spec_from_file_location("validate_report", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validate_report.py from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flatten_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        values: list[str] = []
        for child in value.values():
            values.extend(flatten_values(child))
        return values
    if isinstance(value, list):
        values = []
        for child in value:
            values.extend(flatten_values(child))
        return values
    return [str(value)]


def schema_errors(review: dict[str, Any]) -> list[str]:
    schema_path = repo_root() / "schemas" / "innovation-review.schema.json"
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    return [f"{'/'.join(map(str, err.absolute_path)) or '<root>'}: {err.message}" for err in sorted(validator.iter_errors(review), key=str)]


def load_index_records(index_path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not index_path.exists():
        return records
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


def validate(
    md_path: Path,
    json_path: Path,
    review_json_path: Path,
    manifest_path: Path | None = None,
    index_path: Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    base_validator = load_validate_report()
    base_result = base_validator.validate(md_path, json_path, manifest_path)
    if base_result.get("status") == "FAIL":
        errors.extend(f"base report: {msg}" for msg in base_result.get("errors", []))
    else:
        warnings.extend(f"base report: {msg}" for msg in base_result.get("warnings", []))

    md_text = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
    base = load_json(json_path) if json_path.is_file() else {}
    review = load_json(review_json_path) if review_json_path.is_file() else {}

    errors.extend(f"schema: {msg}" for msg in schema_errors(review))

    base_paper = base.get("paper", {}) if isinstance(base.get("paper"), dict) else {}
    review_paper = review.get("paper", {}) if isinstance(review.get("paper"), dict) else {}
    if base_paper.get("id") != review_paper.get("id"):
        errors.append("standard JSON and innovation review paper.id do not match")
    if base_paper.get("title") != review_paper.get("title"):
        errors.append("standard JSON and innovation review paper.title do not match")
    if review_paper.get("id") and str(review_paper.get("id")) not in md_text:
        warnings.append("Markdown does not mention review paper.id")
    if review_paper.get("title") and str(review_paper.get("title")) not in md_text:
        errors.append("Markdown title/content does not match innovation review paper.title")

    expected_ext = review_json_path.name
    ext = base.get("extensions", {}) if isinstance(base.get("extensions"), dict) else {}
    if ext.get("innovation_review") and Path(str(ext["innovation_review"])).name != expected_ext:
        errors.append("standard JSON extensions.innovation_review does not point to review JSON")

    for section in REQUIRED_SECTIONS:
        if section not in md_text:
            errors.append(f"Markdown missing innovation-review section/content: {section}")

    claims = review.get("innovation_claims", []) if isinstance(review.get("innovation_claims"), list) else []
    claim_ids = [item.get("claim_id") for item in claims if isinstance(item, dict)]
    duplicate_claims = sorted({cid for cid in claim_ids if claim_ids.count(cid) > 1})
    if duplicate_claims:
        errors.append(f"duplicate claim IDs: {', '.join(duplicate_claims)}")
    claim_set = set(claim_ids)
    for claim in claims:
        if not claim.get("evidence"):
            errors.append(f"claim {claim.get('claim_id', '<unknown>')} missing evidence")

    tables = review.get("experiment_tables", []) if isinstance(review.get("experiment_tables"), list) else []
    table_ids = [item.get("table_id") for item in tables if isinstance(item, dict)]
    duplicate_tables = sorted({tid for tid in table_ids if table_ids.count(tid) > 1})
    if duplicate_tables:
        errors.append(f"duplicate table IDs: {', '.join(duplicate_tables)}")
    for table in tables:
        if not table.get("evidence"):
            errors.append(f"table {table.get('table_id', '<unknown>')} missing evidence")

    audited_claims: set[str] = set()
    for audit in review.get("experiment_audit", []):
        claim_id = audit.get("claim_id")
        if claim_id not in claim_set:
            errors.append(f"experiment_audit references unknown claim_id: {claim_id}")
        audited_claims.add(claim_id)
    for claim_id in sorted(claim_set - audited_claims):
        errors.append(f"claim {claim_id} has no experiment_audit entry")

    for exp in review.get("proposed_experiments", []):
        claim_id = exp.get("claim_id")
        if claim_id != "general" and claim_id not in claim_set:
            errors.append(f"proposed_experiments references unknown claim_id: {claim_id}")

    for idea in review.get("improvement_ideas", []):
        target = idea.get("targets_claim")
        if target != "general" and target not in claim_set:
            errors.append(f"improvement_ideas references unknown targets_claim: {target}")

    review_values = "\n".join(flatten_values(review))
    for table in tables:
        for row in table.get("rows", []):
            for number in NUMBER_RE.findall(json.dumps(row, ensure_ascii=False)):
                if number and number not in md_text:
                    warnings.append(f"table number appears in review JSON but not Markdown: {number}")
                if number and number not in review_values:
                    errors.append(f"internal number sync failed for: {number}")

    index_card = review.get("index_card", {}) if isinstance(review.get("index_card"), dict) else {}
    for key in ("report_path", "analysis_json_path", "innovation_review_path"):
        value = index_card.get(key)
        if value:
            candidate = Path(value)
            if not candidate.is_absolute():
                candidate = review_json_path.parent / candidate
            if not candidate.exists():
                alt = repo_root() / str(value)
                if not alt.exists():
                    warnings.append(f"index_card.{key} path does not exist: {value}")

    if index_path:
        try:
            records = load_index_records(index_path)
        except ValueError as exc:
            errors.append(str(exc))
            records = []
        matches = [item for item in records if item.get("paper_id") == review_paper.get("id") and item.get("title") == review_paper.get("title")]
        if len(matches) != 1:
            errors.append(f"index must contain exactly one current paper record when --index is used, found {len(matches)}")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {
        "schema_version": "1.0",
        "paper_id": review_paper.get("id", ""),
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "base_report_status": base_result.get("status"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate innovation-review mode outputs.")
    parser.add_argument("--md", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True, help="Standard paper-analysis JSON")
    parser.add_argument("--review-json", type=Path, required=True, help="Innovation review extension JSON")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--index", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    result = validate(args.md, args.json, args.review_json, args.manifest, args.index)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if result["status"] == "FAIL":
        raise SystemExit(1)
    if result["status"] == "WARN" and args.strict:
        raise SystemExit(2)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
