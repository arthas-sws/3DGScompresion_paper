# Evidence Policy

## 证据等级

- A：论文表格、公式、图、附录或官方代码直接支持；
- B：项目主页、官方 README、官方 release 支持；
- C：第三方实现或复现实验支持，必须标注非官方；
- D：独立判断，只能作为分析，不得写成事实；
- U：未知、冲突或无法核实。

## 必须记录位置

所有关键数字、公式解释、代码映射、baseline 公平性和局限结论都要给出位置。

可用位置格式：

- `Sec. 3.1`
- `Eq. 4`
- `Table 2`
- `Fig. 5`
- `Supplement p. 8`
- `models/gaussian_model.py::densify_and_prune`

## 数字记录

记录数字时同步写清：

- 数据集和场景；
- 指标和方向；
- 本文值和 baseline 值；
- 差值是否由论文直接给出；
- 可比性标签；
- 证据位置；
- 缺失或冲突说明。

## 不确定信息

无法核实时不要删除该项。写入 Markdown，并在 JSON 的 `warnings`、`limitations` 或对应结果 `notes` 中记录。
