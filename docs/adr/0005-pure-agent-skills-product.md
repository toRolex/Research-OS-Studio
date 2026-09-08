---
status: accepted
---

# 纯 Agent Skills 取代专用 Research OS runtime

Research OS Studio 以可由通用 Skills CLI 安装的自包含 Skills 为唯一产品形态，不再以 provider-neutral Core、typed contracts、统一 validators、Adapters、digest／receipt、Publication freeze 或 port database 约束研究工作。相比保留兼容 runtime 或并行维护 legacy，这一选择让成熟上游 Skill 正文和用户可读项目文件成为实际执行核心；代价是后续迁移必须删除旧实现与旧 CI，并由 Git 历史而非产品树保存旧架构。

## Consequences

- `docs/adr/0001`–`0004` 的旧架构决策被本 ADR 取代；它们保留为历史记录，实施不得继续据其增加 Core、Artifact、Publication 或 port gate。
- 来源与许可证仍需集中记录并保留必要 notices，但不转化为 hash 协议、认证数据库或运行时 blocker。
- 迁移只删除已提交且由对应 Ticket 拥有的旧资产；不得提前删除用户未提交内容。
