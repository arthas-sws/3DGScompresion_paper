---
name: 3dgs-paper-batch-orchestrator
description: 批量调度 3DGS、NeRF、神经渲染和三维视觉论文分析任务。逐篇隔离调用 3dgs-paper-analyzer，强制中文输出，执行结果完整性与语言质量检查，对失败项自动纠正重试，并在全部单篇报告通过后生成中文批次总览、方法对比和失败清单。适用于批量精读、批量审稿、批量复现调研、综述整理和文献矩阵构建。
---

# 3DGS 论文批量调度器

你是论文批处理任务的调度器，不直接替代单篇分析 Skill。

你的职责是：

1. 建立论文清单和稳定编号；
2. 为每篇论文创建隔离任务；
3. 每次重新加载 `3dgs-paper-analyzer`；
4. 强制每篇报告使用中文；
5. 检查结果汇报、证据、局限和最终总结是否完整；
6. 对失败报告进行针对性重试；
7. 保存单篇报告，不在批处理过程中覆盖；
8. 只基于通过质量检查的单篇报告生成批次汇总；
9. 明确列出失败、缺失和不可比较项目。

## 一、为什么必须使用调度层

批量分析时常见的质量下降原因包括：

- 一次把多篇论文全文放入同一上下文，后半批被压缩；
- 英文论文持续进入上下文，输出语言逐渐漂移为英文；
- 只在批次开始读取一次单篇 Skill，后续任务偏离框架；
- 多篇论文的术语、指标和数字相互污染；
- 未完成单篇证据核查就提前生成总表；
- 没有逐篇质量门禁，缺失结果章节的报告直接进入汇总；
- 多个并行任务共享上下文；
- 为了完成数量，后半批报告明显缩短。

本 Skill 使用“单篇隔离—质量门禁—针对性重试—二次汇总”解决这些问题。

## 二、依赖

必须能够访问：

```text
3dgs-paper-analyzer/SKILL.md
```

按以下顺序寻找：

1. 当前项目 `.ai/skills/3dgs-paper-analyzer/SKILL.md`；
2. 当前项目 `.codex/skills/3dgs-paper-analyzer/SKILL.md`；
3. `$CODEX_HOME/skills/3dgs-paper-analyzer/SKILL.md`；
4. Windows：`C:\Users\<用户名>\.codex\skills\3dgs-paper-analyzer\SKILL.md`；
5. Linux：`~/.codex/skills/3dgs-paper-analyzer/SKILL.md`。

找不到时停止正式批处理并报告缺少依赖。不要用调度 Skill 自行简化代替单篇分析 Skill。

## 三、默认规则

### 3.1 中文规则

除非用户明确要求英文：

- 所有单篇报告必须使用中文；
- 批次状态、日志、失败原因和批次总览必须使用中文；
- 论文标题、方法名、数据集名、代码路径可保留英文；
- 英文摘要不能直接复制成报告正文；
- 不能把中文章节改成 `Summary`、`Method`、`Results`；
- 允许英文术语和代码，但解释必须使用中文。

### 3.2 单篇隔离规则

一篇论文对应一个独立任务单元。每个任务只能读取：

- 当前论文及补充材料；
- 当前论文的项目主页和代码；
- `3dgs-paper-analyzer` 的规则；
- 当前任务配置；
- 必要的公共分类说明。

不能把其他论文的全文、未核实数字、报告全文或工作笔记放入当前任务上下文。

### 3.3 并发规则

默认：

```yaml
parallel_workers: 1
```

只有环境支持真正隔离的 worker/subtask 时才允许设为 2，最多不超过 3。多个任务共享同一上下文时不属于隔离并发，必须顺序执行。

### 3.4 批次大小

建议：

| 模式 | 每个子批次 |
|---|---:|
| 深度精读 | 3—8 篇 |
| 审稿 | 3—6 篇 |
| 复现调研 | 2—5 篇 |
| 精炼速读 | 5—15 篇 |
| 元信息整理 | 10—30 篇 |

超过建议规模时拆成 `part-01`、`part-02`，各子批次完成后再做父批次汇总。

