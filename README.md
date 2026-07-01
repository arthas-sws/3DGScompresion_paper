# 3DGS Paper Skills

这是一个面向 3D Gaussian Splatting、Gaussian Splatting、NeRF、神经渲染和三维重建论文处理的 Codex Skills 工具集。

仓库只保留三个职责分离的 Skill：

```text
skills/
├── paper-retrieval-downloader/
├── 3dgs-paper-analyzer/
└── 3dgs-paper-batch-orchestrator/
```

## 三阶段工作流

```text
paper-retrieval-downloader
        │
        │ manifest.json + PDF
        ▼
3dgs-paper-batch-orchestrator
        │
        │ 每篇独立调用
        ▼
3dgs-paper-analyzer
```

单篇场景也可以直接使用：

```text
PDF / URL
    ▼
3dgs-paper-analyzer
```

## 三个 Skill 的职责

`paper-retrieval-downloader`

- 检索论文、解析 arXiv 元信息、去重、下载 PDF；
- 生成 `manifest.json`、`failures.json`、`metadata/` 和 `papers.md`；
- 不分析方法，不维护 README/abs/archive/venue，不生成 Changelog。

`3dgs-paper-analyzer`

- 对单篇论文做中文精读；
- 阅读论文、补充材料、项目主页和官方代码；
- 分析 3DGS 表示、渲染、优化、密度控制、压缩、实验、公平性、效率和局限；
- 同时输出 `P001.md` 和 `P001.json`；
- 不做批量调度，不下载多篇论文，不生成固定字数 HTML 长文。

`3dgs-paper-batch-orchestrator`

- 读取 retrieval `manifest.json`；
- 为每篇论文生成独立任务包；
- 调用 `3dgs-paper-analyzer` 的单篇流程；
- 维护 `status.json`，支持中断恢复、重试、质量门槛和汇总；
- 只用 `validated` 项生成批次总结、方法矩阵和结果矩阵。

## 目录结构

```text
3DGScompresion_paper/
├── README.md
├── LICENSE
├── ATTRIBUTION.md
├── CHANGELOG.md
├── pyproject.toml
├── schemas/
│   ├── retrieval-manifest.schema.json
│   ├── failures.schema.json
│   ├── paper-analysis.schema.json
│   └── batch-status.schema.json
├── skills/
│   ├── paper-retrieval-downloader/
│   ├── 3dgs-paper-analyzer/
│   └── 3dgs-paper-batch-orchestrator/
└── tests/
    ├── test_retrieval_manifest.py
    ├── test_analysis_output.py
    └── test_batch_validation.py
```

## 安装

将 `skills/<skill-name>/` 复制到 Codex Skills 目录，或直接在本仓库中引用。

Windows PowerShell：

```powershell
$RepoSkills = (Resolve-Path ".\skills").Path
$CodexSkills = "$env:USERPROFILE\.codex\skills"

New-Item -ItemType Directory -Force -Path $CodexSkills | Out-Null
Copy-Item "$RepoSkills\paper-retrieval-downloader" "$CodexSkills\" -Recurse -Force
Copy-Item "$RepoSkills\3dgs-paper-analyzer" "$CodexSkills\" -Recurse -Force
Copy-Item "$RepoSkills\3dgs-paper-batch-orchestrator" "$CodexSkills\" -Recurse -Force
```

Linux/macOS：

```bash
repo_skills="$HOME/path/to/3DGScompresion_paper/skills"
codex_skills="${CODEX_HOME:-$HOME/.codex}/skills"

mkdir -p "$codex_skills"
cp -R "$repo_skills/paper-retrieval-downloader" "$codex_skills/"
cp -R "$repo_skills/3dgs-paper-analyzer" "$codex_skills/"
cp -R "$repo_skills/3dgs-paper-batch-orchestrator" "$codex_skills/"
```

## 依赖安装

Python 最低版本：`3.10`。

使用 `uv`：

```powershell
uv sync --extra test
```

使用 `pip`：

```powershell
python -m pip install -e .[test]
```

Linux/macOS：

```bash
uv sync --extra test
python -m pip install -e '.[test]'
```

说明：

- 核心脚本尽量使用 Python 标准库；
- `markdown` 用于可选 HTML 渲染；
- `jsonschema` 可用于外部 schema 校验；
- `beautifulsoup4`、`requests` 预留给更复杂的网页元信息解析；
- Windows PowerShell 下建议保持 UTF-8 文件编码，避免用旧控制台编码重写中文 Markdown。

## 检索下载示例

Windows PowerShell：

