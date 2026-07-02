#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "schemas").is_dir() and (parent / "skills").is_dir():
            return parent
    return Path.cwd()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_errors(data: dict[str, Any]) -> list[str]:
    schema = load_json(repo_root() / "schemas" / "paper-source-pack.schema.json")
    validator = Draft202012Validator(schema)
    return [f"{'/'.join(map(str, err.absolute_path)) or '<root>'}: {err.message}" for err in sorted(validator.iter_errors(data), key=str)]


def duplicate_values(items: list[dict[str, Any]], key: str) -> list[str]:
    values = [str(item.get(key, "")) for item in items if isinstance(item, dict) and item.get(key)]
    return sorted({value for value in values if values.count(value) > 1})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def referenced_evidence_ids(data: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    for collection in ("equations", "figures", "experiment_tables", "code_map"):
        for item in data.get(collection, []) if isinstance(data.get(collection), list) else []:
            if isinstance(item, dict):
                refs.update(str(x) for x in item.get("evidence_ids", []) if x)
    return refs


def validate(path: Path, expected_pdf: Path | None = None, expected_code_commit: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    data: dict[str, Any] = {}
    if not path.is_file():
        errors.append(f"Source Pack missing: {path}")
    else:
        try:
            data = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"Source Pack JSON decode failed: {exc}")

    if data:
        errors.extend(f"schema: {msg}" for msg in schema_errors(data))
        evidence = data.get("evidence_ledger", []) if isinstance(data.get("evidence_ledger"), list) else []
        tables = data.get("experiment_tables", []) if isinstance(data.get("experiment_tables"), list) else []
        mappings = data.get("code_map", []) if isinstance(data.get("code_map"), list) else []
        for label, items, key in (
            ("evidence", evidence, "evidence_id"),
            ("table", tables, "table_id"),
            ("mapping", mappings, "mapping_id"),
        ):
            dupes = duplicate_values(items, key)
            if dupes:
                errors.append(f"duplicate {label} IDs: {', '.join(dupes)}")

        evidence_ids = {str(item.get("evidence_id")) for item in evidence if isinstance(item, dict)}
        missing_refs = sorted(referenced_evidence_ids(data) - evidence_ids)
        if missing_refs:
            errors.append(f"referenced evidence IDs missing from ledger: {', '.join(missing_refs)}")

        for table in tables:
            if not isinstance(table, dict):
                continue
            columns = table.get("columns", [])
            rows = table.get("rows", [])
            if not columns:
                errors.append(f"table {table.get('table_id', '<unknown>')} has no columns")
            if not isinstance(rows, list):
                errors.append(f"table {table.get('table_id', '<unknown>')} rows must be a list")
            if table.get("verification_status") == "unverified" and not table.get("uncertain_cells"):
                warnings.append(f"table {table.get('table_id', '<unknown>')} is unverified without uncertain_cells")

        provenance = data.get("provenance", {}) if isinstance(data.get("provenance"), dict) else {}
        paper = data.get("paper", {}) if isinstance(data.get("paper"), dict) else {}
        if provenance.get("pdf_hash") != paper.get("pdf_hash"):
            errors.append("provenance.pdf_hash and paper.pdf_hash differ")
        if expected_pdf:
            if not expected_pdf.is_file():
                errors.append(f"expected PDF does not exist: {expected_pdf}")
            else:
                actual = sha256_file(expected_pdf)
                if actual != paper.get("pdf_hash"):
                    errors.append("PDF hash does not match Source Pack")
        if expected_code_commit is not None and expected_code_commit != str(provenance.get("code_commit") or ""):
            errors.append("code commit does not match Source Pack provenance")
        if provenance.get("stale") is True:
            errors.append("Source Pack is marked stale")
        if not provenance.get("paper_version"):
            warnings.append("paper_version is empty; reuse must be checked manually")
        if not provenance.get("code_commit"):
            warnings.append("code_commit is empty; official code may be unavailable or unchecked")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {
        "schema_version": "1.0",
        "paper_id": (data.get("paper", {}) or {}).get("id", "") if data else "",
        "status": status,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a paper Source Pack.")
    parser.add_argument("--source-pack", type=Path, required=True)
    parser.add_argument("--expected-pdf", type=Path)
    parser.add_argument("--expected-code-commit")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = validate(args.source_pack, args.expected_pdf, args.expected_code_commit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(1 if result["status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
