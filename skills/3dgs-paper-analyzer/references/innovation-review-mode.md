# Innovation Review Mode

Use `innovation-review` mode when the user asks to deeply inspect a single 3DGS compression paper's innovation claims, experimental support, similar papers, improvement directions, or supplemental experiment design.

This is a mode of `3dgs-paper-analyzer`, not a separate skill. Always produce the standard analyzer outputs first:

```text
<paper_id>.md
<paper_id>.json
```

The standard JSON must continue to follow `schemas/paper-analysis.schema.json` so batch tools can validate and aggregate it. In innovation-review mode, also produce:

```text
<paper_id>.innovation-review.json
```

Set the standard JSON extension pointer:

```json
{
  "extensions": {
    "innovation_review": "P001.innovation-review.json"
  }
}
```

## Required Review Content

- Paper identity and version.
- Problem definition and compression target.
- Method framework.
- Author innovation claims.
- Independent interpretation for each claim.
- Paper location and evidence for each claim.
- Key experiment tables, faithfully preserved.
- Experiment support level for each claim.
- Similar papers and similarity scope.
- Practical differences between the paper and similar papers.
- Improvement ideas.
- Proposed supplemental experiments.
- Reproducibility risks.
- Conclusion boundaries.

Use stable IDs:

- Claims: `C1`, `C2`, `C3`
- Tables: `T1`, `T2`, `T3`

## Related Paper Boundary

Do not silently download related papers. Use this order:

1. Read related work, method discussion, and experiment baselines in the main paper.
2. Search provided retrieval manifest and local retrieval outputs.
3. If a key related paper is missing, write an explicit retrieval request list for `paper-retrieval-downloader`.
4. Download only after the user explicitly agrees.

Do not create `.agent-config`, `paper-library`, or root `paper-index.jsonl`.

## Novelty Assessment

Do not use keyword blacklists or absolute novelty conclusions. Use `novelty_assessment` with bounded evidence:

- It is allowed to say the current checked scope did not find a highly similar method.
- It is allowed to say evidence is insufficient to support an innovation claim.
- It is allowed to say a related method is highly similar while listing concrete differentiators.
- It is not allowed to make source-free absolute conclusions.

## Validation

Run both validators when delivering innovation-review mode:

```powershell
python skills\3dgs-paper-analyzer\scripts\validate_report.py `
  --md P001.md `
  --json P001.json

python skills\3dgs-paper-analyzer\scripts\validate_innovation_review.py `
  --md P001.md `
  --json P001.json `
  --review-json P001.innovation-review.json `
  --strict
```
