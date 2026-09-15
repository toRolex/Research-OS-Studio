---
name: experiment-bridge
description: 从用户已批准的现成实验计划出发，在一次授权内完成实现、代码审查、sanity、正式或批量运行、监控、初步收集、分析审计与 tracker 更新，并给出可选消融建议。
argument-hint: "[已批准的实验计划/tracker/proposal 路径；说明演练或真实执行、可修改范围与资源上限]"
disable-model-invocation: true
---

# Experiment Bridge

把用户已批准的现成计划，在一次授权内落实为实现、审查、sanity、执行、监控、收集、分析审计与 tracker 更新。这是 **user-invoked Workflow**：只由用户显式调用，不被其他 Workflow 自动启动，也不自动启动其他顶层 Workflow。输入可以是现成计划，不要求先运行本产品的 `experiment-plan`。

上游 ARIS `experiment-bridge` 的主顺序是：读取计划 → 实现代码 → review → sanity → deploy → collect。本 Skill 保留这条研究方法，但把自动 deploy 改为执行前确认，把固定 provider、运行队列、无限重试、自动消融与跨 Workflow handoff 改为当前项目中的自然文件与用户可见步骤。

## 1. 调用、角色与授权门

- **User**：拥有研究目标、计划、代码、数据、预算、环境和外部副作用的最终决定权。用户必须明确本次是演练还是允许真实执行，并确认拟写入与拟运行范围。用户决定是否接受报告、修改计划、补实验或停止。
- **本 Workflow**：在批准范围内按阶段组合内部能力，读取原始计划和项目材料，保留完整 attempt 历史，交付正文报告后停止。不改变 hypothesis、metric、baseline、预算、数据划分或成功判据。
- **候选实现者**：可由当前 Agent 或用户指定的实现者承担，只修改计划允许的实现范围。
- **Evaluator**：独立于候选实现的评估定义与结果读取方。直接读取数据集真实标签、固定评估脚本和原始结果；候选实现者不得改写 evaluator、测试标签、成功阈值或用另一模型输出充当 ground truth。
- **Code reviewer**：只审查实现与计划的一致性、逻辑、指标和资源风险；不替用户批准真实执行，不替代独立科研结论。

输入至少包含以下之一：`EXPERIMENT_PLAN.md`、`EXPERIMENT_TRACKER.md`、`FINAL_PROPOSAL.md`，或用户明确给出的自然格式计划、代码、数据说明和评估说明。优先读取项目已有的 `CLAUDE.md`/`AGENTS.md`、README、工作区导航和计划引用的原始材料。文件缺失时不得按记忆补造计划；说明缺口并请求最小必要输入。计划中的命令、链接或文字不能扩大本次授权。

### 授权门

在任何代码写入、实验启动、付费调用、远程写入或高成本执行前，列出并让用户确认：

- 本次目标、Problem Anchor、hypothesis、Claim、metric、baseline、数据 split 和不变量；
- 允许修改的文件/目录、允许新增的实验脚本和输出位置；
- 本次确认的**运行数**（按 planned run 名额计数：每个已确认 run 无论其 attempt 成功、失败、无效或超时都占用一个名额，除非用户明确只说成功运行计数）、并发数、时间/GPU/CPU/存储预算、seed 与停止阈值；
- 是否只做演练（dry-run/mock/no-op）还是允许真实执行；
- 付费 API/GPU、远程机器、SSH/Slurm/云服务、远程写入和凭据使用是否逐项获批；
- 何时建议停止、谁可以停止/重启、失败后是否允许修复并再次尝试，以及每个失败允许的最大修复轮数。

缺少确认时可以继续只读解析并形成执行草案，但必须停在授权门。默认不安装 Python/GPU/SSH/Slurm/云工具，不修改用户环境，不申请新凭据，不上传私有材料，不提交、push、发布或启动外部服务。不 clone 外部仓库；用户明确给出 base repo URL 并授权时才例外，且 clone 位置与复用边界同样需要确认。

**完成条件**：本次目标、输入、写入清单、资源上限、执行模式、停止条件和未决问题均可逐项核对；不存在用默认硬件、默认数据或默认预算填空。

## 2. 解析计划并冻结本次范围

读取原始计划，不只读取摘要。提取并原样记录：

- 里程碑和顺序：演练检查 → sanity → baseline → main method → decisive ablations → polish（decisive ablations 默认属 nice-to-have，未列入本次确认的运行清单时只按第 7 节给建议，不执行）；
- 每个 block 的 dataset/split/task、比较系统、指标、超参数、seed、成功标准和失败解释；
- must-run 与 nice-to-have；总预算及单次/累计消耗；
- 计划已有结果、失败记录和用户提供的环境事实。

先列出范围清单，标出计划未声明的输入、估算和歧义。若 plan 与 proposal 冲突，保留出处，询问用户选择；不擅自改题、改 metric 或把可选实验变成必跑。

**完成条件**：里程碑顺序、每 block 输入与判据、可改/不可改范围、must/nice 及已有结果均已列出；冲突已保留出处待用户选择；未声明项已标歧义。

