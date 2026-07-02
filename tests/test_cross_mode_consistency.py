from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from test_analysis_output import sample_json, source_pack
from test_innovation_review_validation import review_json, standard_json

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "validate_cross_mode_consistency.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_cross_mode_consistency", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class CrossModeConsistencyTest(unittest.TestCase):
    def test_consistent_modes_pass(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            paths = {
                "sp": temp / "P001.source-pack.json",
                "std": temp / "standard.json",
                "inv": temp / "innovation.json",
                "review": temp / "review.json",
            }
            paths["sp"].write_text(json.dumps(source_pack()), encoding="utf-8")
            paths["std"].write_text(json.dumps(sample_json()), encoding="utf-8")
            paths["inv"].write_text(json.dumps(standard_json()), encoding="utf-8")
            paths["review"].write_text(json.dumps(review_json()), encoding="utf-8")
            result = validator.validate(paths["sp"], paths["std"], paths["inv"], paths["review"])
            self.assertEqual(result["status"], "PASS", result)

    def test_metric_mismatch_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            inv = standard_json()
            inv["analysis"]["main_results"][0]["method_value"] = 31.0
            sp = temp / "P001.source-pack.json"
            std = temp / "standard.json"
            invp = temp / "innovation.json"
            review = temp / "review.json"
            sp.write_text(json.dumps(source_pack()), encoding="utf-8")
            std.write_text(json.dumps(sample_json()), encoding="utf-8")
            invp.write_text(json.dumps(inv), encoding="utf-8")
            review.write_text(json.dumps(review_json()), encoding="utf-8")
            result = validator.validate(sp, std, invp, review)
            self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
