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


def sample_json(value: float = 30.5) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "paper": {
            "id": "P001",
            "title": "Test Paper",
            "authors": ["A"],
            "arxiv_id": "2403.17888",
            "source_url": "https://arxiv.org/abs/2403.17888",
            "pdf_path": "papers/P001.pdf",
            "code_url": "",
            "paper_version": "",
            "code_commit": "",
        },
        "analysis": {
            "task": "3DGS compression",
            "core_contribution": "提出一个可测试的压缩模块。",
            "method_summary": "方法摘要。",
            "method_category": ["compression"],
            "datasets": ["Synthetic-NeRF"],
            "metrics": ["PSNR"],
            "main_results": [
                {
                    "dataset": "Synthetic-NeRF",
                    "scene": "lego",
                    "metric": "PSNR",
                    "method_value": value,
                    "baseline_name": "Baseline",
                    "baseline_value": 29.1,
                    "difference": 1.4,
                    "comparison_direction": "higher_is_better",
                    "comparability": "论文报告、基本可比",
                    "evidence": "Table 1",
                    "notes": "",
                }
            ],
            "efficiency": ["论文未报告显存"],
            "ablations": ["论文未报告"],
            "code_mapping": ["代码未公开"],
            "limitations": ["未评估大场景"],
            "claims": ["作者主张压缩质量较好"],
            "evidence": ["Table 1"],
            "comparability": ["论文报告、基本可比"],
            "reproducibility": {"status": "部分可复现"},
        },
        "validation": {"language": "zh-CN", "status": "PASS", "missing_sections": [], "warnings": []},
    }


class AnalysisOutputTest(unittest.TestCase):
    def test_valid_markdown_and_json_pass(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            md = temp / "P001.md"
            js = temp / "P001.json"
            md.write_text(
                """# 《Test Paper》中文精读报告

论文 ID：P001

## 0. 汇报摘要
本文分析 Test Paper。
## 8. 结果汇报与分析
主要结果显示 PSNR 30.5 dB [论文 Table 1]。
## 9. 效率、存储、显存与训练代价
显存论文未报告。
## 11. 局限、适用边界与未证明内容
未评估大场景。
## 12. 可复现性结论
代码未公开，部分可复现。
""",
                encoding="utf-8",
            )
            js.write_text(json.dumps(sample_json(), ensure_ascii=False), encoding="utf-8")
            result = validator.validate(md, js)
            self.assertEqual(result["status"], "PASS")

    def test_metric_number_missing_from_json_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            md = temp / "P001.md"
            js = temp / "P001.json"
            md.write_text(
                """# 《Test Paper》中文精读报告

论文 ID：P001

## 0. 汇报摘要
本文分析 Test Paper。
## 8. 结果汇报与分析
主要结果显示 PSNR 31.7 dB [论文 Table 1]。
## 9. 效率、存储、显存与训练代价
显存论文未报告。
## 11. 局限、适用边界与未证明内容
未评估大场景。
## 12. 可复现性结论
代码未公开，部分可复现。
""",
                encoding="utf-8",
            )
            js.write_text(json.dumps(sample_json(30.5), ensure_ascii=False), encoding="utf-8")
            result = validator.validate(md, js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("31.7" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
