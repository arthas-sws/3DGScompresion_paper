from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "render_html.py"


class HtmlModeRenderingTest(unittest.TestCase):
    def test_html_contains_status_classes_and_mathjax(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            md = temp / "P001.md"
            html = temp / "P001.html"
            md.write_text("# Test\n\n<span class=\"support-direct\">直接</span>\n<span class=\"priority-p0\">P0</span>\n\n\\[\nH = J_R^\\top J_R\n\\]\n\n<details><summary>附录</summary>表格</details>\n", encoding="utf-8")
            subprocess.run([sys.executable, str(RENDER), str(md), str(html)], cwd=ROOT, check=True)
            text = html.read_text(encoding="utf-8")
            self.assertIn("support-direct", text)
            self.assertIn("priority-p0", text)
            self.assertIn("tex-mml-chtml", text)
            self.assertIn("<details>", text)


if __name__ == "__main__":
    unittest.main()
