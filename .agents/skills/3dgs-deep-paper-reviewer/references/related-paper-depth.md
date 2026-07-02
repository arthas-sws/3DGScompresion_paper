# Related Paper Depth

Related papers support interpretation and improvement ideas. They do not support first-version novelty rejection conclusions.

## Relation Types

- `baseline_in_experiments`: a method compared in the main paper experiments.
- `similar_innovation`: a paper with a similar compression idea, representation, coding method, training strategy, or evaluation goal.
- `transfer_candidate`: a paper outside 3DGS compression whose idea may transfer into 3DGS compression.

## Read Depth

### full_read

Use for the closest related papers or central baselines. Read abstract, introduction, method, experiments, ablations, limitations, and key tables.

Use this depth when the paper strongly affects how to understand a main-paper innovation or improvement opportunity.

### targeted_read

Use for a paper that answers one specific question. Read only the abstract, the relevant method subsection, the relevant experiment table or ablation, and any needed setup details.

Examples:

- Check whether a quantization mechanism resembles the main paper's module.
- Check whether a baseline includes decoder size in reported model size.
- Check whether a rate-distortion setting is comparable.
- Check whether a NeRF or transmission idea could transfer into 3DGS compression.

### metadata_only

Use for weakly related papers. Record title, year, link, why it was mentioned, and relation type. Do not use metadata-only papers as core evidence for or against an innovation claim.

## Retrieval Limits

Start from the main paper's references, method discussion, and experiment baselines. Search the local library before network retrieval. Download at most 5 missing strongly related papers for one main review unless the user explicitly expands the limit.
