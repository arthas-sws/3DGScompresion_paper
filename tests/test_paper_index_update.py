from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "update_paper_index.py"


def load_module():
    spec = importlib.util.spec_from_file_location("update_paper_index", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def review(arxiv_id: str = "2403.17888v1", title: str = "Test Paper") -> dict[str, object]:
    return {
        "paper": {
            "id": "P001",
            "title": title,
            "arxiv_id": arxiv_id,
            "doi": "",
            "pdf_hash": "a" * 64,
        },
        "index_card": {
            "method_tags": ["quantization"],
            "innovation_tags": ["claim-audit"],
            "report_path": "P001.md",
            "analysis_json_path": "P001.json",
            "innovation_review_path": "P001.innovation-review.json",
        },
    }


class PaperIndexUpdateTest(unittest.TestCase):
    def test_insert_then_update_does_not_duplicate(self) -> None:
        updater = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "paper-index.jsonl"
            first = updater.build_record(review())
            second_review = review()
            second_review["index_card"]["innovation_tags"] = ["updated"]
            second = updater.build_record(second_review)
            self.assertEqual(updater.upsert(index, first)["action"], "inserted")
            self.assertEqual(updater.upsert(index, second)["action"], "updated")
            lines = index.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["innovation_tags"], ["updated"])

    def test_arxiv_versions_share_canonical_key(self) -> None:
        updater = load_module()
        first = updater.build_record(review("2403.17888v1"))
        second = updater.build_record(review("2403.17888v2"))
        self.assertEqual(updater.canonical_key(first), updater.canonical_key(second))

    def test_dry_run_does_not_create_index(self) -> None:
        updater = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "paper-index.jsonl"
            updater.upsert(index, updater.build_record(review()), dry_run=True)
            self.assertFalse(index.exists())


if __name__ == "__main__":
    unittest.main()
