# 实验能力组合图

`run-experiment` 是唯一执行控制：负责已授权范围内的实现、执行路由、作业记账、恢复与初步结果报告。它不取代其他职责，不自动启动下列能力；按当前委托选择需要的分支。

| 需要的职责 | 独立 Skill | 边界与缺失处理 |
|---|---|---|
| 把问题写成有界计划 | `experiment-plan` | 只规划，不启动运行；需要规划而未安装时该分支 `blocked`。 |
| 管理大批量、网格或阶段依赖 | `experiment-queue` | 只管理批次，不重置 `run-experiment` 的授权；批量路由需要但未安装时该分支 `blocked`，独立小批次不受影响。 |
| 观察运行状态 | `monitor-experiment` | 记录运行事实，不控制作业或作科学判断；用户要求观察而未安装时该分支 `blocked`。 |
| 诊断训练健康 | `training-health-check` | 只诊断并建议，不自行 kill、重启或迁移；用户要求诊断而未安装时该分支 `blocked`。 |
| 统计分析与不确定性 | `analyze-results` | 独立分析全部 attempts、选择偏差与多重比较；用户要求分析而未安装时该分支 `blocked`。 |
| 独立完整性审计 | `experiment-audit` | 独立审查 protocol、代码与原始结果，不代替执行者自审；用户要求审计而未安装时该分支 `blocked`。 |
| 判断证据能支持的 Claim | `result-to-claim` | 与执行、产物有效性和统计分析分开；用户要求 Claim 判断而未安装时该分支 `blocked`。 |

被选中的每个分支沿用同一委托与适用额度；未安装的能力只阻塞其自身职责，不把缺失说成已完成。`experiment-bridge` 只作为用户表达需求时 `/research-os` 配方的历史称呼，不是可安装或可调用的 Skill。
