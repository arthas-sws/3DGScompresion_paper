from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "validate_innovation_review.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_innovation_review", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def standard_json(title: str = "Test Paper", paper_id: str = "P001") -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "paper": {
            "id": paper_id,
            "title": title,
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
            "core_contribution": "鎻愬嚭涓€涓彲娴嬭瘯鐨勫帇缂╂ā鍧椼€?",
            "method_summary": "鏂规硶鎽樿銆?",
            "method_category": ["compression"],
            "datasets": ["Synthetic-NeRF"],
            "metrics": ["PSNR"],
            "main_results": [
                {
                    "dataset": "Synthetic-NeRF",
                    "scene": "lego",
                    "metric": "PSNR",
                    "method_value": 30.5,
                    "baseline_name": "Baseline",
                    "baseline_value": 29.1,
                    "difference": 1.4,
                    "comparison_direction": "higher_is_better",
                    "comparability": "璁烘枃鎶ュ憡銆佸熀鏈彲姣?",
                    "evidence": "Table 1",
                    "notes": "",
                }
            ],
            "efficiency": ["璁烘枃鏈姤鍛婃樉瀛?"],
            "ablations": ["璁烘枃鏈姤鍛?"],
            "code_mapping": ["浠ｇ爜鏈叕寮€"],
            "limitations": ["鏈瘎浼板ぇ鍦烘櫙"],
            "claims": ["浣滆€呬富寮犲帇缂╄川閲忚緝濂?"],
            "evidence": ["Table 1"],
            "comparability": ["璁烘枃鎶ュ憡銆佸熀鏈彲姣?"],
            "reproducibility": {"status": "閮ㄥ垎鍙鐜?"},
        },
        "extensions": {"innovation_review": f"{paper_id}.innovation-review.json"},
        "validation": {"language": "zh-CN", "status": "PASS", "missing_sections": [], "warnings": []},
    }


def review_json(title: str = "Test Paper", paper_id: str = "P001") -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "paper": {
            "id": paper_id,
            "title": title,
            "authors": ["A"],
            "year": 2026,
            "venue_or_arxiv": "arXiv",
            "arxiv_id": "2403.17888v1",
            "doi": None,
            "source_url": "https://arxiv.org/abs/2403.17888",
            "pdf_path": "papers/P001.pdf",
            "pdf_hash": "a" * 64,
            "paper_version": "v1",
            "analysis_scope": "unit test",
        },
        "index_card": {
            "task": "3DGS compression",
            "method_tags": ["quantization"],
            "innovation_tags": ["table-preserving-review"],
            "compression_targets": ["attributes"],
            "main_metrics": ["PSNR"],
            "datasets": ["Synthetic-NeRF"],
            "one_sentence_takeaway": "Test takeaway.",
            "best_use_for_future_reading": "schema test",
            "open_questions": [],
            "report_path": f"{paper_id}.md",
            "analysis_json_path": f"{paper_id}.json",
            "innovation_review_path": f"{paper_id}.innovation-review.json",
        },
        "innovation_claims": [
            {
                "claim_id": "C1",
                "claim": "Improves compression with a test module.",
                "method_location": "Paper Sec. 3",
                "author_claim": "Author claims compression improvement.",
                "interpretation": "The module targets attribute size.",
                "method_components": ["quantization"],
                "evidence": ["Paper Sec. 3"],
            }
        ],
        "experiment_tables": [
            {
                "table_id": "T1",
                "caption": "Main results",
                "evidence": "Paper Table 1",
                "source_page": 10,
                "extraction_method": "automatic",
                "verification_status": "verified",
                "comparability": "directly_comparable",
                "columns": ["Method", "PSNR"],
                "rows": [{"Method": "Ours", "PSNR": "30.5"}],
                "uncertain_cells": [],
                "notes": None,
            }
        ],
        "experiment_audit": [
            {
                "claim_id": "C1",
                "support_level": "directly_supported",
                "reasoning": "Table reports the target metric.",
                "evidence": ["Paper Table 1"],
                "missing_evidence": [],
            }
        ],
        "novelty_assessment": {
            "scope": "checked_references_and_retrieval_scope",
            "closest_prior_work": [],
            "overlap": [],
            "differentiators": [],
            "evidence_limitations": [],
            "confidence": "medium",
            "conclusion": "No global novelty conclusion is made.",
        },
        "improvement_ideas": [
            {
                "idea": "Add a rate-distortion ablation.",
                "category": "experiment_only_fix",
                "targets_claim": "C1",
                "motivation": "Claim needs curve evidence.",
                "expected_benefit": "Clearer validation.",
                "risk": "Extra training cost.",
                "experiment_to_validate": "Run three bitrate points.",
                "evidence_basis": "Independent judgment",
            }
        ],
        "proposed_experiments": [
            {
                "claim_id": "C1",
                "missing_or_weak_evidence": "Only one bitrate point.",
                "proposed_experiment": "Rate-distortion curve.",
                "control_baselines": ["Baseline"],
                "datasets": ["Synthetic-NeRF"],
                "metrics": ["PSNR"],
                "expected_observation": "Quality-size tradeoff remains stable.",
                "failure_interpretation": "Claim may depend on a single rate.",
            }
        ],
        "related_papers": [
            {
                "title": "Related Baseline",
                "relation_type": "baseline_in_experiments",
                "read_depth": "targeted_read",
                "similarity_summary": "Shares quantization target.",
                "similarity_level": "medium",
                "local_match_status": "matched",
                "local_path": "papers/P000.pdf",
                "used_for_claims": ["C1"],
                "evidence": ["Paper Table 1"],
            }
        ],
        "validation": {"language": "zh-CN", "status": "PASS", "warnings": [], "missing_sections": []},
    }


