---
name: research-os
description: "科研任务的唯一编排入口：按意图、材料和规模选路线；只读请求只给推荐。"
disable-model-invocation: true
---

# Research OS

用户显式调用 `/research-os` 后，本入口按研究委托组织底层能力：用户给目标，入口在委托给的权限与额度内自主编排，交付由目标决定。除 `setup-research-os` 外，各 skill 仍由用户点名或由本入口按路径级联读取；模型不自动发现它们。

Gates: none

## 研究委托

一次调用是一份委托。目标、权限、研究额度与完成／停止语义以[委托合同](references/mandate.md)为唯一权威；本文件只负责匹配与编排。

- **持续的是委托，不是路线。** 路线、辅助命题、特殊情形与证明策略可自由更换；只有目标替换才停下确认，其余分支继续推进。
- **授权继承。** 内部级联、进入下一项能力或完成一次审查都不重置授权，也不要求用户再次点名。只读、只规划、只求建议的请求保持该范围。
- **额度不因并行、重试、恢复而重置。** 没有 setup 或显式额度时按有界首轮开始，不推导无限或付费许可。
- **已迁移能力**遵循该合同；**未迁移能力**仍按自身门声明停下确认，边界见[迁移边界](references/migration-boundary.md)。continuation 路线按同一委托执行并在该边界登记；不把整包说成已统一。
- 需要越权、超额、未授权的破坏性或对外动作时只阻塞那一步，其他工作继续。

## 匹配

用户意图和只读约束优先，材料状态限定入口，规模决定编排方式。任意大任务不等于 improvement。命中的是起点：同一委托内可来回调用多项能力；用户说 new task 或替换主要目标时重新匹配。

用户点名 arena 或要比较多候选方案时，打开 `arena` Skill（安装 slug 为 `arena`）：它按委托合同迁移，继承本次委托的权限与额度，缺子代理工具时需要的阶段标 blocked。它不依赖其他组织能力，也不进路由表。

无已交付路线时打开 [custom](playbooks/custom.md)：先写出有界流程，再按委托直接开始其中不需要额外授权的步骤，只有真歧义才问。不要把未交付路线的文件写成已经存在。

形式化不是必经路线：需要对关键代码性质、形式模型或定理编码建立或维护检查时，直接点名 `create-formal-verification-skill` 或 `maintain-formal-verification-skill`。它们只在该问题确实需要范围内每种情况时使用，普通测试够用就不升级。

软件、CLI 或服务需要可脚本化运行的行为证明时，直接点名 `create-verification-skill` 建立项目本地 verify skill（启动、doctor、按用户路径驱动、证据与特征覆盖映射），或点名 `maintain-verification-skill` 随应用变化保持映射诚实。行为验证不宣称数学定理成立；定理编码与形式化由上一行两条能力负责。

## 路由表

| 路线 | 变体 | 触发词 | 适用条件 | 只读约束 | playbook |
|---|---|---|---|---|---|
| route-only | — | 我该从哪开始、该用哪个、只看推荐、推荐入口、不要执行 | 用户只要入口或下一步建议 | yes | [route-only](playbooks/route-only.md) |
| literature | — | 查文献、文献综述、梳理 related work、这批论文怎么看 | 已有明确主题或论文集合，要在有界额度内完成一次文献综合并验收 | no | [literature-review](playbooks/literature-review.md) |
| discovery | — | 我有研究方向，想从研究方向到 Proposal、形成完整 Proposal | 只有方向或 brief，希望按缺口整合文献、候选、查新、fresh 独立评审与方案收敛 | no | [discovery](playbooks/discovery.md) |
| experiment-plan | — | 设计实验、写实验计划、做实验方案 | 已有研究问题，要的是有界计划而不是开跑 | no | [experiment-plan](playbooks/experiment-plan.md) |
| experiment-bridge | — | 跑完这个实验并分析、按计划跑实验、实验桥接 | Research OS 需求配方名（非 Skill）；执行控制唯一委托给 run-experiment，分析、监控与审计按需调用独立能力 | no | [experiment-bridge](playbooks/experiment-bridge.md) |
| paper-writing | general | 写论文 | 已有研究材料要写成论文，且材料不是机器学习实验、也不是以系统设计与实现为核心贡献 | no | [paper-writing-general](playbooks/paper-writing-general.md) |
| paper-writing | ml | 机器学习 | 材料是机器学习或人工智能实验，要按专业标准组织论文写作 | no | [paper-writing-ml](playbooks/paper-writing-ml.md) |
| paper-writing | systems | 系统论文 | 材料以系统设计与实现为核心贡献，要按专业标准组织论文写作 | no | [paper-writing-systems](playbooks/paper-writing-systems.md) |
| proof | — | 接续数学成果、续证明、证明交接、推广受阻 | 已有定理、证明、推导、计算或推广障碍，要围绕原问题继续研究 | no | [proof](playbooks/proof.md) |
| rebuttal | — | 回复审稿、逐条回应审稿意见、写 rebuttal | 已有论文与审稿意见，要逐 concern 候选回复 | no | [rebuttal](playbooks/rebuttal.md) |
| resubmit | — | 转投、换 venue 重投、保留旧稿改投 | 已有投稿目录，要在新目录适配另一 venue 并保留旧稿 | no | [resubmit](playbooks/resubmit.md) |
| paper-talk | — | 做会议演讲、生成 slides notes script、准备 paper talk | 已有论文，要 slides、notes 与逐字 script | no | [paper-talk](playbooks/paper-talk.md) |
| improvement | — | 整体改进、有界循环、review 后修复再审 | 用户要在固定轮数和写入范围内改进已有研究整体 | no | [improvement](playbooks/improvement.md) |
| continuation | — | 继续研究、暂停研究、恢复研究、额度收束 | 同一委托在授权和额度内持续推进、安全暂停或恢复 | no | [continuation](playbooks/continuation.md) |
| pickup | — | 接上次会话、从交接恢复、新会话续接 | 已保存交接、批准或作业记录，要在新会话恢复 | no | [pickup](playbooks/pickup.md) |
| custom | — | 没有对应流程、设计一个流程 | 已交付路线都不匹配 | no | [custom](playbooks/custom.md) |
| swarm | — | 并行覆盖、分片排查、多方案竞赛、全面摸排 | 已有明确问题，要在有界额度内用并行子代理分片、竞赛或混合探索并汇总 | no | [swarm](playbooks/swarm.md) |

