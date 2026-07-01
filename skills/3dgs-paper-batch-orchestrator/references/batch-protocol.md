# Batch Protocol

批量入口是 retrieval `manifest.json`。batch 初始化时会复制 manifest，并把 PDF 相对路径改写为相对 batch 输出目录的路径，确保恢复执行时可以定位 PDF。

每篇论文独立处理，任务 prompt 存在 `attempts/`。通过校验的最终报告固定为：

```text
items/P001.md
items/P001.json
```

旧 attempt 不覆盖，重试 prompt 写入 `retry-prompts/`。
