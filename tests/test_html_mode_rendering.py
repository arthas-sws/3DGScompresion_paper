from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "skills" / "3dgs-paper-analyzer" / "scripts" / "render_html.py"


class HtmlModeRenderingTest(unittest.TestCase):
    def test_html_contains_status_classes_mathjax_toc_and_table_scroll(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            md = temp / "P001.md"
            html = temp / "P001.html"
            md.write_text(
                "# Test\n\n"
                "## 1. Section\n\n"
                "| A | B |\n|---|---|\n| 1 | 2 |\n\n"
                "<span class=\"support-direct\">direct</span>\n"
                "<span class=\"priority-p0\">P0</span>\n\n"
                "\\[\nH = J_R^\\top J_R\n\\]\n\n"
                "<details><summary>Appendix</summary>table</details>\n",
                encoding="utf-8",
            )
            subprocess.run([sys.executable, str(RENDER), str(md), str(html)], cwd=ROOT, check=True)
            text = html.read_text(encoding="utf-8")
            self.assertIn("support-direct", text)
            self.assertIn("priority-p0", text)
            self.assertIn("tex-mml-chtml", text)
            self.assertIn("<details>", text)
            self.assertIn("class=\"toc\"", text)
            self.assertIn("目录", text)
            self.assertIn("class=\"table-scroll\"", text)


if __name__ == "__main__":
    unittest.main()
