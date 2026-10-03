## Agent skills

### Issue tracker

本仓库使用 GitHub Issues，所有操作通过 `gh` CLI。详见 `docs/agents/issue-tracker.md`。

### Triage labels

使用五个标准 triage 标签：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。详见 `docs/agents/triage-labels.md`。

### Domain docs

采用单上下文布局：根目录 `GLOSSARY.md` 与 `docs/adr/`。详见 `docs/agents/domain.md`。

### Implementation notes

实现决策与因果记录存放在 `.agents/notes/`，记录决策、取舍与偏离，供下一次尝试学习。
