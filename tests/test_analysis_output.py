from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "validate_report.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_report", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def source_pack() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "paper": {"id": "P001", "title": "Test Paper", "authors": ["A"], "arxiv_id": "2403.17888", "source_url": "https://arxiv.org/abs/2403.17888", "pdf_path": "papers/P001.pdf", "pdf_hash": "a" * 64, "paper_version": "v1", "code_url": "", "code_commit": "abc123"},
        "source_boundary": {"paper": "full_read", "supplement": "not_available", "project_page": "not_available", "official_code": "checked", "related_papers": "not_checked"},
        "evidence_ledger": [{"evidence_id": "E001", "source_type": "paper", "location": "Paper Table 1", "page": 10, "summary": "Main PSNR result.", "verification_status": "verified", "source_path_or_url": "papers/P001.pdf", "source_version": "v1"}],
        "equations": [],
        "figures": [],
        "experiment_tables": [{"table_id": "T1", "caption": "Main results", "source": "Paper Table 1", "source_page": 10, "columns": ["Dataset", "Scene", "PSNR"], "rows": [{"Dataset": "Synthetic-NeRF", "Scene": "lego", "PSNR": "30.5"}], "extraction_method": "manual_transcription", "verification_status": "verified", "uncertain_cells": [], "comparability": "paper_reported", "evidence_ids": ["E001"]}],
        "code_map": [{"mapping_id": "M1", "paper_component": "compression module", "paper_location": ["Sec. 3"], "code_location": ["model.py"], "mapping_level": "direct", "differences": [], "evidence_ids": ["E001"]}],
        "reported_limitations": [],
        "unverified_items": [],
        "provenance": {"created_at": "2026-07-02T00:00:00Z", "generator": "unit-test", "pdf_hash": "a" * 64, "paper_version": "v1", "code_commit": "abc123", "stale": False, "stale_reasons": []},
    }


def sample_json(value: float = 30.5) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "analysis_mode": "standard-analysis",
        "source_pack_path": "P001.source-pack.json",
        "paper": {"id": "P001", "title": "Test Paper", "authors": ["A"], "arxiv_id": "2403.17888", "source_url": "https://arxiv.org/abs/2403.17888", "pdf_path": "papers/P001.pdf", "code_url": "", "paper_version": "v1", "code_commit": "abc123"},
        "analysis": {
            "task": "3DGS compression",
            "core_contribution": "提出可验证的压缩模块。",
            "method_summary": "方法摘要。",
            "method_category": ["compression"],
            "datasets": ["Synthetic-NeRF"],
            "metrics": ["PSNR"],
            "main_results": [{"dataset": "Synthetic-NeRF", "scene": "lego", "metric": "PSNR", "method_value": value, "baseline_name": "Baseline", "baseline_value": 29.1, "difference": 1.4, "comparison_direction": "higher_is_better", "comparability": "论文报告，基本可比", "evidence": "T1", "notes": ""}],
            "efficiency": [],
            "ablations": [],
            "code_mapping": [{"mapping_id": "M1", "paper_component": "compression module"}],
            "limitations": ["未评估大场景"],
            "claims": ["作者主张压缩质量较好"],
            "evidence": ["E001"],
            "comparability": ["论文报告，基本可比"],
            "reproducibility": {"status": "部分可复现"},
        },
        "extensions": {"source_pack": "P001.source-pack.json"},
        "validation": {"language": "zh-CN", "status": "PASS", "missing_sections": [], "warnings": []},
    }


def markdown(number: str = "30.5") -> str:
    return f"""# 《Test Paper》中文精读报告
论文 ID：P001

## 0. 快速判断
| 项目 | 结论 |
|---|---|
| 方法类型 | 压缩 |
| 压缩对象 | attributes |
| 核心贡献 | 压缩模块 |
| 最强实验依据 | T1 |
| 最大质量风险 | 高压缩率退化 |
| 最大工程代价 | 编码时间 |
| 论文代码一致性 | 基本一致 |
| 复现难度 | 中 |
| 是否值得复现 | 是 |
| 对综述的价值 | 可作为代表方法 |

## 1. 论文信息与分析边界
Test Paper。
## 7. 论文与代码差异
| 差异 ID | 论文描述 | 代码实现 | 影响 | 严重程度 | 是否需要实验 |
|---|---|---|---|---|---|
| D1 | 无 | 无 | 无 | minor | 否 |
## 9. 代表性结果
PSNR {number} dB [论文 Table 1 / T1]。
## 10. 效率、存储和部署代价
论文未报告。
## 12. 局限和未证明内容
未评估大场景。
## 13. 可复现性结论
部分可复现。
"""


class AnalysisOutputTest(unittest.TestCase):
    def write_case(self, temp: Path, data: dict[str, object] | None = None, md_text: str | None = None) -> tuple[Path, Path]:
        md = temp / "P001.md"
        js = temp / "P001.json"
        sp = temp / "P001.source-pack.json"
        md.write_text(md_text or markdown(), encoding="utf-8")
        js.write_text(json.dumps(data or sample_json(), ensure_ascii=False), encoding="utf-8")
        sp.write_text(json.dumps(source_pack(), ensure_ascii=False), encoding="utf-8")
        return md, js

    def test_valid_markdown_json_and_source_pack_pass(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            md, js = self.write_case(Path(tmp))
            result = validator.validate(md, js)
            self.assertEqual(result["status"], "PASS", result)

    def test_metric_number_missing_from_json_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            md, js = self.write_case(Path(tmp), data=sample_json(30.5), md_text=markdown("31.7"))
            result = validator.validate(md, js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("31.7" in error for error in result["errors"]))

    def test_missing_source_pack_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            md, js = self.write_case(Path(tmp))
            (Path(tmp) / "P001.source-pack.json").unlink()
            result = validator.validate(md, js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("Source Pack" in error or "source pack" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
