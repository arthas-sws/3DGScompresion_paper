# Table Fidelity

Preserve experiment tables as evidence. Do not rewrite table data into approximate prose.

Full raw tables are extracted once into `<paper_id>.source-pack.json`. The innovation extension may mirror complete tables for evidence, but the Markdown main body should only show claim-relevant rows, core comparisons, key ablations, and failure points.

Put complete tables in `## 附录：完整实验表格`, preferably folded in HTML.

Rules:

- keep original metric names, units, dataset names, scene names, bitrate points, method names, and captions;
- do not normalize units, average rows, merge bitrate points, fill missing cells, or recompute values unless explicitly reported;
- mark unclear cells in `uncertain_cells`;
- record extraction method and verification status.
