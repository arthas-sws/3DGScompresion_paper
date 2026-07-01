# 3dgs-paper-batch-orchestrator

批量调度 3DGS 论文单篇精读。它读取 retrieval `manifest.json`，为每篇论文生成独立任务包，等待 `3dgs-paper-analyzer` 逐篇产出 Markdown 和 JSON，然后校验、重试并汇总。

```powershell
python skills\3dgs-paper-batch-orchestrator\scripts\init_batch.py `
  --manifest paper-retrieval-output\compression-survey-01\manifest.json `
  --output-dir paper-batch-output\compression-survey-01

python skills\3dgs-paper-batch-orchestrator\scripts\run_batch.py `
  --batch-dir paper-batch-output\compression-survey-01
```

默认不会假装自动调用 Codex 子任务；未生成单篇报告时状态为 `waiting_for_agent`，并在 `attempts/` 中写入 prompt。
