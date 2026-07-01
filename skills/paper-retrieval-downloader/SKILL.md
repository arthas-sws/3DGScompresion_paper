---
name: paper-retrieval-downloader
description: 检索、去重、下载和整理 3D Gaussian Splatting、Gaussian Splatting、NeRF 及相关论文。用于根据关键词、时间范围、arXiv ID、URL 或论文清单获取元信息和 PDF，生成标准 manifest.json、failures.json、metadata 和 papers.md，作为单篇或批量论文分析 Skill 的输入。
---

# Paper Retrieval Downloader

本 Skill 只负责论文获取层：检索、去重、下载、元信息整理、失败记录和清单生成。它不分析论文技术内容，不维护大型论文库 README，不做会议归档，不生成摘要页或 Changelog。

## 职责边界

负责：

- 根据关键词、arXiv ID、URL 或清单检索论文；
- 解析 arXiv 元信息、PDF URL、版本号和作者信息；
- 识别重复论文，arXiv 不同版本视为同一论文；
- 下载 PDF，默认不覆盖已有文件；
- 为每篇论文生成稳定 ID，例如 `P001`；
- 生成 `manifest.json`、`failures.json`、`metadata/*.json` 和 `papers.md`；
- 显式记录下载、元信息和失败状态。

不负责：

- 单篇精读、方法优劣判断、实验审计或长篇报告；
- 批量调度分析任务；
- 修改 README、abs、archive、年份会议目录、计数索引或 Changelog；
- 自动提交、push 或删除用户已有 PDF。

## 标准输出

默认输出目录：

```text
paper-retrieval-output/<batch_id>/
├── manifest.json
├── failures.json
├── papers/
│   ├── P001.pdf
│   └── P002.pdf
├── metadata/
│   ├── P001.json
│   └── P002.json
└── papers.md
```

`manifest.json` 遵循仓库根目录 `schemas/retrieval-manifest.schema.json`。`failures.json` 遵循 `schemas/failures.schema.json`。

## 工作流

1. 建立候选论文：

```powershell
python skills\paper-retrieval-downloader\scripts\fetch.py `
  --batch-id compression-survey-01 `
  --keyword "3D Gaussian Splatting compression" `
  --keyword "Gaussian Splatting pruning" `
  --max-results 20 `
  --output tmp\compression-candidates.json
```

2. 可选去重或差集：

```powershell
python skills\paper-retrieval-downloader\scripts\deduplicate.py `
  --input tmp\compression-candidates.json `
  --output tmp\compression-deduped.json

python skills\paper-retrieval-downloader\scripts\diff.py `
  --input tmp\compression-deduped.json `
  --against paper-retrieval-output\old-batch\manifest.json `
  --output tmp\compression-new.json
```

3. 下载 PDF 并生成标准 manifest：

```powershell
python skills\paper-retrieval-downloader\scripts\download.py `
  --input tmp\compression-new.json `
  --batch-id compression-survey-01 `
  --output-dir paper-retrieval-output\compression-survey-01
```

4. 校验结果：

```powershell
python skills\paper-retrieval-downloader\scripts\validate_manifest.py `
  paper-retrieval-output\compression-survey-01\manifest.json
```

Linux/macOS 命令等价：

```bash
python skills/paper-retrieval-downloader/scripts/download.py \
  --input tmp/compression-new.json \
  --batch-id compression-survey-01 \
  --output-dir paper-retrieval-output/compression-survey-01
```

如使用 `uv`，将 `python` 替换为 `uv run python`。

## 输入方式

支持：

- `--keyword`：arXiv 关键词检索；
- `--arxiv-id`：单个或多个 arXiv ID，可包含版本号；
- `--input-list`：文本清单，每行一个 arXiv ID、arXiv URL、PDF URL 或标题；
- `--input`：读取上一阶段 JSON，例如 candidates、deduped 或 manifest。

清单示例：

```text
2403.17888
https://arxiv.org/abs/2406.04329v2
https://arxiv.org/pdf/2501.01234
Unpublished Local Paper Title
```

## 去重规则

按以下优先级生成 canonical key：

1. arXiv base ID，去掉 `v1/v2/...`；
2. DOI；
3. 规范化标题。

重复项只保留一条。保留项会记录：

```json
"deduplication": {
  "canonical_key": "arxiv:2403.17888",
  "duplicates": ["https://arxiv.org/abs/2403.17888v2"],
  "reason": "same_arxiv_base_id"
}
```

## 安全规则

- 默认不覆盖 `papers/Pxxx.pdf`，除非显式传入 `--overwrite`；
- 所有网络请求必须设置超时和有限重试；
- arXiv 请求默认有短暂间隔，批量任务不要高频请求；
- 下载失败必须写入 `failures.json`，不得静默跳过；
- 只写入用户指定输出目录；
- 不自动删除用户已有论文文件；
- 不读写用户全局 Codex Skill 目录；
- 不提交 API Key、Cookie、Token 或代理密码。

## 交给后续 Skill

批量分析直接消费：

```text
paper-retrieval-output/<batch_id>/manifest.json
```

单篇分析可读取 manifest 中的某个 paper 条目及其 `local_pdf`。

## 相关脚本

- `scripts/fetch.py`：arXiv 检索和清单解析；
- `scripts/metadata.py`：根据 arXiv ID 补全元信息；
- `scripts/deduplicate.py`：候选清单去重；
- `scripts/diff.py`：与已有 manifest/candidates 做差集；
- `scripts/download.py`：下载 PDF 并生成标准输出目录；
- `scripts/validate_manifest.py`：检查 manifest、PDF、metadata 和 failures。
