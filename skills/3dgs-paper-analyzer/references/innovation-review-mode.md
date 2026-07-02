# Innovation Review Mode

`innovation-review` is a mode of `3dgs-paper-analyzer`, not a separate skill.

Always produce:

```text
<paper_id>.source-pack.json
<paper_id>.md
<paper_id>.json
<paper_id>.innovation-review.json
```

The standard JSON follows `schemas/paper-analysis.schema.json` and points to the shared Source Pack and innovation extension:

```json
{
  "source_pack_path": "P001.source-pack.json",
  "extensions": {
    "source_pack": "P001.source-pack.json",
    "innovation_review": "P001.innovation-review.json"
  }
}
```

The innovation extension follows `schemas/innovation-review.schema.json` schema version `1.1`. Old `1.0` outputs must be migrated explicitly.

## Required Structure

Innovation review must include:

- review card;
- identity and analysis boundary;
- review depth;
- author innovation claims;
- full Claim cards;
- Claim-Evidence matrix;
- key experiment results;
- evidence gaps;
- closest prior work;
- practical differences;
- prioritized method improvements;
- supplemental experiments;
- implementation and reproducibility risks;
- bounded final conclusion;
- full experiment table appendix.

## Claim Contract

Each Claim must include title, author claim, interpreted mechanism, paper location, code location, evidence IDs, counter-evidence IDs, support level, missing evidence, closest prior work, differentiators, and confidence.

## Matrix Contract

The Claim-Evidence matrix columns are theory, main results, ablation, efficiency, failure cases, code, and final judgment. Cells are limited to `直接`, `部分`, `间接`, `无`, or `冲突`.

## Related Paper Depth

Do not silently download related papers. Search local manifests and user-provided files first. If a key paper is missing, write `<paper_id>.related-paper-request.json`.

Set `review_depth` to `preliminary` unless at least one closest paper is `full_read` and at least two important papers are `targeted_read`. Preliminary reviews must not make global absolute novelty conclusions.
