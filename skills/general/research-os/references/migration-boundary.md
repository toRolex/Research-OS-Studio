# 迁移边界

本页记录 Research OS 路由能力的委托继承登记与边界资源。已登记的委托能力遵循[研究委托合同](mandate.md)；独立只读的 `proof-review` 不继承委托写权限。不要再把当前套件描述成“新旧两批旧门并行”，也不要把 `proof-review` 误写成委托级联叶。

## 委托继承能力与相关资源

| 能力 | 正文 | 委托落点 |
| --- | --- | --- |
| 委托入口 | `skills/general/research-os/SKILL.md` | 「研究委托」小节 + 本目录合同与 `playbooks/literature-review.md` |
| 数学研究证明配方 | `skills/general/research-os/playbooks/proof.md` | #55/#60 唯一证明总控；按证据交替使用独立能力，不设固定阶段；proof-orchestrator 控制器已删除，原数学方法与交接资源归 proof-review 随包按需读取；缺少某 slug 只阻塞其依赖分支 |
| 认知转换 | `skills/idea-cycle/creative-thinking-for-research/SKILL.md` | 「委托继承」小节；只贡献洞见，不裁决候选池 |
| Discovery 配方 | `skills/general/research-os/playbooks/discovery.md` | `research-os` 唯一入口内的完整方向→Proposal 用户目标；按缺口组合 Required 能力子集，支持重排/回访与分支阻塞；fresh 独立评审不退化为自查 |
| 候选生成 | `skills/idea-cycle/idea-generation/SKILL.md` | 「委托继承」小节；多视角、去重与硬约束筛选 |
| 候选细化 | `skills/idea-cycle/idea-refinement/SKILL.md` | 「委托继承」小节；保留 Problem Anchor，目标替换仍停 |
| 独立评审 | `skills/idea-cycle/idea-review/SKILL.md` | 「委托继承」小节；评审者直达原始材料 |
| 查新 | `skills/idea-cycle/novelty-check/SKILL.md` | 「委托继承」小节；closest prior work 与证据缺口 |
| 文献综合 | `skills/idea-cycle/research-lit/SKILL.md` | 「委托继承」小节；无旧门，写入与预算由委托给 |
| 候选比较（arena） | `skills/organization/arena/SKILL.md` | 「委托继承」小节；无旧门，子代理缺失时该阶段标 blocked |
| 并行覆盖（swarm） | `skills/general/swarm/SKILL.md` | 「委托继承」小节；新增能力，非旧门迁移，改编自 pstack swarm（MIT，LICENSE 随目录共置） |
| 对抗审查 | `skills/general/interrogate/SKILL.md` | 「委托继承」小节；无旧门，始终只读，修复由委托按授权另行组织 |
| 学术绘图 | `skills/writing-cycle/academic-plotting/SKILL.md` | 「委托继承」小节；数据图与示意图，外部副作用仍授权 |
| 形式化检查创建 | `skills/validation-cycle/create-formal-verification-skill/SKILL.md` | 「委托继承」小节；项目内验证资产与依赖准备在授权内，缺子代理时独立复核标 blocked |
| 形式化检查维护 | `skills/validation-cycle/maintain-formal-verification-skill/SKILL.md` | 「委托继承」小节；只改验证不改产品代码，同步 commit 与假设版本随检查推进 |
| 持续推进、暂停恢复与改进 | `skills/general/research-os/playbooks/continuation.md`；`skills/writing-cycle/research-improvement/SKILL.md` | 入口明确路由；恢复核对原始产物、开放义务与活跃作业；改进继承委托，批次与公共行为修改保留决定门 |
| 行为验证创建 | `skills/validation-cycle/create-verification-skill/SKILL.md` | 「委托继承」小节；项目内启动、驱动与验证资产在授权内，缺子代理时源读/复核标 blocked |
| 行为验证维护 | `skills/validation-cycle/maintain-verification-skill/SKILL.md` | 「委托继承」小节；只改验证 skill 自身目录，现场驱动与证据清理随轮次推进 |
| 实验计划 | `skills/validation-cycle/experiment-plan/SKILL.md` | 「委托继承」小节；只规划，未来预算不等于执行授权；对照按问题选，不硬套训练 baseline |
| 实验执行 | `skills/validation-cycle/run-experiment/SKILL.md` | 「委托继承」小节；唯一执行控制、批次路由、运行合同、断线恢复和远程执行位置合并在此；Research OS 的“实验桥接”仅为需求配方名 |
| 实验队列 | `skills/validation-cycle/experiment-queue/SKILL.md` | 「委托继承」小节；有界批次、依赖、有限重试、原作业查询与产物判定 |
| 实验观察 | `skills/validation-cycle/monitor-experiment/SKILL.md` | 「委托继承」小节；只读运行事实，不做作业控制或科学判断 |
| 训练健康诊断 | `skills/validation-cycle/training-health-check/SKILL.md` | 「委托继承」小节；只读诊断和建议，不控制作业 |
| 结果分析 | `skills/validation-cycle/analyze-results/SKILL.md` | 「委托继承」小节；统计可信度与偏差限制，不升级为 Claim |
| 实验审计 | `skills/validation-cycle/experiment-audit/SKILL.md` | 「委托继承」小节；只读完整性审计，分开作业退出、产物有效和科学结论 |
| 结果到 Claim | `skills/validation-cycle/result-to-claim/SKILL.md` | 「委托继承」小节；范围受限候选主张，采用由用户决定 |
| 数学公式推导 | `skills/validation-cycle/formula-derivation/SKILL.md` | 「委托继承」小节；委托写域内可建新文件，原对象/假设变化须用户确认；推导不自动变成证明 |
| 证明构造 | `skills/validation-cycle/proof-writer/SKILL.md` | 「委托继承」小节；保留原命题、假设、失败路线和有限尝试；不自动进入审查或修复 |
| 证明修复 | `skills/validation-cycle/proof-repair/SKILL.md` | 「委托继承」小节；修复限于 finding 和委托写域，命题/假设变化仍需决定，编译命令及副产物范围单独核对 |
| Proof 审计/数学方法资源 | `skills/validation-cycle/proof-review/SKILL.md` 与其 `references/` | 旧控制器已删除；审计、独立意见、压力测试、记号、Lean、提示/交接模板与 EtaSkill NOTICE 随 proof-review 包共置，按审查分支披露 |
| 统一写作 | `skills/writing-cycle/paper-writing/SKILL.md` | 「委托继承」小节；ML/Systems 标准按需引用，委托内编译与引用修复继承授权，不自动投稿 |
| 论文规划 | `skills/writing-cycle/paper-plan/SKILL.md` | 「委托继承」小节；写入与报告路径由委托覆盖 |
| 论文起草 | `skills/writing-cycle/paper-drafting/SKILL.md` | 「委托继承」小节；证据缺口在授权内处理且不捏造 |
| 编译检查 | `skills/writing-cycle/paper-compile/SKILL.md` | 「委托继承」小节；只读检查，授权内修复由 repair 承接 |
| 编译修复 | `skills/writing-cycle/paper-compile-repair/SKILL.md` | 「委托继承」小节；精确 diff 不绕过，独立调用按其边界授权，委托内已授权时继承 |
| 引用审查 | `skills/writing-cycle/citation-audit/SKILL.md` | 「委托继承」小节；保持只读，修复由 apply 承接 |
| 引用修复 | `skills/writing-cycle/apply-citation-fixes/SKILL.md` | 「委托继承」小节；精确 diff 不绕过，独立调用按其边界授权，委托内已授权时继承 |
| 主张审计 | `skills/writing-cycle/paper-claim-audit/SKILL.md` | 「委托继承」小节；保持只读并如实标缺口 |
| 拒稿攻击 | `skills/writing-cycle/claim-stress-test/SKILL.md` | 「委托继承」小节；保持只读并如实标缺口 |
| 审稿回复 | `skills/writing-cycle/rebuttal/SKILL.md` | 「委托继承」小节；不自动投稿或扩大任务 |
| 转投适配 | `skills/writing-cycle/resubmit-pipeline/SKILL.md` | 「委托继承」小节；旧稿只读，不自动投稿 |
| 会议演讲 | `skills/writing-cycle/paper-talk/SKILL.md` | 「委托继承」小节；只准备材料，不自动发布 |

