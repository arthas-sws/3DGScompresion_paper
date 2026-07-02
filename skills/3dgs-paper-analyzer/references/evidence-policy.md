# Evidence Policy

## Evidence Types

Separate four kinds of statements:

- author claim: what the paper, project page, or README claims;
- direct evidence: equations, figures, tables, appendix, or official code;
- independent judgment: analysis derived from evidence;
- uncertainty: missing, conflicting, or unverifiable information.

Do not turn author claims into verified facts.

## Source Pack Evidence Ledger

Every reusable fact should be recorded once in `<paper_id>.source-pack.json` with a stable ID such as `E001`.

Evidence IDs, table IDs, and code mapping IDs must be unique. Markdown and mode-specific JSON may cite these IDs but must not create a second conflicting transcription of the same table, code commit, paper version, or metric value.

If a fact is not verified, keep it in `unverified_items` or mark its `verification_status` as `partial` or `unverified`.

## Required Evidence

Evidence is required for:

- core method mechanisms;
- PSNR, SSIM, LPIPS, FPS, MB, GB, training time, rendering time, and similar numbers;
- code mapping;
- baseline comparability;
- limitations, failure cases, and reproducibility risks.
