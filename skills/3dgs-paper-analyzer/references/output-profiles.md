# Output Profiles

The analyzer supports exactly two report modes: `standard-analysis` and `innovation-review`.

## Shared Source Pack

Both modes share `<paper_id>.source-pack.json`. The Source Pack is an internal fact layer, not an `auto` mode and not a third report profile. It contains verified facts only: paper identity, PDF hash, paper version, code commit, evidence ledger, equations, figures, experiment tables, code map, reported limitations, unverified items, and provenance.

Do not store mode-specific prose, final conclusions, innovation judgments, or improvement plans in the Source Pack.

Reuse the Source Pack when PDF hash, paper version, code commit, and validation match. If any source changes, mark it stale and re-check affected facts.

## standard-analysis

Use for full technical understanding, method explanation, code mapping, experiment audit, and reproducibility judgment.

Main-body result reporting is intentionally selective:

- at most one representative quality table;
- at most one efficiency/cost table;
- at most one ablation table;
- roughly ten key numeric observations;
- complete raw tables belong in Source Pack and appendix.

Required standard sections include quick judgment, paper/code mapping, paper/code differences, experiment comparability, representative results, cost, limitations, and reproducibility.

## innovation-review

Use for innovation-claim audit, evidence sufficiency, prior work, risk, improvement ideas, and supplemental experiments.

It must not read like a normal paper summary. It must include:

- `review_depth`: `preliminary` or `deep`;
- full Claim cards;
- Claim-Evidence matrix;
- related-paper depth boundary;
- prioritized improvement ideas (`P0`, `P1`, `P2`);
- engineering-ready supplemental experiment designs;
- complete raw tables in appendix, not as the main body.
