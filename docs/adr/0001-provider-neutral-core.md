# ADR-0001：用户控制的 provider-neutral Research OS Core

- 状态：已接受
- 日期：2026-09-04
- 范围：Research OS P0 总体边界

## 决策

Research OS Core 使用 provider-neutral 的 Agent Skills、typed file Artifact handoff 和确定性 validators。workflow 只能由用户显式调用，discipline 只能在当前 workflow 内由模型调用；workflow 完成后写结果、保留失败、列出下一步并停止。Adapter 只负责平台投影、能力探测、调用映射和阻止，不复制研究语义。

用户拥有研究语义、目标、评价标准、预算和 workflow 间推进权。Core 不保存全局 phase，不提供中央 planner、自动科研 runtime、默认自动继续或无界循环。

## 原因

现有参考系统的主要风险是自动跨阶段推进、provider 绑定和将模型判断冒充验证。薄 Core 能在不同宿主复用，并让平台差异不改变研究契约。

## 后果

- 平台无法表达必要隔离时必须返回结构化 `BLOCKED`，不能静默降级。
- 运行时自动化只能发生在当前 user-invoked workflow 的明确预算内。
- 删除 Adapter 后，Core 仍应可阅读、验证和手工执行。
- 跨 workflow 只能通过固定 Artifact 发生。

## 证据

`CONTEXT.md`、`PRODUCT.md`、`planning/research-os-wayfinder/resolutions/D01.md`、`planning/research-os-wayfinder/resolutions/D04.md`，以及 `docs/research/sources/comparison.md` 的参考系统对比。
