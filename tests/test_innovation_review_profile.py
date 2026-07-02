from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "skills" / "3dgs-paper-batch-orchestrator" / "scripts"


def manifest(temp: Path) -> Path:
    retrieval = temp / "retrieval"
    (retrieval / "papers").mkdir(parents=True)
    (retrieval / "papers" / "P001.pdf").write_bytes(b"%PDF-1.4 p1")
    payload = {
        "schema_version": "1.0",
        "batch_id": "batch-test",
        "created_at": "2026-07-01T00:00:00Z",
        "query": {"keywords": ["test"], "date_from": None, "date_to": None},
        "papers": [
            {
                "id": "P001",
                "title": "Test Paper One",
                "authors": ["A"],
                "arxiv_id": "2403.17888",
                "source_url": "https://arxiv.org/abs/2403.17888",
                "pdf_url": "",
                "local_pdf": "papers/P001.pdf",
                "download_status": "downloaded",
                "metadata_status": "complete",
            }
        ],
    }
    path = retrieval / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class InnovationReviewProfileTest(unittest.TestCase):
    def test_innovation_review_profile_generates_task_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            batch_dir = temp / "batch"
            source_manifest = manifest(temp)
            subprocess.run(
                [
                    sys.executable,
                    str(BATCH / "init_batch.py"),
                    "--manifest",
                    str(source_manifest),
                    "--output-dir",
                    str(batch_dir),
                    "--profile",
                    "innovation-review",
                ],
                check=True,
                cwd=ROOT,
            )
            subprocess.run(
                [sys.executable, str(BATCH / "build_task.py"), "--batch-dir", str(batch_dir), "--paper-id", "P001"],
                check=True,
                cwd=ROOT,
            )
            status = json.loads((batch_dir / "status.json").read_text(encoding="utf-8"))
            prompt = next((batch_dir / "attempts").glob("P001.attempt-*.prompt.md")).read_text(encoding="utf-8")
            self.assertEqual(status["profile"], "innovation-review")
            self.assertIn("P001.innovation-review.json", prompt)
            self.assertIn("innovation-review", prompt)

    def test_standard_analysis_profile_still_generates_standard_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            batch_dir = temp / "batch"
            source_manifest = manifest(temp)
            subprocess.run(
                [sys.executable, str(BATCH / "init_batch.py"), "--manifest", str(source_manifest), "--output-dir", str(batch_dir)],
                check=True,
                cwd=ROOT,
            )
            subprocess.run(
                [sys.executable, str(BATCH / "build_task.py"), "--batch-dir", str(batch_dir), "--paper-id", "P001"],
                check=True,
                cwd=ROOT,
            )
            status = json.loads((batch_dir / "status.json").read_text(encoding="utf-8"))
            prompt = next((batch_dir / "attempts").glob("P001.attempt-*.prompt.md")).read_text(encoding="utf-8")
            self.assertEqual(status["profile"], "standard-analysis")
            self.assertIn("standard-analysis", prompt)


if __name__ == "__main__":
    unittest.main()
