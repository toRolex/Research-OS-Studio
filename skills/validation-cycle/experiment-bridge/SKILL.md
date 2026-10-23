---
name: experiment-bridge
description: 兼容入口：把旧的“实验桥接”请求指向 run-experiment 的统一执行控制；不重复编排、不授权、不执行。
disable-model-invocation: true
---

# Experiment Bridge（compatibility entry）

这是旧请求名的兼容入口。实验桥接的重复控制已合入 `run-experiment`：它拥有执行控制，可在同一运行批次内路由小批量或队列、组合观察/健康/收集。规划、批量队列、观察、健康诊断、统计分析和审计仍是独立能力。

Gates: none

## 委托合同依赖

- 单装包随本叶携带 [委托合同分发摘录](references/mandate.md)，覆盖目标、权限、额度、完成/停止与验收的必需规则；完整规范的唯一权威仍是 `skills/general/research-os/references/mandate.md`。
- 分发摘录缺失、与完整规范冲突或本次动作超出摘录时，标为 `blocked` 并停止受影响动作；不得从开发仓库路径或其他叶推断授权。

## 联装能力依赖

- 本兼容入口必须能调用 `run-experiment`；联装能力缺失时标为 `blocked`，不开始相应分支。规划、队列、观察、健康诊断、统计分析与审计分别依赖 `experiment-plan`、`experiment-queue`、`monitor-experiment`、`training-health-check`、`analyze-results`、`experiment-audit`；未安装的分支不可当作已完成。
- 一次补齐本入口和所有被引用能力：`npx skills add <repo> -s research-os -s experiment-bridge -s run-experiment -s experiment-plan -s experiment-queue -s monitor-experiment -s training-health-check -s analyze-results -s experiment-audit -a claude-code -y`。

## 委托继承

- 调用本入口时，立即按同一委托读取 run-experiment，不在此创建第二份授权、里程碑、报告或 tracker 更新。
- 本入口不再重复执行控制，不启动任何运行，不更新 tracker，不代写分析结论。
- 用户只要求规划时，委托 `experiment-plan`；只要求批次管理时，委托 `experiment-queue`。仅安装本叶时，这些分支不可用；按“联装能力依赖”补装后再执行。
- 用户明确要求分析或审计时，执行报告后组合 `analyze-results` 和／或 `experiment-audit`，将它们的只读内容作为运行报告章节，不再创建第二份主报告。仅安装本叶时，这些分支不可用；按“联装能力依赖”补装后再执行。没有这项委托时，执行报告后停止。

## 兼容映射

| 旧请求 | 现职责 |
| --- | --- |
| “按计划跑实验” | run-experiment 的执行控制与运行合同 |
| “跑完并分析” | run-experiment 交付运行事实后，由用户或委托显式选择 analyze-results / experiment-audit / result-to-claim |
| “实验桥接” | run-experiment；本名仅为兼容保留，不是第二控制器 |