### 3.5 不降低单篇标准

批量任务不得：

- 删除结果总表、效率存储分析、消融、局限、代码状态或最终总结；
- 用摘要替代全文；
- 用“其余类似”省略论文；
- 为赶进度缩短后半批；
- 为了表格完整而填写论文未报告的数据。

## 四、输入格式

优先接受 JSON：

```json
{
  "batch_id": "compression-survey-01",
  "mode": "中文精读",
  "parallel_workers": 1,
  "max_retries": 2,
  "output_dir": "paper-batch-output/compression-survey-01",
  "papers": [
    {
      "id": "P001",
      "title": "LightGaussian",
      "source": "https://arxiv.org/abs/...",
      "code": "https://github.com/...",
      "notes": "重点关注 pruning 和蒸馏"
    }
  ]
}
```

也可接受 CSV、Markdown 表格、URL 列表、PDF 文件夹或论文标题列表。非 JSON 输入先标准化，保证每篇论文有唯一 `id`。

## 五、输出目录

```text
paper-batch-output/<batch_id>/
├── manifest.json
├── status.json
├── items/
│   ├── P001.attempt-1.md
│   ├── P001.md
│   └── ...
├── validation/
│   ├── P001.json
│   └── ...
├── retry-prompts/
├── batch-index.md
├── batch-summary.md
├── comparison-matrix.md
└── failed-items.md
```

规则：

- 单篇报告是一级成果；
- 重试不能覆盖旧版本；
- `items/P001.md` 只代表通过质量门禁的最终版本；
- 失败论文必须保留原因。

## 六、执行流程

### 阶段 0：预检

1. 定位并读取 `3dgs-paper-analyzer/SKILL.md`；
2. 读取其 `3dgs-analysis-schema.md`、`evidence-policy.md`、`result-reporting.md`、`output-profiles.md`；
3. 检查论文数量、身份和输出目录；
4. 建立 `manifest.json` 与 `status.json`；
5. 论文过多时拆分子批次。

### 阶段 1：建立单篇任务包

每篇任务必须包含：

```text
任务 ID：
论文标题：
论文来源：
代码来源：
分析模式：
用户特别关注：
输出语言：中文
输出路径：
质量门禁：启用
```

使用 `templates/item-task-prompt.md`。

### 阶段 2：隔离分析

对每篇论文：

1. 重新读取 `3dgs-paper-analyzer/SKILL.md`；
2. 重新读取必要参考文件；
3. 只加载当前论文；
4. 按指定模式完成分析；
5. 输出独立 Markdown；
6. 不生成跨论文结论；
7. 更新状态为 `generated`。

环境支持隔离 worker 时，每个 worker 只处理一篇论文且只返回文件路径和状态。环境不支持时顺序处理，上一份报告保存后不将其全文复制进下一任务。

### 阶段 3：质量门禁

运行：

```bash
python scripts/validate_item.py \
  paper-batch-output/<batch_id>/items/P001.attempt-1.md \
  --mode 中文精读 \
  --json-output paper-batch-output/<batch_id>/validation/P001.json
```

检查四类内容：

- 语言：中文比例、英文大段、英文主标题；
- 结构：汇报摘要、方法、实验、结果、局限、代码、总结；
- 结果：数据集、指标、baseline、可比性、收益和代价；
- 证据：表格/章节/代码位置、缺失信息标记、论文身份一致性。

### 阶段 4：针对性重试

失败时先读取校验 JSON，再使用：

```text
上一版未通过批量质量门禁。

论文 ID：
未通过项：
1. ...
2. ...

修订要求：
- 保留已核实内容；
- 全文使用中文；
- 补齐缺失章节；
- 不删除已有结果；
- 不编造数据；
- 未报告信息明确标注；
- 输出完整修订版，不输出修改说明。
```

默认最多 2 次。每次保存独立 attempt。仍未通过则标记 `failed_quality_gate`，不得进入正式比较矩阵。

### 阶段 5：锁定成果

通过后：

1. 标记 `validated`；
2. 保存为 `items/<id>.md`；
3. 记录尝试次数、校验状态、中文比例、缺失项、论文版本和代码状态。

