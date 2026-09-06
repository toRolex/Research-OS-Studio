# Issue #25 实施记录：治理与契约基线

## 目标

建立 Research OS P0 的实现基线：统一 GitHub Issue 与旧 Wayfinder 快照的真源关系，恢复并固定分析材料与历史原型证据，固化领域术语、架构约束及社区能力 port 的准入硬门。

## 已有现场核对

- 保留中断前的 T10 改动：`planning/research-os-wayfinder/MAP.md`、`implementation-notes.md`、`tickets/T10.md`、`tracker.json` 与 `resolutions/T10.md`。
- T10 的 `blocked_by: [T07]` 与 `status: closed` 属历史 Wayfinder 快照状态，T07 在本地仍 open，存在状态矛盾；Issue #25 不重新裁决 T10，因此在归档说明中明确：GitHub Issues 是当前规划/状态真源，本地 tracker/MAP/tickets 只作历史快照，不将该快照作为当前 frontier 或阻塞依据。
- 两个原型提交已验证可达：`3428eb72aa31ed532a036909e857e768441c0bcb` 的 `prototypes/artifact-min-contract-prototype.html`；`6c24ac721af4ccdbc8c57eb980abe006477d477a` 的 `minimal-project-workstream-publication-prototype.html`。两者仅作为契约决策先例，不作为生产运行 seam。

## 决策

- 证据文件采用原工作树已有 `analysis/` 材料；已将四份被引用报告归档至 `docs/research/sources/`，记录原始路径、报告审计所用上游完整 revision 与 SHA-256 digest。
- 根 `CONTEXT.md` 与 `docs/adr/` 作为单上下文领域真源；Glossary 固定 Project、Workstream、Artifact、Claim、Evidence、Assessment、Publication、workflow、discipline、validator、Adapter、port、target 的规范含义。
- Issue #25 的治理基线不引入运行时、全局状态机或自动推进；validator 结果使用结构化报告和稳定退出码，来源/许可证证据缺失为 hard block。

## Deviations

- 计划中的分析材料只存在于原主工作树，Issue worktree 初始不包含它们；已从该固定本地来源逐字节归档四份报告到 `docs/research/sources/`，核对 digest，并补记报告审计所用上游完整 revision。
- 不把 T07 自动改为 closed 来消除快照矛盾：这会改写历史规划决策，且超出 Issue #25 的治理基线范围；改为在 domain/ADR 归档中显式标记快照优先级和矛盾处理规则。

## 验证

- 验证两个原型的完整 commit、路径与对象类型。
- 验证分析材料逐份来源、revision 与 digest。
- 运行 Markdown/JSON/YAML 结构检查、链接检查及 Git diff --check。
- 确认 `git diff main..HEAD` 仅包含 Issue #25 所需基线文件。