def markdown(title: str = "Test Paper", paper_id: str = "P001") -> str:
    base = f"""# 《Test Paper》中文精读报告
论文 ID：{paper_id}
{title}

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
"""
    return base + f"""

## 0. 备案卡片
## 1. 论文身份与版本
## 2. 问题定义与压缩目标
## 3. 方法框架
## 4. 作者创新主张
## 5. 创新主张逐项解释
## 6. 关键实验表格
PSNR 30.5 dB [Paper Table 1]
## 7. 实验对创新主张的支撑
## 8. 相似论文与相似范围
## 9. 与相似论文的实际差别
## 10. 改进建议
## 11. 建议补充实验
## 12. 复现风险
## 13. 结论边界
"""


class InnovationReviewValidationTest(unittest.TestCase):
    def write_case(self, temp: Path, std: dict[str, object] | None = None, review: dict[str, object] | None = None, md_text: str | None = None) -> tuple[Path, Path, Path]:
        md = temp / "P001.md"
        js = temp / "P001.json"
        review_js = temp / "P001.innovation-review.json"
        md.write_text(md_text or markdown(), encoding="utf-8")
        js.write_text(json.dumps(std or standard_json(), ensure_ascii=False), encoding="utf-8")
        review_js.write_text(json.dumps(review or review_json(), ensure_ascii=False), encoding="utf-8")
        return md, js, review_js

    def test_valid_innovation_review_passes_schema(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            md, js, review_js = self.write_case(Path(tmp))
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "PASS", result)

    def test_invalid_enum_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["experiment_tables"][0]["verification_status"] = "checked"
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("verification_status" in error for error in result["errors"]))

    def test_duplicate_claim_id_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["innovation_claims"].append(dict(review["innovation_claims"][0]))
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("duplicate claim" in error for error in result["errors"]))

    def test_duplicate_table_id_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["experiment_tables"].append(dict(review["experiment_tables"][0]))
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("duplicate table" in error for error in result["errors"]))

    def test_audit_unknown_claim_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["experiment_audit"][0]["claim_id"] = "C9"
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("unknown claim_id" in error for error in result["errors"]))

    def test_claim_missing_evidence_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["innovation_claims"][0]["evidence"] = []
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("evidence" in error for error in result["errors"]))

    def test_missing_markdown_section_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            md, js, review_js = self.write_case(Path(tmp), md_text=markdown().replace("结论边界", ""))
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("结论边界" in error for error in result["errors"]))

    def test_paper_id_mismatch_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json(paper_id="P002")
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("paper.id" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
