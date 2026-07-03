---
name: 3dgs-paper-analyzer
description: 单篇 3D Gaussian Splatting、Gaussian Splatting、NeRF、神经渲染、三维重建及相关论文中文精读 Skill。用于完整阅读一篇论文及其补充材料，核查项目主页和官方代码，分析表示、渲染、优化、密度控制、压缩机制、实验公平性、效率、局限和可复现性，并同时输出 Markdown 报告和机器可读 JSON。
---

# 3DGS Paper Analyzer

You analyze one paper at a time. Do not batch multiple full papers in one context, do not silently download related papers, and do not create a third report mode.

The goal is evidence-traceable Chinese analysis with machine-readable JSON.

## Modes

There are exactly two modes:

- `standard-analysis`: complete technical understanding, method explanation, code mapping, experiment audit, and reproducibility judgment.
- `innovation-review`: innovation-claim audit, experiment support, related-paper depth, research improvements, and supplemental experiment design.

There is no `auto` mode. `innovation-review` is a mode of this skill, not a separate reviewer skill.

## Shared Source Pack

Every run must generate or reuse:

```text
<paper_id>.source-pack.json
```

The Source Pack is an internal fact layer, not a user report mode. It stores verified facts only:

- paper identity, PDF hash, paper version, code commit;
- evidence ledger with stable IDs such as `E001`;
- equations, figures, and full experiment tables;
- code mapping with stable IDs such as `M1`;
- reported limitations and unverified items;
- provenance and stale state.

If the Source Pack exists and PDF hash, paper version, code commit, and validation still match, reuse it. If any source changed, mark it stale and re-check affected facts. Do not maintain two Source Packs for the same paper.

The two modes may share facts, evidence IDs, tables, code mappings, limitations, and provenance. They must not copy each other's Markdown prose, final conclusions, innovation judgments, or improvement ideas.

## Outputs

`standard-analysis` must write:

```text
<paper_id>.source-pack.json
<paper_id>.md
<paper_id>.json
<paper_id>.html
<paper_id>.validation.json
```

`<paper_id>.json` follows `schemas/paper-analysis.schema.json` and must include `source_pack_path` or `extensions.source_pack`.

`innovation-review` must write:

```text
<paper_id>.source-pack.json
<paper_id>.md
<paper_id>.json
<paper_id>.innovation-review.json
<paper_id>.html
<paper_id>.validation.json
```

following `schemas/innovation-review.schema.json` schema version `1.1`.

HTML is a required delivery artifact, not an optional rendering step. Internal working materials such as full text extraction, table extraction, cloned code, screenshots, and logs must go under:

```text
<output-dir>/_work/
```

`_work/` is not a formal delivery artifact, must not be used for batch aggregation, and must not be counted when checking delivery completeness.

## standard-analysis Contract

Use this structure:

```markdown
# 《论文标题》中文精读报告
## 0. 快速判断
## 1. 论文信息与分析边界
## 2. 一句话核心贡献
## 3. 问题、动机与方法位置
## 4. 方法总体流程
## 5. 技术方法分析
## 6. 论文与代码映射
## 7. 论文与代码差异
## 8. 实验设置与可比性
## 9. 代表性结果
## 10. 效率、存储和部署代价
## 11. 消融、失败案例与敏感条件
## 12. 局限和未证明内容
## 13. 可复现性结论
## 14. 最终总结
## 附录：完整证据与表格索引
```

The quick judgment card must include method type, compression target, core contribution, strongest evidence, largest quality risk, largest engineering cost, paper/code consistency, reproduction difficulty, whether it is worth reproducing, and survey value.

The main body is not a raw data archive. Show only representative results: one quality table, one efficiency/cost table, one ablation table, and no more than roughly ten key numeric observations. Full raw tables belong in Source Pack and appendix.

List paper/code differences in a dedicated table with severity `minor`, `moderate`, `major`, or `unclear`.

Core equations must use MathJax block syntax:

```tex
\[
H = J_R^\top J_R
\]
```

