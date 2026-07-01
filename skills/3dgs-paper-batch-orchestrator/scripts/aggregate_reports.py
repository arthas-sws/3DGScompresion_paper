#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from batch_common import load_manifest, load_status, utc_now_iso, write_json


def read_analysis(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def aggregate(batch_dir: Path) -> dict[str, Any]:
    manifest = load_manifest(batch_dir)
    status = load_status(batch_dir)
    papers_by_id = {p["id"]: p for p in manifest.get("papers", []) if isinstance(p, dict) and p.get("id")}
    validated = [paper_id for paper_id, item in status.get("items", {}).items() if item.get("status") == "validated"]
    failed = [
        {"id": paper_id, "status": item.get("status"), "errors": item.get("errors", [])}
        for paper_id, item in status.get("items", {}).items()
        if item.get("status") != "validated"
    ]

    results: list[dict[str, Any]] = []
    paper_summaries: list[dict[str, str]] = []
    for paper_id in validated:
        analysis_path = batch_dir / "items" / f"{paper_id}.json"
        if not analysis_path.is_file():
            failed.append({"id": paper_id, "status": "failed_analysis", "errors": ["validated item missing JSON"]})
            continue
        payload = read_analysis(analysis_path)
        paper = payload.get("paper", {})
        analysis = payload.get("analysis", {})
        paper_summaries.append(
            {
                "id": paper_id,
                "title": str(paper.get("title") or papers_by_id.get(paper_id, {}).get("title", "")),
                "method_category": ", ".join(analysis.get("method_category", [])),
                "core_contribution": str(analysis.get("core_contribution", "")),
            }
        )
        for result in analysis.get("main_results", []):
            if not isinstance(result, dict):
                continue
            results.append(
                {
                    "paper_id": paper_id,
                    "title": str(paper.get("title", "")),
                    "dataset": result.get("dataset", ""),
                    "scene": result.get("scene", ""),
                    "metric": result.get("metric", ""),
                    "method_value": result.get("method_value"),
                    "baseline_name": result.get("baseline_name", ""),
                    "baseline_value": result.get("baseline_value"),
                    "difference": result.get("difference"),
                    "comparison_direction": result.get("comparison_direction", ""),
                    "comparability": result.get("comparability", ""),
                    "evidence": result.get("evidence", ""),
                    "notes": result.get("notes", ""),
                }
            )

    matrix = {
        "schema_version": "1.0",
        "batch_id": manifest.get("batch_id", batch_dir.name),
        "created_at": utc_now_iso(),
        "papers": paper_summaries,
        "results": results,
        "failed": failed,
    }
    write_json(batch_dir / "result-matrix.json", matrix)

    summary_lines = [f"# Batch Summary: {matrix['batch_id']}", "", f"- Validated: {len(validated)}", f"- Failed or waiting: {len(failed)}", ""]
    summary_lines.append("## Papers")
    for item in paper_summaries:
        summary_lines.append(f"- **{item['id']}** {item['title']}: {item['core_contribution']}")
    summary_lines.append("")
    (batch_dir / "batch-summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    comp_lines = ["# Comparison Matrix", "", "| Paper | Metric | Value | Baseline | Comparability | Evidence |", "|---|---|---:|---:|---|---|"]
    for result in results:
        comp_lines.append(
            f"| {result['paper_id']} | {result['metric']} | {result['method_value']} | {result['baseline_value']} | {result['comparability']} | {result['evidence']} |"
        )
    (batch_dir / "comparison-matrix.md").write_text("\n".join(comp_lines) + "\n", encoding="utf-8")

    failed_lines = ["# Failed Items", ""]
    for item in failed:
        failed_lines.append(f"- **{item['id']}** `{item['status']}`: {'; '.join(item.get('errors', []))}")
    (batch_dir / "failed-items.md").write_text("\n".join(failed_lines) + "\n", encoding="utf-8")
    return matrix


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate validated batch reports.")
    parser.add_argument("--batch-dir", type=Path, required=True)
    args = parser.parse_args()
    matrix = aggregate(args.batch_dir)
    print(json.dumps({"validated": len(matrix["papers"]), "results": len(matrix["results"]), "failed": len(matrix["failed"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
