# 3dgs-paper-batch-orchestrator

Batch orchestration skill for 3DGS paper analysis. It reads a retrieval `manifest.json`, creates isolated per-paper task prompts, waits for `3dgs-paper-analyzer` outputs, validates them, retries failed items, and aggregates validated standard JSON files.

## Profiles

- `standard-analysis`: default analyzer report.
- `innovation-review`: asks the analyzer to produce the standard `Pxxx.md` and `Pxxx.json` plus `Pxxx.innovation-review.json`.

Batch aggregation continues to read only standard `Pxxx.json`.

## Usage

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\init_batch.py `
  --manifest paper-retrieval-output\compression-survey-01\manifest.json `
  --output-dir paper-batch-output\compression-survey-01

python skills\3dgs-paper-batch-orchestrator\scripts\run_batch.py `
  --batch-dir paper-batch-output\compression-survey-01
```

Innovation-review profile:

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\init_batch.py `
  --manifest paper-retrieval-output\compression-survey-01\manifest.json `
  --output-dir paper-batch-output\compression-survey-01 `
  --profile innovation-review
```

The orchestrator does not pretend to automatically run Codex agents. If an item has no generated report yet, its status is `waiting_for_agent` and the prompt is written under `attempts/`.
