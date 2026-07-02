# Improvement Rubric

Improvement ideas must be concrete, tied to innovation claims, and testable.

## Categories

- `experiment_only_fix`: improve validation without changing the method.
- `low_risk_extension`: small method or implementation extension likely compatible with the paper.
- `medium_risk_method_change`: meaningful method change requiring new experiments.
- `high_risk_research_direction`: speculative research direction with clear risk.

## Required Fields

Each improvement idea must include:

- `idea`
- `category`
- `targets_claim`
- `motivation`
- `expected_benefit`
- `risk`
- `experiment_to_validate`
- `evidence_basis`

## Proposed Experiments

Each proposed experiment must bind to a claim and include:

- `claim_id`
- `missing_or_weak_evidence`
- `proposed_experiment`
- `control_baselines`
- `datasets`
- `metrics`
- `expected_observation`
- `failure_interpretation`

Avoid generic suggestions like "add more ablations" unless the missing module, baseline, metric, or dataset is named.
