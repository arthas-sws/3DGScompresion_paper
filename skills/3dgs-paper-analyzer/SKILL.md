---
name: 3dgs-paper-analyzer
description: 单篇 3D Gaussian Splatting、Gaussian Splatting、NeRF、神经渲染、三维重建及相关论文中文精读 Skill。用于完整阅读一篇论文及其补充材料，核查项目主页和官方代码，分析表示、渲染、优化、密度控制、压缩机制、实验公平性、效率、局限和可复现性，并同时输出 Markdown 报告和机器可读 JSON。
---

# 3DGS Paper Analyzer

你是单篇论文分析者。一次只分析一篇论文，不调度批量任务，不维护论文数据库，不下载多篇论文，不生成固定字数的故事长文。

目标是产出一份证据可追踪、数字可汇总、结论有边界的中文精读报告，并同步产出结构化 JSON。

## 0. 模式选择

本 Skill 有两个模式：

### standard-analysis

默认模式。保持既有单篇中文精读能力：方法、代码、实验、效率、局限、复现和可比性分析。输出：

```text
<paper_id>.md
<paper_id>.json
```

`<paper_id>.json` 必须遵循 `schemas/paper-analysis.schema.json`。

### innovation-review

当用户要求拆解论文创新点、判断实验是否支撑创新主张、比较相似论文、提出方法改进、设计补充实验或保全论文主要实验表格时使用。

调用示例：

```text
使用 $3dgs-paper-analyzer 的 innovation-review 模式，
对 P001 做创新主张、实验支撑、相似论文和改进方向分析。
```

innovation-review 不是独立 Skill。它必须仍然输出标准文件：

```text
<paper_id>.md
<paper_id>.json
```

标准 JSON 继续遵循 `schemas/paper-analysis.schema.json`，并额外输出：

```text
<paper_id>.innovation-review.json
```

标准 JSON 中可加入扩展引用：

```json
{
  "extensions": {
    "innovation_review": "P001.innovation-review.json"
  }
}
```

innovation-review 的详细协议见 `references/innovation-review-mode.md`；表格保真、相关论文阅读深度和改进建议分别见：

- `references/innovation-review/table-fidelity.md`
- `references/innovation-review/related-paper-depth.md`
- `references/innovation-review/improvement-rubric.md`

## 1. 输入

可接受：

- 单篇 PDF、本地路径、arXiv URL、DOI、项目主页或论文标题；
- 来自 retrieval manifest 的单篇 paper 条目；
- 用户给出的官方代码仓库、补充材料、实验日志或关注点。

输入不完整时继续完成可核实部分，但必须在报告开头写明分析边界。若论文身份无法确定，应停止并列出候选，不分析错误对象。

## 2. 输出合同

每篇论文必须同时输出：

```text
<paper_id>.md
<paper_id>.json
```

若用户未提供 `paper_id`，使用 `P001` 或用户指定文件名，但 Markdown 与 JSON 内部 ID 必须一致。

JSON 必须遵循仓库根目录：

```text
schemas/paper-analysis.schema.json
```

最小结构：

```json
{
  "schema_version": "1.0",
  "paper": {
    "id": "P001",
    "title": "",
    "authors": [],
    "arxiv_id": "",
    "source_url": "",
    "pdf_path": "",
    "code_url": "",
    "paper_version": "",
    "code_commit": ""
  },
  "analysis": {
    "task": "",
    "core_contribution": "",
    "method_summary": "",
    "method_category": [],
    "datasets": [],
    "metrics": [],
    "main_results": [],
    "efficiency": [],
    "ablations": [],
    "code_mapping": [],
    "limitations": [],
    "claims": [],
    "evidence": [],
    "comparability": [],
    "reproducibility": {}
  },
  "validation": {
    "language": "zh-CN",
    "status": "PASS",
    "missing_sections": [],
    "warnings": []
  }
}
```

关键数字不能只写在 Markdown 中，必须同步进入 JSON。每条主要结果建议包含：

```json
{
  "dataset": "",
  "scene": "",
  "metric": "",
  "method_value": null,
  "baseline_name": "",
  "baseline_value": null,
  "difference": null,
  "comparison_direction": "higher_is_better",
  "comparability": "论文报告、基本可比",
  "evidence": "Table 2",
  "notes": ""
}
```

## 3. 语言规则

- 默认输出中文，除非用户明确要求英文；
- 论文标题、方法名、数据集名、代码路径和指标名可保留英文；
- 重要术语首次出现时使用“中文解释（English term）”；
- 不逐句翻译论文原文，要基于理解重组；
- 不复制大段英文摘要或论文正文。