## innovation-review Contract

Use this structure:

```markdown
# 《论文标题》创新评审报告
## 0. 评审卡片
## 1. 论文身份与分析边界
## 2. 创新评审深度
## 3. 问题定义与方法定位
## 4. 作者创新主张总览
## 5. 创新主张逐项审计
## 6. Claim—Evidence 矩阵
## 7. 关键实验结果
## 8. 实验支撑缺口
## 9. 最近前作与相似论文
## 10. 与最近前作的实际差异
## 11. 方法改进优先级
## 12. 建议补充实验
## 13. 复现和实现风险
## 14. 创新性结论边界
## 15. 最终评审结论
## 附录：完整实验表格
```

Each Claim must use a fixed card with author claim, interpreted mechanism, paper location, code location, direct evidence, counter/conflict evidence, support level, missing evidence, closest prior work, differentiators, and confidence.

The Claim-Evidence matrix must cover all Claims. Matrix cells are limited to `直接`, `部分`, `间接`, `无`, or `冲突`.

Set `review_depth` to `preliminary` unless the closest related paper has `full_read` and at least two important papers have `targeted_read`. If the deep threshold is not met, list missing related papers and do not make global absolute novelty conclusions.

Improvement ideas must include value, implementation cost, failure risk, required resources, minimum validation, priority (`P0`, `P1`, `P2`), and evidence IDs.

Supplemental experiments must include goal, hypothesis, independent variables, baselines, datasets, metrics, implementation steps, expected result, failure interpretation, estimated cost, and priority.

## Validation

Finalize every report before delivery:

1. Generate or reuse Source Pack, Markdown, and JSON.
2. Run the relevant validators.
3. Save `<paper_id>.validation.json`.
4. Only if validation has no FAIL, generate `<paper_id>.html`.
5. Check HTML exists, is non-empty, contains HTML markup, includes the report title and table of contents, and wraps tables in `table-scroll`.
6. Only then report `COMPLETE` or `COMPLETE_WITH_WARNINGS`.

Use the unified finalization script:

```powershell
python skills\3dgs-paper-analyzer\scripts\finalize_report.py --mode standard-analysis --paper-id P001 --output-dir analysis-output\P001
python skills\3dgs-paper-analyzer\scripts\finalize_report.py --mode innovation-review --paper-id P001 --output-dir analysis-output\P001 --strict
```

Completion states:

- `COMPLETE`: all required files exist, Source Pack PASS, report validator PASS, innovation strict validator PASS when applicable, HTML generated and non-empty.
- `COMPLETE_WITH_WARNINGS`: no FAIL, at least one WARN, HTML generated and non-empty; the final response must list warnings.
- `INCOMPLETE`: any FAIL, missing JSON/Markdown/Source Pack, missing or empty HTML, missing validation JSON, or failed innovation strict validation.

Do not report a task as complete while any validator still FAILs or HTML is missing.

The underlying validators are:

```powershell
python skills\3dgs-paper-analyzer\scripts\validate_source_pack.py --source-pack P001.source-pack.json
python skills\3dgs-paper-analyzer\scripts\validate_report.py --md P001.md --json P001.json
python skills\3dgs-paper-analyzer\scripts\validate_innovation_review.py --md P001.md --json P001.json --review-json P001.innovation-review.json --strict
python skills\3dgs-paper-analyzer\scripts\validate_cross_mode_consistency.py --source-pack P001.source-pack.json --standard-json standard-analysis\P001.json --innovation-json innovation-review\P001.json --review-json innovation-review\P001.innovation-review.json --output cross-mode-validation.json
```

## References

- `references/evidence-policy.md`
- `references/result-reporting.md`
- `references/output-profiles.md`
- `references/innovation-review-mode.md`
- `references/innovation-review/table-fidelity.md`
- `references/innovation-review/related-paper-depth.md`
- `references/innovation-review/improvement-rubric.md`
- `templates/standard-analysis-template.md`
- `templates/innovation-review-template.md`
