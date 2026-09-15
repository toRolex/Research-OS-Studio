# 组合映射

`research-improvement` 在一次授权内组合哪些内部能力、在哪一步、以何种产出贡献正文报告。被组合能力只在本次已确认的职责、写入范围和资源授权内工作；本映射不是自动调用链，不授予被组合能力之外的权限，也不改变第 1 节授权门。

| 本 Workflow 阶段 | 组合的内部能力 | 贡献的正文报告章节 | 不做的事 |
|---|---|---|---|
| 独立审查 | [paper-claim-audit](../../paper-claim-audit/SKILL.md) | 数字、比较、配置、表格/caption、实验覆盖的独立发现 | 不改稿，不替代引用/证明/论证审查 |
| 独立审查 | [citation-audit](../../citation-audit/SKILL.md) | 引用身份、元数据与语境支持的发现 | 不改 BibTeX 或正文 |
| 独立审查 | [claim-stress-test](../../claim-stress-test/SKILL.md) | 整篇拒稿论证与独立裁决 | 不替代数字/引用/证明专项审查，不作最终裁定 |
| 独立审查 | [proof-review](../../../validation-cycle/proof-review/SKILL.md) | 现成证明的义务、缺口、反例与影响范围 | 只读，不改证明、不编译 |
| 独立审查 | [experiment-audit](../../../validation-cycle/experiment-audit/SKILL.md) | protocol conformance 与独立真实性审查 | 不修代码，不重跑实验 |
| 独立审查 | [analyze-results](../../../validation-cycle/analyze-results/SKILL.md) | 描述统计、不确定性、选择偏差与多重比较 | 不补实验，不改代码 |
| 授权内补实验 | [run-experiment](../../../validation-cycle/run-experiment/SKILL.md) | 单次/少量运行的实现、sanity 与 attempt 记录 | 不改 hypothesis/metric/预算，不自动分析或转 Claim |
| 授权内补实验 | [experiment-queue](../../../validation-cycle/experiment-queue/SKILL.md) | 多作业批次、波次状态与失败留存 | 不引入常驻 scheduler，不自动扩预算 |
| 授权内补实验 | [monitor-experiment](../../../validation-cycle/monitor-experiment/SKILL.md) | running/completed/crashed/unknown 运行事实 | 不判 Claim，不触发分析，不停止或重启作业 |
| 授权内补实验 | [training-health-check](../../../validation-cycle/training-health-check/SKILL.md) | NaN/发散/OOM/停滞/日志完整性诊断 | 不停止或重启作业，不写研究结果 |
| 修复后验证 | [paper-compile](../../paper-compile/SKILL.md) | 真实 build/error、PDF 与格式发现 | check-only，不改源码，不自动启动修复 |

被组合能力不可用或超出本次授权时，在正文报告对应章节如实标注缺口并停止该分支，不伪造其输出，不以执行者摘要代替其直接读取。

## 本 Workflow 不启动的顶层入口

以下均为 user-invoked，只能由用户在另一轮显式调用；`research-improvement` 不自动启动、不代为授权、不据其名称暗示已执行：

- `experiment-bridge`、`experiment-plan`（完整实验计划与执行宏流程）
- `paper-writing`（完整写作总流程，当前为计划入口 #25）
- `paper-compile-repair`、`apply-citation-fixes`、`proof-repair`（专项修复入口）
- `result-to-claim`（计划 #14，尚未交付）、`rebuttal`、`resubmit-pipeline`、`paper-talk`
- `proof-orchestrator`、`setup-research-os`、`ask-research-os`

需要上述能力时，把精确问题、当前材料定位与建议范围交回用户，由用户另行点名。
