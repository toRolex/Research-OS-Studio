# 迁移边界

本发行按批迁移到[研究委托合同](mandate.md)。**已迁移**能力遵循该合同；**未迁移**能力保留旧门声明并照旧可用。两批并存是设计，不是遗漏：不把整包说成已统一。

## 已迁移

| 能力 | 正文 | 委托落点 |
| --- | --- | --- |
| 委托入口 | `skills/general/research-os/SKILL.md` | 「研究委托」小节 + 本目录合同与 `playbooks/literature-review.md` |
| 文献综合 | `skills/idea-cycle/research-lit/SKILL.md` | 「委托继承」小节；无旧门，写入与预算由委托给 |
| 形式化检查创建 | `skills/validation-cycle/create-formal-verification-skill/SKILL.md` | 「委托继承」小节；项目内验证资产与依赖准备在授权内，缺子代理时独立复核标 blocked |
| 形式化检查维护 | `skills/validation-cycle/maintain-formal-verification-skill/SKILL.md` | 「委托继承」小节；只改验证不改产品代码，同步 commit 与假设版本随检查推进 |
| 实验计划 | `skills/validation-cycle/experiment-plan/SKILL.md` | 「委托继承」小节；只规划，未来预算不等于执行授权；对照按问题选，不硬套训练 baseline |
| 实验桥接兼容入口 | `skills/validation-cycle/experiment-bridge/SKILL.md` | 「委托继承」小节；旧名映射到 run-experiment，不再重复执行控制 |
| 实验执行 | `skills/validation-cycle/run-experiment/SKILL.md` | 「委托继承」小节；执行控制、批次路由、运行合同、断线恢复和远程执行位置合并在此 |
| 实验队列 | `skills/validation-cycle/experiment-queue/SKILL.md` | 「委托继承」小节；有界批次、依赖、有限重试、原作业查询与产物判定 |
| 实验观察 | `skills/validation-cycle/monitor-experiment/SKILL.md` | 「委托继承」小节；只读运行事实，不做作业控制或科学判断 |
| 训练健康诊断 | `skills/validation-cycle/training-health-check/SKILL.md` | 「委托继承」小节；只读诊断和建议，不控制作业 |
| 结果分析 | `skills/validation-cycle/analyze-results/SKILL.md` | 「委托继承」小节；统计可信度与偏差限制，不升级为 Claim |
| 实验审计 | `skills/validation-cycle/experiment-audit/SKILL.md` | 「委托继承」小节；只读完整性审计，分开作业退出、产物有效和科学结论 |
| 结果到 Claim | `skills/validation-cycle/result-to-claim/SKILL.md` | 「委托继承」小节；范围受限候选主张，采用由用户决定 |

迁移一个能力的完整动作：把正文改成继承委托（去掉旧 `Gate:`，写出该能力的边界与完成条件），在 `scripts/check-skills.py` 的 `MIGRATED_CONTRACT` 登记路径与小节名，把同一行加入本表，并从 `LEGACY_LEAF_GATES` 删除。

## 未迁移

其余叶 Skill 仍以 `Gate: <id> | before=… | approval=explicit-user | source=…` 声明自己的批准点；权威清单是 `scripts/check-skills.py` 的 `LEGACY_LEAF_GATES`，本文件不复制整表以免两份漂移。

由委托级联进入未迁移能力时，仍按该能力自己的门停下确认；这不撤销委托，处理完该点后同一委托继续。等该能力迁移，这个中途停点才消失。

## 迁移期间仍生效的完整性检查

迁移只改授权与停点语义，不放宽结构约束：门声明格式、来源锚点与追踪状态、frontmatter 与调用策略、共置资源与相对链接、README 清单与实际目录的一致性都继续检查。已迁移能力额外检查合同小节是否存在，因此删门不会连职责约束一起丢。

## 参考

- 合同正文：[mandate.md](mandate.md)
- 委托额度与运行批次：[batch-authorization.md](batch-authorization.md)
- 完整链路示例：[literature-review](../playbooks/literature-review.md)
