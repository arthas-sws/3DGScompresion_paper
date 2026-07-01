from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARXIV_ID_RE = re.compile(r"(?P<base>\d{4}\.\d{4,5})(?:v(?P<version>\d+))?", re.I)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def skill_dir() -> Path:
    return script_dir().parent


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "schemas").is_dir() and (parent / "skills").is_dir():
            return parent
    return Path.cwd()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(value: str | None) -> str:
    return " ".join((value or "").replace("\xa0", " ").split())


def normalize_title(value: str | None) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text)
    return " ".join(text.split())


def normalize_arxiv_id(raw: str | None) -> tuple[str, str]:
    value = (raw or "").strip()
    if not value:
        return "", ""
    value = value.replace("/pdf/", "/abs/")
    value = value.removesuffix(".pdf")
    match = ARXIV_ID_RE.search(value)
    if not match:
        return "", ""
    return match.group("base"), (match.group("version") or "")


def arxiv_abs_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""


def arxiv_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else ""


def candidate_key(item: dict[str, Any]) -> tuple[str, str]:
    arxiv_id, _ = normalize_arxiv_id(str(item.get("arxiv_id") or item.get("source_url") or item.get("pdf_url") or ""))
    if arxiv_id:
        return f"arxiv:{arxiv_id}", "same_arxiv_base_id"
    doi = clean_text(str(item.get("doi", ""))).casefold()
    if doi:
        return f"doi:{doi}", "same_doi"
    title = normalize_title(str(item.get("title", "")))
    if title:
        return f"title:{title}", "same_normalized_title"
    source = clean_text(str(item.get("source_url", "") or item.get("pdf_url", "")))
    return f"source:{source}", "same_source_url"


def metadata_score(item: dict[str, Any]) -> int:
    score = 0
    for key in ("title", "authors", "arxiv_id", "source_url", "pdf_url", "published_at", "doi", "code_url"):
        value = item.get(key)
        if value:
            score += 2 if isinstance(value, list) and value else 1
    return score


def merge_missing(base: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in candidate.items():
        if key == "deduplication":
            continue
        if not merged.get(key) and value:
            merged[key] = value
    return merged


def deduplicate_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for raw in items:
        item = normalize_candidate(raw)
        key, reason = candidate_key(item)
        if key not in kept:
            item["deduplication"] = {"canonical_key": key, "duplicates": [], "reason": reason}
            kept[key] = item
            order.append(key)
            continue
        current = kept[key]
        duplicate_source = item.get("source_url") or item.get("pdf_url") or item.get("arxiv_id") or item.get("title") or key
        current.setdefault("deduplication", {"canonical_key": key, "duplicates": [], "reason": reason})
        current["deduplication"].setdefault("duplicates", []).append(str(duplicate_source))
        if metadata_score(item) > metadata_score(current):
            item = merge_missing(item, current)
            item["deduplication"] = current["deduplication"]
            kept[key] = item
        else:
            kept[key] = merge_missing(current, item)
    return [kept[key] for key in order]


def normalize_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    item = dict(raw)
    arxiv_id, version = normalize_arxiv_id(str(item.get("arxiv_id") or item.get("source_url") or item.get("pdf_url") or ""))
    if arxiv_id:
        item["arxiv_id"] = arxiv_id
        item["arxiv_version"] = version
        item.setdefault("source_url", arxiv_abs_url(arxiv_id))
        item.setdefault("pdf_url", arxiv_pdf_url(arxiv_id))
    item["title"] = clean_text(str(item.get("title", "")))
    authors = item.get("authors", [])
    if isinstance(authors, str):
        authors = [clean_text(x) for x in re.split(r",|;", authors) if clean_text(x)]
    item["authors"] = authors if isinstance(authors, list) else []
    for key in ("source_url", "pdf_url", "doi", "code_url", "published_at", "updated_at", "venue", "notes"):
        item[key] = clean_text(str(item.get(key, "")))
    return item


def extract_candidates(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload.get("candidates"), list):
        return [x for x in payload["candidates"] if isinstance(x, dict)]
    if isinstance(payload.get("papers"), list):
        return [x for x in payload["papers"] if isinstance(x, dict)]
    if isinstance(payload.get("new"), list):
        return [x for x in payload["new"] if isinstance(x, dict)]
    raise ValueError("Input JSON must contain candidates, papers, or new.")


def stable_paper_id(index: int) -> str:
    return f"P{index:03d}"


def rel_posix(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def metadata_status(item: dict[str, Any]) -> str:
    required = ["title", "authors", "source_url", "pdf_url"]
    present = sum(1 for key in required if item.get(key))
    if present == len(required):
        return "complete"
    if present:
        return "partial"
    return "missing"
