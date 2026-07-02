from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from test_analysis_output import markdown as standard_markdown
from test_analysis_output import sample_json, source_pack

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "validate_innovation_review.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_innovation_review", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def standard_json() -> dict[str, object]:
    data = sample_json()
    data["analysis_mode"] = "innovation-review"
    data["extensions"] = {"source_pack": "P001.source-pack.json", "innovation_review": "P001.innovation-review.json"}
    return data


def review_json(depth: str = "preliminary") -> dict[str, object]:
    related = [
        {"title": "Related Baseline", "relation_type": "baseline_in_experiments", "read_depth": "targeted_read", "similarity_summary": "Shares compression target.", "similarity_level": "medium", "local_match_status": "matched", "local_path": "papers/P000.pdf", "used_for_claims": ["C1"], "evidence": ["Paper Table 1"]}
    ]
    if depth == "deep":
        related = [
            {"title": "Closest Paper", "relation_type": "similar_innovation", "read_depth": "full_read", "similarity_summary": "Closest mechanism.", "similarity_level": "high", "local_match_status": "matched", "local_path": "papers/P000.pdf", "used_for_claims": ["C1"], "evidence": ["full read"]},
            {"title": "Target Paper A", "relation_type": "baseline_in_experiments", "read_depth": "targeted_read", "similarity_summary": "Baseline protocol.", "similarity_level": "medium", "local_match_status": "matched", "local_path": "papers/P002.pdf", "used_for_claims": ["C1"], "evidence": ["targeted read"]},
            {"title": "Target Paper B", "relation_type": "transfer_candidate", "read_depth": "targeted_read", "similarity_summary": "Coding idea.", "similarity_level": "low", "local_match_status": "matched", "local_path": "papers/P003.pdf", "used_for_claims": ["C1"], "evidence": ["targeted read"]},
        ]
    return {
        "schema_version": "1.1",
        "source_pack_path": "P001.source-pack.json",
        "review_depth": depth,
        "paper": {"id": "P001", "title": "Test Paper", "authors": ["A"], "arxiv_id": "2403.17888", "source_url": "https://arxiv.org/abs/2403.17888", "pdf_path": "papers/P001.pdf", "pdf_hash": "a" * 64, "paper_version": "v1", "code_commit": "abc123", "analysis_scope": "unit test"},
        "index_card": {"task": "3DGS compression", "method_tags": ["quantization"], "innovation_tags": ["claim-audit"], "compression_targets": ["attributes"], "main_metrics": ["PSNR"], "datasets": ["Synthetic-NeRF"], "one_sentence_takeaway": "Bounded review.", "open_questions": [], "report_path": "P001.md", "analysis_json_path": "P001.json", "innovation_review_path": "P001.innovation-review.json"},
        "innovation_claims": [
            {"claim_id": "C1", "title": "Compression module", "author_claim": "Improves compression.", "interpretation": "Targets attribute size.", "method_location": ["Paper Sec. 3"], "code_location": ["model.py"], "evidence_ids": ["E001"], "counter_evidence_ids": [], "support_level": "direct", "missing_evidence": [], "closest_prior_work": ["Related Baseline"], "differentiators": ["Different coding target"], "confidence": "medium"}
        ],
        "claim_evidence_matrix": [{"claim_id": "C1", "theory": "部分", "main_results": "直接", "ablation": "无", "efficiency": "部分", "failure_cases": "无", "code": "直接", "final_judgment": "directly supported by T1"}],
        "experiment_tables": [{"table_id": "T1", "caption": "Main results", "source": "Paper Table 1", "columns": ["Dataset", "PSNR"], "rows": [{"Dataset": "Synthetic-NeRF", "PSNR": "30.5"}]}],
        "experiment_audit": [{"claim_id": "C1", "support_level": "direct", "reasoning": "T1 reports target metric.", "evidence_ids": ["E001"], "missing_evidence": []}],
        "novelty_assessment": {"scope": "checked local references only", "closest_prior_work": ["Related Baseline"], "overlap": ["compression target"], "differentiators": ["coding target"], "evidence_limitations": ["preliminary depth"], "confidence": "medium", "conclusion": "Only a bounded preliminary conclusion is made."},
        "improvement_ideas": [{"idea_id": "I1", "idea": "Add rate-distortion ablation.", "targets_claim": "C1", "research_value": "high", "implementation_cost": "medium", "failure_risk": "medium", "required_resources": ["training script"], "minimum_validation": "three bitrate points", "priority": "P0", "evidence_ids": ["E001"]}],
        "proposed_experiments": [{"experiment_id": "X1", "claim_id": "C1", "goal": "Validate rate-distortion stability.", "hypothesis": "Quality-size tradeoff remains stable.", "independent_variables": ["bitrate"], "control_baselines": ["Baseline"], "datasets": ["Synthetic-NeRF"], "metrics": ["PSNR"], "implementation_steps": ["train three rates"], "expected_result": "curve remains competitive", "failure_interpretation": "claim depends on one rate", "estimated_cost": "medium", "priority": "P0"}],
        "related_papers": related,
        "validation": {"language": "zh-CN", "status": "PASS", "warnings": [], "missing_sections": []},
    }


