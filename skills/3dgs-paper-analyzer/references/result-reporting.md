# Result Reporting

## Source Pack First

Extract full experiment tables once into Source Pack. Standard reports quote representative rows only. Innovation reports show claim-relevant rows in the main body and reserve complete raw tables for the appendix and JSON evidence.

`analysis.main_results` in standard JSON should hold representative results, not every raw cell. Full rows belong to `source_pack.experiment_tables`.

## Standard Main Body

The standard Markdown main body should include:

- one representative quality result table;
- one efficiency/cost table;
- one ablation table;
- no more than about ten key numeric observations.

## Innovation Main Body

The innovation Markdown main body should include:

- rows directly tied to Claims;
- core comparisons;
- key ablations;
- failure points;
- a folded or appendix section for complete raw tables.

Do not recompute numbers unless the paper explicitly reports the derived value.
