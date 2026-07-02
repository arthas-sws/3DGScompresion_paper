# Related Paper Depth

Related papers support interpretation and improvement ideas. They do not replace the main paper review.

## Read Depth

- `full_read`: abstract, introduction, method, experiments, ablations, limitations, and key tables.
- `targeted_read`: abstract, relevant method subsection, relevant experiment table or ablation, and needed setup details.
- `metadata_only`: title, year, link, why it was mentioned, and relation type only.

## Review Depth Gate

Set the whole review to `preliminary` unless the related-paper evidence meets deep-review requirements. Deep review requires at least one closest related paper with `full_read` and at least two important related papers with `targeted_read`.

If the gate is not met, list missing related papers and avoid global novelty conclusions.

## Retrieval Boundary

Search existing manifests and local retrieval outputs first. If a key PDF is absent, generate `<paper_id>.related-paper-request.json` with title, reason, required depth, and target claims. Do not download silently.
