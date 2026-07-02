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


if __name__ == "__main__":
    unittest.main()
