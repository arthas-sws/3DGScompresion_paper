# 3DGS 论文深度分析器（中文版）

这是一个面向 3D Gaussian Splatting、NeRF 和神经渲染论文的 Codex Skill。

本版本重点修复：

- 全部核心指令改为中文；
- 默认强制中文输出；
- 增加“汇报摘要”；
- 增加主要结果总表；
- 增加效率、存储、逐场景一致性和消融总结；
- 增加“结果证明了什么 / 尚未证明什么”；
- 增加最终汇报总结；
- 中文化校验脚本；
- 简化 Codex frontmatter。

## 放置位置

全局使用：

```text
C:\Users\<用户名>\.codex\skills\3dgs-paper-analyzer\
```

项目内版本管理：

```text
项目目录\.ai\skills\3dgs-paper-analyzer\
```

推荐让全局目录通过 Junction 指向项目内目录。

## 最终目录

```text
3dgs-paper-analyzer/
├── SKILL.md
├── references/
│   ├── 3dgs-analysis-schema.md
│   ├── evidence-policy.md
│   ├── result-reporting.md
│   └── output-profiles.md
├── scripts/
│   ├── render_html.py
│   └── validate_report.py
├── assets/
│   └── article-template.html
└── examples/
    └── sample-request.md
```

## 使用示例

```text
使用 3dgs-paper-analyzer 对这篇论文进行中文精读。
必须汇报主要实验结果、逐场景稳定性、效率与存储代价，
并总结实验真正证明了什么、还没有证明什么。
```

```text
使用 3dgs-paper-analyzer 的审稿模式。
重点检查场景选择、baseline 公平性、结果是否支持中心结论，
最后给出中文审稿总结。
```
