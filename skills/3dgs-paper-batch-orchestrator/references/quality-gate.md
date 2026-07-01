# Quality Gate

单篇质量门槛以 `3dgs-paper-analyzer/scripts/validate_report.py` 为准，batch 层额外检查：

- manifest 中存在该 paper ID；
- title 与 manifest 一致；
- 当前报告不包含其他 paper ID；
- validated 状态必须有 `items/Pxxx.md` 与 `items/Pxxx.json`；
- failed 状态必须进入失败清单；
- 重试不得覆盖已有 attempt。
