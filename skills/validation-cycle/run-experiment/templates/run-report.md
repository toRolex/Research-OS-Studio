# Run Experiment 报告

**Plan / Proposal**：[实际读取的路径]
**Problem Anchor**：[一句话]
**Run mode**：dry-run / real（选择实际模式）
**Authorization**：[本次确认覆盖的命令、资源与副作用；未确认项]
**Budget used**：[实际消耗 vs 批准上限]

## Milestones

| Milestone | Planned runs | Executed | Status | Notes |
|---|---|---|---|---|
| sanity | | | | |
| baseline | | | | |
| main method | | | | |
| ablations | | | | |
| polish | | | | |

## Attempts

每次 attempt 一行；成功、失败、无效、超时、取消、未执行都保留。

| Run ID | Milestone | System/Variant | Split | Seed | Metric | Status | Raw result | Failure reason |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

Status 取值：`completed` / `failed` / `invalid` / `timeout` / `oom` / `cancelled` / `not-run`。

## Baseline vs Attempts

- Baseline：[配置、原始结果位置、状态]
- All attempts：[与 baseline 并列的完整列表]
- Failures / invalid / timeout：[逐项原因与日志位置]

## Evaluation Surface

- Evaluator：[脚本/协议位置与版本]
- Ground truth：[真实标签来源；是否对所有系统一致]
- Data coverage / split：[实际使用的数据范围]
- Review limits：[独立代码审查是否执行；未执行的原因]

## Success Criteria Check

| Criterion | Planned bar | Observed fact | Met? | Raw evidence |
|---|---|---|---|---|
| | | | | |

只做事实对照；阈值命中不等于 Claim 已证明。

## Resources, Side Effects, Cleanup

- Compute / storage / wall time：
- Paid / remote actions：
- Cleanup：[已停止的资源；未能清理的原因]

## Not Executed / Gaps / Next Options

- Nice-to-have not run：
- Unresolved gaps / blockers：
- User options：[接受 / 修改计划 / 另行分析·审计 / 停止]

> 本报告只包含事实与可核对的派生数值。统计可信度、选择偏差与 Claim 范围判断属于分析、统计检查与 Results-to-Claims，不由 run-experiment 代做。
