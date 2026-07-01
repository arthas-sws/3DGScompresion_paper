from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "skills" / "3dgs-paper-batch-orchestrator" / "scripts"
ANALYZER = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts"


class BatchValidationTest(unittest.TestCase):
    def test_batch_aggregates_only_validated_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            retrieval = temp / "retrieval"
            (retrieval / "papers").mkdir(parents=True)
            (retrieval / "papers" / "P001.pdf").write_bytes(b"%PDF-1.4 p1")
            (retrieval / "papers" / "P002.pdf").write_bytes(b"%PDF-1.4 p2")
            manifest = {
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
                    },
                    {
                        "id": "P002",
                        "title": "Test Paper Two",
                        "authors": ["B"],
                        "arxiv_id": "2403.17889",
                        "source_url": "https://arxiv.org/abs/2403.17889",
                        "pdf_url": "",
                        "local_pdf": "papers/P002.pdf",
                        "download_status": "downloaded",
                        "metadata_status": "complete",
                    },
                ],
            }
            source_manifest = retrieval / "manifest.json"
            source_manifest.write_text(json.dumps(manifest), encoding="utf-8")
            batch_dir = temp / "batch"

            subprocess.run([sys.executable, str(BATCH / "init_batch.py"), "--manifest", str(source_manifest), "--output-dir", str(batch_dir)], check=True, cwd=ROOT)
            subprocess.run([sys.executable, str(BATCH / "run_batch.py"), "--batch-dir", str(batch_dir)], check=True, cwd=ROOT)
            subprocess.run(
                [
                    sys.executable,
                    str(ANALYZER / "create_analysis_stub.py"),
                    "--paper-id",
                    "P001",
                    "--title",
                    "Test Paper One",
                    "--output-dir",
                    str(batch_dir / "items"),
                    "--source-url",
                    "https://arxiv.org/abs/2403.17888",
                    "--pdf-path",
                    str(retrieval / "papers" / "P001.pdf"),
                ],
                check=True,
                cwd=ROOT,
            )
            subprocess.run([sys.executable, str(BATCH / "run_batch.py"), "--batch-dir", str(batch_dir)], check=True, cwd=ROOT)
            subprocess.run([sys.executable, str(BATCH / "aggregate_reports.py"), "--batch-dir", str(batch_dir)], check=True, cwd=ROOT)
            subprocess.run([sys.executable, str(BATCH / "validate_batch.py"), "--batch-dir", str(batch_dir)], check=True, cwd=ROOT)

            status = json.loads((batch_dir / "status.json").read_text(encoding="utf-8"))
            matrix = json.loads((batch_dir / "result-matrix.json").read_text(encoding="utf-8"))
            self.assertEqual(status["items"]["P001"]["status"], "validated")
            self.assertEqual(status["items"]["P002"]["status"], "waiting_for_agent")
            self.assertEqual([paper["id"] for paper in matrix["papers"]], ["P001"])
            self.assertEqual(matrix["failed"][0]["id"], "P002")


if __name__ == "__main__":
    unittest.main()
