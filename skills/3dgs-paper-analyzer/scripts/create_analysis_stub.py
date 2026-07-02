#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_hash(path_value: str | None) -> str:
    if not path_value:
        return "0" * 64
    path = Path(path_value)
    return sha256_file(path) if path.is_file() else "0" * 64


def source_pack_json(args: argparse.Namespace) -> dict[str, object]:
    digest = pdf_hash(args.pdf_path)
    return {
        "schema_version": "1.0",
        "paper": {
            "id": args.paper_id,
            "title": args.title,
            "authors": [],
            "arxiv_id": args.arxiv_id or "",
            "source_url": args.source_url or "",
            "pdf_path": args.pdf_path or "",
            "pdf_hash": digest,
            "paper_version": "",
            "code_url": args.code_url or "",
            "code_commit": "",
        },
        "source_boundary": {
            "paper": "stub generated; replace with verified reading notes before final delivery",
            "supplement": "not_checked",
            "project_page": "not_checked",
            "official_code": "not_checked",
            "related_papers": "not_checked",
        },
        "evidence_ledger": [
            {
                "evidence_id": "E001",
                "source_type": "paper",
                "location": "Paper identity",
                "page": None,
                "summary": "Stub identity evidence.",
                "verification_status": "partial",
                "source_path_or_url": args.pdf_path or args.source_url or "",
                "source_version": "",
            }
        ],
        "equations": [],
        "figures": [],
        "experiment_tables": [
            {
                "table_id": "T1",
                "caption": "Stub placeholder; replace with verified paper table.",
                "source": "Paper Table pending",
                "source_page": None,
                "columns": ["Item", "Value"],
                "rows": [{"Item": "pending", "Value": "unverified"}],
                "extraction_method": "manual_transcription",
                "verification_status": "unverified",
                "uncertain_cells": ["all"],
                "comparability": "not_checked",
                "evidence_ids": ["E001"],
            }
        ],
        "code_map": [
            {
                "mapping_id": "M1",
                "paper_component": "official implementation",
                "paper_location": ["not_checked"],
                "code_location": [],
                "mapping_level": "not_found",
                "differences": [],
                "evidence_ids": ["E001"],
            }
        ],
        "reported_limitations": [],
        "unverified_items": ["stub generated; replace placeholders before final analysis"],
        "provenance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "generator": "create_analysis_stub.py",
            "pdf_hash": digest,
            "paper_version": "",
            "code_commit": "",
            "stale": False,
            "stale_reasons": [],
        },
    }


def base_json(args: argparse.Namespace) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "analysis_mode": "standard-analysis",
        "source_pack_path": f"{args.paper_id}.source-pack.json",
        "paper": {
            "id": args.paper_id,
            "title": args.title,
            "authors": [],
            "arxiv_id": args.arxiv_id or "",
            "source_url": args.source_url or "",
            "pdf_path": args.pdf_path or "",
            "code_url": args.code_url or "",
            "paper_version": "",
            "code_commit": "",
        },
        "analysis": {
            "task": "",
            "core_contribution": "",
            "method_summary": "",
            "method_category": [],
            "datasets": [],
            "metrics": [],
            "main_results": [
                {
                    "dataset": "not_reported",
                    "scene": "not_reported",
                    "metric": "not_reported",
                    "method_value": None,
                    "baseline_name": "",
                    "baseline_value": None,
                    "difference": None,
                    "comparison_direction": "not_applicable",
                    "comparability": "not_checked",
                    "evidence": "T1",
                    "notes": "stub placeholder",
                }
            ],
            "efficiency": [],
            "ablations": [],
            "code_mapping": [{"mapping_id": "M1", "paper_component": "official implementation", "mapping_level": "not_found"}],
            "limitations": [],
            "claims": [],
            "evidence": ["E001"],
            "comparability": [],
            "reproducibility": {},
        },
        "extensions": {"source_pack": f"{args.paper_id}.source-pack.json"},
        "validation": {"language": "zh-CN", "status": "WARN", "missing_sections": [], "warnings": ["stub generated; fill analysis before validation"]},
    }


def base_markdown(args: argparse.Namespace) -> str:
    return f"""# 《{args.title}》中文精读报告

论文 ID：{args.paper_id}

## 0. 快速判断

| 项目 | 结论 |
|---|---|
| 方法类型 | 待分析 |
| 压缩对象 | 待分析 |
| 核心贡献 | 待分析 |
| 最强实验依据 | 待核实 |
| 最大质量风险 | 待分析 |
| 最大工程代价 | 待分析 |
| 论文代码一致性 | 待核查 |
| 复现难度 | 待判断 |
| 是否值得复现 | 待判断 |
| 对综述的价值 | 待判断 |

## 1. 论文信息与分析边界

- 标题：{args.title}
- PDF：{args.pdf_path or '待补充'}
- 来源：{args.source_url or '待补充'}
- 代码：{args.code_url or '待补充'}
- Source Pack：{args.paper_id}.source-pack.json

## 2. 一句话核心贡献

待分析。

## 3. 问题、动机与方法位置

待分析。

## 4. 方法总体流程

待分析。

## 5. 技术方法分析

待分析。

核心公式必须使用 MathJax block，例如：

\\[
H = J_R^\\top J_R
\\]

## 6. 论文与代码映射

待核查。

## 7. 论文与代码差异

| 差异 ID | 论文描述 | 代码实现 | 影响 | 严重程度 | 是否需要实验 |
|---|---|---|---|---|---|
| D1 | 待核查 | 待核查 | 待判断 | unclear | 是 |

## 8. 实验设置与可比性

待分析。

## 9. 代表性结果

| 数据集 | 场景 | 指标 | 本文方法 | baseline | 差值 | 趋势 | 可比性 | 证据 | 说明 |
|---|---|---:|---:|---:|---:|---|---|---|---|
| not_reported | not_reported | not_reported | 未报告 | 未报告 | 未报告 | 不适用 | not_checked | T1 | stub placeholder |

## 10. 效率、存储和部署代价

论文未报告或待核查。

## 11. 消融、失败案例与敏感条件

论文未报告或待核查。

## 12. 局限和未证明内容

待分析。

## 13. 可复现性结论

待核查。

## 14. 最终总结

待分析。

## 附录：完整证据与表格索引

完整事实、证据和原始表格位于 `{args.paper_id}.source-pack.json`。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Markdown, JSON, and Source Pack stubs for one paper analysis.")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--arxiv-id")
    parser.add_argument("--source-url")
    parser.add_argument("--pdf-path")
    parser.add_argument("--code-url")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    md_path = args.output_dir / f"{args.paper_id}.md"
    json_path = args.output_dir / f"{args.paper_id}.json"
    source_pack_path = args.output_dir / f"{args.paper_id}.source-pack.json"
    if md_path.exists() or json_path.exists() or source_pack_path.exists():
        raise SystemExit("Refusing to overwrite existing analysis files.")
    md_path.write_text(base_markdown(args), encoding="utf-8")
    json_path.write_text(json.dumps(base_json(args), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_pack_path.write_text(json.dumps(source_pack_json(args), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created {md_path}")
    print(f"created {json_path}")
    print(f"created {source_pack_path}")


if __name__ == "__main__":
    main()
