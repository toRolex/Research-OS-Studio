---
name: experiment-bridge
description: 兼容入口：把旧的“实验桥接”请求指向 run-experiment 的统一执行控制；不重复编排、不授权、不执行。
disable-model-invocation: true
---

# Experiment Bridge（compatibility entry）

这是旧请求名的兼容入口。实验桥接的重复控制已合入 [run-experiment](../run-experiment/SKILL.md)：它拥有执行控制，可在同一运行批次内路由小批量或队列、组合观察/健康/收集。规划、批量队列、观察、健康诊断、统计分析和审计仍是独立能力。

Gates: none

## 委托继承

- 调用本入口时，立即按同一委托读取 run-experiment，不在此创建第二份授权、里程碑、报告或 tracker 更新。
- 本入口不再重复执行控制，不启动任何运行，不更新 tracker，不代写分析结论。
- 用户只要求规划时，指向 [experiment-plan](../experiment-plan/SKILL.md)；只要批次管理时，指向 [experiment-queue](../experiment-queue/SKILL.md)。

## 兼容映射

| 旧请求 | 现职责 |
| --- | --- |
| “按计划跑实验” | run-experiment 的执行控制与运行合同 |
| “跑完并分析” | run-experiment 交付运行事实后，由用户或委托显式选择 analyze-results / experiment-audit / result-to-claim |
| “实验桥接” | run-experiment；本名仅为兼容保留，不是第二控制器 |