已命名、文件未交付：无。写作统一进入 `paper-writing`；general、ml、systems 选择专业分支与资源。旧 ML/Systems 独立写作入口已合并到该统一能力，不再承诺旧 Skill 路径可调用。

不占路线的独立能力：用户要对抗审查、独立挑战或多模型审查时，委托内由编排者或用户直接点名 `interrogate`：独立 reviewer 逐模型挑战、findings 去重、分歧保留，主审四桶有据判断；该调用始终只读，修复由委托按授权另行组织（如 `proof-repair`、`research-improvement`）。独立能力未安装时只阻塞依赖它的分支，不阻塞其他委托工作。

## 只读优先

只要用户是在问该从哪开始、该用哪个、或明确不要执行，就打开 [route-only](playbooks/route-only.md)。即使句子里同时出现「写论文」「跑实验」「设计实验」等执行词，当前命中路线是 route-only；执行词只帮助选择推荐对象，不改变当前路线。回复区分「当前路线：route-only」与「推荐入口：…」。route-only 不创建任务、不联网、不写文件、不派子代理。

## 模型

Role: orchestrator

项目角色表是研究项目里的 `.agents/research-os-models.md`，一行一个角色：`reviewer: provider/model-id | high`。角色只有 orchestrator、literature、ideator、implementer、analyst、prover、writer、reviewer。thinking 只能是 off、minimal、low、medium、high、xhigh、max，而且必须是该模型支持的值。正文引用写成 `Role: reviewer`。

每个执行阶段按 playbook 的独立 `Role:` 声明解析本研究项目已确认的角色行，核实 provider/model-id 可用且支持 thinking；fresh dispatch 显式传入这两个值，并记录角色、解析来源、实际模型与 thinking。Role 管阶段执行者，不只是任务标签。当前宿主进程的 model 不改；orchestrator 配置不同于当前宿主时，把获准编排阶段派到对应 fresh 执行者，当前宿主只监督；没有该派发能力时如实标 blocked 并说明宿主模型差异，不把当前宿主自己跑说成已派发。

文件或角色行缺失时使用当前 session 实际可用的模型与 thinking，并明示回退及原因，不编造 slug。显式指定模型不可用或 thinking 不支持时，先核对有效原委托的明确替代授权；已覆盖的替代在实际可用、档位受支持且费用/范围允许时可继承，记录授权来源及实际模型/thinking，不重复索权。没有替代权时停下，请用户确认替代；行重复或格式错误仍停下澄清，不静默改配置，不以一般任务或余额推导任意替代。同上下文里的自审不是 fresh 独立审查；同模型 fresh 上下文可保留独立性，但不得冒充跨家族。无 fresh 能力时该阶段标 blocked 并写明 `independent review not performed`，不把同上下文自查记成执行或独立 review。不修改 `~/.agents/pstack-models.md`。

## 算力

工作区 `compute-policy.md` 是默认政策，不是本批运行许可。未配置时范围未指定，费用、算力和运行数都是 0，有效期 0 小时。有界首轮不由此获得运行许可：它只允许不占用付费资源、不改写既有成果的小步工作，见[研究额度](references/mandate.md)。experiment-plan、experiment-bridge 与 improvement 补实验分支按 [batch-authorization.md](references/batch-authorization.md) 核对已记入研究日志的本批授权；route-only 与未批准的 custom 不消耗额度。

