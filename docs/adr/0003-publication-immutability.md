# ADR-0003：Publication 是不可覆盖的用户确认投影

- 状态：已接受
- 日期：2026-09-04
- 范围：Publication Core 与发布门

## 决策

Publication 只能在用户显式调用并确认后创建。它是封闭、版本化的发布投影，必须固定唯一主要公开文本、成员及用途、Project、贡献、重要 Claim、支持 Evidence、条件、限制、材料 revision/hash、外部引用 retrieval receipts 和纳入的 Assurance Assessment。

冻结后不得覆盖。替代、撤回、提醒和 stale audit 结果以包外追加记录表达；同一 Project 可以创建第二份独立 Publication。必需成员、依赖、外部 receipt 或 gate 无法固定时，validator 返回 hard block。

## 原因

发布记录需要保持长期可追溯。允许上游更新直接改变已发布内容，会破坏历史复现并掩盖证据漂移。技术 validator 也不能代替用户的人类接受。

## 后果

- Publication validator 必须检查成员封闭性、主要文本唯一性、固定 target/hash、引用 receipt 和 gate 状态。
- 外部来源失联时保留 digest、receipt、日志和最小合法证据，禁止静默换源。
- stale 或替代记录不修改原 Publication。

## 证据

`CONTEXT.md`、`PRODUCT.md`、Issue #24/#23 的 P0 Implementation Spec，以及已验证的 Project/Workstream/Publication 原型提交 `6c24ac721af4ccdbc8c57eb980abe006477d477a`。
