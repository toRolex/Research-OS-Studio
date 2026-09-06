---
id: research-os-architecture-map
title: 规划用户控制型 Research OS 终态与 P0 路线
label: wayfinder:map
tracker: local-markdown
---

## Destination

形成一份无重大未决架构问题、可直接交给实现阶段的 Research OS P0 spec：公开、符合通用 Agent Skills 格式，由人掌握 workflow 间推进权；使用薄 Research Core、typed file artifacts、可组合 workflow/discipline，正式覆盖 AI/ML 计算实验、数学证明/Lean 与 Publication，并通过逐项移植社区最佳资产实现，而非重写成熟能力或接入自动科研 runtime。

## Notes

- 本 map 只解决决策并产出最终 implementation spec，不执行 Research OS 实现。
- 每次 Wayfinder 会话最多 claim 并解决一个开放 ticket。
- 用 ticket 名称引用决策，不用裸编号代替名称。
- 循环是 workflow 组织视图，不是中央 planner、scheduler 或项目全局 phase 状态机。
- 社区资产遵循 port-first / minimal adaptation，并保存来源、commit 与许可证。
- 历史必读清单原指向 `analysis/` 工作树材料；仓库内稳定归档现见 `docs/research/sources/README.md`。
- `tracker.json` 仅是当时 local tracker 的关系快照；当前规划状态以 GitHub Issues 及其原生关系为准。

## Decisions so far

- [锁定 Research OS 产品与控制边界](tickets/D01.md)：公开通用 skills 仓库；人控制 workflow 间推进，agent 只拥有当前 workflow 内执行权。
- [锁定跨学科能力与项目形态](tickets/D02.md)：项目可混合计算实验、数学证明、Lean 和发布能力，并可产生多个 Publication。
- [锁定 Artifact 与验证原则](tickets/D03.md)：重要 artifact 有稳定身份、来源和 typed relations；验证采用多轴 assurance。
- [锁定社区资产移植策略](tickets/D04.md)：逐项复制成熟资产并最小改造，不 fork 自动 runtime，不凭感觉重写。
- [完成参考系统与官方数学原型审计](tickets/D05.md)：六仓调研及 Anthropic/OpenAI 数学工作流已提供决策依据。
- [确定数学证明与 Lean 内循环 workflow 边界](tickets/T10.md)：采用细粒度、用户显式调用的数学 workflow；反例、失败尝试和陈述修订均版本化保留，只有带完整环境与 axiom/sorry 记录的 kernel verification 才支持形式证明 claim。

## Not yet specified

- P0 之后，多项目全局索引、跨项目 artifact 查询与可选图数据库投影。
- Systematic review、dataset/benchmark、position/conceptual 的完整专用 Publication Adapter。
- 多人协作、并发修改、权限和远程团队工作区。
- SSH/SLURM 之外的云 GPU、实验平台和 proof service Adapter。
- 公开生态的长期 benchmark、compatibility matrix、release cadence 与社区贡献治理。

## Out of scope

- Central planner、自动阶段推进、默认 `AUTO_PROCEED`、无界 `/loop` 或 agent 自行宣布研究完成。
- 在本 map 中实际创建 Research OS skills、运行真实科研项目、提交论文或执行 GPU/Lean 研究。
- P0 建设 graph database、SaaS dashboard、通用 scheduler 或完整多用户平台。
- 首个版本内置所有科学学科的领域 workflow。
