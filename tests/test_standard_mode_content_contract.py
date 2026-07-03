from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_analysis_output import load_validator, markdown, sample_json, source_pack
import json


class StandardModeContentContractTest(unittest.TestCase):
    def test_standard_requires_quick_card_and_code_difference(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            (temp / "P001.json").write_text(json.dumps(sample_json()), encoding="utf-8")
            (temp / "P001.source-pack.json").write_text(json.dumps(source_pack()), encoding="utf-8")
            (temp / "P001.md").write_text(markdown().replace("论文与代码差异", "代码差异缺失"), encoding="utf-8")
            result = validator.validate(temp / "P001.md", temp / "P001.json")
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("论文与代码差异" in error for error in result["errors"]))

    def test_standard_rejects_claim_matrix(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            (temp / "P001.json").write_text(json.dumps(sample_json()), encoding="utf-8")
            (temp / "P001.source-pack.json").write_text(json.dumps(source_pack()), encoding="utf-8")
            (temp / "P001.md").write_text(markdown() + "\n## Claim—Evidence 矩阵\n", encoding="utf-8")
            result = validator.validate(temp / "P001.md", temp / "P001.json")
            self.assertEqual(result["status"], "FAIL")


    def write_case(self, temp: Path, md_text: str) -> None:
        (temp / "P001.json").write_text(json.dumps(sample_json()), encoding="utf-8")
        (temp / "P001.source-pack.json").write_text(json.dumps(source_pack()), encoding="utf-8")
        (temp / "P001.md").write_text(md_text, encoding="utf-8")

    def result_table_markdown(self, rows: int) -> str:
        body = markdown() + "\n\n## 9. 代表性结果\n| Method | Value | Evidence |\n|---|---:|---|\n"
        body += "\n".join(f"| M{i} | {i} | T1 |" for i in range(rows))
        return body

    def test_structural_tables_over_global_18_rows_still_pass(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            extra = "\n\n## 6. 论文与代码映射\n| ID | A | B |\n|---|---|---|\n" + "\n".join(f"| M{i} | a | b |" for i in range(12))
            self.write_case(temp, markdown() + extra)
            result = validator.validate(temp / "P001.md", temp / "P001.json")
            self.assertEqual(result["status"], "PASS", result)

    def test_representative_results_10_rows_pass(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            self.write_case(temp, self.result_table_markdown(10))
            result = validator.validate(temp / "P001.md", temp / "P001.json")
            self.assertEqual(result["status"], "PASS", result)

    def test_representative_results_11_rows_fail(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            self.write_case(temp, self.result_table_markdown(11))
            result = validator.validate(temp / "P001.md", temp / "P001.json")
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("section 9" in error for error in result["errors"]))

    def test_large_ablation_table_warns_not_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            md = markdown() + "\n\n## 11. 消融、失败案例与敏感条件\n| Variant | Value | Evidence |\n|---|---:|---|\n"
            md += "\n".join(f"| V{i} | {i} | T1 |" for i in range(11))
            self.write_case(temp, md)
            result = validator.validate(temp / "P001.md", temp / "P001.json")
            self.assertEqual(result["status"], "WARN", result)

    def test_full_raw_table_in_main_results_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            self.write_case(temp, self.result_table_markdown(16))
            result = validator.validate(temp / "P001.md", temp / "P001.json")
            self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
