# 领域文档

工程 skill 在探索代码库时应如何消费本仓库的领域文档。

## 探索之前，先读这些

- **仓库根目录的 `CONTEXT.md`**，或
- **仓库根目录的 `CONTEXT-MAP.md`**（如果存在）：它指向每个 context 的 `CONTEXT.md`。阅读与主题相关的每一个。
- **`docs/adr/`**：阅读涉及你即将工作的区域的 ADR。在多上下文仓库中，还要查看 `src/<context>/docs/adr/` 以了解限定于上下文的决策。

如果这些文件中有任何不存在，**静默继续**。不要提示它们缺失；不要一开始就建议创建它们。`/domain-modeling` skill（通过 `/grill-with-docs` 和 `/improve-codebase-architecture` 触达）会在术语或决策真正被解决时惰性创建它们。

## 文件结构

单上下文仓库（绝大多数仓库）：

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文仓库（根目录存在 `CONTEXT-MAP.md`）：

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← context-specific decisions
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用词汇表的词汇

当你的输出提到某个领域概念（在 issue 标题、重构提案、假设、测试名称中）时，使用 `CONTEXT.md` 中定义的那个术语。不要偏移到词汇表明确回避的同义词。

如果你需要的概念还不在词汇表中，那是一个信号：要么你在发明项目并不使用的语言（重新考虑），要么确实存在空白（记下来交给 `/domain-modeling`）。

## 标记 ADR 冲突

如果你的输出与现有 ADR 相矛盾，明确指出来，而不是静默覆盖：

> _与 ADR-0007（event-sourced orders）相矛盾，但值得重新讨论，因为……_
