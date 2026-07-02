# 3dgs-paper-analyzer

Single-paper Chinese review skill for 3DGS, Gaussian Splatting, NeRF, neural rendering, reconstruction, and especially 3DGS compression papers.

It has two modes:

- `standard-analysis`: default method/code/experiment/efficiency/reproducibility analysis.
- `innovation-review`: deeper innovation-claim review with experiment table preservation, similar-paper context, improvement ideas, and proposed supplemental experiments.

## Standard Output

Every mode writes:

```text
P001.md
P001.json
```

`P001.json` follows:

```text
schemas/paper-analysis.schema.json
```

## Innovation Review Extension

`innovation-review` additionally writes:

```text
P001.innovation-review.json
```

and `P001.json` may point to it:

```json
{
  "extensions": {
    "innovation_review": "P001.innovation-review.json"
  }
}
```

The extension follows:

```text
schemas/innovation-review.schema.json
```

## Validation

```powershell
python skills\3dgs-paper-analyzer\scripts\validate_report.py `
  --md analysis-output\P001\P001.md `
  --json analysis-output\P001\P001.json

python skills\3dgs-paper-analyzer\scripts\validate_innovation_review.py `
  --md analysis-output\P001\P001.md `
  --json analysis-output\P001\P001.json `
  --review-json analysis-output\P001\P001.innovation-review.json `
  --strict
```

## Optional Index

The analyzer does not create a root paper index by default. Use explicit opt-in:

```powershell
python skills\3dgs-paper-analyzer\scripts\update_paper_index.py `
  --review-json analysis-output\P001\P001.innovation-review.json `
  --index path\to\paper-index.jsonl
```

## HTML

```powershell
python skills\3dgs-paper-analyzer\scripts\render_html.py `
  analysis-output\P001\P001.md `
  analysis-output\P001\P001.html
```
