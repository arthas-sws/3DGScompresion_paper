#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REQUIRED_SECTIONS = [
    "评审卡片",
    "论文身份与分析边界",
    "创新评审深度",
    "问题定义与方法定位",
    "作者创新主张总览",
    "创新主张逐项审计",
    "Claim—Evidence 矩阵",
    "关键实验结果",
    "实验支撑缺口",
    "最近前作与相似论文",
    "方法改进优先级",
    "建议补充实验",
    "复现和实现风险",
    "创新性结论边界",
]
MATRIX_VALUES = {"直接", "部分", "间接", "无", "冲突"}
SUPPORT_TO_MATRIX = {
    "direct": "直接",
    "partial": "部分",
    "indirect": "间接",
    "none": "无",
    "conflict": "冲突",
}


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "schemas").is_dir() and (parent / "skills").is_dir():
            return parent
    return Path.cwd()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_validator(name: str, filename: str):
    path = Path(__file__).resolve().parent / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def schema_errors(review: dict[str, Any]) -> list[str]:
    schema = load_json(repo_root() / "schemas" / "innovation-review.schema.json")
    validator = Draft202012Validator(schema)
    return [f"{'/'.join(map(str, err.absolute_path)) or '<root>'}: {err.message}" for err in sorted(validator.iter_errors(review), key=str)]


def resolve_sibling(path_value: str, base_file: Path) -> Path:
    candidate = Path(path_value)
    return candidate if candidate.is_absolute() else base_file.parent / candidate


def duplicate_values(items: list[dict[str, Any]], key: str) -> list[str]:
    values = [str(item.get(key, "")) for item in items if isinstance(item, dict) and item.get(key)]
    return sorted({value for value in values if values.count(value) > 1})


