# Table Fidelity

Preserve experiment tables as evidence, not as rewritten prose.

## Rules

- Prefer automatic table extraction.
- If automatic extraction fails, record `extraction_status: "auto_failed"` before any manual entry.
- Manual screenshot reading or manual transcription is allowed only with `entry_method: "manual_transcription"`.
- Keep original metric names, units, arrows, dataset names, scene names, bitrate points, and method names.
- Do not normalize units, average rows, merge bitrate points, fill missing cells, or recompute values unless the paper explicitly reports the derived value.
- Mark unclear cells with `uncertain: true` and do not guess.
- Mark every table with evidence such as `Paper Table 2`.
- Store full table rows in `experiment_tables`; the global `paper-index.jsonl` must store only summary tags and paths.

## Extraction Status Values

- `verified`: extracted and checked against the paper.
- `auto_failed`: automatic extraction failed.
- `manual_transcription`: manually entered from PDF page or screenshot.
- `partial`: only part of the table was readable.
- `not_applicable`: no relevant table exists.

## Required Audit

For each main table, explain whether it supports any innovation claim. If a table compares methods under different settings, mark comparability as `not_directly_comparable` instead of ranking the methods.
