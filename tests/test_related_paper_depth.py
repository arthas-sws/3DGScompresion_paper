from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test_analysis_output import source_pack
from test_innovation_review_validation import innovation_markdown, load_validator, review_json, standard_json


class RelatedPaperDepthTest(unittest.TestCase):
    def test_preliminary_allows_metadata_only_boundary(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            review = review_json()
            review["related_papers"][0]["read_depth"] = "metadata_only"
            (temp / "P001.md").write_text(innovation_markdown(), encoding="utf-8")
            (temp / "P001.json").write_text(json.dumps(standard_json()), encoding="utf-8")
            (temp / "P001.innovation-review.json").write_text(json.dumps(review), encoding="utf-8")
            (temp / "P001.source-pack.json").write_text(json.dumps(source_pack()), encoding="utf-8")
            result = validator.validate(temp / "P001.md", temp / "P001.json", temp / "P001.innovation-review.json")
            self.assertEqual(result["status"], "PASS", result)


if __name__ == "__main__":
    unittest.main()
