# Retrieval Protocol

`manifest.json` 是检索下载 Skill 与后续 Skill 的唯一正式接口。后续工具不得依赖候选 JSON 的内部格式。

每个 paper 条目必须包含稳定 ID、标题、作者数组、来源链接、PDF 链接、本地 PDF 相对路径、下载状态、元信息状态和去重记录。

失败必须写入 `failures.json`。失败项保留论文 ID、标题、失败阶段、原因、重试次数和是否可重试。
