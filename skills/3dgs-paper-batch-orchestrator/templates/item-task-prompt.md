请使用 `3dgs-paper-analyzer` 对以下单篇论文做中文分析。

## Profile

- Profile: `{{PROFILE}}`
- Profile instructions: {{PROFILE_INSTRUCTIONS}}

## 任务边界

- 只分析当前论文。
- 必须输出标准 Markdown 和标准 JSON。
- 标准 JSON 必须遵循 `schemas/paper-analysis.schema.json`。
- 不得编造论文未报告的实验数字。
- 所有关键数字必须带证据和可比性标签。
- 如果 profile 是 `innovation-review`，还必须输出 `{{OUTPUT_REVIEW_JSON}}`。

## 论文信息

- Paper ID: {{PAPER_ID}}
- Title: {{TITLE}}
- Authors: {{AUTHORS}}
- arXiv ID: {{ARXIV_ID}}
- Source URL: {{SOURCE_URL}}
- PDF Path: {{PDF_PATH}}
- Code URL: {{CODE_URL}}

## 输出路径

- Markdown: {{OUTPUT_MD}}
- JSON: {{OUTPUT_JSON}}
- Innovation review JSON: {{OUTPUT_REVIEW_JSON}}

## 必须完成

1. 重新读取 `3dgs-paper-analyzer/SKILL.md` 和必要 references。
2. 阅读论文、补充材料和官方代码可得部分。
3. 分析 3DGS 表示、渲染、优化、密度控制、实验、效率、局限和可复现性。
4. 标准 JSON 遵循 `schemas/paper-analysis.schema.json`。
5. innovation-review profile 额外遵循 `schemas/innovation-review.schema.json`。
6. 完成后运行对应 validator，或等待 batch 质量门槛校验。