将能力纳入委托继承登记时：把正文改为继承委托（移除不再适用的旧 `Gate:`，写清该能力的边界与完成条件），在 `scripts/check-skills.py` 的 `MIGRATED_CONTRACT` 登记路径与小节名，并在本表记录同一能力。不能为满足迁移表而给独立只读能力虚构旧门或委托继承关系。

## 未迁移

本节说明不纳入 Research OS 委托继承登记的独立能力，不表示仍有一批旧批准门与委托合同并行。

| 能力 | 正文 | 边界 |
| --- | --- | --- |
| 证明审查 | `skills/validation-cycle/proof-review/SKILL.md` | 独立 fresh 只读返回 findings；正文显式 `Gates: none`；不继承调用者的写权限，也不修改证明或替代修复授权。所需方法、交接模板、许可证与 NOTICE 随包共置，按审查分支读取。 |

委托可以按授权调用该只读审查能力；能力不可用或必要输入无法读取时，只将受影响的审查标为 blocked，不以自查替代独立意见。它不是仍待移除的一批旧阶段门。

若未来有未迁移叶能力声明旧门，权威门基线以 `scripts/check-skills.py` 的 `LEGACY_LEAF_GATES` 为准；当前 `proof-review` 对应的门集合为空，与正文 `Gates: none` 一致。

## 持续有效的完整性检查

委托继承登记只改授权与停点语义，不放宽结构约束：门声明格式、来源锚点与追踪状态、frontmatter 与调用策略、共置资源与相对链接、README 清单与实际目录的一致性都持续检查。登记为委托继承的能力额外检查合同小节是否存在，因此删去不适用的旧门不会连职责约束一起丢。

## 参考

- 合同正文：[mandate.md](mandate.md)
- 委托额度与运行批次：[batch-authorization.md](batch-authorization.md)
- 完整链路示例：[literature-review](../playbooks/literature-review.md)
