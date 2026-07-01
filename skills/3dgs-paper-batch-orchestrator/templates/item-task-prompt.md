请使用 `3dgs-paper-analyzer` 对以下单篇论文做中文精读。

## 任务边界

- 只分析当前论文，不读取其他论文全文。
- 必须输出 Markdown 和 JSON。
- 不得编造论文未报告的实验数字。
- 所有关键数字必须带证据和可比性标签。

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

## 必须完成

1. 重新读取 `3dgs-paper-analyzer/SKILL.md` 和必要 references。
2. 阅读论文、补充材料和官方代码可得部分。
3. 分析 3DGS 表示、渲染、优化、密度控制、实验、效率、局限和可复现性。
4. JSON 遵循 `schemas/paper-analysis.schema.json`。
5. 完成后运行 `validate_report.py` 或等待 batch 质量门槛校验。
