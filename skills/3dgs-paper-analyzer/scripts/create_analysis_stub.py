#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def base_json(args: argparse.Namespace) -> dict[str, object]:
    return {
        "schema_version": "1.0",
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
            "main_results": [],
            "efficiency": [],
            "ablations": [],
            "code_mapping": [],
            "limitations": [],
            "claims": [],
            "evidence": [],
            "comparability": [],
            "reproducibility": {},
        },
        "validation": {"language": "zh-CN", "status": "WARN", "missing_sections": [], "warnings": ["stub generated; fill analysis before validation"]},
    }


def base_markdown(args: argparse.Namespace) -> str:
    return f"""# 《{args.title}》中文精读报告

论文 ID：{args.paper_id}

## 0. 汇报摘要

待分析。

## 1. 论文信息与分析边界

- 标题：{args.title}
- PDF：{args.pdf_path or '待补充'}
- 来源：{args.source_url or '待补充'}
- 代码：{args.code_url or '待补充'}

## 2. 一句话核心贡献

待分析。

## 3. 问题、动机与相关方法位置

待分析。

## 4. 方法总体流程

待分析。

## 5. 技术方法分析

待分析。

## 6. 论文与代码对应关系

待核查。

## 7. 实验设置审计

待分析。

## 8. 结果汇报与分析

| 数据集 | 场景 | 指标 | 本文方法 | baseline | 差值 | 趋势 | 可比性 | 证据 | 说明 |
|---|---|---:|---:|---:|---:|---|---|---|---|
| 论文未报告 | 论文未报告 | 论文未报告 | 论文未报告 | 论文未报告 | 论文未报告 | 论文未报告 | 不可直接比较 | 待核实 | 待分析 |

## 9. 效率、存储、显存与训练代价

论文未报告或待核查。

## 10. 消融实验与失败案例

论文未报告或待核查。

## 11. 局限、适用边界与未证明内容

待分析。

## 12. 可复现性结论

待核查。

## 13. 最终汇报总结

待分析。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Markdown and JSON stubs for one paper analysis.")
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
    if md_path.exists() or json_path.exists():
        raise SystemExit("Refusing to overwrite existing analysis files.")
    md_path.write_text(base_markdown(args), encoding="utf-8")
    json_path.write_text(json.dumps(base_json(args), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created {md_path}")
    print(f"created {json_path}")


if __name__ == "__main__":
    main()
