# paper-retrieval-downloader

检索、去重、下载和整理 3DGS/NeRF 相关论文，输出后续分析可直接消费的 `manifest.json`。

常用命令：

```powershell
python skills\paper-retrieval-downloader\scripts\fetch.py `
  --batch-id compression-survey-01 `
  --keyword "3D Gaussian Splatting compression" `
  --output tmp\candidates.json

python skills\paper-retrieval-downloader\scripts\download.py `
  --input tmp\candidates.json `
  --batch-id compression-survey-01 `
  --output-dir paper-retrieval-output\compression-survey-01
```

输出目录包含 `manifest.json`、`failures.json`、`papers/`、`metadata/` 和 `papers.md`。
