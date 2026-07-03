#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "schemas").is_dir() and (parent / "skills").is_dir():
            return parent
    return Path.cwd()


def status_rank(status: str) -> int:
    return {"PASS": 0, "WARN": 1, "FAIL": 2}.get(str(status), 2)


def aggregate_status(results: list[dict[str, Any]]) -> str:
    worst = max((status_rank(result.get("status", "FAIL")) for result in results), default=2)
    return "FAIL" if worst == 2 else ("WARN" if worst == 1 else "PASS")


def required_paths(output_dir: Path, paper_id: str, mode: str) -> dict[str, Path]:
    paths = {
        "source_pack": output_dir / f"{paper_id}.source-pack.json",
        "markdown": output_dir / f"{paper_id}.md",
        "analysis_json": output_dir / f"{paper_id}.json",
        "html": output_dir / f"{paper_id}.html",
        "validation": output_dir / f"{paper_id}.validation.json",
    }
    if mode == "innovation-review":
        paths["innovation_review_json"] = output_dir / f"{paper_id}.innovation-review.json"
    return paths


def missing_required_inputs(paths: dict[str, Path], mode: str) -> list[str]:
    required = ["source_pack", "markdown", "analysis_json"]
    if mode == "innovation-review":
        required.append("innovation_review_json")
    missing = []
    for key in required:
        path = paths[key]
        if not path.is_file():
            missing.append(f"missing required file: {path}")
    return missing


def markdown_title(md_path: Path) -> str:
    if not md_path.is_file():
        return ""
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md_path.stem


def validate_html(html_path: Path, expected_title: str) -> list[str]:
    errors: list[str] = []
    if not html_path.is_file():
        return [f"HTML missing: {html_path}"]
    text = html_path.read_text(encoding="utf-8")
    if not text.strip():
        errors.append(f"HTML is empty: {html_path}")
    lowered = text.lower()
    if "<html" not in lowered and "<!doctype html" not in lowered:
        errors.append("HTML does not contain <html or <!DOCTYPE html>")
    if expected_title and expected_title not in text:
        errors.append("HTML does not contain report title")
    if 'class="toc"' not in text and "目录" not in text and "鐩綍" not in text:
        errors.append("HTML does not contain a table of contents")
    if 'class="table-scroll"' not in text:
        errors.append("HTML tables are not wrapped in table-scroll")
    return errors


def write_validation(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finalize(mode: str, paper_id: str, output_dir: Path, strict: bool = False) -> dict[str, Any]:
    paths = required_paths(output_dir, paper_id, mode)
    components: dict[str, Any] = {}
    errors = missing_required_inputs(paths, mode)
    warnings: list[str] = []

    if errors:
        payload = {
            "schema_version": "1.0",
            "paper_id": paper_id,
            "mode": mode,
            "completion_status": "INCOMPLETE",
            "status": "FAIL",
            "errors": errors,
            "warnings": warnings,
            "components": components,
            "html_path": str(paths["html"]),
        }
        write_validation(paths["validation"], payload)
        return payload

    validators = script_dir()
    source_pack_validator = load_module("validate_source_pack", validators / "validate_source_pack.py")
    report_validator = load_module("validate_report", validators / "validate_report.py")
    source_pack_result = source_pack_validator.validate(paths["source_pack"])
    report_result = report_validator.validate(paths["markdown"], paths["analysis_json"])
    components["source_pack"] = source_pack_result
    components["report"] = report_result
    results = [source_pack_result, report_result]

    if mode == "innovation-review":
        innovation_validator = load_module("validate_innovation_review", validators / "validate_innovation_review.py")
        innovation_result = innovation_validator.validate(paths["markdown"], paths["analysis_json"], paths["innovation_review_json"])
        components["innovation_review"] = innovation_result
        results.append(innovation_result)
        if strict and innovation_result.get("status") == "WARN":
            innovation_result = dict(innovation_result)
            innovation_result["status"] = "FAIL"
            innovation_result.setdefault("errors", []).append("strict innovation-review validation treats WARN as incomplete")
            components["innovation_review"] = innovation_result
            results[-1] = innovation_result

    validation_status = aggregate_status(results)
    for result in results:
        errors.extend(str(err) for err in result.get("errors", []))
        warnings.extend(str(warn) for warn in result.get("warnings", []))

    if validation_status == "FAIL":
        payload = {
            "schema_version": "1.0",
            "paper_id": paper_id,
            "mode": mode,
            "completion_status": "INCOMPLETE",
            "status": "FAIL",
            "errors": errors,
            "warnings": warnings,
            "components": components,
            "html_path": str(paths["html"]),
        }
        write_validation(paths["validation"], payload)
        return payload

    render_script = validators / "render_html.py"
    render = subprocess.run([sys.executable, str(render_script), str(paths["markdown"]), str(paths["html"])], cwd=repo_root(), text=True, capture_output=True)
    components["render_html"] = {"status": "PASS" if render.returncode == 0 else "FAIL", "stdout": render.stdout, "stderr": render.stderr}
    if render.returncode != 0:
        errors.append(f"render_html.py failed: {render.stderr.strip() or render.stdout.strip()}")

    html_errors = validate_html(paths["html"], markdown_title(paths["markdown"]))
    errors.extend(html_errors)

    if errors:
        completion = "INCOMPLETE"
        final_status = "FAIL"
    elif warnings:
        completion = "COMPLETE_WITH_WARNINGS"
        final_status = "WARN"
    else:
        completion = "COMPLETE"
        final_status = "PASS"

    payload = {
        "schema_version": "1.0",
        "paper_id": paper_id,
        "mode": mode,
        "completion_status": completion,
        "status": final_status,
        "errors": errors,
        "warnings": warnings,
        "components": components,
        "html_path": str(paths["html"]),
    }
    write_validation(paths["validation"], payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize analyzer outputs: validate, save validation JSON, render and verify HTML.")
    parser.add_argument("--mode", choices=["standard-analysis", "innovation-review"], required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    result = finalize(args.mode, args.paper_id, args.output_dir, args.strict)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(result["completion_status"])
    raise SystemExit(0 if result["completion_status"] in {"COMPLETE", "COMPLETE_WITH_WARNINGS"} else 1)


if __name__ == "__main__":
    main()
