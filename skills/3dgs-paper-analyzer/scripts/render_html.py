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


def slugify(value: str) -> str:
    slug = re.sub(r"\s+", "-", re.sub(r"[^\w\u4e00-\u9fff\s-]", "", value.lower())).strip("-")
    return slug or "section"


def build_nav(source: str) -> str:
    items: list[str] = []
    seen: dict[str, int] = {}
    for match in re.finditer(r"^(#{2,3})\s+(.+?)\s*$", source, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        base = slugify(title)
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchor = base if count == 0 else f"{base}-{count + 1}"
        items.append(f'<li class="toc-level-{level}"><a href="#{anchor}">{html.escape(title)}</a></li>')
    if not items:
        return ""
    return '<nav class="toc"><strong>目录</strong><ul>' + "\n".join(items) + "</ul></nav>"


def add_heading_ids(body: str) -> str:
    seen: dict[str, int] = {}

    def repl(match: re.Match[str]) -> str:
        tag = match.group(1)
        attrs = match.group(2) or ""
        title = re.sub(r"<.*?>", "", match.group(3)).strip()
        if ' id="' in attrs:
            return match.group(0)
        base = slugify(html.unescape(title))
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchor = base if count == 0 else f"{base}-{count + 1}"
        return f"<{tag}{attrs} id=\"{anchor}\">{match.group(3)}</{tag}>"

    return re.sub(r"<(h[2-3])([^>]*)>(.*?)</\1>", repl, body)


def wrap_tables(body: str) -> str:
    return re.sub(r"(<table>.*?</table>)", r'<div class="table-scroll">\1</div>', body, flags=re.DOTALL)


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
    body = wrap_tables(add_heading_ids(body))
    nav = build_nav(source)
    template = args.template.read_text(encoding="utf-8")
    if "{{TITLE}}" not in template or "{{CONTENT}}" not in template:
        raise SystemExit("Template must contain {{TITLE}} and {{CONTENT}}.")
    result = template.replace("{{TITLE}}", html.escape(extract_title(source, args.input.stem))).replace("{{CONTENT}}", nav + body)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"generated {args.output}")


if __name__ == "__main__":
    main()
