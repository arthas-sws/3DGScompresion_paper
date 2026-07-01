# 论文分析 Skills 使用说明

本仓库内置 3 个用于 3D Gaussian Splatting（3DGS）、NeRF、神经渲染和三维视觉论文分析的 Codex Skills。

## 目录结构

```text
.ai/skills/
├── 3dgs-paper-reader/
├── 3dgs-paper-analyzer/
└── 3dgs-paper-batch-orchestrator/
```

> 实际目录名以仓库中的文件夹名称为准。每个 Skill 目录下都必须包含 `SKILL.md`。

## 三个 Skill 的定位

### 1. `3dgs-paper-reader`

适合快速阅读单篇 3DGS/NeRF 论文。

主要用途：

- 快速提取论文元信息；
- 总结研究问题和核心创新；
- 梳理方法结构；
- 提取数据集、指标和主要实验结果；
- 给出局限性和相关工作关系。

推荐调用：

```text
使用 $3dgs-paper-reader 快速阅读这篇论文，
用中文总结研究问题、核心方法、主要实验结果和局限性。
```

### 2. `3dgs-paper-analyzer`

适合对单篇论文进行中文深度精读、审稿、代码核查或复现分析。

主要用途：

- 完整阅读论文和补充材料；
- 分析 Gaussian 表示、渲染、损失和密度控制；
- 核对官方代码与论文描述；
- 汇报定量结果、速度、显存和模型大小；
- 分析逐场景结果、消融和失败案例；
- 判断实验真正证明了什么；
- 输出中文精读报告、审稿报告或复现计划。

推荐调用：

```text
使用 $3dgs-paper-analyzer 对这篇论文进行中文精读。

必须包含：
1. 汇报摘要；
2. 方法总体流程；
3. 主要实验结果总表；
4. 效率与存储结果；
5. 逐场景稳定性；
6. 消融实验总结；
7. 结果证明了什么；
8. 结果尚未证明什么；
9. 最终汇报总结。
```

审稿模式：

```text
使用 $3dgs-paper-analyzer 的审稿模式检查这篇论文。
重点审核方法正确性、数据集与场景选择、baseline 公平性、
实验是否支撑中心结论、代码完整性和可复现性。
```

### 3. `3dgs-paper-batch-orchestrator`

适合批量整理多篇论文。

该 Skill 不替代单篇分析，而是负责：

- 建立论文清单；
- 将每篇论文拆成独立任务；
- 每篇重新调用 `3dgs-paper-analyzer`；
- 强制中文输出；
- 检查结果完整性和证据；
- 对失败任务进行重试；
- 生成批次总览和方法对比矩阵。

推荐调用：

```text
使用 $3dgs-paper-batch-orchestrator 批量分析 batch.json 中的论文。

要求：
1. 单篇使用中文精读模式；
2. 默认顺序处理；
3. 每篇重新加载 $3dgs-paper-analyzer；
4. 每篇报告单独保存；
5. 通过中文、结果完整性和证据检查后才能进入汇总；
6. 失败任务最多重试两次；
7. 最后生成批次总结、方法矩阵、结果矩阵和失败清单。
```

## Skill 之间的调用关系

```text
快速阅读单篇论文
    └── 3dgs-paper-reader

深度分析单篇论文
    └── 3dgs-paper-analyzer

批量分析多篇论文
    └── 3dgs-paper-batch-orchestrator
            └── 逐篇调用 3dgs-paper-analyzer
```

## 在 Codex 中安装

### Windows 全局安装目录

```text
C:\Users\<用户名>\.codex\skills\
```

例如：

```text
C:\Users\artha\.codex\skills\
```

将仓库中的三个 Skill 复制到全局目录：

```powershell
$RepoSkills = "D:\github\3D-Gaussian-Splatting-Papers\.ai\skills"
$CodexSkills = "C:\Users\artha\.codex\skills"

New-Item -ItemType Directory -Force -Path $CodexSkills | Out-Null

Copy-Item "$RepoSkills\3dgs-paper-reader" `
  "$CodexSkills\" -Recurse -Force

Copy-Item "$RepoSkills\3dgs-paper-analyzer" `
  "$CodexSkills\" -Recurse -Force

Copy-Item "$RepoSkills\3dgs-paper-batch-orchestrator" `
  "$CodexSkills\" -Recurse -Force
```

复制后重新打开 Codex 会话。

## 推荐的开发方式

仓库内的 `.ai/skills/` 作为唯一维护版本。

修改 Skill 后，再同步到 Codex 全局目录：

```powershell
$RepoSkills = "D:\github\3D-Gaussian-Splatting-Papers\.ai\skills"
$CodexSkills = "C:\Users\artha\.codex\skills"

$Skills = @(
  "3dgs-paper-reader",
  "3dgs-paper-analyzer",
  "3dgs-paper-batch-orchestrator"
)

foreach ($Skill in $Skills) {
  Remove-Item "$CodexSkills\$Skill" -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item "$RepoSkills\$Skill" "$CodexSkills\" -Recurse -Force
}
```

也可以使用 Junction，让全局目录直接指向仓库：

```powershell
$RepoSkills = "D:\github\3D-Gaussian-Splatting-Papers\.ai\skills"
$CodexSkills = "C:\Users\artha\.codex\skills"

$Skills = @(
  "3dgs-paper-reader",
  "3dgs-paper-analyzer",
  "3dgs-paper-batch-orchestrator"
)

New-Item -ItemType Directory -Force -Path $CodexSkills | Out-Null

foreach ($Skill in $Skills) {
  Remove-Item "$CodexSkills\$Skill" -Recurse -Force -ErrorAction SilentlyContinue
  New-Item -ItemType Junction `
    -Path "$CodexSkills\$Skill" `
    -Target "$RepoSkills\$Skill" | Out-Null
}
```

使用 Junction 后，只需修改仓库中的 Skill，无需再次复制。

## 仓库内的 AGENTS.md 建议

可在仓库根目录的 `AGENTS.md` 中加入：

```markdown
## Paper Analysis Skills

When working with 3DGS, NeRF, neural rendering, or 3D vision papers:

- For quick single-paper reading, use `.ai/skills/3dgs-paper-reader/SKILL.md`.
- For deep single-paper analysis, review, code inspection, or reproduction, use `.ai/skills/3dgs-paper-analyzer/SKILL.md`.
- For multi-paper batch analysis, use `.ai/skills/3dgs-paper-batch-orchestrator/SKILL.md`.
- Unless the user explicitly requests English, all paper reports and batch summaries must be written in Chinese.
- Batch analysis must process papers independently and validate each report before aggregation.
```

## 注意事项

1. 不要只上传 `SKILL.md`，应上传整个 Skill 文件夹。
2. `references/`、`scripts/`、`templates/`、`assets/` 都可能被主 Skill 引用。
3. 不要提交批量分析产生的大型 PDF、缓存和临时结果。
4. 批处理结果建议放入独立目录，并根据需要加入 `.gitignore`。
5. 修改 Skill 后，应检查 `SKILL.md` 的相对路径是否仍然正确。
6. 批量分析时优先顺序执行，只有在任务真正隔离时才开启并行。
