---
name: 3dgs-deep-paper-reviewer
description: Deep Chinese review of one 3DGS compression paper from a PDF. Use when Codex must read a single 3D Gaussian Splatting compression paper in depth, extract innovation claims, preserve original experiment table data, judge whether experiments support the paper's own claims, list similar related papers without novelty-rejection conclusions, propose method improvements and validation experiments, and append reusable tags to paper-index.jsonl.
---

# 3DGS Deep Paper Reviewer

Review one 3DGS compression paper deeply. This skill is not a batch orchestrator and not a novelty-rejection judge. Its first-version goal is to understand the main paper, preserve evidence, extract reusable tags, and propose credible improvements.

Default language is Chinese. Keep paper titles, method names, dataset names, metrics, paths, and code identifiers in English when useful.

## Scope

Use this skill only for single-paper deep review of 3DGS compression papers. Related NeRF, SLAM, reconstruction, transmission, point cloud, image compression, or video compression papers may be recorded only as background or transfer candidates unless they directly support 3DGS compression analysis.

Do not conclude that an innovation is "not novel", "already covered", or "rejected by prior work". If similar papers are found, describe what is similar, how similar it is, and the evidence scope.

If no similar paper is found, write that no highly similar 3DGS compression paper was found within the checked references, baselines, local library, and retrieval scope.

## Inputs

Default input is a PDF path for one selected paper. Also accept a retrieval manifest entry when it points to one PDF.

At the start of the first use, confirm or create the local paper library configuration:

```text
.agent-config/3dgs-deep-paper-reviewer.json
```

If no local library exists, create this default layout after confirming the path:

```text
paper-library/
+-- papers/
+-- metadata/
+-- text/
+-- manifests/
+-- paper-index.jsonl
```

The global index path is the repository root:

```text
paper-index.jsonl
```

Deduplicate index records by `title + arxiv_id + pdf_hash`. Update the existing record instead of appending a duplicate.

## Outputs

Create one folder per paper. The exact output root may follow the current project convention, but each paper must have its own folder.

Required files:

```text
<paper_folder>/<paper_id>.md
<paper_folder>/<paper_id>.review.json
paper-index.jsonl
```

Optional supporting files:

```text
<paper_folder>/related-papers.json
<paper_folder>/table-extraction-notes.md
```

The JSON must follow:

```text
schemas/innovation-review.schema.json
```

Before final delivery, run:

```powershell
python .agents\skills\3dgs-deep-paper-reviewer\scripts\validate_review.py `
  --json <paper_folder>\<paper_id>.review.json `
  --md <paper_folder>\<paper_id>.md `
  --index paper-index.jsonl
```

## Workflow

1. Confirm paper identity: title, authors, arXiv ID or DOI if available, PDF path, version, and whether it is a 3DGS compression paper.
2. Read the full main paper: abstract, introduction, related work, method, experiments, ablations, limitations, conclusion, and appendix if available.
3. Build a paper map: problem, compression target, pipeline, representation, training changes, coding or storage design, renderer changes, and evaluation setup.
4. Extract innovation claims. Each claim must include claim ID, author wording summary, independent interpretation, method location, and evidence anchors.
5. Preserve experiment tables faithfully. Follow `references/table-fidelity.md`.
6. Audit whether experiments support the paper's own claims. Do not audit global novelty.
7. Find similar related papers from references, method discussion, experiment baselines, and local library. Download at most 5 missing strongly related papers only when needed and allowed by the user/environment.
8. Assign related paper read depth using `references/related-paper-depth.md`.
9. Propose improvements and validation experiments. Follow `references/improvement-rubric.md`.
10. Write Markdown, JSON, and index record. Keep key numbers synchronized between Markdown and JSON.
11. Validate outputs with `scripts/validate_review.py`; fix the files, not the validator output.

## Required JSON Shape

The JSON must include these top-level fields:

```json
{
  "schema_version": "1.0",
  "paper": {},
  "index_card": {},
  "innovation_claims": [],
  "experiment_tables": [],
  "experiment_audit": [],
  "improvement_ideas": [],
  "proposed_experiments": [],
  "related_papers": [],
  "validation": {}
}
```

Use stable claim IDs such as `C1`, `C2`, and table IDs such as `T1`, `T2`.

## Markdown Structure

Use this report structure unless the user asks otherwise:

```markdown
# <paper title> 深度精读报告

## 0. 备案卡片
## 1. 论文身份与分析边界
## 2. 一句话总结
## 3. 问题定义与压缩目标
## 4. 方法框架
## 5. 创新点拆解
## 6. 实验表格原始数据保全
## 7. 实验是否支撑创新点
## 8. 相似相关论文
## 9. 方法改进建议
## 10. 建议补充实验
## 11. 复现风险与工程注意事项
## 12. 最终总结
```

## Evidence Rules

Every important claim, table number, metric, comparison, limitation, and improvement motivation must cite evidence such as:

- `[Paper Sec. 3.2]`
- `[Paper Eq. 4]`
- `[Paper Table 1]`
- `[Paper Fig. 3]`
- `[Appendix p. 8]`
- `[Related Paper Table 2]`
- `[Independent judgment]`
- `[Not reported]`
- `[Unverified]`

Never invent PSNR, SSIM, LPIPS, FPS, model size, bitrate, training time, GPU type, scene split, baseline setting, or compression ratio. Use `null`, `not_reported`, or `unverified` in JSON when the paper does not provide the value.

## Related Resources

- `references/table-fidelity.md`
- `references/related-paper-depth.md`
- `references/improvement-rubric.md`
- `scripts/validate_review.py`
