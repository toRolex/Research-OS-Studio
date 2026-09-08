# Issue tracker: GitHub

本仓库的 issue 和 spec 都以 GitHub issue 形式存在。所有操作使用 `gh` CLI。

## 惯例

- **创建 issue**：`gh issue create --title "..." --body "..."`。多行 body 使用 heredoc。
- **读取 issue**：`gh issue view <number> --comments`，用 `jq` 过滤评论，并同时获取 label。
- **列出 issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，配合适当的 `--label` 和 `--state` 过滤器。
- **在 issue 上评论**：`gh issue comment <number> --body "..."`
- **添加 / 移除 label**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭**：`gh issue close <number> --comment "..."`

从 `git remote -v` 推断仓库；在 clone 内部运行时 `gh` 会自动完成这一操作。

## 将 Pull requests 作为 triage 请求面

**PRs as a request surface: no.** _（如果本仓库将外部 PR 视为 feature request，请改为 `yes`；`/triage` 会读取此标志。）_

设为 `yes` 时，PR 与 issue 一样经历相同的 label 和状态流转，使用对应的 `gh pr` 命令：

- **读取 PR**：`gh pr view <number> --comments`，diff 用 `gh pr diff <number>`。
- **列出待 triage 的外部 PR**：`gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`，然后只保留 `authorAssociation` 为 `CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR` 或 `NONE` 的 PR（丢弃 `OWNER`/`MEMBER`/`COLLABORATOR`）。
- **评论 / 打 label / 关闭**：`gh pr comment`、`gh pr edit --add-label`/`--remove-label`、`gh pr close`。

GitHub 的 issue 和 PR 共享同一编号空间，因此裸 `#42` 可能指其中任一：用 `gh pr view 42` 判定，失败则回退到 `gh issue view 42`。

## 当某个 skill 说“发布到 issue tracker”时

创建一个 GitHub issue。

## 当某个 skill 说“获取相关 ticket”时

运行 `gh issue view <number> --comments`。

## Wayfinding 操作

由 `/wayfinder` 使用。**map** 是一个单独的 issue，**child** issue 作为 ticket。

- **Map**：一个标记为 `wayfinder:map` 的单独 issue，承载 Notes / Decisions-so-far / Fog 正文。`gh issue create --label wayfinder:map`。
- **Child ticket**：作为 GitHub sub-issue 链接到 map 的 issue（在 sub-issues 端点用 `gh api`）。如果未启用 sub-issue，把 child 加入 map 正文的 task list，并在 child 正文顶部加上 `Part of #<map>`。label：`wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）。一旦认领，ticket 会分配给主导开发的开发者。
- **Blocking**：GitHub 的**原生 issue dependencies**，规范且 UI 可见的表示方式。用 `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>` 添加一条边，其中 `<blocker-db-id>` 是阻塞项的数值**数据库 id**（`gh api repos/<owner>/<repo>/issues/<n> --jq .id`，_不是_ `#number` 或 `node_id`）。GitHub 通过 `issue_dependencies_summary.blocked_by` 报告（仅开放中的阻塞项，即实时门控）。在 dependencies 不可用的情况下，回退到在 child 正文顶部写一行 `Blocked by: #<n>, #<n>`。当所有阻塞项都关闭时，ticket 解除阻塞。
- **Frontier query**：列出 map 开放中的 child（`gh issue list --state open`，限定到 map 的 sub-issues / task list），丢弃任何有开放中 blocker（`issue_dependencies_summary.blocked_by > 0`，或在 `Blocked by` 行有开放 issue）或有 assignee 的项；按 map 顺序排最前者获胜。
- **Claim**：`gh issue edit <n> --add-assignee @me`，本次会话的第一次写入。
- **Resolve**：`gh issue comment <n> --body "<answer>"`，然后 `gh issue close <n>`，再把 context 指针（gist + 链接）追加到 map 的 Decisions-so-far。
