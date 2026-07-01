#!/usr/bin/env python3
"""将 Markdown 论文报告转换为 HTML。"""

from __future__ import annotations
import argparse
import html
import re
from pathlib import Path


def load_markdown():
    try:
        import markdown
    except ImportError as exc:
        raise SystemExit("缺少 markdown：python -m pip install markdown") from exc
    return markdown


def convert_mermaid(text: str) -> str:
    pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    return pattern.sub(
        lambda m: f'<pre class="mermaid">{html.escape(m.group(1).strip())}</pre>',
        text,
    )


def extract_title(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets" / "article-template.html",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"找不到输入文件：{args.input}")
    if not args.template.is_file():
        raise SystemExit(f"找不到模板：{args.template}")

    source = args.input.read_text(encoding="utf-8")
    template = args.template.read_text(encoding="utf-8")
    if "{{TITLE}}" not in template or "{{CONTENT}}" not in template:
        raise SystemExit("模板必须包含 {{TITLE}} 和 {{CONTENT}}。")

    source = convert_mermaid(source)
    markdown = load_markdown()
    body = markdown.markdown(
        source,
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        output_format="html5",
    )
    title = extract_title(source, args.input.stem)
    result = template.replace("{{TITLE}}", html.escape(title)).replace("{{CONTENT}}", body)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"已生成：{args.output}")


if __name__ == "__main__":
    main()
