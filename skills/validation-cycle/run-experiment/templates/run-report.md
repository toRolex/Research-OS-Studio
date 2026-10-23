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

| Run ID | 输入版本 | 工具链 | 独立目录 | 作业身份 | Milestone | System/Variant | Split | Seed | Metric | 退出码 | 原始日志 | 产物 | Status | Artifact validity | Scientific conclusion | Failure reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | | | | | |

`Scientific conclusion` only records `not-judged / supported / needs-narrowing / unsupported / invalid / unknown` assigned later by analysis, audit or Results-to-Claims; `run-experiment` never upgrades 产物有效 to 科学结论.

Status 取值：`completed` / `failed` / `invalid` / `timeout` / `oom` / `cancelled` / `not-run`。

## Plan-declared comparison vs Attempts

- Comparison：[计划声明的 baseline / control / certificate replay，配置、原始结果位置、状态]
- All attempts：[与 baseline 并列的完整列表]
- Failures / invalid / timeout：[逐项原因与日志位置]

## Evaluation Surface

- Evaluator：[脚本/协议位置与版本]
- Ground truth：[真实标签来源；是否对所有系统一致]
- Data coverage / split：[实际使用的数据范围]
- Review limits：[独立代码审查是否执行；未执行的原因]

## Implementation and Code Review

- 实现范围：[允许／禁止修改的路径 · 复用代码 · 新增脚本]
- Evaluator 与 ground truth：[定义位置 · 真值来源 · 是否对各系统一致]
- Review result and repair history：[审查是否执行 · 发现 · 修复与剩余缺口]
- Not implemented：[文件／功能 · 原因]

## Success Criteria Check

| Criterion | Planned bar | Observed fact | Met? | Raw evidence |
|---|---|---|---|---|
| | | | | |

只做事实对照；阈值命中不等于 Claim 已证明。

## Monitoring and Health (if requested)

- Observation facts：[running / completed / crashed / unknown · 原始证据 · 时间]
- Health diagnosis：[由 `training-health-check` 提供的结论与建议；未调用时标为 not requested]
- Unobserved surfaces：[未观察项及其限制]

## Recovery

- Disconnection / interruption：[先按本次作业身份查询原任务、调度器状态、远端日志和退出码；不要盲目重跑]
- Retry basis：[原失败证据 · 经授权的最小修复 · 同一批次仍可用的 attempt 名额]

## Analysis and Independent Audit (separate capabilities only)

- Analysis：[仅引用 `analyze-results` 的只读产物；未调用时标为 not requested]
- Audit：[仅引用 `experiment-audit` 的独立产物；未调用时标为 not requested]
- Findings：[级别 · 原始材料定位 · 保守结论 · 需另行授权的最小补救]
- These sections record companion results; `run-experiment` does not perform or replace analysis, audit, or Claim judgment.

## Tracker Update

- Tracker path and write authorization：[路径 · 授权依据]
- Updated facts：[状态 · 结果位置 · 失败原因 · 资源事实]
- Pre-write conflict check：[no conflict / confirmed diff / re-confirmed after external change]

## Optional Ablation Suggestions (advice only)

- Suggested comparison：[component · design · discriminating observation · estimated resources · stop condition]
- Skip rationale：[主结果负向／不确定时填写]

## Resources, Side Effects, Cleanup

- Compute / storage / wall time：
- Paid / remote actions：
- Cleanup：[已停止的资源；未能清理的原因]

## Not Executed / Gaps / Next Options

- Nice-to-have not run：
- Unresolved gaps / blockers：
- Unstarted workflows：[result-to-claim / writing / next run remain unstarted unless separately requested]
- User options：[接受 / 修改计划 / 另行分析·审计 / 停止]

> 本报告只包含事实与可核对的派生数值。统计可信度、选择偏差与 Claim 范围判断属于独立分析、审计与 Results-to-Claims 能力，不由 run-experiment 代做。
