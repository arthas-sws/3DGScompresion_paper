# Changelog

## Unreleased

- Restructure the repository around a three-stage Skill pipeline:
  retrieval and download, single-paper analysis, and batch orchestration.
- Integrate the previous deep reviewer draft into `3dgs-paper-analyzer` as
  `innovation-review` mode instead of maintaining a fourth top-level Skill.
- Add schema-driven innovation-review validation, optional paper index upsert,
  batch profile support, and tests for the new mode.
