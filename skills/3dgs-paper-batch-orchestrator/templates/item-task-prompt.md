请使用 `3dgs-paper-analyzer` 对以下单篇论文做中文分析。

## Profile

- Profile: `{{PROFILE}}`
- Profile instructions: {{PROFILE_INSTRUCTIONS}}

## 任务边界

- 只分析当前论文。
- 必须先生成或复用共享 Source Pack，再输出模式报告。
- 标准 Markdown 和标准 JSON 始终必需。
- 标准 JSON 必须遵循 `schemas/paper-analysis.schema.json`。
- Source Pack 必须遵循 `schemas/paper-source-pack.schema.json`。
- 不得编造论文未报告的实验数字。
- 所有关键信息必须带证据和可比性标记。
- 如果 profile 是 `innovation-review`，还必须输出 `{{OUTPUT_REVIEW_JSON}}`。
- 不得静默下载相关论文；缺少关键相关论文时写 retrieval request JSON。

## 论文信息

- Paper ID: {{PAPER_ID}}
- Title: {{TITLE}}
- Authors: {{AUTHORS}}
- arXiv ID: {{ARXIV_ID}}
- Source URL: {{SOURCE_URL}}
- PDF Path: {{PDF_PATH}}
- Code URL: {{CODE_URL}}

## 输出路径

- Source Pack: {{OUTPUT_SOURCE_PACK}}
- Markdown: {{OUTPUT_MD}}
- JSON: {{OUTPUT_JSON}}
- Innovation review JSON: {{OUTPUT_REVIEW_JSON}}

## 必须完成

1. 重新读取 `3dgs-paper-analyzer/SKILL.md` 和必要 references。
2. 如果 `{{OUTPUT_SOURCE_PACK}}` 已存在且 PDF hash、paper version、code commit 与当前来源一致，复用它；否则重新核查受影响事实。
3. Source Pack 保存 evidence ledger、公式、表格、代码映射、局限和未核实项，不保存长篇模式结论。
4. standard-analysis 主正文只展示代表性结果，完整原始表格放入 Source Pack 和附录。
5. innovation-review 必须使用完整 Claim 卡片、Claim-Evidence 矩阵、review_depth、改进优先级和工程化补充实验。
6. 标准 JSON 设置 `source_pack_path` 或 `extensions.source_pack` 指向 `{{OUTPUT_SOURCE_PACK}}`。
7. innovation-review profile 额外遵循 `schemas/innovation-review.schema.json`。
8. 完成后运行对应 validator，或等待 batch 质量门槛校验。