### 阶段 6：批次汇总

汇总阶段只读取：

- `manifest.json`；
- 通过门禁的 `items/<id>.md`；
- `validation/<id>.json`。

默认不重新加载全部论文全文。只在解决冲突时回到对应论文。

按 `references/aggregation-schema.md` 生成：

1. 完成情况；
2. 单篇一句话总结；
3. 方法分类；
4. 创新矩阵；
5. 结果对比；
6. 速度、存储与复杂度；
7. 代码和复现状态；
8. 共性局限；
9. 不可比较项；
10. 失败清单；
11. 批次总体结论。

### 阶段 7：批次校验

```bash
python scripts/validate_batch.py \
  paper-batch-output/<batch_id> \
  --manifest paper-batch-output/<batch_id>/manifest.json
```

## 七、单篇硬性输出合同

每个完整模式必须包含：

```markdown
# 《论文标题》中文分析报告

## 0. 汇报摘要
## 1. 论文信息与分析范围
## 2. 一句话核心贡献
## 3. 问题与动机
## 4. 方法总体流程
## 5. 技术方法分析
## 6. 论文与代码对应
## 7. 实验设置
## 8. 结果汇报与分析
### 8.1 主要结果总表
### 8.2 效率、存储与计算代价
### 8.3 逐数据集或逐场景一致性
### 8.4 消融实验
### 8.5 定性结果与失败案例
### 8.6 结果证明了什么
### 8.7 结果尚未证明什么
### 8.8 结果汇报总结
## 9. 相关工作关系
## 10. 局限性与适用边界
## 11. 可复现性
## 12. 最终汇报总结
```

精炼模式可合并章节，但不能删除汇报摘要、主要结果、结果解读、局限和最终结论。

## 八、汇总原则

### 8.1 证据链

批次数字必须满足：

```text
批次总结 → 单篇报告 → 论文/代码证据
```

### 8.2 不强行排名

数据集、场景、分辨率、硬件、模型大小口径、训练预算或指标实现不同，必须标注：

- `受控可比`
- `论文报告、基本可比`
- `部分可比`
- `不可直接比较`

### 8.3 汇总仍然使用中文

方法名和表头可包含英文，但分类说明、结果解读、局限、选型建议和最终结论必须使用中文。

## 九、状态机

```text
pending
acquiring
analyzing
generated
validating
retrying
validated
failed_source
failed_analysis
failed_quality_gate
```

状态必须写入 `status.json`，支持中断恢复。

## 十、中断恢复

重新启动时：

1. 读取 manifest 和 status；
2. 跳过 `validated`；
3. 对 `generated` 重新校验；
4. 对 `retrying` 从最近 attempt 继续；
5. 不覆盖已有通过报告。

## 十一、禁止事项

- 禁止把所有 PDF 全文拼入同一提示词；
- 禁止前几篇精读、后几篇只写摘要；
- 禁止把上一篇数字复制到下一篇；
- 禁止不校验就生成总表；
- 禁止因论文为英文而输出英文正文；
- 禁止将失败项伪装成完成项；
- 禁止统一套话替代逐篇判断；
- 禁止填补论文未报告的数据；
- 禁止在不可比时做总排名；
- 禁止汇总阶段擅自改写单篇数值。

## 十二、推荐调用方式

```text
使用 3dgs-paper-batch-orchestrator 批量分析这些论文。

要求：
- 单篇模式为中文精读；
- 顺序处理；
- 每篇重新加载 3dgs-paper-analyzer；
- 每篇独立保存；
- 通过中文、结果完整性和证据检查后才进入汇总；
- 失败项最多重试 2 次；
- 最后生成批次总览、方法对比、结果对比和失败清单。
```

## 十三、相关文件

- `references/batch-protocol.md`
- `references/quality-gate.md`
- `references/aggregation-schema.md`
- `templates/item-task-prompt.md`
- `templates/batch-summary-template.md`
- `scripts/init_batch.py`
- `scripts/validate_item.py`
- `scripts/validate_batch.py`
