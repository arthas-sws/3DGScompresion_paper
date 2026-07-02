# Table Fidelity

Preserve experiment tables as evidence. Do not rewrite table data into approximate prose.

## Rules

- Prefer automatic extraction when available.
- If automatic extraction fails and manual reading is used, record `extraction_method: "manual_transcription"` and `verification_status: "partial"` or `"verified"`.
- Keep original metric names, units, arrows, dataset names, scene names, bitrate points, method names, and table captions.
- Do not normalize units, average rows, merge bitrate points, fill missing cells, or recompute values unless the paper explicitly reports the derived value.
- Mark unclear cells in `uncertain_cells`; do not guess.
- Every table must include evidence such as `Paper Table 2`.
- Full rows belong in `<paper_id>.innovation-review.json`; the optional paper index stores only summary tags and paths.

## Table Fields

Use:

```json
{
  "table_id": "T1",
  "caption": "",
  "evidence": "Paper Table 1",
  "source_page": 10,
  "extraction_method": "automatic",
  "verification_status": "verified",
  "comparability": "directly_comparable",
  "columns": [],
  "rows": [],
  "uncertain_cells": []
}
```

`comparability` describes whether the table can support cross-method comparison under compatible settings.
