# 3DGS Paper Skills

This repository contains three Codex Skills for 3D Gaussian Splatting paper workflows:

```text
skills/
+-- paper-retrieval-downloader/
+-- 3dgs-paper-analyzer/
+-- 3dgs-paper-batch-orchestrator/
```

`.agents/skills/` is only a local installed-skill cache. It is ignored by git and is not the source directory for this repository.

## Workflow

```text
paper-retrieval-downloader
  -> manifest.json + PDFs
3dgs-paper-batch-orchestrator
  -> per-paper task prompts and validation
3dgs-paper-analyzer
  -> Source Pack + Markdown + JSON + validation JSON + HTML, with optional innovation-review extension
```

Single-paper use can call `3dgs-paper-analyzer` directly from a PDF, URL, or manifest entry.

## Skill Responsibilities

`paper-retrieval-downloader`

- Searches, deduplicates, downloads, and records 3DGS/NeRF-related papers.
- Produces `manifest.json`, `failures.json`, `metadata/`, `papers/`, and `papers.md`.
- Does not analyze paper methods or experiments.

`3dgs-paper-analyzer`

- Reviews one paper at a time.
- Default mode: `standard-analysis`.
- Optional mode: `innovation-review`.
- Always produces `Pxxx.source-pack.json`, `Pxxx.md`, `Pxxx.json`, `Pxxx.html`, and `Pxxx.validation.json`.
- Reuses the Source Pack across both modes when PDF hash, paper version, code commit, and validation match.
- `Pxxx.json` follows `schemas/paper-analysis.schema.json`.
- In `innovation-review` mode, also produces `Pxxx.innovation-review.json` following `schemas/innovation-review.schema.json`.

`3dgs-paper-batch-orchestrator`

- Reads retrieval manifests.
- Creates isolated per-paper task prompts.
- Maintains `status.json`.
- Supports profiles: `standard-analysis` and `innovation-review`.
- Aggregates only validated standard JSON files, so innovation-review remains batch-compatible.

## Analyzer Modes

### standard-analysis

Use for normal single-paper Chinese analysis: method, code, experiments, efficiency, limitations, comparability, and reproducibility.

Outputs:

```text
P001.source-pack.json
P001.md
P001.json
P001.html
P001.validation.json
```

### innovation-review

Use when the user asks to:

- extract innovation claims;
- judge whether experiments support those claims;
- preserve major experiment tables;
- compare similar papers without unsupported global novelty conclusions;
- propose method improvements;
- design supplemental experiments.

Outputs:

```text
analysis-output/P001/
+-- P001.md
+-- P001.json
+-- P001.source-pack.json
+-- P001.innovation-review.json
+-- P001.html
+-- P001.validation.json
```

The standard JSON may include:

```json
{
  "extensions": {
    "source_pack": "P001.source-pack.json",
    "innovation_review": "P001.innovation-review.json"
  }
}
```

`innovation-review` uses schema version `1.1`, full Claim cards, a Claim-Evidence matrix, `review_depth`, prioritized improvement ideas, and engineering-ready supplemental experiments.

## Examples

### Retrieval

```powershell
python skills\paper-retrieval-downloader\scripts\fetch.py `
  --batch-id compression-survey-01 `
  --keyword "3D Gaussian Splatting compression" `
  --max-results 20 `
  --output tmp\compression-candidates.json

python skills\paper-retrieval-downloader\scripts\download.py `
  --input tmp\compression-candidates.json `
  --batch-id compression-survey-01 `
  --output-dir paper-retrieval-output\compression-survey-01
```

### Standard Single-Paper Analysis

Recommended current request shape:

```text
请使用 $3dgs-paper-analyzer 的 standard-analysis 模式。

输入 PDF：
paper-retrieval-output/compression-survey-01/papers/P001.pdf

