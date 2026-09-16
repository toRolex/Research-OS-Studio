# Composition Map

`experiment-bridge` 在一次授权内组合哪些内部能力、在哪一步、以何种产出贡献正文报告。被组合能力只在本次已确认的职责、写入范围和资源授权内工作；本映射不是自动调用链，不授予被组合能力之外的权限。

| 本 Workflow 阶段 | 组合的内部能力 | 贡献的正文报告章节 | 不做的事 |
|---|---|---|---|
| 实现、代码审查、sanity | [run-experiment](../../run-experiment/SKILL.md) | 实现范围、审查结果、sanity 状态、attempt 草稿 | 不改 hypothesis/metric/预算，不配置环境 |
| 大批量或多阶段作业 | [experiment-queue](../../experiment-queue/SKILL.md)（仅当某 milestone 声明 ≥10 作业、多 seed 网格或阶段依赖时；约 ≤5 作业留在 run-experiment 内；6–9 按并发上限、状态可见性和用户偏好决定） | 批次清单、波次状态、OOM/停滞处理、attempt 汇总 | 不引入常驻 scheduler，不自动扩预算 |
| 运行中观测 | [monitor-experiment](../../monitor-experiment/SKILL.md)（每次调用一次被动观测） | 运行事实（running/completed/crashed/unknown）与证据定位 | 不判 Claim，不触发分析，不停止或重启作业 |
| 训练健康诊断 | [training-health-check](../../training-health-check/SKILL.md)（有训练观测时） | 健康诊断与继续/停止调查/补观测建议 | 不停止或重启作业，不写研究结果 |
| 结果分析 | [analyze-results](../../analyze-results/SKILL.md)（已有完整结果后） | 描述统计、不确定性、选择偏差与多重比较检查 | 不补实验，不改代码，不启动下游 |
| 完整性审计 | [experiment-audit](../../experiment-audit/SKILL.md)（默认只输出发现） | protocol conformance 与独立完整性审查、发现分级 | 不修代码，不重跑实验 |

被组合能力不可用或超出本次授权时，在正文报告对应章节如实标注缺口并停止该分支，不伪造其输出，不以执行者摘要代替其直接读取。`result-to-claim`（#14）是独立 user-invoked 入口，本 Workflow 不启动它；需要判断能说什么时由用户另行显式调用。