## 4. 来源完整性

条件允许时必须读取：

- 摘要、引言、方法、实验、消融、局限和结论；
- 附录、补充材料、表注、图注；
- 项目主页、官方代码 README、配置、训练入口、评估入口、核心模型和损失实现；
- 论文声明的实验设置和 baseline 信息。

如果某项来源不可用，写明：

- `论文未报告`
- `补充材料未提供`
- `当前代码中未找到`
- `无法从现有材料核实`

不得静默省略。

## 5. 证据账本

重要结论必须能追踪到证据。使用以下证据标签：

- `[论文 Sec. 3.2]`
- `[论文 Eq. 6]`
- `[论文 Table 2]`
- `[论文 Fig. 4]`
- `[补充材料 p. 8]`
- `[代码 models/gaussian.py::densify_and_split]`
- `[作者主张]`
- `[独立判断]`
- `[待核实]`

必须带证据的内容：

- 方法核心机制；
- PSNR、SSIM、LPIPS、FPS、模型大小、显存、训练时间等数字；
- 代码映射；
- baseline 公平性判断；
- 局限、失败案例和复现风险。

详细规则见 `references/evidence-policy.md`。

## 6. 四类陈述

报告中必须区分：

1. 作者主张：论文或项目页声称了什么；
2. 直接证据：表格、公式、图、代码直接显示什么；
3. 独立判断：你基于证据得出的分析；
4. 不确定信息：缺失、冲突或无法核实的信息。

不要把作者主张写成已证实事实。

## 7. 禁止编造

不得编造、估算或默认存在：

- PSNR、SSIM、LPIPS、FPS、MB、GB、训练小时数；
- Gaussian 数量、码率、显存、模型大小；
- 数据集划分、分辨率、硬件型号、训练步数；
- 代码路径、函数名、配置项或 commit；
- 会议录用状态。

找不到时明确写“未报告”或“无法核实”。

## 8. 可比性原则

只有在数据集、场景、划分、分辨率、指标定义、训练预算、硬件和模型大小口径基本一致时，才允许计算差值或下“更优”结论。

对每个比较项标注：

- `受控可比`
- `论文报告、基本可比`
- `部分可比`
- `不可直接比较`

不可比论文不得强行排名。

## 9. 分析流程

1. 确认论文身份、版本、PDF、补充材料、项目页和代码来源；
2. 建立论文结构地图：问题、假设、方法、公式、主表、消融、失败案例；
3. 按 3DGS 专业框架分析表示、渲染、优化、密度控制和任务特定模块；
4. 核查官方代码，记录论文到代码的映射；
5. 审计实验设置、baseline、指标和可比性；
6. 提取主要结果、效率、模型大小、训练代价和消融；
7. 写出局限、复现风险和未证明内容；
8. 生成 Markdown 与 JSON；
9. 运行 `scripts/validate_report.py` 做交付前检查。

3DGS taxonomy 见 `references/3dgs-analysis-schema.md`。

## 10. Markdown 报告结构

默认使用以下结构，可根据任务轻微调整，但不得删除结果、代价、局限和复现结论。

```markdown
# 《论文标题》中文精读报告

## 0. 汇报摘要
## 1. 论文信息与分析边界
## 2. 一句话核心贡献
## 3. 问题、动机与相关方法位置
## 4. 方法总体流程
## 5. 技术方法分析
## 6. 论文与代码对应关系
## 7. 实验设置审计
## 8. 结果汇报与分析
## 9. 效率、存储、显存与训练代价
## 10. 消融实验与失败案例
## 11. 局限、适用边界与未证明内容
## 12. 可复现性结论
## 13. 最终汇报总结
```

结果表详细规则见 `references/result-reporting.md`。输出模式和精简模板见 `references/output-profiles.md`。

## 11. JSON 字段填充规则

`analysis.task`：

- 写论文解决的具体任务，不写泛泛的“提升 3DGS”；
- 示例：`3DGS compression`、`sparse-view novel view synthesis`、`dynamic scene reconstruction`。

`analysis.core_contribution`：

- 用 1 到 3 句话概括真正贡献；
- 不直接复制摘要；
- 避免写没有证据的“首次”“最优”“SOTA”。

`analysis.method_category`：

- 使用可汇总标签；
- 示例：`pruning`、`quantization`、`entropy coding`、`feed-forward`、`SLAM`、`dynamic 4DGS`。

`analysis.main_results`：

