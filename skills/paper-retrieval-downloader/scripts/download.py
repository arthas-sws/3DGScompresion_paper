#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, url2pathname, urlopen

from retrieval_common import (
    deduplicate_items,
    extract_candidates,
    metadata_status,
    read_json,
    rel_posix,
    stable_paper_id,
    utc_now_iso,
    write_json,
)

HEADERS = {"User-Agent": "3dgs-paper-retrieval-downloader/1.0"}


def fetch_bytes(url: str, timeout: int) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return Path(url2pathname(parsed.path)).read_bytes()
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def download_pdf(url: str, destination: Path, overwrite: bool, timeout: int, retries: int, delay: float) -> tuple[str, str, int]:
    if destination.exists() and not overwrite:
        return "skipped_existing", "", 0
    if not url:
        return "failed", "missing pdf_url", 0

    attempts = 0
    last_error = ""
    for attempt in range(1, retries + 1):
        attempts = attempt
        try:
            data = fetch_bytes(url, timeout)
            destination.parent.mkdir(parents=True, exist_ok=True)
            tmp = destination.with_suffix(destination.suffix + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(destination)
            return "downloaded", "", attempts
        except Exception as exc:  # noqa: BLE001 - record external IO failure details.
            last_error = str(exc)
            if attempt < retries and delay:
                time.sleep(delay)
    return "failed", last_error or "download failed", attempts


def render_papers_md(manifest: dict[str, object]) -> str:
    lines = [f"# Paper List: {manifest['batch_id']}", ""]
    for paper in manifest["papers"]:
        title = paper.get("title") or paper.get("arxiv_id") or paper["id"]
        lines.append(f"- **{paper['id']}** {title}")
        lines.append(f"  - PDF: `{paper.get('local_pdf', '')}`")
        if paper.get("source_url"):
            lines.append(f"  - Source: {paper['source_url']}")
        if paper.get("code_url"):
            lines.append(f"  - Code: {paper['code_url']}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download PDFs and build standard retrieval manifest.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--delay", type=float, default=2.0)
    args = parser.parse_args()

    payload = read_json(args.input)
    candidates = deduplicate_items(extract_candidates(payload))
    output_dir = args.output_dir
    papers_dir = output_dir / "papers"
    metadata_dir = output_dir / "metadata"
    papers: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []

    for index, candidate in enumerate(candidates, start=1):
        paper_id = stable_paper_id(index)
        pdf_path = papers_dir / f"{paper_id}.pdf"
        metadata_path = metadata_dir / f"{paper_id}.json"
        status = "not_requested"
        reason = ""
        attempts = 0
        if not args.no_download:
            status, reason, attempts = download_pdf(
                str(candidate.get("pdf_url", "")),
                pdf_path,
                overwrite=args.overwrite,
                timeout=args.timeout,
                retries=args.retries,
                delay=args.delay,
            )
        record = {
            "id": paper_id,
            "title": candidate.get("title", ""),
            "authors": candidate.get("authors", []),
            "arxiv_id": candidate.get("arxiv_id", ""),
            "arxiv_version": candidate.get("arxiv_version", ""),
            "doi": candidate.get("doi", ""),
            "source_url": candidate.get("source_url", ""),
            "pdf_url": candidate.get("pdf_url", ""),
            "local_pdf": rel_posix(pdf_path, output_dir),
            "metadata_path": rel_posix(metadata_path, output_dir),
            "code_url": candidate.get("code_url", ""),
            "published_at": candidate.get("published_at", ""),
            "updated_at": candidate.get("updated_at", ""),
            "venue": candidate.get("venue", ""),
            "download_status": status,
            "metadata_status": metadata_status(candidate),
            "deduplication": candidate.get("deduplication", {}),
            "notes": candidate.get("notes", ""),
        }
        papers.append(record)
        write_json(metadata_path, {**candidate, "id": paper_id})
        if status == "failed":
            failures.append(
                {
                    "id": paper_id,
                    "title": record["title"],
                    "source_url": record["source_url"],
                    "stage": "download",
                    "reason": reason,
                    "attempts": attempts,
                    "retryable": True,
                }
            )

    manifest = {
        "schema_version": "1.0",
        "batch_id": args.batch_id,
        "created_at": utc_now_iso(),
        "query": payload.get("query", {"keywords": [], "date_from": None, "date_to": None}),
        "papers": papers,
    }
    failures_payload = {"schema_version": "1.0", "batch_id": args.batch_id, "failures": failures}
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "failures.json", failures_payload)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "papers.md").write_text(render_papers_md(manifest), encoding="utf-8")
    print(f"manifest papers={len(papers)} failures={len(failures)} output={output_dir}")


if __name__ == "__main__":
    main()
