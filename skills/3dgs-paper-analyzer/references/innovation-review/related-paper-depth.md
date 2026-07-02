# Related Paper Depth

Related papers support interpretation and improvement ideas. They do not replace the main paper review.

## Relation Types

- `baseline_in_experiments`: a method compared in the main paper experiments.
- `similar_innovation`: a paper with a similar compression idea, representation, coding method, training strategy, or evaluation goal.
- `transfer_candidate`: a paper outside 3DGS compression whose idea may transfer into 3DGS compression.

## Read Depth

### full_read

Use for closest related papers or central baselines. Read abstract, introduction, method, experiments, ablations, limitations, and key tables.

### targeted_read

Use for a paper that answers one specific question. Read abstract, relevant method subsection, relevant experiment table or ablation, and needed setup details.

Examples:

- Check whether a quantization mechanism resembles the main paper's module.
- Check whether a baseline includes decoder size in reported model size.
- Check whether a rate-distortion setting is comparable.
- Check whether a NeRF or transmission idea could transfer into 3DGS compression.

### metadata_only

Use for weakly related papers. Record title, year, link, why it was mentioned, and relation type. Do not use metadata-only papers as core evidence for strong technical judgments.

## Retrieval Boundary

Search existing manifests and local retrieval outputs first. If a key PDF is absent, generate a retrieval request for `paper-retrieval-downloader` instead of downloading silently.
