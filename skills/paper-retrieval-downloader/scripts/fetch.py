#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from retrieval_common import (
    arxiv_abs_url,
    arxiv_pdf_url,
    clean_text,
    deduplicate_items,
    normalize_arxiv_id,
    normalize_candidate,
    utc_now_iso,
    write_json,
)

API_ENDPOINT = "https://arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
HEADERS = {"User-Agent": "3dgs-paper-retrieval-downloader/1.0"}


def build_query_url(search_query: str, max_results: int) -> str:
    return f"{API_ENDPOINT}?{urlencode({'search_query': search_query, 'max_results': max_results, 'sortBy': 'submittedDate', 'sortOrder': 'descending'})}"


def build_id_url(ids: list[str]) -> str:
    return f"{API_ENDPOINT}?{urlencode({'id_list': ','.join(ids), 'max_results': len(ids)})}"


def fetch_feed(url: str, timeout: int) -> ElementTree.Element:
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=timeout) as response:
        return ElementTree.fromstring(response.read())


def parse_feed(feed: ElementTree.Element) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for entry in feed.findall("atom:entry", ATOM_NS):
        raw_id = clean_text(entry.findtext("atom:id", default="", namespaces=ATOM_NS))
        arxiv_id, version = normalize_arxiv_id(raw_id)
        if not arxiv_id:
            continue
        authors = []
        for author_node in entry.findall("atom:author", ATOM_NS):
            name = clean_text(author_node.findtext("atom:name", default="", namespaces=ATOM_NS))
            if name:
                authors.append(name)
        doi = ""
        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "doi":
                doi = link.attrib.get("href", "")
        items.append(
            normalize_candidate(
                {
                    "title": clean_text(entry.findtext("atom:title", default="", namespaces=ATOM_NS)),
                    "authors": authors,
                    "abstract": clean_text(entry.findtext("atom:summary", default="", namespaces=ATOM_NS)),
                    "arxiv_id": arxiv_id,
                    "arxiv_version": version,
                    "doi": doi,
                    "source_url": arxiv_abs_url(arxiv_id),
                    "pdf_url": arxiv_pdf_url(arxiv_id),
                    "published_at": clean_text(entry.findtext("atom:published", default="", namespaces=ATOM_NS)),
                    "updated_at": clean_text(entry.findtext("atom:updated", default="", namespaces=ATOM_NS)),
                }
            )
        )
    return items


def parse_input_list(path: Path) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        arxiv_id, version = normalize_arxiv_id(value)
        if arxiv_id:
            items.append(
                normalize_candidate(
                    {
                        "arxiv_id": arxiv_id,
                        "arxiv_version": version,
                        "source_url": arxiv_abs_url(arxiv_id),
                        "pdf_url": arxiv_pdf_url(arxiv_id),
                    }
                )
            )
        elif value.startswith("http"):
            items.append(normalize_candidate({"source_url": value, "pdf_url": value if value.lower().endswith(".pdf") else ""}))
        else:
            items.append(normalize_candidate({"title": value}))
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch 3DGS-related paper candidates from arXiv or an input list.")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--keyword", action="append", default=[])
    parser.add_argument("--arxiv-id", action="append", default=[])
    parser.add_argument("--input-list", type=Path)
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidates: list[dict[str, object]] = []
    if args.input_list:
        candidates.extend(parse_input_list(args.input_list))

    arxiv_ids = []
    for value in args.arxiv_id:
        arxiv_id, _ = normalize_arxiv_id(value)
        if arxiv_id:
            arxiv_ids.append(arxiv_id)
    if arxiv_ids:
        candidates.extend(parse_feed(fetch_feed(build_id_url(arxiv_ids), args.timeout)))
        if args.delay:
            time.sleep(args.delay)

    for keyword in args.keyword:
        feed = fetch_feed(build_query_url(f'all:"{keyword}"', args.max_results), args.timeout)
        candidates.extend(parse_feed(feed))
        if args.delay:
            time.sleep(args.delay)

    payload = {
        "schema_version": "1.0",
        "batch_id": args.batch_id,
        "created_at": utc_now_iso(),
        "query": {
            "keywords": args.keyword,
            "date_from": args.date_from,
            "date_to": args.date_to,
            "source": "arxiv",
        },
        "candidates": deduplicate_items(candidates),
    }
    write_json(args.output, payload)
    print(f"wrote {len(payload['candidates'])} candidates to {args.output}")


if __name__ == "__main__":
    main()