```powershell
python skills\paper-retrieval-downloader\scripts\fetch.py `
  --batch-id compression-survey-01 `
  --keyword "3D Gaussian Splatting compression" `
  --keyword "Gaussian Splatting pruning" `
  --max-results 20 `
  --output tmp\compression-candidates.json

python skills\paper-retrieval-downloader\scripts\download.py `
  --input tmp\compression-candidates.json `
  --batch-id compression-survey-01 `
  --output-dir paper-retrieval-output\compression-survey-01
```

Linux/macOS：

```bash
python skills/paper-retrieval-downloader/scripts/fetch.py \
  --batch-id compression-survey-01 \
  --keyword "3D Gaussian Splatting compression" \
  --keyword "Gaussian Splatting pruning" \
  --max-results 20 \
  --output tmp/compression-candidates.json

python skills/paper-retrieval-downloader/scripts/download.py \
  --input tmp/compression-candidates.json \
  --batch-id compression-survey-01 \
  --output-dir paper-retrieval-output/compression-survey-01
```

`uv` 形式：

```powershell
uv run python skills\paper-retrieval-downloader\scripts\download.py `
  --input tmp\compression-candidates.json `
  --batch-id compression-survey-01 `
  --output-dir paper-retrieval-output\compression-survey-01
```

## 单篇分析示例

直接请求 Codex：

```text
使用 3dgs-paper-analyzer 分析 paper-retrieval-output/compression-survey-01/manifest.json 中的 P001。
输出 analysis-output/P001.md 和 analysis-output/P001.json。
关键数字必须进入 JSON，并带证据和可比性标签。
```

生成空模板：

```powershell
python skills\3dgs-paper-analyzer\scripts\create_analysis_stub.py `
  --paper-id P001 `
  --title "Paper Title" `
  --output-dir analysis-output `
  --pdf-path paper-retrieval-output\compression-survey-01\papers\P001.pdf
```

校验：

```powershell
python skills\3dgs-paper-analyzer\scripts\validate_report.py `
  --md analysis-output\P001.md `
  --json analysis-output\P001.json `
  --manifest paper-retrieval-output\compression-survey-01\manifest.json
```

## 批量分析示例

初始化批次：

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\init_batch.py `
  --manifest paper-retrieval-output\compression-survey-01\manifest.json `
  --output-dir paper-batch-output\compression-survey-01
```

生成任务包或恢复批次：

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\run_batch.py `
  --batch-dir paper-batch-output\compression-survey-01
```

当 `items/P001.md` 和 `items/P001.json` 由单篇 analyzer 生成后：

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\validate_item.py `
  --batch-dir paper-batch-output\compression-survey-01 `
  --paper-id P001

python skills\3dgs-paper-batch-orchestrator\scripts\aggregate_reports.py `
  --batch-dir paper-batch-output\compression-survey-01

python skills\3dgs-paper-batch-orchestrator\scripts\validate_batch.py `
  --batch-dir paper-batch-output\compression-survey-01
```

Linux/macOS 将反斜杠换成 `/`，并可使用 `uv run python ...`。

## 输入输出协议

检索输出：

```text
paper-retrieval-output/<batch_id>/
├── manifest.json
├── failures.json
├── papers/
├── metadata/
└── papers.md
```

单篇输出：

```text
P001.md
P001.json
```

批量输出：

```text
paper-batch-output/<batch_id>/
├── manifest.json
├── status.json
├── items/
├── attempts/
├── validation/
├── retry-prompts/
├── batch-summary.md
├── comparison-matrix.md
├── result-matrix.json
└── failed-items.md
```

## 常见错误

- `waiting_for_agent`：当前环境没有自动调用 Codex 子任务。打开 `attempts/*.prompt.md`，逐篇交给 `3dgs-paper-analyzer` 执行。
- `failed_source`：manifest 中的 PDF 路径不存在。检查 retrieval 输出目录是否移动，或重新运行下载。
- `failed_quality_gate`：单篇 Markdown/JSON 缺少结构、证据或关键数字。按 `validation/Pxxx.json` 修正后重试。
- `result-matrix.json not generated yet`：先运行 `aggregate_reports.py`。
- Windows 中文乱码：确保文件按 UTF-8 保存；不要用旧编码的编辑器重写 `SKILL.md`。
- 下载失败：查看 `failures.json`，失败不会静默跳过；默认不会覆盖已有 PDF，需覆盖时显式使用 `--overwrite`。

## License 和 Attribution

仓库脚本和 Skill 文档采用 MIT License，见 `LICENSE`。

论文、PDF、项目主页和代码仓库仍归原作者、出版方或对应开源许可证所有。见 `ATTRIBUTION.md`。
