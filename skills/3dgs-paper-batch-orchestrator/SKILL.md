---
name: 3dgs-paper-batch-orchestrator
description: 批量调度 3DGS、Gaussian Splatting、NeRF 和神经渲染论文分析任务。用于读取 retrieval manifest，逐篇隔离调用 3dgs-paper-analyzer，生成任务包、维护 status.json、保存独立 Markdown/JSON 报告、执行质量检查、重试失败项，并只基于 validated 项生成批次总结、方法矩阵、结果矩阵和失败清单。
---

# 3DGS Paper Batch Orchestrator

你是批量调度层，不是单篇论文分析者。你必须逐篇隔离任务，调用 `3dgs-paper-analyzer`，不得把多篇 PDF 全文放入同一上下文，也不得自行简化替代单篇分析。

## 1. 输入

优先读取 retrieval downloader 生成的：

```text
paper-retrieval-output/<batch_id>/manifest.json
```

也可读取同结构 manifest。不得要求用户重复手工整理相同论文信息。

## 2. 输出

```text
paper-batch-output/<batch_id>/
├── manifest.json
├── status.json
├── items/
│   ├── P001.md
│   ├── P001.json
│   └── ...
├── attempts/
├── validation/
├── retry-prompts/
├── batch-summary.md
├── comparison-matrix.md
├── result-matrix.json
└── failed-items.md
```

`status.json` 遵循仓库根目录 `schemas/batch-status.schema.json`。

## 3. 状态机

支持状态：

```text
pending
source_ready
waiting_for_agent
analyzing
generated
validating
retrying
validated
failed_source
failed_analysis
failed_quality_gate
```

规则：

- `validated` 才能进入汇总；
- `failed_*` 必须进入 `failed-items.md`；
- 重试不得覆盖旧 attempt；
- 中断恢复时跳过 `validated`，继续 `waiting_for_agent`、`generated`、`retrying`。

## 4. 依赖定位

定位 `3dgs-paper-analyzer/SKILL.md` 时按顺序尝试：

1. 当前仓库 `skills/3dgs-paper-analyzer/SKILL.md`；
2. 当前项目 `.ai/skills/3dgs-paper-analyzer/SKILL.md`；
3. `$CODEX_HOME/skills/3dgs-paper-analyzer/SKILL.md`；
4. Windows 用户全局 `.codex/skills/3dgs-paper-analyzer/SKILL.md`；
5. Linux/macOS 用户全局 `.codex/skills/3dgs-paper-analyzer/SKILL.md`。

脚本必须使用 `Path(__file__).resolve()` 推导自身位置，不写死用户路径。

## 5. 执行流程

1. `init_batch.py` 读取 retrieval manifest，创建输出目录、重写 PDF 相对路径、初始化 `status.json`；
2. `build_task.py` 为每篇论文生成独立任务 prompt；
3. `run_batch.py` 顺序检查每篇论文：
   - PDF 存在则 `source_ready`；
   - 已有 `items/Pxxx.md` 和 `items/Pxxx.json` 则校验；
   - 未有报告则生成 attempt prompt，标记 `waiting_for_agent`；
   - 通过质量门槛则标记 `validated`；
   - 失败则标记 `failed_quality_gate` 或 `failed_source`；
4. `retry_failed.py` 为失败项生成针对性 retry prompt，不覆盖历史 attempt；
5. `aggregate_reports.py` 只读取 `validated` 项生成 summary、comparison matrix 和 result matrix；
6. `validate_batch.py` 检查汇总一致性。

若当前 Python 环境不能直接调用 Codex 子任务，不要伪装自动分析。输出任务包并将状态标记为 `waiting_for_agent`，由 Codex 主流程逐篇执行。

## 6. 单篇任务包要求

每个任务必须包含：

- paper ID、标题、作者、arXiv ID、PDF 路径、source URL、code URL；
- 输出路径 `items/Pxxx.md` 和 `items/Pxxx.json`；
- 必须重新读取 `3dgs-paper-analyzer`；
- 只分析当前论文；
- 中文输出；
- JSON 与 Markdown 同步；
- 关键数字、证据和可比性标签；
- 失败时写明原因。

## 7. 质量门槛

单篇校验至少检查：

- Markdown 与 JSON 是否都存在；
- 论文 ID 与 manifest 一致；
- 标题与 manifest 一致；
- JSON 必填字段完整；
- Markdown 中主要指标数字能在 JSON 中找到；
- 每条主要结果有证据；
- PSNR、SSIM、LPIPS、FPS、模型大小等数字不能无证据；
- 不混入其他论文 ID；
- 存在结果、代价、局限和可复现性结论；
- 中文比例合理，无大段英文正文。

## 8. 汇总规则

汇总只能读取：

- `manifest.json`；
- `status.json` 中 `validated` 的条目；
- `items/Pxxx.json` 的结构化结果；
- 必要时读取对应 `items/Pxxx.md` 作为文字解释。

禁止：

- 从 failed 项猜测结果；
- 修改单篇 JSON 中的数值；
- 在不可比条件下统一排名；
- 把不同数据集、分辨率、模型大小口径混成单表结论；
- 将失败报告纳入 result matrix。

## 9. 常用命令

初始化：

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\init_batch.py `
  --manifest paper-retrieval-output\compression-survey-01\manifest.json `
  --output-dir paper-batch-output\compression-survey-01
```

生成/恢复批次任务：

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\run_batch.py `
  --batch-dir paper-batch-output\compression-survey-01
```

校验单项：

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\validate_item.py `
  --batch-dir paper-batch-output\compression-survey-01 `
  --paper-id P001
```

汇总：

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\aggregate_reports.py `
  --batch-dir paper-batch-output\compression-survey-01
```

## 10. 禁止事项

- 禁止将所有 PDF 拼入一个上下文；
- 禁止不调用单篇 Skill 而自行简化分析；
- 禁止让后一篇报告继承前一篇正文；
- 禁止覆盖旧 attempt；
- 禁止未校验就汇总；
- 禁止把失败项纳入结果矩阵；
- 禁止在没有结构化 JSON 时猜测比较数字。

## 11. 相关资源

- `references/batch-protocol.md`
- `references/quality-gate.md`
- `references/aggregation-schema.md`
- `templates/item-task-prompt.md`
- `templates/batch-summary-template.md`

## Profile Extension

Batch supports two profiles:

- `standard-analysis`: default. Each item asks `3dgs-paper-analyzer` for `Pxxx.md` and standard `Pxxx.json`.
- `innovation-review`: each item still requires `Pxxx.md` and standard `Pxxx.json`, and additionally asks for `Pxxx.innovation-review.json`.

`status.json` must record the selected `profile`. Aggregation continues to read only standard `Pxxx.json`; innovation-review JSON is additional evidence and must not replace the standard JSON.

Example:

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\init_batch.py `
  --manifest paper-retrieval-output\compression-survey-01\manifest.json `
  --output-dir paper-batch-output\compression-survey-01 `
  --profile innovation-review
```
- `scripts/init_batch.py`
- `scripts/build_task.py`
- `scripts/run_batch.py`
- `scripts/update_status.py`
- `scripts/retry_failed.py`
- `scripts/aggregate_reports.py`
- `scripts/validate_item.py`
- `scripts/validate_batch.py`
