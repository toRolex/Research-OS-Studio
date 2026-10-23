# 迁移边界

本发行按批迁移到[研究委托合同](mandate.md)。**已迁移**能力遵循该合同；**未迁移**能力保留旧门声明并照旧可用。两批并存是设计，不是遗漏：不把整包说成已统一。

## 已迁移

| 能力 | 正文 | 委托落点 |
| --- | --- | --- |
| 委托入口 | `skills/general/research-os/SKILL.md` | 「研究委托」小节 + 本目录合同与 `playbooks/literature-review.md` |
| 文献综合 | `skills/idea-cycle/research-lit/SKILL.md` | 「委托继承」小节；无旧门，写入与预算由委托给 |
| 候选比较（arena） | `skills/organization/arena/SKILL.md` | 「委托继承」小节；无旧门，子代理缺失时该阶段标 blocked |
| 并行覆盖（swarm） | `skills/general/swarm/SKILL.md` | 「委托继承」小节；新增能力，非旧门迁移，改编自 pstack swarm（MIT，LICENSE 随目录共置） |
| 对抗审查 | `skills/general/interrogate/SKILL.md` | 「委托继承」小节；无旧门，始终只读，修复由委托按授权另行组织 |
| 形式化检查创建 | `skills/validation-cycle/create-formal-verification-skill/SKILL.md` | 「委托继承」小节；项目内验证资产与依赖准备在授权内，缺子代理时独立复核标 blocked |
| 形式化检查维护 | `skills/validation-cycle/maintain-formal-verification-skill/SKILL.md` | 「委托继承」小节；只改验证不改产品代码，同步 commit 与假设版本随检查推进 |
| 持续推进、暂停恢复与改进 | `skills/general/research-os/playbooks/continuation.md`；`skills/writing-cycle/research-improvement/SKILL.md` | 入口明确路由；恢复核对原始产物、开放义务与活跃作业；改进继承委托，批次与公共行为修改保留决定门 |
| 行为验证创建 | `skills/validation-cycle/create-verification-skill/SKILL.md` | 「委托继承」小节；项目内启动、驱动与验证资产在授权内，缺子代理时源读/复核标 blocked |
| 行为验证维护 | `skills/validation-cycle/maintain-verification-skill/SKILL.md` | 「委托继承」小节；只改验证 skill 自身目录，现场驱动与证据清理随轮次推进 |
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
| 统一写作 | `skills/writing-cycle/paper-writing/SKILL.md` | 「委托继承」小节；ML/Systems 标准按需引用，委托内编译与引用修复继承授权，不自动投稿 |
| 论文规划 | `skills/writing-cycle/paper-plan/SKILL.md` | 「委托继承」小节；写入与报告路径由委托覆盖 |
| 论文起草 | `skills/writing-cycle/paper-drafting/SKILL.md` | 「委托继承」小节；证据缺口在授权内处理且不捏造 |
| 编译检查 | `skills/writing-cycle/paper-compile/SKILL.md` | 「委托继承」小节；只读检查，授权内修复由 repair 承接 |
| 编译修复 | `skills/writing-cycle/paper-compile-repair/SKILL.md` | 「委托继承」小节；精确 diff 不绕过，独立调用按其边界授权，委托内已授权时继承 |
| 引用审查 | `skills/writing-cycle/citation-audit/SKILL.md` | 「委托继承」小节；保持只读，修复由 apply 承接 |
| 引用修复 | `skills/writing-cycle/apply-citation-fixes/SKILL.md` | 「委托继承」小节；精确 diff 不绕过，独立调用按其边界授权，委托内已授权时继承 |
| 主张审计 | `skills/writing-cycle/paper-claim-audit/SKILL.md` | 「委托继承」小节；保持只读并如实标缺口 |
| 拒稿攻击 | `skills/writing-cycle/claim-stress-test/SKILL.md` | 「委托继承」小节；保持只读并如实标缺口 |
| ML 写作兼容层 | `skills/writing-cycle/ml-paper-writing/SKILL.md` | 「委托继承」小节；保留旧平行入口，新委托优先统一入口 |
| Systems 写作兼容层 | `skills/writing-cycle/systems-paper-writing/SKILL.md` | 「委托继承」小节；保留旧平行入口，新委托优先统一入口 |
| 审稿回复 | `skills/writing-cycle/rebuttal/SKILL.md` | 「委托继承」小节；不自动投稿或扩大任务 |
| 转投适配 | `skills/writing-cycle/resubmit-pipeline/SKILL.md` | 「委托继承」小节；旧稿只读，不自动投稿 |
| 会议演讲 | `skills/writing-cycle/paper-talk/SKILL.md` | 「委托继承」小节；只准备材料，不自动发布 |
## 未迁移

其余叶 Skill 仍以 `Gate: <id> | before=… | approval=explicit-user | source=…` 声明自己的批准点；权威清单是 `scripts/check-skills.py` 的 `LEGACY_LEAF_GATES`，本文件不复制整表以免两份漂移。

由委托级联进入未迁移能力时，仍按该能力自己的门停下确认；这不撤销委托，处理完该点后同一委托继续。等该能力迁移，这个中途停点才消失。

## 迁移期间仍生效的完整性检查

迁移只改授权与停点语义，不放宽结构约束：门声明格式、来源锚点与追踪状态、frontmatter 与调用策略、共置资源与相对链接、README 清单与实际目录的一致性都继续检查。已迁移能力额外检查合同小节是否存在，因此删门不会连职责约束一起丢。

## 参考

- 合同正文：[mandate.md](mandate.md)
- 委托额度与运行批次：[batch-authorization.md](batch-authorization.md)
- 完整链路示例：[literature-review](../playbooks/literature-review.md)
