# 3DGS 论文批量调度器

该 Skill 与 `3dgs-paper-analyzer` 配合使用，解决批量处理中出现的中文漂移、后半批缩水、结果汇报缺失、论文数据互相污染和未校验即汇总等问题。

## 安装结构

```text
.codex/skills/
├── 3dgs-paper-analyzer/
└── 3dgs-paper-batch-orchestrator/
```

Windows 全局路径：

```text
C:\Users\<用户名>\.codex\skills\3dgs-paper-batch-orchestrator
```

项目内版本管理：

```text
项目\.ai\skills\3dgs-paper-batch-orchestrator
```

推荐调用：

```text
使用 3dgs-paper-batch-orchestrator 批量分析清单中的论文。
单篇使用中文精读模式并顺序处理。
每篇重新加载 3dgs-paper-analyzer、单独保存并执行质量检查。
失败项最多重试两次，全部完成后再生成中文汇总和对比矩阵。
```