输出目录：
analysis-output/P001
```

The analyzer must read the paper, generate or reuse the Source Pack, generate
Markdown and JSON, run finalization, save `P001.validation.json`, render
`P001.html`, check delivery completeness, and report `COMPLETE`,
`COMPLETE_WITH_WARNINGS`, or `INCOMPLETE`. Users do not need to separately ask
for HTML.

```text
使用 3dgs-paper-analyzer 的 standard-analysis 模式，
分析 paper-retrieval-output/compression-survey-01/manifest.json 中的 P001。
输出 analysis-output/P001/P001.md 和 analysis-output/P001/P001.json。
```

### Innovation Review

```text
使用 3dgs-paper-analyzer 的 innovation-review 模式，
对 P001 做创新主张、实验支撑、相似论文和改进方向分析。
仍然输出 P001.md 和 P001.json，并额外输出 P001.innovation-review.json。
```

Validation:

```powershell
python skills\3dgs-paper-analyzer\scripts\validate_report.py `
  --md analysis-output\P001\P001.md `
  --json analysis-output\P001\P001.json

python skills\3dgs-paper-analyzer\scripts\validate_source_pack.py `
  --source-pack analysis-output\P001\P001.source-pack.json

python skills\3dgs-paper-analyzer\scripts\validate_innovation_review.py `
  --md analysis-output\P001\P001.md `
  --json analysis-output\P001\P001.json `
  --review-json analysis-output\P001\P001.innovation-review.json `
  --strict

python skills\3dgs-paper-analyzer\scripts\validate_cross_mode_consistency.py `
  --source-pack analysis-output\P001\P001.source-pack.json `
  --standard-json analysis-output\P001\standard-analysis\P001.json `
  --innovation-json analysis-output\P001\innovation-review\P001.json `
  --review-json analysis-output\P001\innovation-review\P001.innovation-review.json `
  --output analysis-output\P001\cross-mode-validation.json
```

Optional index update:

```powershell
python skills\3dgs-paper-analyzer\scripts\update_paper_index.py `
  --review-json analysis-output\P001\P001.innovation-review.json `
  --index path\to\paper-index.jsonl
```

No root `paper-index.jsonl` is created unless `--index` is explicitly provided.

### HTML Rendering

Use finalization for delivery:

```powershell
python skills\3dgs-paper-analyzer\scripts\finalize_report.py `
  --mode standard-analysis `
  --paper-id P001 `
  --output-dir analysis-output\P001
```

```powershell
python skills\3dgs-paper-analyzer\scripts\render_html.py `
  analysis-output\P001\P001.md `
  analysis-output\P001\P001.html
```

`finalize_report.py` calls the renderer after validation succeeds. The renderer supports table rendering, heading navigation, wide-table horizontal scrolling, Mermaid blocks, and MathJax formulas.

Internal fulltext/table dumps, cloned official code, screenshots, and other work materials belong under `<output-dir>/_work/`; they are not delivery artifacts.

### Batch Profiles

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\init_batch.py `
  --manifest paper-retrieval-output\compression-survey-01\manifest.json `
  --output-dir paper-batch-output\compression-survey-01 `
  --profile innovation-review

python skills\3dgs-paper-batch-orchestrator\scripts\run_batch.py `
  --batch-dir paper-batch-output\compression-survey-01
```

Use `--profile standard-analysis` or omit `--profile` for the existing default flow.

## Schemas

```text
schemas/
+-- retrieval-manifest.schema.json
+-- failures.schema.json
+-- paper-source-pack.schema.json
+-- paper-analysis.schema.json
+-- innovation-review.schema.json
+-- batch-status.schema.json
```

## Tests

```powershell
python -m unittest discover -s tests -v
python -m pytest -q
```

## Notes

- Related paper downloads belong to `paper-retrieval-downloader`; analyzer must not silently download missing related papers.
- Batch aggregation reads standard `Pxxx.json` only. Innovation-review JSON is an extension artifact.
- `.agent-config/`, `paper-library/`, `.agents/skills/`, and root `paper-index.jsonl` are ignored local artifacts.