def innovation_markdown() -> str:
    return standard_markdown() + """

## 0. 评审卡片
Test Paper。
## 1. 论文身份与分析边界
## 2. 创新评审深度
preliminary。
## 3. 问题定义与方法定位
## 4. 作者创新主张总览
## 5. 创新主张逐项审计
### C1：Compression module
| 字段 | 内容 |
|---|---|
| 作者主张 | Improves compression |
| 实际技术机制 | Targets attribute size |
| 论文位置 | Paper Sec. 3 |
| 代码位置 | model.py |
| 直接证据 | E001 |
| 反面或冲突证据 | 无 |
| 实验支撑等级 | direct |
| 尚缺证据 | 无 |
| 最近前作 | Related Baseline |
| 与前作差异 | Different coding target |
| 判断置信度 | medium |
## 6. Claim—Evidence 矩阵
| Claim | 理论推导 | 主结果 | 消融 | 效率 | 失败案例 | 代码 | 最终判断 |
|---|---|---|---|---|---|---|---|
| C1 | 部分 | 直接 | 无 | 部分 | 无 | 直接 | direct |
## 7. 关键实验结果
PSNR 30.5 dB [论文 Table 1 / T1]。
## 8. 实验支撑缺口
## 9. 最近前作与相似论文
## 10. 与最近前作的实际差异
## 11. 方法改进优先级
P0。
## 12. 建议补充实验
X1。
## 13. 复现和实现风险
## 14. 创新性结论边界
preliminary only。
## 15. 最终评审结论
bounded。
## 附录：完整实验表格
<details><summary>完整表格</summary>

| Dataset | PSNR |
|---|---:|
| Synthetic-NeRF | 30.5 |

</details>
"""


class InnovationReviewValidationTest(unittest.TestCase):
    def write_case(self, temp: Path, review: dict[str, object] | None = None, md_text: str | None = None) -> tuple[Path, Path, Path]:
        md = temp / "P001.md"
        js = temp / "P001.json"
        review_js = temp / "P001.innovation-review.json"
        sp = temp / "P001.source-pack.json"
        md.write_text(md_text or innovation_markdown(), encoding="utf-8")
        js.write_text(json.dumps(standard_json(), ensure_ascii=False), encoding="utf-8")
        review_js.write_text(json.dumps(review or review_json(), ensure_ascii=False), encoding="utf-8")
        sp.write_text(json.dumps(source_pack(), ensure_ascii=False), encoding="utf-8")
        return md, js, review_js

    def test_valid_innovation_review_passes_schema(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            md, js, review_js = self.write_case(Path(tmp))
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "PASS", result)

    def test_duplicate_claim_id_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["innovation_claims"].append(dict(review["innovation_claims"][0]))
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("duplicate claim" in error for error in result["errors"]))

    def test_matrix_must_cover_claims(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["claim_evidence_matrix"] = []
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("matrix" in error.lower() for error in result["errors"]))

    def test_deep_requires_related_paper_depth(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["review_depth"] = "deep"
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("deep review requires" in error for error in result["errors"]))

    def test_deep_passes_with_one_full_two_targeted(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            md, js, review_js = self.write_case(Path(tmp), review=review_json("deep"))
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "PASS", result)

    def test_improvement_priority_required(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["improvement_ideas"][0]["priority"] = "P3"
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("priority" in error for error in result["errors"]))

    def test_proposed_experiment_requires_failure_interpretation(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            review = review_json()
            review["proposed_experiments"][0]["failure_interpretation"] = ""
            md, js, review_js = self.write_case(Path(tmp), review=review)
            result = validator.validate(md, js, review_js)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("failure_interpretation" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
