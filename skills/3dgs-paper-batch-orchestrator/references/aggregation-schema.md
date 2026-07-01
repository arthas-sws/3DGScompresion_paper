# Aggregation Schema

汇总读取 `items/Pxxx.json` 中的结构化字段，不重新发明数字。

`result-matrix.json`：

```json
{
  "schema_version": "1.0",
  "batch_id": "",
  "papers": [],
  "results": [],
  "failed": []
}
```

每个 `results` 项来自单篇 `analysis.main_results`，必须带 `paper_id`、`title`、`metric`、`comparability` 和 `evidence`。

不可比结果保留，但不得进入统一排名。
