#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import re
from pathlib import Path


def load_markdown():
    try:
        import markdown
    except ImportError as exc:
        raise SystemExit("Missing dependency: python -m pip install markdown") from exc
    return markdown


def convert_mermaid(text: str) -> str:
    pattern = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
    return pattern.sub(lambda m: f'<pre class="mermaid">{html.escape(m.group(1).strip())}</pre>', text)


def embed_images(text: str, base_dir: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        alt, src = match.groups()
        if re.match(r"^[a-z]+://|^data:", src):
            return match.group(0)
        image_path = (base_dir / src).resolve()
        if not image_path.is_file():
            return match.group(0)
        mime = mimetypes.guess_type(image_path.name)[0] or "image/png"
        data = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return f"![{alt}](data:{mime};base64,{data})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, text)


def extract_title(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Markdown paper analysis report to HTML.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--template", type=Path, default=Path(__file__).resolve().parents[1] / "assets" / "article-template.html")
    parser.add_argument("--embed-images", action="store_true")
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Input file not found: {args.input}")
    if not args.template.is_file():
        raise SystemExit(f"Template file not found: {args.template}")

    source = args.input.read_text(encoding="utf-8")
    if args.embed_images:
        source = embed_images(source, args.input.parent)
    source = convert_mermaid(source)

    markdown = load_markdown()
    body = markdown.markdown(source, extensions=["tables", "fenced_code", "sane_lists", "toc"], output_format="html5")
    template = args.template.read_text(encoding="utf-8")
    if "{{TITLE}}" not in template or "{{CONTENT}}" not in template:
        raise SystemExit("Template must contain {{TITLE}} and {{CONTENT}}.")
    result = template.replace("{{TITLE}}", html.escape(extract_title(source, args.input.stem))).replace("{{CONTENT}}", body)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"generated {args.output}")


if __name__ == "__main__":
    main()
