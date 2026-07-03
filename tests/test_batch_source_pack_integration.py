from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "skills" / "3dgs-paper-batch-orchestrator" / "scripts"


class BatchSourcePackIntegrationTest(unittest.TestCase):
    def test_prompt_mentions_source_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            retrieval = temp / "retrieval"
            (retrieval / "papers").mkdir(parents=True)
            (retrieval / "papers" / "P001.pdf").write_bytes(b"%PDF-1.4")
            manifest = {"schema_version": "1.0", "batch_id": "batch-test", "created_at": "2026-07-01T00:00:00Z", "query": {"keywords": ["test"], "date_from": None, "date_to": None}, "papers": [{"id": "P001", "title": "Test Paper", "authors": ["A"], "arxiv_id": "2403.17888", "source_url": "https://arxiv.org/abs/2403.17888", "pdf_url": "", "local_pdf": "papers/P001.pdf", "download_status": "downloaded", "metadata_status": "complete"}]}
            source_manifest = retrieval / "manifest.json"
            source_manifest.write_text(json.dumps(manifest), encoding="utf-8")
            batch_dir = temp / "batch"
            subprocess.run([sys.executable, str(BATCH / "init_batch.py"), "--manifest", str(source_manifest), "--output-dir", str(batch_dir)], cwd=ROOT, check=True)
            subprocess.run([sys.executable, str(BATCH / "build_task.py"), "--batch-dir", str(batch_dir), "--paper-id", "P001"], cwd=ROOT, check=True)
            prompt = next((batch_dir / "attempts").glob("P001.attempt-*.prompt.md")).read_text(encoding="utf-8")
            self.assertIn("P001.source-pack.json", prompt)
            self.assertIn("Source Pack", prompt)
            self.assertIn("P001.html", prompt)
            self.assertIn("P001.validation.json", prompt)
            self.assertIn("_work", prompt)


if __name__ == "__main__":
    unittest.main()
