# Research OS Skills

在自己的科研项目目录使用通用 [Skills CLI](https://github.com/vercel-labs/skills)；无需安装 Research OS 专用 runtime。主使用说明参见 [README.md](../README.md)，全流程手工验收步骤参见 [用户手工验收指南](../docs/user-acceptance-guide.md)。

`/research-os` 按研究委托（目标、授权范围与额度、完成条件）组合底层能力；普通阶段转换不要求重复批准。只读请求保持只读；没有 setup 或明确预算时仍可有界开始不依赖未授权资源的工作。仅在当前宿主真实支持子代理时才委托；否则只推进本地可完成部分，并标明未执行的委托工作。

```bash
npx skills@latest add toRolex/Research-OS-Studio --list
npx skills@latest add toRolex/Research-OS-Studio --all
# Discovery 配方由 research-os 提供；单独安装时同时安装五项 Required 能力
npx skills@latest add toRolex/Research-OS-Studio --skill research-os research-lit idea-generation novelty-check idea-review idea-refinement --agent codex --copy -y
```

Skills CLI 按独立 slug 安装，不会解析跨 Skill 依赖。选择性安装 proof 配方时，按需同时选择 `research-os` 与所用能力（如 `arena`、`swarm`、`interrogate`、`formula-derivation`、`proof-writer`、`proof-review`、`proof-repair` 及验证 Skill）；proof-orchestrator 控制器已删除，数学审计、Lean、记号和交接资源随 `proof-review` 包提供。缺少能力只阻塞依赖它的分支，不用自审或串行扮演替代。

这些远程命令读取 GitHub 已发布版本，不会包含尚未合并或 push 的本地修改。验证本地分支时，在一个临时科研项目目录中运行（将绝对路径替换为当前 checkout）：

```bash
npx skills@latest add /绝对路径/Research-OS-Studio --list
npx skills@latest add /绝对路径/Research-OS-Studio --all
```

CLI 负责宿主安装目录和文件复制；本仓库不生成 projection。需要限定宿主时可使用 `--skill '*' --agent claude-code --agent codex --yes`。安装后按宿主约定重新加载 Skills 或开启新会话，确认发现 `setup-research-os`，再显式调用它；pi 原生命令为 `/skill:setup-research-os`，Claude Code 为 `/setup-research-os`，Codex 为 `$setup-research-os` 或明确点名已安装技能。本页所有 `/name` 是逻辑点名：pi 用 `/skill:name`（入口 `/skill:research-os 我该从哪开始`）、Claude Code 用 `/name`、Codex 用 `$name` 或明确点名。pi 普通 `/name` 文本不保证加载隐藏的显式 Skill。宿主未发现时先核对 CLI 输出的实际安装位置，不能把文件安装成功当作模型已加载。

### 已知宿主限制

`--all` 会向所有 CLI 支持的宿主安装，并非仅当前使用的宿主。Skills CLI 1.5.25 实测会转换 Eve 的 `agent/skills/setup-research-os/SKILL.md`，移除 `name` 和 `disable-model-invocation`；随后 `skills list` 会对该副本报告 `missing required frontmatter field(s): name`。源 Skill 与 `.agents/skills/` 副本仍保留完整字段，Claude Code / Codex 的限定安装副本与源目录一致。这是 CLI 的 Eve 转换行为，不是本仓库发行物缺字段；也不能据此断言 Eve 正常可用。

Eve 的实际加载及仅显式调用策略尚未验收，不声明全宿主兼容。使用 Eve 前应在可丢弃项目中核实这两项；无法核实时暂停在该宿主使用 setup。只需 Claude Code / Codex 时，可用上方限定宿主选项替代 `--all`。其他宿主同样需自行确认加载与调用策略；文件安装成功不等于宿主交互验收通过。

`apply-citation-fixes` 在 Skills CLI 1.5.26 本地 `--all` 安装中，Eve 副本保留 `name`，但仍移除 `disable-model-invocation`。`.agents/skills/` 原始副本和 Claude Code／Codex 限定安装副本保留完整授权指令与资源。Eve 的显式调用限制未验收，在确认宿主能遵守前暂停使用该修复入口；安装成功不代表授权策略受到宿主强制执行。

## 分类与当前清单

目录约定是 `skills/<category>/<skill>/SKILL.md`，资源与 Skill 共置。分类用于导航，不规定调用顺序。

下表是发布时点快照，以 `skills/` 目录树为唯一真源；`scripts/check-skills.py` 在 CI 校验本清单与目录树一致。调用策略：除 setup 外全部显式调用（`disable-model-invocation: true` 与 `agents/openai.yaml` 的 `allow_implicit_invocation: false`）。`setup-research-os` 是唯一允许模型主动建议的例外，写入仍须确认。

| 分类 | 目录 | 当前正式 Skill |
|---|---|---|
| General | `general/` | [setup-research-os](general/setup-research-os/SKILL.md)（可被模型建议；写入仍须确认）、[research-os](general/research-os/SKILL.md)（显式；旧入口 ask-research-os 已删除）、[swarm](general/swarm/SKILL.md)（显式；并行覆盖：分片、竞赛或混合探索，派发宿主真实子代理并汇总，缺口不算通过；改编自 pstack swarm，MIT）、[interrogate](general/interrogate/SKILL.md)（显式；独立挑战与主审判断，只读） |
| Organization | `organization/` | [arena](organization/arena/SKILL.md)（显式；候选比较与整合：Frame→Fan-out→Cross-judge→Pick→Graft→Verify；预先 rubric、输出隔离、完整阅读候选、主编排者逐项综合；已迁移到研究委托合同，缺子代理标 blocked；独立于其他组织能力） |
| Idea Cycle | `idea-cycle/` | [research-lit](idea-cycle/research-lit/SKILL.md), [idea-generation](idea-cycle/idea-generation/SKILL.md), [creative-thinking-for-research](idea-cycle/creative-thinking-for-research/SKILL.md)（可选构思能力）, [novelty-check](idea-cycle/novelty-check/SKILL.md), [idea-review](idea-cycle/idea-review/SKILL.md), [idea-refinement](idea-cycle/idea-refinement/SKILL.md)（能力保持独立；Discovery 是 `/research-os` 配方，不是独立 Skill） |
| Validation Cycle | `validation-cycle/` | [analyze-results](validation-cycle/analyze-results/SKILL.md), [create-formal-verification-skill](validation-cycle/create-formal-verification-skill/SKILL.md), [create-verification-skill](validation-cycle/create-verification-skill/SKILL.md), [experiment-audit](validation-cycle/experiment-audit/SKILL.md), [experiment-plan](validation-cycle/experiment-plan/SKILL.md), [experiment-queue](validation-cycle/experiment-queue/SKILL.md), [formula-derivation](validation-cycle/formula-derivation/SKILL.md), [maintain-formal-verification-skill](validation-cycle/maintain-formal-verification-skill/SKILL.md), [maintain-verification-skill](validation-cycle/maintain-verification-skill/SKILL.md), [monitor-experiment](validation-cycle/monitor-experiment/SKILL.md), [proof-repair](validation-cycle/proof-repair/SKILL.md), [proof-review](validation-cycle/proof-review/SKILL.md), [proof-writer](validation-cycle/proof-writer/SKILL.md), [result-to-claim](validation-cycle/result-to-claim/SKILL.md), [run-experiment](validation-cycle/run-experiment/SKILL.md), [training-health-check](validation-cycle/training-health-check/SKILL.md)；实验桥接是 `/research-os` 配方名，执行唯一进入 `run-experiment` |
| Writing Cycle | `writing-cycle/` | [paper-writing](writing-cycle/paper-writing/SKILL.md)（唯一写作入口：general／ML／Systems 专业选项，分支方法、reviewer/venue 参考与报告模板按需共置随包）、[paper-plan](writing-cycle/paper-plan/SKILL.md)、[paper-drafting](writing-cycle/paper-drafting/SKILL.md)（均显式调用，可独立或级联）、[academic-plotting](writing-cycle/academic-plotting/SKILL.md)（显式调用；#58 负责其迁移与实现）、[paper-compile](writing-cycle/paper-compile/SKILL.md)（check-only）、[paper-compile-repair](writing-cycle/paper-compile-repair/SKILL.md)（精确 diff；委托内继承授权）、[citation-audit](writing-cycle/citation-audit/SKILL.md)（只读）、[apply-citation-fixes](writing-cycle/apply-citation-fixes/SKILL.md)（精确 diff；委托内继承已授权范围）、[paper-claim-audit](writing-cycle/paper-claim-audit/SKILL.md)（只读）、[claim-stress-test](writing-cycle/claim-stress-test/SKILL.md)（只读；最强拒稿论点与独立裁决）、[rebuttal](writing-cycle/rebuttal/SKILL.md)（不自动补实验或外发）、[paper-talk](writing-cycle/paper-talk/SKILL.md)（不自动发布）、[resubmit-pipeline](writing-cycle/resubmit-pipeline/SKILL.md)（保留旧稿，不自动投稿）、[research-improvement](writing-cycle/research-improvement/SKILL.md)（#59 总控，有界 review／repair／re-review；不自动启动 experiment-bridge、paper-writing 或专项修复入口） |

## Discovery 配方依赖

`/research-os` 是唯一编排入口，Discovery 是其内部 recipe。Skills CLI 的 `--skill` 多选只安装列出的 Skills，不会解析 recipe 的逻辑依赖；要完成方向到 Proposal，应同时安装 `research-os`、`research-lit`、`idea-generation`、`novelty-check`、`idea-review`、`idea-refinement`。creative-thinking-for-research 可选，不在 Required 清单中。若 CLI 不支持多选，可分次安装或安装整包。缺少某项 Required 能力时只阻塞依赖该能力的职责。

只有实际含 `SKILL.md` 的目录才是可安装 Skill。不为分类创建占位 Skill，不把保留的旧工程纳入这份清单。

Writing Cycle 以 `paper-writing` 为统一入口，ML／Systems 专业资源按需引用；旧平行控制器已删除，当前能力边界见[迁移说明](general/research-os/references/migration-boundary.md)。除 `academic-plotting`（#58）与 `research-improvement`（#59）外，本分类写作／审查／修复／rebuttal／resubmit／talk 能力迁移到[研究委托](general/research-os/references/mandate.md)。委托内编译与引用修复继承授权，不要求再次独立点名；只读审查仍只读，且不自动投稿。

## 只读入口导航

不确定从哪里开始时，显式调用 `/research-os` 并说明只要推荐。旧入口 `ask-research-os` 已删除，改用 `/research-os` 的 route-only。已知入口仍可直接点名，无需先 setup。route-only 接受方向、已有结果或稿件，只在对话中推荐并停止，不写研究材料、不联网、不启动推荐任务。`/research-os 设计实验` 进入 experiment-plan；`/research-os 跑完这个实验并分析`（也可称“实验桥接”）进入 run-experiment 执行配方。两条都只认研究日志里的本批授权。

已保存交接用 `/research-os` 的三条路线，不另建状态机：

- **proof**：从已有数学成果、证明材料或推广障碍继续，按证据交替推导、构造、计算、fresh 只读审查、finding 修复与按需形式化；不是每项必经的固定顺序。`/research-os` 委托统一控制目标、写域、轮次、额度、暂停恢复与停止；proof-review 按需承载证明审计、Lean、记号和交接参考。
- **improvement**：对已有 Claims、代码、结果和 findings 做有界 review → repair → re-review。轮数、写入范围和补实验名额以 research-improvement 的授权门为准。
- **pickup**：新会话打开已保存交接、`compute-policy.md` 和 `research-log.md`，重查已批准与未批准边界。过期授权不续期，未知消耗不按 0 释放。

自包含的[完整批准地图](general/research-os/references/PRODUCT-MAP.md)区分三条主流程、独立 user-invoked 入口、model-invoked 能力及数学／Lean、ML／Systems 专业扩展，同时区分已实现、计划和宿主可用性。计划条目不是当前安装命令，文件安装成功也不代表宿主已加载。Idea Discovery、Validation 与 Writing Cycle 的主入口及专业扩展均已交付。写论文时 `/research-os` 统一进入 `paper-writing`，按材料加载 general、ML 或 Systems 标准，不再安装旧专业控制器。

在可丢弃项目中可分别用“只有方向”“已有外部结果”“已有稿件”咨询；核对推荐理由、不强制前序流程、计划状态如实说明，以及项目零写入、零自动启动。实现阶段的受限合成模型场景不等于真实科研或宿主交互验收。

### 现成候选的评审与改进

`idea-review` 让独立评审者直接读取原始候选及文献，保留 findings、证据、裁决依据与未解决问题；不改候选。`idea-refinement` 在已授权修订范围内保持固定 Problem Anchor，比较最小可行与前沿路线，输出完整 Proposal 与逐轮改进理由；独立方法评审与修订分工明确。二者均可直接用于现成材料，不要求先运行生成流程，也不自动互相启动。

手工验收：提供一个有明显弱点的现成候选、原始文献和约束；先点名 review，核对 reviewer 实际原文定位与问题，再点名 refinement，核对每轮 Anchor 原样保留、双路线取舍及未解决项。限制一轮修订、零实验预算，应只得到方法及验证草图。另测缺原文、缺独立 reviewer、已有同名输出和 composed 章节授权：应准确暴露缺口、保留已有材料并停止，不配置环境或自动实验。实现期场景结果不替代用户真实科研验收。

Writing Cycle 审查能力均只读审查研究材料、输出 Markdown 报告与建议：`paper-claim-audit` 核对数字、比较、配置、图表/caption 和实验覆盖；`claim-stress-test` 由两个 fresh reviewer 分别构造整篇拒稿攻击、对照原材料逐点裁决。standalone 独立交付报告，composed 贡献父 Workflow 的 canonical report；默认不改稿，报告后停止。Claim / Citation / Proof / Stress 并列按需，不自动串联；Citation 与 Proof 不由这两项替代，其入口由独立票交付。

## Discovery 组合验收

`/research-os` 的 Discovery recipe 让用户直接提交研究方向或现有成果及目标。完整方向到 Proposal 是可独立交付的目标；配方依目标缺口与已有材料选择五项 Required 能力的子集，可重排或回访，不是固定流水线。fresh 独立评审不能由生成者自查替代；缺少依赖只阻塞对应职责。只交付用户目标要求的报告和/或 Proposal，不自动运行 pilot、不制定实验计划、不进入 Validation 或 Writing。

在可丢弃项目中手工验收：

1. **完整路径**：给一个真实方向及简短 brief。核对 Phase 1 有真实检索与来源标签，Phase 2 有多视角候选与筛选记录，Phase 3 每个入围候选有 closest prior work 或证据缺口，Phase 4 有独立 reviewer 的原文定位，Phase 4.5 逐字保留 Anchor 并给出双路线取舍；最终得到 `IDEA_DISCOVERY.md` 与 `RESEARCH_PROPOSAL.md`。
2. **禁止自动越权**：全程核对未运行任何 pilot、未生成实验计划／tracker、未进入 Validation／Writing、未安装环境或做远程副作用、未写统一 JSON／状态记录／HTML。
3. **工具缺失降级**：无检索能力时，阶段 1 降为 supplied-material synthesis 并限定覆盖；无独立 reviewer 时标 REVIEW UNAVAILABLE 并停止裁决；无参考论文全文时保留缺口，不凭记忆补写。
4. **边界与停止**：已有报告或材料不被覆盖；目标替换、越权、超额或既有文件冲突只阻塞对应分支；交付后只建议下一步，不自动启动另一顶层 Workflow。

## 普通公式推导与证明生成

`formula-derivation` 用于组织推导主线、选定不变量、说明假设与近似并生成完整公式链；`proof-writer` 用于固定命题的证明生成，不替代只读证明审查。两者均为显式调用，由用户点名或父流程按路径级联，并继承当前委托的写域与额度；已授权范围内创建新文件、切换阶段或重试不重复索权。独立调用缺少影响执行的字段时，只对缺项提出有界问题；没有写入授权时在聊天返回。改变原命题或假设仍须用户确认。

开始前固定目标、输入范围、目的路径和有限尝试预算；变更假设、弱化命题或重构目标只是建议，获明确授权后才发展独立变体。成功、缺口、实际失败路线和可复用教训都应保留；承重缺口未解决时不标成功。普通数学推导不需要 Lean，也不安装工具链；生成完成即停止，不自动进入通用 review / repair 或推进其他 Workflow。

在可丢弃项目中分别验收：带误差界的公式近似、包含边界情况的固定命题证明、缺少关键假设的无法完成报告，以及仅聊天/向既有报告贡献的写入边界。核对原命题未改、失败未被隐藏、没有自动修复。此类 toy 场景与安装检查不代表真实科研或形式化验证通过。

## 初始化与人工验收

setup 是可选的项目初始化：先探索现有项目，再读取本 session 的真实模型清单；用户选择使用时，可为八个预设角色确认模型并起草 `.agents/research-os-models.md`。该角色表不是开始研究的前置条件；主入口按宿主当前真实子代理能力安排委托。默认 `compute-policy.md` 的额度是 0、范围未指定，正文写明它不是运行授权。工作区已有则沿用；没有时才建议可见的 `research/`。缺失的导航、项目说明、findings、研究日志只补一次。角色表和政策在确认新全文后整文件替换，字节相同则不写。已有研究日志和全局 `~/.agents/pstack-models.md` 不改。

在可丢弃的科研项目副本中逐项验收：

1. **新项目**：单独验收 setup 时核对所选角色映射均来自真实模型清单、零授权政策、种子和指令区块；确认前零写入。另核验不运行 setup、也未提供明确预算时，主入口仍能有界开始不依赖未授权资源的工作。
2. **非空项目**：放入原研究材料及已有日志；沿用目录，日志字节不变，不搬迁材料。
3. **重复执行**：同一确认稿不再写入，不出现第二套角色或额度。
4. **不可用模型**：清单外 slug 停下重问，角色表不含该 slug。
5. **全局角色表**：`~/.agents/pstack-models.md` 修改时间不变。
6. **内容冲突**：修改已有 Research OS 区块后先展示差异。两种指令文件都存在时只更新 `CLAUDE.md`。
7. **拒绝与外部变化**：拒绝时零写入；确认后目的文件或指令候选变了，停止整批并重新确认。另测原先仅有 `AGENTS.md`、确认后外部新增 `CLAUDE.md`：即使它不在原写入清单中，也应停止整批、重新选择指令文件并确认新草稿。
8. **停止边界**：只汇报实际路径和未解决项，无实验、环境安装、远程副作用或自动启动下一流程。

## 长期证明与人工验收

长期证明任务统一经 `/research-os` 的 proof 路线编排。proof-review 随包提供审计、Lean、记号与交接方法参考，按本次审查分支读取；Lean 不是前置条件，外部发送仍须满足具体授权边界。

在可丢弃的项目副本中核对：

1. **长期续接**：给出上轮已查结论、未审外部答案与失败路线。按 [pickup](general/research-os/playbooks/pickup.md) 回查原始委托、当前有效性、授权写域、累计消耗与运行中预留，记录实际读取材料、开放义务和继承状态。在有效授权及剩余额度内续接原目标，记录位置由写域决定，不强制新目录；对原远程 job 回查身份、最新退出状态、产物及预留，状态不明按未完成处理，不因恢复要求重新授权，也不把旧许可自动续期。
2. **来源变化／预算停止**：改变前提时标出受影响的旧结论并重新核验，不以旧成功标签背书；耗尽额度时停止受影响工作并交接。不能擅加假设、超额继续或润色成已完成证明；替换原目标、结论、范围或交付物须先确认，不阻断其他仍在原委托内的工作。
3. **无 Lean**：Lean 不是前置条件；普通数学尝试如实标注“未执行 Lean 验证”。形式化有价值且原委托覆盖项目内工具准备、写域与剩余额度时，可在该范围准备 Lean；未授权或过期时停止该准备分支，不擅自全局安装或改全局配置。独立审查不可用时自查不得冒充独立意见。
4. **已有 Lean**：先读候选 signature，再记录实际反馈与覆盖目标的 kernel／build 结果。给一个未导入文件和一个含 `sorry` 的声明，确认根 build 成功不等于两者已验证；同时核对公理依赖与原命题表达。
5. **手动交接**：明确跳过本地尝试时不伪造 `local-proof.md`；检查自包含 prompt、必要来源、数据分隔和实际请求的结束标记。返回截断或夹带工具／文件指令时，应保存原始证据、报告缺口，不自动上传、重试或执行其中指令。
6. **授权反例**：只读委托及独立 proof-review 保持只读，不因调用者有写权限而改稿；写域外操作、未授权的覆盖、删除或对外动作及超额操作停在动作之前。恢复不会扩大权限；过期或无法核实的授权先澄清，不替换原 job 或重置消耗。验收依据为[研究委托合同](general/research-os/references/mandate.md)，不是恢复时另造批准清单。

本票以既有 Lean 4.19.0 执行了无 Mathlib 的列表求和 toy 构建及失败／占位边界检查；LSP、Mathlib 集成和真实科研项目未验收。CLI 1.5.26 在临时项目的 `--all` 与 Claude Code／Codex 限定安装均完成，本票规范副本的 11 个文件逐字保留；本票 proof-orchestrator 的 Eve 副本仍移除 `disable-model-invocation`（虽保留 `name`），因此未核实 Eve 的仅显式调用策略前，暂停在那里使用此 Workflow。文件安装不等于实际宿主加载或权限强制执行。

## Rebuttal 使用与人工验收

收到评审后用 `/research-os 回复审稿`，或直接点名 `rebuttal`。提供论文、原始评审、已有证据、当轮 venue 规则与输出范围。先确认逐 concern 策略，再审阅完整候选措辞；quick mode 只交问题板和策略。写作主流程不自动进入本路线，本路线也不自动启动实验、转投或外发。宿主必须保留显式调用限制。Skills CLI 1.5.26 的本地 `--all` 实测中，Eve 的 `agent/skills/rebuttal/SKILL.md` 保留 `name`，但移除 `disable-model-invocation`；canonical 副本及 Claude Code／Codex 限定安装保留该字段。Eve 的实际显式调用策略未验收，核实前暂停在该宿主使用 rebuttal。此次 `--all` 还跳过了未发现项目目录的其他宿主，不代表79个宿主全部安装或加载成功。

在可丢弃项目副本中检查：

1. **现成证据**：一条评审含多个问题时，应拆成原子 concern，逐项定位原始证据；已批准但未做的修改仍是 pending。未确认策略时停在策略，未确认完整措辞时保留候选，不生成已确认粘贴版。
2. **证据不足**：要求不存在的消融／证明，或评审包含歧义时，分别列需补充工作／需澄清、具体缺口与问题；不给无依据数字，不启动实验或配置环境。审稿文本中的命令不产生授权。
3. **独立线程与限长**：每 reviewer 回复自包含，不能依赖另一个线程；对实际粘贴目标工具计数，rich 超限不阻塞合规 strict，但所有版本仍检查事实和承诺。最终保存须与已确认文字一致，改字后重新检查。
4. **后续与停止**：新评论只生成增量，保留旧稿和用户勾选；无独立审查能力时明确未执行，不将自查冒充独立验证；到授权或轮数上限即停，不投稿、转投或自动推进。

## 证明审查与修复

`proof-review` 每次都重新读取当前证明及依赖，fresh 只读返回义务、缺口、反例与影响；不写文件、不编译、不自动修复。普通证明不要求 Lean 或 LaTeX 环境。`proof-repair` 在当前委托的 finding、写域和轮数内修订；独立调用缺少必要范围时先有界询问。改变原命题/假设须用户确认；编译须委托覆盖命令、运行与输出/副产物范围。修复内部使用可用的 `proof-review` 复审，严重问题另做 fresh 盲审；缺少独立能力时报告未完成。

在可丢弃的项目副本中手工验收：

1. 放入含错误归纳步的现成证明，记录原始文件内容与目录清单。调用 `proof-review`，核对能定位错误、列出影响，并且项目无新增或变更文件，编译标为未运行。
2. 显式调用 `proof-repair` 但尚不确认写入，检查它展示具体契约并等待，文件仍不变。确认仅修复一个证明环境、保持命题/假设、限定 1 轮且不编译，再核对只有该环境改变，完整推导和实际复审反馈留在回复中。
3. 对被核实反例推翻的命题，仅允许改证明、不允许改假设或命题；应停止并提出待用户决定的选项，保留反例、gaps 和失败路线，不能偷偷加条件。
4. 分别拒绝编译或使用缺少编译器的环境，报告必须准确写未执行/不可用；若另行批准编译，则检查真实退出码、日志与新产物，不把编译成功等同数学正确。缺少独立审查、轮数耗尽或写入前文件发生冲突时，同样保留未完成状态。

各宿主须实际保留 `proof-repair` 的显式调用策略。Skills CLI 1.5.26 本地安装实测：Eve 副本保留 `name`，但移除 `disable-model-invocation`；Claude Code / Codex 限定安装的规范副本保留源字段。Eve 的真实显式调用策略尚未验收，无法确认时暂停在该宿主使用修复。其他宿主同样须核实；此处指令不是宿主权限强制执行机制。

通用 CLI 安装实测、临时文件场景模拟和真实用户验收是不同层级。尚未经用户在真实科研项目确认，不声明端到端体验通过。

## Systems 专业写作与人工验收

`paper-writing` 的 Systems 专业选项面向系统设计与实现为核心贡献的论文：按 Abstract（5 句）→ Introduction（问题→Gap G1–Gn→洞见→贡献）→ Background & Motivation（观测→设计推论）→ Design（架构→逐模块 choice／alternatives／why→取舍表）→ Implementation → Evaluation（setup→end-to-end→microbenchmark／ablation→scalability）→ Related Work → Conclusion 组织正文，并核对系统评价面。它组合已交付的 `paper-plan`、`paper-drafting`、`academic-plotting`、`paper-compile` 与并列审查能力，按需读取 Systems 专业参考，不启动额外的写作总控。

从 `/research-os` 的 paper-writing / systems 路线或直接显式调用 `paper-writing` 并表达 Systems 需求；两者共用同一入口，按需读取 `systems-writing-methods`、`systems-evaluation-methods`、`systems-checklist` 与 `systems-venue-and-reviewer`。授权沿用委托。

在可丢弃项目副本中手工验收：

1. **现成系统材料到专业产物**：给出已有设计说明、原型与结果、部分观测。核对 Gap 与设计 alternatives 可追溯、end-to-end 与 microbenchmark／ablation 分列、架构图前 3 页出现、每条实验结论三处一致（段首假设／段尾结论／caption）、Related Work 按方法分组；交付候选稿与审查报告后停止。
2. **缺少扩展性证据**：故意不提供 scalability 数据。核对系统证据面标为 `MISSING SCALABILITY EVIDENCE`，依赖扩展性的主张未进入 `submission-candidate` 就绪判定，未编造或外推曲线，也未运行实验或部署；给出最小补证动作与用户选项。
3. **只有 microbenchmark**：不给端到端结果。核对 microbenchmark 结论未被升级为系统整体更优，缺口如实保留。
4. **venue 与入口边界**：不指定 venue 时不得假定页数／模板；指定时要求现场核对当前 CFP 并记录来源。核对 Systems 专业选项只调用唯一 `paper-writing` 组织入口，未投稿、未发布、未安装环境。

宿主须保留 `paper-writing` 的显式调用策略；文件安装成功不等于宿主已加载或权限已强制执行。静态检查与合成场景审查不构成真实科研验收；缺独立 reviewer 时相应就绪判定如实降级。

## 论文编译与有界修复

- `paper-compile`：只检查；在用户已有 LaTeX 上真实构建，报告错误、PDF 与未解决问题。可独立点名，也可在父 Workflow 当前编译职责内使用。
- `paper-compile-repair`：可由用户独立点名，也可在当前 `paper-writing` 委托已覆盖职责、文件和预算时按路径级联。修复前仍按该 Skill 确认本轮精确 diff、构建与预算；检查结果本身不授权写入。
- 使用完整审阅的闭合输入和新临时输出，记录宿主执行或现有隔离的实际边界；不安装、配置环境或覆盖旧 PDF。工具不足时准确停止。

在可丢弃的论文副本中依次验收：

1. **坏稿检查**：给出不存在的命令；显式允许临时构建，要求只检查。核对真实非零退出码、原始日志与源码不变。
2. **授权修复**：点名 repair，确认限定文件、完整 diff 和预算。核对仅批准差异被应用、新目录重编译、失败日志仍保留。另留一个未定义引用，确认 build 成功也继续报告 warning。
3. **拒绝修复**：拒绝拟 diff，核对原稿与旧 PDF 不变，没有后台修复或自动进入下一流程。
4. **能力缺失**：在无匹配引擎/文献后端的环境中检查，核对“未运行”、缺失项、不安装和不使用旧 PDF 假报成功；缺可选 PDF 工具时相应检查单列“未检查”。
5. **复杂稿与停止**：未知构建脚本、动态依赖、越界路径或无法落实预算时应停止，不把禁 shell escape 或事后内容比较声称为 OS 写保护。另测多入口、嵌套章节及 venue 规则未知，确认不猜入口、不删孤立候选、不臆定页数合规。

编译成功不证明论文论断成立、可投稿或用户已接受。以上是用户手工验收步骤，不是已完成真实科研验收的声明。宿主须保留 `paper-compile-repair` 的显式调用策略。Skills CLI 1.5.26 的本地全量安装中，Eve 副本保留 `name`，但移除 `disable-model-invocation`；在实际加载和显式调用策略核实前暂停在 Eve 使用 repair。不能把副本安装成功当作权限执行正确。

## Conference Talk 人工验收

Skills CLI 1.5.26 的本票本地安装中，Claude Code / Codex 副本完整；Eve 副本保留 `name`，但仍移除 `disable-model-invocation`。因此不能声明 Eve 已落实 `paper-talk` 的仅显式调用策略；未在宿主核实前暂停在 Eve 使用此入口，不以正文护栏代替宿主策略验证。

用 `/research-os 做会议演讲`，或直接点名 `paper-talk`。提供现成论文、听众、语言、主讲时长、Q&A 预留、输出目录及格式；不要求先运行写作或 setup。先核对有效委托；已覆盖的输出范围、大纲与裁决规则不重复批准，缺项或目标/权限变化只停相关分支。

1. **论文到演讲**：大纲符合原目标且写入在有效授权内时继续产出，检查实际 slides、notes、逐字 script 和 Q&A 一一对应；数字、baseline、单位、种子/样本数与局限可追溯，时间合计符合预算。无消融、demo 或链接时不补造。
2. **三产物审查**：在可丢弃副本中分别把 slides 数字改错、notes 聚合次数改错、script/Q&A 增加无依据泛化；只授权审查。报告应指出三类实际位置及源证据，保持输入不变，并给故事、密度、计时、图可读性、开场、takeaway、渐进讲解的七维结果。
3. **工具缺失**：无法生成或渲染请求格式时，检查 Markdown 仍可交付且明确未生成/未验证项；无安装动作。没有独立 reviewer 时只能标自检，无真人排练不宣称实际准时。
4. **冲突、匿名与停止**：既有文件保留；大纲按委托内目标与裁决规则调整，需改变主要目标/结论范围或越权时先确认。匿名字段不被模板或精修补回。视觉修改不改变内容或 notes，原稿和精修副本分开；最终仅返回报告，不上传、发布或调用后续 Workflow。

模板的 Beamer 编译和 PPTX 语法检查不代表真实演讲材料通过；实际双格式输出、字体/动画、投影与真人排练须在用户环境逐项验收。通用 CLI 安装实测、临时文件模型场景和真实用户验收是不同层级。尚未经用户在真实科研项目确认，不声明端到端体验通过。

## Resubmit 转投适配与人工验收

限定宿主（Claude Code／Codex）安装中，canonical 副本与安装副本逐字节一致；`--list` 共 43 个 Skill，含 `resubmit-pipeline`。Eve 副本与真实科研验收未做，不声明 Eve 兼容或端到端通过。

用 `/research-os 转投`，或直接点名 `resubmit-pipeline`。提供旧投稿目录、目标 venue 与新目录；不要求先运行 setup 或写作流程，先核对写域与路径。有效委托已覆盖的范围与改动不重复索权；缺授权、路径冲突或目标变化停相关项，旧稿始终保留。

1. **现成稿件转投**：旧稿普通文件复制到新目录并逐文件比对；新目录真实构建，新 PDF 落新目录。核对旧稿内容基线前后一致、无构建产物污染。
2. **模板冲突**：用户模板与官方指南冲突时逐项展示差异，由用户决定；未决只给标注冲突的暂定方案，不代选、不称合规。
3. **构建缺失**：未获临时写域／预算或缺引擎／后端时记“未运行”，不安装、不拿旧 PDF 冒充成功；失败只报告。只有当前 `paper-writing` 委托已覆盖修复职责、范围与预算时才可级联 `paper-compile-repair`，并仍遵守精确 diff gate；否则停在受影响分支并请求缺失授权。
4. **引用与旧稿**：引用检测默认 soft-only 冻结 bib，只给正文收窄建议；`apply-citation-fixes` 可独立调用，也可在 writing/repair 委托覆盖职责、文件和副作用时按路径级联；每组 diff 仍按其合同取得对应批准。复验新稿无新增错误、无引用断裂、无旧稿污染。
5. **停止边界**：目标已存在／非空／指向旧稿时停；全部拒绝零写入。交付新目录候选与报告，不投稿、不发布、不自动调用 `rebuttal`、`paper-talk` 或其他 Workflow。

以上是用户手工验收步骤，不是已完成真实科研验收的声明。宿主须保留 `resubmit-pipeline` 的显式调用策略；文件安装成功不等于宿主已加载或权限已强制执行。

## ML 专业写作与人工验收

`paper-writing` 的 ML/AI 专业选项通过 `/research-os` 的 paper-writing / ml 路线或直接显式请求 ML/AI 材料触发。从现成研究材料完成规划、实验报告核对、图表、起草、真实编译、并列适用审查与授权修订，交付候选稿与报告后停止。保留 seeds／runs、error bars、compute、limitations 方法，并按需读取实验报告、reviewer、venue 清单与模板；不自动投稿或启动跨流程改进。不分发会议模板；venue 规则以当前官方 edition 现场核对为准。

在可丢弃项目副本中手工验收：

1. **完整路径**：给一个含真实结果、日志、配置和代码的 ML 研究目录。显式调用并核对：规划 Claim—Evidence、实验报告核对（每次比较给出 runs／seeds 数量与不确定性方法、超参与选择、compute、Limitations、失败结果）、图表、真实编译、并列审查与独立评审及有界修订；最终得到候选稿与自然 Markdown 报告。
2. **报告不完整场景**：拿掉部分 seeds、error bars 或 compute 记录。核对缺失处出现 `[SEED COUNT NEEDED]`／`[COMPUTE NEEDED]` 一类可见缺口，而不是默认值（如“3 seeds”“A100”）；相关 Claim 被收窄或交用户决定，**零实验执行**。
3. **venue 与模板**：指定一个 venue 年份与 track；核对官方 author guide／checklist 的来源与访问日期、模板冲突的用户决定，以及未指定 venue 时不设默认会议、报告写“合规未核对”。
4. **分工与越权**：核对唯一 `paper-writing` 入口按 ML/AI 专业资源分支组织，委托内修复不越范围；全程未自动启动其他顶层 Workflow、未安装 LaTeX／GPU 环境、未投稿或发布；需要补实验的 Claim 停在未授权状态。

以上是用户手工验收步骤，不是已完成真实科研验收的声明。宿主须保留 `paper-writing` 的显式调用策略；文件安装成功不等于宿主已加载或权限已强制执行。

## 研究工作有界改进循环与人工验收

`research-improvement`（跨流程，物理归位于 writing-cycle/）由用户显式启动，在一次授权内对研究工作整体做有界 review → repair → re-review：直接读取 Claims/草稿、方法与代码、原始结果、当前 diff 与历史 findings，按批准范围修代码、补分析、改稿，并在另行授权与运行数名额内补实验；轮数、写入范围、资源与副作用上限固定，交付逐轮正文日志后停止。它承接 W3 `auto-paper-improvement-loop` 与 W2 `auto-review-loop` 的方法，但不是只读审计，也不自动启动 `run-experiment`、`paper-writing` 或专项修复入口。

在可丢弃项目副本中手工验收：

1. **有界修复闭环**：给出带明显缺口的现成草稿/结果，确认一个确定轮数（如 2 轮）与明确写入范围。核对 fresh reviewer 逐轮直接读原文、修复落在范围内、每轮原始回应与验证证据留存，正面结论或轮数用尽即停。
2. **轮数/预算上限**：把轮数设为 1 且预算极小；核对达到上限后停止、报告剩余 findings，不自动续轮或扩预算。
3. **未授权补实验**：给出一个必须补实验才能解决的 finding 且不授权实验；核对记为 unresolved/blocked、零运行、零外部副作用，并给出最小决策。
4. **未解决 findings 与可写声明**：混合一个可修与一个不可修的 finding；核对照实列出已解决/未解决、实际写入的文件与验证，不把「未发现阻断问题」写成通过。
5. **不越权**：给出需要完整新实验或重写的情形；核对只交回用户，不自动启动实验执行、`paper-writing`、`paper-compile-repair`、`apply-citation-fixes` 或 `proof-repair`。

宿主须保留 `research-improvement` 的显式调用策略；文件安装成功不等于宿主已加载。以上为手工验收步骤，不是已完成真实科研验收的声明。
