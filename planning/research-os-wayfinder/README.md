# Research OS Wayfinder 历史快照

此目录保存早期 local-markdown Wayfinder 规划快照，仅用于追溯当时的决策过程。

- GitHub Issues 及其原生 parent、blocked-by、status 关系是当前规划和状态真源。
- `MAP.md`、`tracker.json`、`tickets/` 与 `resolutions/` 均为历史快照；不得据此计算当前 frontier、分配工作或覆盖 GitHub 状态。
- 快照内部可能保留矛盾，例如 T10 为 `closed`，同时仍被当时尚未关闭的 T07 阻塞。这类矛盾应原样保留并记录，不代表当前实现阻塞。
- 当前工作使用仓库规范的 `gh` CLI 流程；详见 `docs/agents/issue-tracker.md`（该治理文档由后续实现 ticket 提供）。

历史文件含义：

- `MAP.md`：当时的低分辨率 map。
- `tickets/*.md`：当时的 decision ticket；关闭票可含 resolution pointer。
- `resolutions/*.md`：当时已关闭 ticket 的详细答案。
- `tracker.json`：当时 local tracker 的 parent、blocked-by、status、assignee 快照。
