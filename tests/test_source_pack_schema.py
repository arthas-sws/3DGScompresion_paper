from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from test_analysis_output import source_pack

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "validate_source_pack.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_source_pack", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class SourcePackSchemaTest(unittest.TestCase):
    def write_pack(self, temp: Path, data: dict[str, object]) -> Path:
        path = temp / "P001.source-pack.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_valid_source_pack_passes(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            result = validator.validate(self.write_pack(Path(tmp), source_pack()))
            self.assertEqual(result["status"], "PASS", result)

    def test_duplicate_evidence_id_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            data = source_pack()
            data["evidence_ledger"].append(dict(data["evidence_ledger"][0]))
            result = validator.validate(self.write_pack(Path(tmp), data))
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("duplicate evidence" in error for error in result["errors"]))

    def test_duplicate_table_id_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            data = source_pack()
            data["experiment_tables"].append(dict(data["experiment_tables"][0]))
            result = validator.validate(self.write_pack(Path(tmp), data))
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("duplicate table" in error for error in result["errors"]))

    def test_invalid_pdf_hash_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            data = source_pack()
            data["paper"]["pdf_hash"] = "bad"
            data["provenance"]["pdf_hash"] = "bad"
            result = validator.validate(self.write_pack(Path(tmp), data))
            self.assertEqual(result["status"], "FAIL")

    def test_stale_source_pack_fails(self) -> None:
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            data = source_pack()
            data["provenance"]["stale"] = True
            data["provenance"]["stale_reasons"] = ["code commit changed"]
            result = validator.validate(self.write_pack(Path(tmp), data))
            self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