## 宿主映射

下文 `/research-os` 表示逻辑入口；实际显式命令按宿主映射。pi 使用 `/skill:research-os`（叶入口同理 `/skill:<skill-name>`，setup 为 `/skill:setup-research-os`），Claude Code 使用 `/research-os`，Codex 使用 `$research-os` 或明确点名并读取已安装 SKILL.md。不要把 pi 中普通文本 `/research-os` 当成已加载入口；`disable-model-invocation` 会将它隐藏于自动发现清单。安装目录和派发方式不同：

| 宿主 | Skills 位置 | 委派 | 会话 |
|---|---|---|---|
| pi | 项目 `.agents/skills/`，也发现用户目录下的 agents skills | `herdr_spawn_agent`；子代理按项目 `.agents/research-os-models.md` 的 `Role:` 选模型 | pi 默认 sessions 目录中的 `--session` 文件 |
| Claude Code | 项目 `.claude/skills/` | Agent tool 派 subagent | 当前 Claude Code 会话 |
| Codex | 项目 `.agents/skills/` 或 Codex 实际报告的 skills 目录 | spawn_agent | Codex 当前 thread / session |

命令存在不等于已经登录或具备委派能力。子代理是这条编排路径的支持前提，按当前会话实际可调用的工具判定，不按宿主品牌推定：有子代理工具时才分派 fan-out 与执行阶段；没有时，需要分派的那一步标 blocked，入口只给只读建议（当前路线、下一步、或该直接点名哪个底层能力），不串行代跑整条 playbook，也不把编排者自己跑记成委托已执行。底层单能力的独立调用不受影响：用户直接点名 `research-lit` 之类的能力时，那一次调用自带边界，是能力本身的真实用途，不是入口的降级模式。

## 级联

命中已交付 playbook 后，把其步骤逐字抄入 todolist，逐步跟踪 pending / in-progress / completed / blocked；清单保留编号、原句及子列表，只附状态和证据定位，不压缩成阶段摘要。首次展示清单后逐项直接对照 playbook，漏句先补齐；仅达到该步骤完成条件才标 completed。用当前会话的清单记录即可；route-only 只在对话内跟踪，不创建任务或文件。

### 统一写作入口与专业分支

`paper-writing` 是唯一写作组织入口；general、ML 与 Systems 仅选择领域分支和按需资源。对应主路由及专业 playbook 都进入 `skills/writing-cycle/paper-writing/SKILL.md`，由该入口与 `skills/writing-cycle/paper-writing/references/standards.md` 组织统一写作；ML/Systems 意图仍可由用户明确表达。审稿回复、转投和演讲仍是独立目的路线，但其 playbook 服从各自 Skill 中的委托继承合同；授权内修复不要求二次点名。

级联进入已迁移叶时沿用本次委托，不重复请求批准；进入未迁移叶时仍按该叶自己的门停下确认，处理完该点后同一委托继续。写作范围内的编译修复与引用修复按委托继承调用，不要求用户另行点名。

每步开始前读对应叶 SKILL.md 全文，再按正文的条件读取点名资源并执行；读过入口、playbook 或步骤清单不等于读过叶正文。没有子代理工具时，需要分派的那一步按上面「宿主映射」标 blocked 并写明缺子代理能力，不把编排者自己读、自己跑记成已执行；只读建议与底层能力独立调用仍可用。仓库路径形如 skills/<category>/<skill-name>/SKILL.md；安装扁平布局时映射到 <安装根>/<skill-name>/SKILL.md（安装根取当前入口 SKILL.md 所在 skill 目录的父级或宿主报告的位置），共置资源相对该叶目录解析。先核实实际文件；找不到时标 blocked 与路径缺口，不猜测已读或跳到后续步骤。

收到子代理结果后，编排者自己核实实际产物、原始依据、读取覆盖及该步骤完成条件，记录定位与未核实项，再决定接受、在现有预算内修复或标 blocked；子代理总结只作线索，不直接转述为已核实结论。编排者核实不冒充独立 fresh review，保留各叶的独立审查隔离要求。

步骤里的反引号路径和 Markdown 链接都要读全文，例如 `references/PRODUCT-MAP.md`、`skills/general/research-os/playbooks/experiment-plan.md`、`skills/general/research-os/playbooks/experiment-bridge.md`、`skills/general/research-os/playbooks/rebuttal.md`、`skills/general/research-os/playbooks/resubmit.md`、`skills/general/research-os/playbooks/paper-talk.md`、`skills/general/research-os/playbooks/proof.md`、`skills/general/research-os/playbooks/improvement.md`、`skills/general/research-os/playbooks/pickup.md`。不把未读文件说成已执行。
