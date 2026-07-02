from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATES = {
    "pending",
    "source_ready",
    "waiting_for_agent",
    "analyzing",
    "generated",
    "validating",
    "retrying",
    "validated",
    "failed_source",
    "failed_analysis",
    "failed_quality_gate",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def skill_dir() -> Path:
    return script_dir().parent


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "skills").is_dir() and (parent / "schemas").is_dir():
            return parent
    return Path.cwd()


def rel_posix(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return os.path.relpath(path.resolve(), base.resolve()).replace("\\", "/")


def resolve_from(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path)


def ensure_batch_dirs(batch_dir: Path) -> None:
    for name in ("items", "attempts", "validation", "retry-prompts"):
        (batch_dir / name).mkdir(parents=True, exist_ok=True)


def load_manifest(batch_dir: Path) -> dict[str, Any]:
    return read_json(batch_dir / "manifest.json")


def load_status(batch_dir: Path) -> dict[str, Any]:
    status_path = batch_dir / "status.json"
    if not status_path.is_file():
        raise FileNotFoundError(status_path)
    return read_json(status_path)


def save_status(batch_dir: Path, status: dict[str, Any]) -> None:
    status["updated_at"] = utc_now_iso()
    write_json(batch_dir / "status.json", status)


def find_paper(manifest: dict[str, Any], paper_id: str) -> dict[str, Any] | None:
    for paper in manifest.get("papers", []):
        if isinstance(paper, dict) and paper.get("id") == paper_id:
            return paper
    return None


def set_item_status(status: dict[str, Any], paper_id: str, state: str, **updates: Any) -> None:
    if state not in STATES:
        raise ValueError(f"unknown state: {state}")
    item = status.setdefault("items", {}).setdefault(paper_id, {"status": "pending", "attempts": 0})
    item["status"] = state
    item.update(updates)


def next_attempt(batch_dir: Path, paper_id: str) -> int:
    existing = list((batch_dir / "attempts").glob(f"{paper_id}.attempt-*.prompt.md"))
    existing += list((batch_dir / "retry-prompts").glob(f"{paper_id}.retry-*.md"))
    return len(existing) + 1


def locate_analyzer_skill() -> Path | None:
    root = repo_root()
    candidates = [
        root / "skills" / "3dgs-paper-analyzer" / "SKILL.md",
        root / ".ai" / "skills" / "3dgs-paper-analyzer" / "SKILL.md",
    ]
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home) / "skills" / "3dgs-paper-analyzer" / "SKILL.md")
    home = Path.home()
    candidates.extend(
        [
            home / ".codex" / "skills" / "3dgs-paper-analyzer" / "SKILL.md",
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


PROFILES = {"standard-analysis", "innovation-review"}


def init_from_manifest(
    source_manifest: Path,
    output_dir: Path,
    batch_id: str | None = None,
    profile: str = "standard-analysis",
) -> tuple[dict[str, Any], dict[str, Any]]:
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    source_manifest = source_manifest.resolve()
    source_dir = source_manifest.parent
    manifest = read_json(source_manifest)
    batch_id = batch_id or str(manifest.get("batch_id") or output_dir.name)
    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_batch_dirs(output_dir)

    rewritten = dict(manifest)
    rewritten["batch_id"] = batch_id
    rewritten["source_manifest"] = str(source_manifest)
    papers = []
    status = {"schema_version": "1.0", "batch_id": batch_id, "profile": profile, "updated_at": utc_now_iso(), "items": {}}
    for paper in manifest.get("papers", []):
        if not isinstance(paper, dict):
            continue
        item = dict(paper)
        pdf_abs = resolve_from(source_dir, str(item.get("local_pdf", "")))
        metadata_abs = resolve_from(source_dir, str(item.get("metadata_path", ""))) if item.get("metadata_path") else None
        if item.get("local_pdf"):
            item["local_pdf"] = rel_posix(pdf_abs, output_dir)
        if metadata_abs:
            item["metadata_path"] = rel_posix(metadata_abs, output_dir)
        papers.append(item)
        paper_id = str(item.get("id", ""))
        pdf_exists = bool(item.get("local_pdf")) and (output_dir / item["local_pdf"]).is_file()
        set_item_status(
            status,
            paper_id,
            "source_ready" if pdf_exists else "failed_source",
            attempts=0,
            report_path=f"items/{paper_id}.md",
            json_path=f"items/{paper_id}.json",
            innovation_review_path=f"items/{paper_id}.innovation-review.json" if profile == "innovation-review" else "",
            errors=[] if pdf_exists else [f"missing PDF: {item.get('local_pdf', '')}"],
            warnings=[],
        )
    rewritten["papers"] = papers
    write_json(output_dir / "manifest.json", rewritten)
    write_json(output_dir / "status.json", status)
    return rewritten, status


def copy_if_validated(batch_dir: Path, paper_id: str, attempt_md: Path, attempt_json: Path) -> None:
    target_md = batch_dir / "items" / f"{paper_id}.md"
    target_json = batch_dir / "items" / f"{paper_id}.json"
    shutil.copy2(attempt_md, target_md)
    shutil.copy2(attempt_json, target_json)
