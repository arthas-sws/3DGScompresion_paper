from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test_analysis_output import sample_json, source_pack
from test_innovation_review_validation import standard_json


class SourcePackReuseTest(unittest.TestCase):
    def test_two_modes_can_reference_same_evidence_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            (temp / "P001.source-pack.json").write_text(json.dumps(source_pack()), encoding="utf-8")
            std = sample_json()
            inv = standard_json()
            self.assertEqual(std["source_pack_path"], inv["source_pack_path"])
            self.assertIn("E001", std["analysis"]["evidence"])
            self.assertIn("E001", inv["analysis"]["evidence"])

    def test_source_pack_has_no_long_conclusion_field(self) -> None:
        data = source_pack()
        forbidden = {"final_conclusion", "innovation_judgment", "improvement_plan", "markdown_body"}
        self.assertTrue(forbidden.isdisjoint(data.keys()))


if __name__ == "__main__":
    unittest.main()
