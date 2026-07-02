# Changelog

## Unreleased

- Add shared `Pxxx.source-pack.json` fact layer for `standard-analysis` and
  `innovation-review`, with schema, stub generator, validator, and batch
  integration.
- Refine `standard-analysis` around quick judgment, representative results,
  paper-code differences, MathJax formula blocks, and reproducibility.
- Upgrade `innovation-review` schema to 1.1 with full Claim cards,
  Claim-Evidence matrix, preliminary/deep review depth, prioritized
  improvements, and engineering-ready supplemental experiments.
- Add cross-mode consistency validation, HTML status classes, and unittest
  coverage for Source Pack, mode contracts, related-paper depth, HTML, and
  batch integration.
- Restructure the repository around a three-stage Skill pipeline:
  retrieval and download, single-paper analysis, and batch orchestration.
- Integrate the previous deep reviewer draft into `3dgs-paper-analyzer` as
  `innovation-review` mode instead of maintaining a fourth top-level Skill.
- Add schema-driven innovation-review validation, optional paper index upsert,
  batch profile support, and tests for the new mode.
