# experiment-bridge

旧的“实验桥接”请求映射到 `run-experiment` 的统一执行控制，不保留第二套授权核验、运行记账或执行状态机。`run-experiment` 交付运行事实后，本 playbook 可按当前委托组合 `analyze-results` 与 `experiment-audit`；二者仅贡献分析／审计章节，不新建独立 Workflow。用户只要运行时在运行报告后停止；明确要求分析与审计时再组合相应只读能力。所有能力继承同一委托与额度，实际合同以对应叶 Skill 与研究委托文档为准。

## 适用

已有计划或 tracker，用户要跑完并分析结果。只有计划还没写时，回到入口重匹配 experiment-plan。规模大不自动改去 improvement。

## 步骤

1. 读 `skills/validation-cycle/experiment-bridge/SKILL.md` 确认这是兼容入口，再读 `skills/validation-cycle/run-experiment/SKILL.md` 全文及 execution/remote references。执行控制、批次路由和报告以 run-experiment 为准。
2. 根据用户明确要求的范围调用执行、分析或审计能力。执行由 `run-experiment` 统一控制；它按 [批次授权](../references/batch-authorization.md) 核验工作区 `research-log.md`、准备项目依赖、记账及恢复。此 playbook 不重复检查授权字段、不另写 attempt 账本，也不为已授权的 milestone 再设审批门。
3. 运行交付后，只有本委托包含结果分析或完整性审计时，才组合调用 `analyze-results` / `experiment-audit`；它们各自负责只读结论和证据边界。把运行事实与科学结论分开报告。
4. 删除或覆盖既有实验结果、超出本批额度或执行范围的动作仍需用户决定；只阻塞对应动作。
5. 按被调用能力的合同交付并停止，不自动进入写作或延长授权有效期。