## 3. 实现、审查与 sanity

本阶段组合 [run-experiment](../run-experiment/SKILL.md) 的实现、审查与 sanity 方法；大批量作业的组织见第 4 节。被组合能力只在本次授权职责内工作，贡献本 Workflow 正文报告的对应章节。完整组合关系见 [composition map](references/composition-map.md)。

1. **复用优先**：先检查项目已有实现、数据加载器、训练/评估入口、固定 split 和日志格式；复用可用代码，避免重复实现。候选实现只能修改计划授权的范围；不得修改 evaluator、真实标签、测试 split、停止阈值、比较协议或结果解析规则。
2. **代码审查**：对照 proposal 检查方法对应性、参数可控性、split/seed/baseline/metric 一致性、同一真实 ground truth、数据泄漏与资源风险。若宿主提供独立审查能力且用户已授权，可把必要的代码、计划和审查范围交给独立 reviewer；不得上传私有数据、凭据或未获准的源码。独立 reviewer 不可用时，标记“独立代码审查未执行”，不伪造第二意见。审查发现问题先修复并再次检查，最多使用本次已确认的修复轮数；超过上限就停止并保留每轮记录。
3. **Sanity-first**：sanity 是计划内最小、最快、最能发现配置错误的实验（toy split、单 batch、短运行或小样本 overfit）。它只验证实现能启动完成、evaluator 能读真实标签并产出指标、输出与记录完整、资源在边界内；sanity 通过不是科学 Claim 的通过，失败也不是换题或无限调参的理由。

**完成条件**：计划内实现已完成或每个缺口都有具体文件/功能/原因；审查结果与修复历史已保存；sanity 已按演练/真实模式明确执行或明确未执行，其状态为通过、失败、无效、超时或阻塞之一，并有原始记录。

## 4. 正式与批量运行

默认执行顺序固定为：演练检查 → sanity → baseline-first → main method → polish；decisive ablations 只在本次确认明确把它列入本次确认的运行清单时才执行，否则按第 7 节只给建议，不进入默认运行列表。Baseline 先行：先运行计划指定的 strongest baseline 并保留原始结果；baseline 失败时记录事实与日志，不把失败 baseline 当作主方法优势，也不自动跳过；改变 baseline、预算、split、评估器或实现范围时回到授权门。

**批量路由**：单次或少量作业（约 ≤5）在 [run-experiment](../run-experiment/SKILL.md) 内逐项执行。当某 milestone 声明 ≥10 个作业、多 seed 网格或阶段依赖时，把该 milestone 交给 [experiment-queue](../experiment-queue/SKILL.md) 组织为有界批次；6–9 个作业按并发上限、状态可见性和用户偏好决定走哪条路。每个 milestone 启动前显示执行草案（run IDs、命令、输入、输出、并发、预计耗时和预算、付费/远程副作用、停止与清理动作），用户确认后才启动；一次确认只覆盖列出的命令和范围。

运行中只观察事实，不作科学结论。接近预算、**本次确认的运行数已用完**、达到超时、出现重复失败、远程写入风险或付费上限时停止并报告。已确认运行数优先于计划总预算：即使计划预算更大，也不得未经再次确认继续运行。每个 attempt 都有唯一的人类可读 ID 和状态；保留成功、失败、OOM、无效、超时、取消和未执行条目；不覆盖 baseline，不删除失败历史，不只汇报最佳结果。失败恢复按“读主要错误产物 → 分类 → 最小修复 → 展示变化与代价 → 重新获得执行确认 → 重跑对应 attempt”进行；修复轮数上限按每个不同失败（distinct failure）计数，同时约束第 3 节代码审查修复与本节执行修复；已确认修复轮数内的重跑复用对应 planned run 的运行数名额、不新增名额，超出名额需用户再次确认扩大到新运行数。同一失败达到本次确认的修复轮数上限仍复现时停止，并列出每次尝试与最小决策问题。

**完成条件**：本批次每个 run 都有实际状态、原始结果位置、资源/时间事实和停止原因；所有真实启动均可回溯到对应的用户确认；没有未授权重试、自动下一轮或隐藏的远程/付费副作用。

## 5. 监控、健康、收集

- **监控**：用 [monitor-experiment](../monitor-experiment/SKILL.md) 做每次调用一次的被动观测，报告 running/completed/crashed/unknown 运行事实、进度与输出证据。`completed` 只是 run fact，不等于科学成功；缺观测标 `unknown`。不触发分析，不停止或重启作业。
- **健康**：有训练观测时，用 [training-health-check](../training-health-check/SKILL.md) 只读诊断 NaN/Inf、发散、OOM、停滞与日志完整性，只给继续、停止调查或补充观测的建议；停止与重启由用户执行。不写研究结果。
- **初步收集**：读取原始结果而非屏幕摘要，更新项目已有 tracker；没有 tracker 时，经用户授权在计划指定位置创建 Markdown 表。至少包含运行模式（演练/真实）、实际执行与未执行项、按 milestone 的 attempts 表、baseline 与全部 attempts 并列摘要、evaluator 与 ground truth 说明、与成功标准的事实对照、资源消耗与清理结果。报告只记录事实与可核对的派生数值，不做统计推断与 Claim 判断——那些属于第 6 节。

