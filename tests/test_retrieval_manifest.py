from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "paper-retrieval-downloader" / "scripts"


def load_common():
    spec = importlib.util.spec_from_file_location("retrieval_common", SCRIPTS / "retrieval_common.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class RetrievalManifestTest(unittest.TestCase):
    def test_arxiv_versions_are_deduplicated(self) -> None:
        common = load_common()
        items = common.deduplicate_items(
            [
                {"title": "Paper v1", "arxiv_id": "2403.17888v1", "source_url": "https://arxiv.org/abs/2403.17888v1"},
                {"title": "Paper v2", "arxiv_id": "2403.17888v2", "source_url": "https://arxiv.org/abs/2403.17888v2", "authors": ["A"]},
            ]
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["arxiv_id"], "2403.17888")
        self.assertEqual(items[0]["deduplication"]["reason"], "same_arxiv_base_id")
        self.assertTrue(items[0]["deduplication"]["duplicates"])

    def test_download_manifest_failures_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            source_pdf = temp / "source.pdf"
            source_pdf.write_bytes(b"%PDF-1.4\nlocal\n")
            candidates = {
                "schema_version": "1.0",
                "batch_id": "local-test",
                "query": {"keywords": ["test"], "date_from": None, "date_to": None},
                "candidates": [
                    {
                        "title": "Downloaded Paper",
                        "authors": ["A"],
                        "arxiv_id": "2403.17888v1",
                        "source_url": "https://arxiv.org/abs/2403.17888v1",
                        "pdf_url": source_pdf.as_uri(),
                    },
                    {
                        "title": "Failed Paper",
                        "authors": ["B"],
                        "arxiv_id": "2403.17889",
                        "source_url": "https://arxiv.org/abs/2403.17889",
                        "pdf_url": "",
                    },
                ],
            }
            input_path = temp / "candidates.json"
            input_path.write_text(json.dumps(candidates), encoding="utf-8")
            output_dir = temp / "out"
            cmd = [
                sys.executable,
                str(SCRIPTS / "download.py"),
                "--input",
                str(input_path),
                "--batch-id",
                "local-test",
                "--output-dir",
                str(output_dir),
                "--delay",
                "0",
            ]
            subprocess.run(cmd, check=True, cwd=ROOT)
            subprocess.run([sys.executable, str(SCRIPTS / "validate_manifest.py"), str(output_dir / "manifest.json")], check=True, cwd=ROOT)
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            failures = json.loads((output_dir / "failures.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["papers"]), 2)
            self.assertEqual(len(failures["failures"]), 1)
            self.assertEqual(manifest["papers"][0]["download_status"], "downloaded")
            subprocess.run(cmd, check=True, cwd=ROOT)
            manifest_again = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest_again["papers"][0]["download_status"], "skipped_existing")


if __name__ == "__main__":
    unittest.main()
