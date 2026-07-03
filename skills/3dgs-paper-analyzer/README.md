# 3dgs-paper-analyzer

Single-paper Chinese review skill for 3DGS, Gaussian Splatting, NeRF, neural rendering, reconstruction, and especially 3DGS compression papers.

The skill has two report modes only:

- `standard-analysis`: technical understanding, method/code mapping, experiment audit, and reproducibility.
- `innovation-review`: innovation-claim audit, experiment support, related-paper depth, improvement ideas, and supplemental experiment design.

There is no `auto` mode and no third reviewer skill.

## Shared Source Pack

Both modes generate or reuse one internal fact file:

```text
P001.source-pack.json
```

The Source Pack is not a report mode. It stores verified paper identity, PDF hash, paper version, code commit, evidence ledger, equations, figures, experiment tables, code mapping, reported limitations, unverified items, and provenance.

`P001.json` must point to it through `source_pack_path` or `extensions.source_pack`. When a second mode runs and PDF hash, paper version, code commit, and Source Pack validation still match, reuse it. If any source changes, mark the Source Pack stale and re-check affected facts.

## Outputs

Every mode writes:

```text
P001.source-pack.json
P001.md
P001.json
P001.html
P001.validation.json
```

`P001.json` follows:

```text
schemas/paper-analysis.schema.json
```

`innovation-review` additionally writes:

```text
P001.innovation-review.json
```

following:

```text
schemas/innovation-review.schema.json
```

## Validation

Use `finalize_report.py` for delivery. It validates the Source Pack and mode
outputs, writes `P001.validation.json`, renders `P001.html`, checks the HTML, and
returns the delivery state.

```powershell
python skills\3dgs-paper-analyzer\scripts\finalize_report.py `
  --mode standard-analysis `
  --paper-id P001 `
  --output-dir analysis-output\P001

python skills\3dgs-paper-analyzer\scripts\finalize_report.py `
  --mode innovation-review `
  --paper-id P001 `
  --output-dir analysis-output\P001 `
  --strict
```

Completion states:

- `COMPLETE`: all required files exist; validators PASS; HTML exists and is non-empty.
- `COMPLETE_WITH_WARNINGS`: no FAIL; at least one WARN; HTML exists and is non-empty.
- `INCOMPLETE`: any required file is missing, any validator FAILs, validation JSON is missing, or HTML is missing/empty/invalid.

Do not report a paper analysis complete unless finalization returns `COMPLETE`
or `COMPLETE_WITH_WARNINGS`.

```powershell
python skills\3dgs-paper-analyzer\scripts\validate_source_pack.py `
  --source-pack analysis-output\P001\P001.source-pack.json

python skills\3dgs-paper-analyzer\scripts\validate_report.py `
  --md analysis-output\P001\P001.md `
  --json analysis-output\P001\P001.json

python skills\3dgs-paper-analyzer\scripts\validate_innovation_review.py `
  --md analysis-output\P001\P001.md `
  --json analysis-output\P001\P001.json `
  --review-json analysis-output\P001\P001.innovation-review.json `
  --strict

python skills\3dgs-paper-analyzer\scripts\validate_cross_mode_consistency.py `
  --source-pack tmp\mode-regression\P001\P001.source-pack.json `
  --standard-json tmp\mode-regression\P001\standard-analysis\P001.json `
  --innovation-json tmp\mode-regression\P001\innovation-review\P001.json `
  --review-json tmp\mode-regression\P001\innovation-review\P001.innovation-review.json `
  --output tmp\mode-regression\P001\cross-mode-validation.json
```

## HTML

HTML is required for final delivery. `finalize_report.py` calls the single renderer:

```powershell
python skills\3dgs-paper-analyzer\scripts\render_html.py `
  analysis-output\P001\P001.md `
  analysis-output\P001\P001.html
```

Internal extraction files, table dumps, cloned official code, and other working
materials belong under `analysis-output\P001\_work\`. `_work\` is not part of
formal delivery and is ignored by batch aggregation.
