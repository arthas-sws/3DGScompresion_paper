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

Use the single renderer:

```powershell
python skills\3dgs-paper-analyzer\scripts\render_html.py `
  analysis-output\P001\P001.md `
  analysis-output\P001\P001.html
```
