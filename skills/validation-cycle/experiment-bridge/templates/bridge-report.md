# Experiment Bridge 报告

这是 [Experiment Bridge](../SKILL.md) 的自然 Markdown 报告骨架，不是机器 schema。按实际读到的原始材料填写；无法定位的项写 `unknown`，不要省略。被组合能力贡献对应章节，不另建重复主报告。

**Plan / Proposal**：[实际读取的路径]
**Problem Anchor**：[一句话]
**Run mode**：dry-run / real（选择实际模式）
**Authorization**：[本次确认覆盖的目标、写入清单、资源上限、执行模式、停止条件；未确认项]
**Budget used**：[实际消耗 vs 批准上限]

## 实现与代码审查

- 实现范围（可改/不可改 · 复用代码位置 · 新增脚本位置）：
- Evaluator 与 ground truth（脚本位置 · 真值来源 · 是否对所有系统一致）：
- 审查结果与修复历史（含独立审查是否执行）：
- 缺口（未实现项 · 文件/功能/原因）：

## 执行与 Attempts

| Milestone | Planned runs | Executed | Status | Notes |
|---|---|---|---|---|
| sanity | | | | |
| baseline | | | | |
| main method | | | | |
| ablations | | | | |
| polish | | | | |

| Run ID | Milestone | System/Variant | Split | Seed | Metric | Status | Raw result | Failure reason |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

Status 取值：`completed` / `failed` / `invalid` / `timeout` / `oom` / `cancelled` / `not-run`。

- Baseline vs attempts（含失败/无效/超时并列）：
- 批量路由（单次执行 / 交 experiment-queue 的 milestone 与理由；6–9 作业的决策依据）：
- 失败恢复（每次尝试 · 错误定位 · 修复与代价 · 重新确认）：

## 监控与健康

- 运行事实（running/completed/crashed/unknown · 证据定位 · 观测时间）：
- 训练健康（诊断结论 · 证据窗口 · 建议；未观测项标缺口）：
- 未观测/缺失表面及其限制：

## 分析

- 描述统计（数值 · 原始定位 · 事实分级）：
- 不确定性（seeds/runs 数 · spread · 敏感子集）：
- 选择偏差与多重比较（分母 · 排除项与理由）：
- Claim 支持边界（观察陈述；排名或单 metric winner 不构成结论）：

## 审计

- Protocol conformance（逐项结论与定位）：
- Independent integrity（A–F、attempt、代码/结果对应的结论与定位）：
- 发现（严重级别 · 材料定位 · 保守结论 · 需另行授权的最小补救）：
- 整体判定：PASS / FAIL / BLOCKED（含缺失材料的 BLOCKED）：

## Tracker 更新

- Tracker 路径与写入授权：
- 已更新的状态、结果位置、失败原因与资源事实：
- 写前冲突检查（无冲突 / 差异已确认 / 外部变化后重新确认）：

## 可选消融建议（仅建议，不执行）

- 建议的消融对照（组件 · 对照设计 · 判别性观察 · 估计资源与停止条件）：
- 跳过理由（主结果负向/不确定时填写）：

## Resources, Side Effects, Cleanup

- Compute / storage / wall time：
- Paid / remote actions：
- Cleanup：[已停止的资源；未能清理的原因]

## Not Executed / Gaps / Next Options

- Nice-to-have not run：
- Unresolved gaps / blockers：
- 未启动的 Workflow（result-to-claim / Writing / 下一轮均未启动）：
- User options：[接受 / 修改计划 / 补实验 / 补分析审计 / 停止]

> 本报告只记录事实、分析与审计发现。统计结论不替代 Claim 判断；Claim 是否成立由证据、独立审查和用户判断约束。消融建议不自动执行。
