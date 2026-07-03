from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from test_analysis_output import markdown, sample_json, source_pack
from test_innovation_review_validation import innovation_markdown, review_json, standard_json

ROOT = Path(__file__).resolve().parents[1]
FINALIZER = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "finalize_report.py"


def load_finalizer():
    spec = importlib.util.spec_from_file_location("finalize_report", FINALIZER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def write_standard(temp: Path, md_text: str | None = None, data: dict[str, object] | None = None) -> None:
    (temp / "P001.md").write_text(md_text or markdown(), encoding="utf-8")
    (temp / "P001.json").write_text(json.dumps(data or sample_json(), ensure_ascii=False), encoding="utf-8")
    (temp / "P001.source-pack.json").write_text(json.dumps(source_pack(), ensure_ascii=False), encoding="utf-8")


def write_innovation(temp: Path) -> None:
    (temp / "P001.md").write_text(innovation_markdown(), encoding="utf-8")
    (temp / "P001.json").write_text(json.dumps(standard_json(), ensure_ascii=False), encoding="utf-8")
    (temp / "P001.source-pack.json").write_text(json.dumps(source_pack(), ensure_ascii=False), encoding="utf-8")
    (temp / "P001.innovation-review.json").write_text(json.dumps(review_json(), ensure_ascii=False), encoding="utf-8")


class FinalizeReportTest(unittest.TestCase):
    def test_standard_report_generates_html_and_validation(self) -> None:
        finalizer = load_finalizer()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            write_standard(temp)
            result = finalizer.finalize("standard-analysis", "P001", temp)
            self.assertIn(result["completion_status"], {"COMPLETE", "COMPLETE_WITH_WARNINGS"}, result)
            self.assertTrue((temp / "P001.html").is_file())
            self.assertTrue((temp / "P001.validation.json").is_file())
            html = (temp / "P001.html").read_text(encoding="utf-8")
            self.assertIn("<html", html.lower())
            self.assertIn("class=\"toc\"", html)
            self.assertIn("class=\"table-scroll\"", html)

    def test_innovation_report_generates_html_and_validation(self) -> None:
        finalizer = load_finalizer()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            write_innovation(temp)
            result = finalizer.finalize("innovation-review", "P001", temp)
            self.assertIn(result["completion_status"], {"COMPLETE", "COMPLETE_WITH_WARNINGS"}, result)
            self.assertTrue((temp / "P001.html").is_file())
            self.assertTrue((temp / "P001.validation.json").is_file())

    def test_validator_fail_returns_incomplete_and_no_html(self) -> None:
        finalizer = load_finalizer()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            write_standard(temp, md_text=markdown("31.7"))
            result = finalizer.finalize("standard-analysis", "P001", temp)
            self.assertEqual(result["completion_status"], "INCOMPLETE")
            self.assertFalse((temp / "P001.html").exists())
            self.assertTrue((temp / "P001.validation.json").is_file())

    def test_missing_required_file_is_incomplete(self) -> None:
        finalizer = load_finalizer()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            (temp / "P001.md").write_text(markdown(), encoding="utf-8")
            result = finalizer.finalize("standard-analysis", "P001", temp)
            self.assertEqual(result["completion_status"], "INCOMPLETE")
            self.assertTrue(any("missing required file" in error for error in result["errors"]))

    def test_html_missing_or_empty_is_invalid(self) -> None:
        finalizer = load_finalizer()
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            html = temp / "P001.html"
            self.assertTrue(finalizer.validate_html(html, "Title"))
            html.write_text("", encoding="utf-8")
            self.assertTrue(any("empty" in error for error in finalizer.validate_html(html, "Title")))


if __name__ == "__main__":
    unittest.main()