def validate(md_path: Path, json_path: Path, review_json_path: Path, manifest_path: Path | None = None, index_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    base_validator = load_validator("validate_report", "validate_report.py")
    base_result = base_validator.validate(md_path, json_path, manifest_path)
    if base_result.get("status") == "FAIL":
        errors.extend(f"base report: {msg}" for msg in base_result.get("errors", []))
    else:
        warnings.extend(f"base report: {msg}" for msg in base_result.get("warnings", []))

    md_text = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
    base = load_json(json_path) if json_path.is_file() else {}
    review = load_json(review_json_path) if review_json_path.is_file() else {}

    if review.get("schema_version") != "1.1":
        errors.append("innovation-review schema_version must be 1.1; migrate old 1.0 outputs explicitly")
    errors.extend(f"schema: {msg}" for msg in schema_errors(review))

    base_paper = base.get("paper", {}) if isinstance(base.get("paper"), dict) else {}
    review_paper = review.get("paper", {}) if isinstance(review.get("paper"), dict) else {}
    for key in ("id", "title", "arxiv_id", "pdf_hash", "code_commit"):
        base_value = base_paper.get(key) or base.get(key)
        review_value = review_paper.get(key)
        if base_value and review_value and base_value != review_value:
            errors.append(f"standard JSON and innovation review differ on paper.{key}")
    if review_paper.get("title") and str(review_paper.get("title")) not in md_text:
        errors.append("Markdown title/content does not match innovation review paper.title")

    expected_ext = review_json_path.name
    ext = base.get("extensions", {}) if isinstance(base.get("extensions"), dict) else {}
    if ext.get("innovation_review") and Path(str(ext["innovation_review"])).name != expected_ext:
        errors.append("standard JSON extensions.innovation_review does not point to review JSON")

    sp_path_value = review.get("source_pack_path")
    if isinstance(sp_path_value, str) and sp_path_value:
        sp_path = resolve_sibling(sp_path_value, review_json_path)
        sp_validator = load_validator("validate_source_pack", "validate_source_pack.py")
        sp_result = sp_validator.validate(sp_path)
        if sp_result.get("status") == "FAIL":
            errors.extend(f"source pack: {msg}" for msg in sp_result.get("errors", []))
        else:
            warnings.extend(f"source pack: {msg}" for msg in sp_result.get("warnings", []))
    else:
        errors.append("innovation review missing source_pack_path")

    for section in REQUIRED_SECTIONS:
        if section not in md_text:
            errors.append(f"Markdown missing innovation-review section/content: {section}")
    if re.search(r"##\s*附录：完整实验表格", md_text) is None:
        errors.append("Markdown missing folded/appendix full experiment table section")
    if md_text.count("|---") > 20 and "附录：完整实验表格" not in md_text:
        errors.append("innovation main body appears to repeat too many raw tables outside appendix")

    claims = review.get("innovation_claims", []) if isinstance(review.get("innovation_claims"), list) else []
    claim_ids = [item.get("claim_id") for item in claims if isinstance(item, dict)]
    duplicate_claims = duplicate_values(claims, "claim_id")
    if duplicate_claims:
        errors.append(f"duplicate claim IDs: {', '.join(duplicate_claims)}")
    claim_set = set(claim_ids)
    for claim in claims:
        claim_id = claim.get("claim_id", "<unknown>")
        for key in ("title", "author_claim", "interpretation", "method_location", "code_location", "evidence_ids", "support_level", "missing_evidence", "closest_prior_work", "differentiators", "confidence"):
            if key not in claim or claim.get(key) in ("", [], None):
                if key in ("counter_evidence_ids", "missing_evidence", "closest_prior_work", "differentiators"):
                    continue
                errors.append(f"claim {claim_id} missing required field: {key}")
        if f"### {claim_id}" not in md_text:
            errors.append(f"Markdown missing Claim card heading for {claim_id}")

    matrix = review.get("claim_evidence_matrix", []) if isinstance(review.get("claim_evidence_matrix"), list) else []
    matrix_claims = {item.get("claim_id") for item in matrix if isinstance(item, dict)}
    if claim_set - matrix_claims:
        errors.append(f"Claim-Evidence matrix missing claims: {', '.join(sorted(claim_set - matrix_claims))}")
    for row in matrix:
        if not isinstance(row, dict):
            continue
        claim_id = row.get("claim_id")
        if claim_id not in claim_set:
            errors.append(f"Claim-Evidence matrix references unknown claim_id: {claim_id}")
        for key in ("theory", "main_results", "ablation", "efficiency", "failure_cases", "code"):
            if row.get(key) not in MATRIX_VALUES:
                errors.append(f"matrix {claim_id}.{key} must be one of {', '.join(sorted(MATRIX_VALUES))}")

    audit_claims: set[str] = set()
    for audit in review.get("experiment_audit", []) if isinstance(review.get("experiment_audit"), list) else []:
        claim_id = audit.get("claim_id")
        if claim_id not in claim_set:
            errors.append(f"experiment_audit references unknown claim_id: {claim_id}")
        audit_claims.add(claim_id)
        claim = next((c for c in claims if c.get("claim_id") == claim_id), {})
        expected = SUPPORT_TO_MATRIX.get(str(audit.get("support_level")))
        row = next((r for r in matrix if r.get("claim_id") == claim_id), {})
        if expected and row and expected not in {row.get("main_results"), row.get("ablation"), row.get("efficiency"), row.get("theory"), row.get("code"), row.get("failure_cases")}:
            errors.append(f"support level and matrix are inconsistent for {claim_id}")
        if claim and audit.get("support_level") != claim.get("support_level"):
            warnings.append(f"claim {claim_id} support_level differs from experiment_audit")
    if claim_set - audit_claims:
        errors.append(f"claims without experiment_audit: {', '.join(sorted(claim_set - audit_claims))}")

    related = review.get("related_papers", []) if isinstance(review.get("related_papers"), list) else []
    full_reads = sum(1 for item in related if item.get("read_depth") == "full_read")
    targeted_reads = sum(1 for item in related if item.get("read_depth") == "targeted_read")
    if review.get("review_depth") == "deep":
        if full_reads < 1 or targeted_reads < 2:
            errors.append("deep review requires at least 1 full_read related paper and 2 targeted_read related papers")
    else:
        conclusion = str((review.get("novelty_assessment", {}) or {}).get("conclusion", ""))
        if re.search(r"全局|确定|彻底|绝对|完全证明|完全否定", conclusion):
            errors.append("preliminary review must not make global absolute novelty conclusions")

    for idea in review.get("improvement_ideas", []) if isinstance(review.get("improvement_ideas"), list) else []:
        target = idea.get("targets_claim")
        if target != "general" and target not in claim_set:
            errors.append(f"improvement_ideas references unknown targets_claim: {target}")
        if idea.get("priority") not in {"P0", "P1", "P2"}:
            errors.append(f"improvement idea {idea.get('idea_id', '<unknown>')} missing P0/P1/P2 priority")
        if idea.get("research_value") == "high" and idea.get("implementation_cost") in {"low", "medium"} and idea.get("priority") not in {"P0", "P1"}:
            errors.append(f"improvement idea {idea.get('idea_id', '<unknown>')} priority does not follow value/cost rule")

    for exp in review.get("proposed_experiments", []) if isinstance(review.get("proposed_experiments"), list) else []:
        claim_id = exp.get("claim_id")
        if claim_id != "general" and claim_id not in claim_set:
            errors.append(f"proposed_experiments references unknown claim_id: {claim_id}")
        for key in ("hypothesis", "independent_variables", "control_baselines", "datasets", "metrics", "implementation_steps", "failure_interpretation", "estimated_cost", "priority"):
            if exp.get(key) in ("", [], None):
                errors.append(f"proposed experiment {exp.get('experiment_id', '<unknown>')} missing {key}")

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
