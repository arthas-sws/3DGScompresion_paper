# 3dgs-paper-analyzer

单篇 3DGS/NeRF 相关论文中文精读 Skill。它不负责批量调度或多篇下载，只负责一篇论文的证据化分析，并输出：

```text
P001.md
P001.json
```

生成空模板：

```powershell
python skills\3dgs-paper-analyzer\scripts\create_analysis_stub.py `
  --paper-id P001 `
  --title "Paper Title" `
  --output-dir analysis-output
```

校验报告：

```powershell
python skills\3dgs-paper-analyzer\scripts\validate_report.py `
  --md analysis-output\P001.md `
  --json analysis-output\P001.json
```

可选 HTML 渲染：

```powershell
python skills\3dgs-paper-analyzer\scripts\render_html.py `
  analysis-output\P001.md `
  analysis-output\P001.html
```