- 只收录可定位证据的主要结果；
- 未报告数字不要填估计值，用 `null` 或 `论文未报告`；
- `difference` 只有论文直接报告或可比条件明确时才填写；
- 每条都必须有 `evidence` 和 `comparability`。

`analysis.efficiency`：

- 分开记录渲染速度、训练时间、显存、模型大小、编码/解码代价；
- 写清统计口径，例如是否包含解码器权重和元数据。

`analysis.code_mapping`：

- 记录论文模块、论文位置、代码路径、配置项、对应程度；
- 没有代码时写 `代码未公开`，不要留空。

`analysis.reproducibility`：

- 至少包含代码状态、数据可得性、命令完整性、环境风险和复现结论。

## 12. 专业分支入口

通用 3DGS 分析必须覆盖：

- Gaussian primitive 的参数化；
- 初始化和输入假设；
- 投影、排序、光栅化和 alpha 合成；
- 损失函数、正则和优化变量；
- densification、split、clone、prune、opacity reset；
- 训练和推理流程；
- 计算、存储和部署代价。

压缩论文额外覆盖：

- 压缩对象和码率口径；
- 剪枝、量化、熵模型、码本、低秩或蒸馏；
- 解码器权重、索引和元数据是否计入大小；
- rate-distortion 曲线或质量-大小权衡；
- 是否牺牲训练时间、解码时间或渲染速度。

动态论文额外覆盖：

- canonical space、deformation field、per-frame Gaussian 或 trajectory；
- 时间一致性和遮挡处理；
- 是否支持拓扑变化和长序列；
- 动态结果是否与静态背景混合统计。

SLAM 论文额外覆盖：

- tracking、mapping、keyframe、loop closure、relocalization；
- ATE/RPE 与渲染质量的关系；
- 传感器输入和实时性；
- 动态物体、漂移和地图增长风险。

Feed-forward 论文额外覆盖：

- 输入视图数和相机姿态要求；
- 跨场景泛化数据；
- 是否与 per-scene optimization 公平比较；
- 推理速度与训练集规模。

## 13. 代码核查

优先顺序：

1. 论文或项目主页给出的官方仓库；
2. 作者组织或实验室官方仓库；
3. arXiv 关联代码；
4. 第三方实现，只能作为参考，必须标注非官方。

至少检查：

- 环境依赖、数据预处理；
- 训练入口、渲染入口、评估脚本；
- Gaussian 参数、rasterizer/CUDA 扩展；
- loss、densification、pruning、quantization、compression；
- 配置默认值和复现实验命令。

输出代码映射表，并在 JSON 的 `analysis.code_mapping` 中同步记录。

## 14. 交付前检查

提交前运行：

```powershell
python skills\3dgs-paper-analyzer\scripts\validate_report.py `
  --md P001.md `
  --json P001.json `
  --manifest paper-retrieval-output\batch\manifest.json
```

检查项：

- Markdown 与 JSON 同时存在；
- paper ID 和标题一致；
- JSON 必填字段完整；
- 主要数字进入 JSON；
- 每条主要结果有证据位置；
- 大段英文正文不过量；
- 结果、代价、局限和可复现性结论存在；
- 没有混入其他论文 ID。

若校验失败，修正文档和 JSON，而不是只改校验输出。

## 15. 失败处理

- 找不到论文：列出候选和缺失信息，不分析错误对象；
- PDF 提取不完整：说明缺失范围，必要时改读 HTML 或截图；
- 代码未公开：写明未公开，不用无关代码替代；
- 指标冲突：保留各来源数值并解释冲突；
- 结果缺失：在 Markdown 和 JSON 都标为未报告；
- 无法判断可比性：标为 `不可直接比较`。

## 16. 禁止事项

- 禁止一次分析多篇论文全文；
- 禁止自行维护批次状态；
- 禁止批量下载大量论文；
- 禁止生成公众号式固定字数文章；
- 禁止用固定公式数量、固定代码段数量填充报告；
- 禁止让后一篇论文继承前一篇正文；
- 禁止在无结构化 JSON 时让批量汇总猜测数字。

## 17. 相关资源

- `references/3dgs-analysis-schema.md`
- `references/evidence-policy.md`
- `references/result-reporting.md`
- `references/output-profiles.md`
- `references/innovation-review-mode.md`
- `references/innovation-review/table-fidelity.md`
- `references/innovation-review/related-paper-depth.md`
- `references/innovation-review/improvement-rubric.md`
- `templates/innovation-review-template.md`
- `scripts/create_analysis_stub.py`
- `scripts/validate_report.py`
- `scripts/validate_innovation_review.py`
- `scripts/update_paper_index.py`
- `scripts/render_html.py`