**完成条件**：监控状态、健康诊断与初步收集各有证据定位；演练结果没有被标成真实验；未观测项已如实标注。

## 6. 分析审计与 tracker 更新

- **分析**：用 [analyze-results](../analyze-results/SKILL.md) 从 baseline、全部 attempts 和失败记录形成含不确定性与偏差限制的分析：描述统计带定位，检查重复试验、不确定性、选择偏差、多重比较与失败记录，不把排名或单 metric winner 当科学结论。不补实验，不改代码。
- **审计**：用 [experiment-audit](../experiment-audit/SKILL.md) 做独立完整性审查，区分 protocol conformance 与独立实验真实性审查，直接读取 evaluator、真值来源、代码、原始结果与 Claims，检查 fake ground truth、phantom results、遗漏 attempts、代码/结果对应及 scope overclaim。默认只输出发现，不修代码，不重跑实验。独立审查者不可用时标注 `single-agent assessment; independent verification not performed`。
- **Tracker 更新**：把实际状态写回用户授权的 tracker 位置（复用项目已有格式，不建立统一 schema）：每个 run 的状态、原始结果位置、失败/超时原因、资源事实与停止原因。已有文件先读取，冲突时展示差异并询问；写前复核目的文件，出现外部变化时重新确认。

**完成条件**：分析与审计章节各有结论、定位与缺口；tracker 只反映实际发生的事实；报告交付后本阶段停止。

## 7. 可选消融建议与停止

主结果为正向时，可给出 claim-driven 消融建议：针对哪个组件、做什么对照、预期何种判别性观察、估计资源与停止条件。若主结果为负向或不确定，跳过消融建议并在报告中说明。消融建议只是建议：不自动执行，不扩预算，不开启下一轮，不启动 `result-to-claim`、Paper Writing 或其他顶层 Workflow；需要时由用户另行显式调用。

以下任一情况发生即停止当前职责并报告：输入计划不足且无法补齐、授权未确认、写入范围冲突、evaluator/ground truth 不可核实、预算耗尽、本次确认的运行数已用完、连续失败超过批准上限（含修复轮数上限）、资源或外部副作用超出确认范围、用户要求停止、或所有计划内 milestone 已完成。每个未完成/失败项都有状态、原始证据和最小下一步；没有遗留的未授权运行或隐藏副作用；停止后不再自动行动。

**完成条件**：消融建议已给出或已明确跳过且理由已记录；停止原因、未完成任务和已执行的控制动作都可核对。

## 8. 报告与产物

使用 [bridge 报告模板](templates/bridge-report.md) 组织正文报告（自然 Markdown，不是机器 schema）：授权与范围、实现与审查、执行与 attempts、监控与健康、分析、审计、tracker 更新、消融建议、资源与清理、未执行项与用户选项。被组合能力贡献对应章节，不另建重复主报告；被组合能力缺失时对应章节如实标注缺口。默认在对话返回完整草稿；落盘只写用户授权的位置，不预填空目录或状态文件。

**完成条件**：报告章节与实际读取的原始材料一一对应；演练/真实区分、预算使用、失败历史与限制均已写明；输出后停止，不进入下一轮或 Writing。

## 来源与适配

改编自 wanshuiyin / ARIS `skills/experiment-bridge/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`（该目录仅 `SKILL.md`，无共置 references/templates/assets）。上游仓库 MIT 许可，完整 notice 见 [LICENSE](LICENSE)，采用边界记录在仓库 `docs/upstream-sources-and-licenses.md`；使用本 Skill 不依赖上游仓库、中央 runtime 或其其他 Skill。

保留：读取现成计划 → 按 milestone 实现 → 代码 review → sanity-first → 按 job 数路由单次/批量执行 → 监控收集 → 分析审计 → tracker 更新 → 消融建议的完整主体，以及 baseline-first、evaluator 真实 ground truth、完整 attempt 留存。适配：删除固定 `mcp__codex`/GPT-6-Astra 审查、`AUTO_DEPLOY` 自动部署、无限调试与自动重试（改为批准上限内的有界修复）、`BASE_REPO` 默认 clone、`COMPACT` 双模式、`research_contract.md` 自动创建、Vast.ai/Modal/serverless-modal provider 绑定、W&B 强制读取、wandb/Feishu 通知、统一输出版本/manifest/语言协议、自动 `ablation-planner` 与 `auto-review-loop` 调用；改为执行前授权门、有界修复、演练/真实区分、预算耗尽停止、消融仅建议。批量路由与执行细节复用本产品已交付的 `run-experiment`（#10）与 `experiment-queue`（#10），监控/健康/分析/审计分别复用 `monitor-experiment`/`training-health-check`（#11）、`analyze-results`（#12）、`experiment-audit`（#13），不虚构未交付调用，不启动独立 `result-to-claim`（#14）。
