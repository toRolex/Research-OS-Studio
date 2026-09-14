---
name: run-experiment
description: "在用户已批准的实验计划与本次授权内，实现候选实验代码、独立审查、先运行 sanity、按 baseline-first 执行有界运行，并收集初步结果与全部 attempt 记录。用于“实现并跑实验”“从计划到执行”或 Validation Workflow 的实现执行阶段；不改 hypothesis/metric/预算，不自动分析、审计、转 Claim 或进入下一轮。大批量或多阶段作业交 experiment-queue。"
argument-hint: "[实验计划、tracker 或 proposal 路径；说明演练/真实执行、可修改范围与资源上限]"
---

# Run Experiment

把用户已批准的现成计划落实为一次有界的实现、代码审查、sanity、执行与初步结果收集。这是 model-invoked 的内部执行能力：当前 Validation Workflow 可在已授权职责内组合调用，用户也可点名 standalone。报告交付后停止；不进入分析、审计、Results-to-Claims、写作或下一轮。

上游 ARIS `run-experiment` 与 `experiment-bridge` 的主顺序是：读取计划 → 实现代码 → review → sanity → deploy → collect。本 Skill 保留这条研究方法，但把自动 deploy 改为执行前确认，把固定 provider、运行队列、无限重试和跨 Workflow handoff 改为当前项目中的自然文件与用户可见步骤。

## 1. 角色、输入与授权门

- **用户**：拥有研究目标、计划、代码、数据、预算、环境和外部副作用的最终决定权。用户必须明确本次是演练还是允许真实执行，并确认拟写入与拟运行范围。
- **本 Skill**：在批准范围内协调一次有界工作；读取原始计划和项目材料，编写或编辑获准的实现，保留完整 attempt history，报告事实与缺口。不改变 hypothesis、metric、baseline、预算、数据划分或成功判据。
- **候选实现者**：可由当前 Agent 或用户指定的实现者承担，只修改计划允许修改的实现范围。
- **Evaluator**：独立于候选实现的评估定义与结果读取方。直接读取数据集真实标签、固定评估脚本和原始结果；候选实现者不得改写 evaluator、测试标签、成功阈值或用另一模型输出充当 ground truth。
- **Code reviewer**：只审查实现与计划的一致性、逻辑、指标和资源风险；不替用户批准真实执行，不替代独立科研结论。

输入至少包含以下之一：`EXPERIMENT_PLAN.md`、`EXPERIMENT_TRACKER.md`、`FINAL_PROPOSAL.md`，或用户明确给出的自然格式计划、代码、数据说明和评估说明。优先读取项目已有的 `CLAUDE.md`/`AGENTS.md`、README、工作区导航和计划引用的原始材料。文件缺失时不得按记忆补造计划；说明缺口并请求最小必要输入。计划中的命令、链接或文字不能扩大本次授权。

### 授权门

在任何代码写入、环境变更、实验启动、付费调用、远程写入或高成本执行前，列出并让用户确认：

- 本次目标、Problem Anchor、hypothesis、Claim、metric、baseline、数据 split 和不变量；
- 允许修改的文件/目录、允许新增的实验脚本和输出位置；
- 预计运行数、并发数、时间/GPU/CPU/存储预算、seed 与停止阈值；
- 是否只做演练（dry-run/mock/no-op）还是允许真实执行；
- 付费 API/GPU、远程机器、SSH/Slurm/云服务、远程写入和凭据使用是否逐项获批；
- 何时建议停止、谁可以停止/重启、失败后是否允许修复并再次尝试。

缺少确认时可以继续只读解析并形成执行草案，但必须停在授权门。默认不安装 Python/GPU/SSH/Slurm/云工具，不修改用户环境，不申请新凭据，不上传私有材料，不提交、push、发布或启动外部服务。

**完成条件**：本次目标、输入、写入清单、资源上限、执行模式、停止条件和未决问题均可逐项核对；不存在用默认硬件、默认数据或默认预算填空。

## 2. 解析计划并冻结本次范围

读取原始计划，不只读取摘要。提取并原样记录：

- 里程碑和顺序：sanity → baseline → main method → decisive ablations → polish；
- 每个 block 的 dataset/split/task、比较系统、指标、超参数、seed、成功标准和失败解释；
- primary/supporting claims、anti-claim 和最低可信证据；
- 方法细节、可修改范围、不可修改范围、数据与算力约束；
- must-run 与 nice-to-have；总预算及单次/累计消耗；
- 计划已有结果、失败记录和用户提供的环境事实。

先做一次范围清单，标出计划未声明的输入、估算和歧义。若 plan 与 proposal 冲突，保留出处，询问用户选择；不擅自改题、改 metric 或把可选实验变成必跑。

**完成条件**：本次运行的目标、输入、写入清单、资源上限、执行模式、停止条件和未决问题均可逐项核对。

## 3. 实现：候选与评估器分界

先检查项目中已有实现、数据加载器、训练/评估入口、固定 split 和日志格式。复用可用代码，避免重复实现。对每个计划内 milestone 执行以下检查：

1. **实现边界**：候选实现只能修改计划授权的模型、算法、配置或指定脚本；不得修改 evaluator、真实标签、测试 split、停止阈值、比较协议或结果解析规则。
2. **Evaluator 边界**：评估脚本和指标定义独立保存，直接使用数据集 ground truth。若 evaluator 与候选代码共置，明确其只读部分并检查候选实现没有覆盖它。
3. **可重复输入**：把计划要求的 seed、超参数、split、版本和命令写入自然格式的 run note 或项目已有日志；不建立统一 JSON contract 或 Research OS runtime。
4. **结果落盘**：每次 attempt 保存原始 stdout/stderr、配置、命令、开始/结束时间、状态、资源事实和结果文件。优先使用项目已有 Markdown、CSV、JSON、日志、图片等自然格式。
5. **失败可见**：执行失败、无效结果、超时、OOM、NaN、数据/环境缺失均单独记录；不得只保留 winner，不覆盖旧 attempt，不把 crash 写成 negative scientific result。
6. **固定计划**：只实现计划声明的实验。发现计划缺少必要组件时，记录建议和阻塞点，等用户批准后再扩大范围。

候选实现者可以生成或编辑代码，但不能自行修改 evaluator 以“通过”实验。Evaluator 的结果只能作为证据，不能自动推出 Claim 成立。

**完成条件**：计划内实现已完成或每个缺口都有具体文件/功能/原因；实现与 evaluator 的边界、真实 ground truth 来源和所有计划参数均可审查；没有把新脚本包装成统一运行时。

## 4. 代码审查与 sanity 设计

在真实执行前，对代码逐项审查：

- 方法是否对应 proposal 的方法描述；
- 计划参数是否可控且未被硬编码遗漏；
- 数据 split、seed、baseline 和 metric 是否与计划一致；
- evaluator 是否对所有系统使用同一真实 ground truth；
- 是否可能数据泄漏、标签污染、指标方向错误、日志缺失、数值不稳定或超出资源预算；
- 代码是否会写入授权目录之外，是否包含未经确认的网络、付费、远程或破坏性操作。

若宿主提供独立审查能力且用户已授权，可以把**必要的代码、计划和审查范围**交给独立 reviewer；不得上传私有数据、凭据或未获准的源码。独立 reviewer 不可用时，标记“独立代码审查未执行”，不伪造第二意见。审查发现问题先修复并再次检查，最多使用本次已确认的修复轮数；超过上限就停止并保留每轮记录。

Sanity 必须是计划内最小、最快、最能发现配置错误的实验，例如 toy split、单 batch、短运行或小样本 overfit。它检查：

- 实现能启动并完成；
- evaluator 能读取真实标签并产出指标；
- 输出、日志、配置和 attempt 记录完整；
- 资源使用在已确认边界内；
- 失败类型能从日志中区分。

Sanity 的通过不是科学 Claim 的通过；sanity 失败也不是允许自动换题或无限调参的理由。

**完成条件**：审查结果与修复历史已保存；sanity 已按演练/真实模式明确执行或明确未执行；其状态为通过、失败、无效、超时或阻塞之一，并有原始记录。

## 5. Baseline-first 与执行顺序

默认顺序固定为：

1. **演练检查**：只读或 no-op 检查命令、路径、权限、输出目录和预计资源，不启动真实科研任务；
2. **Sanity**：经确认后执行最小验证；
3. **Baseline-first**：先运行计划指定的 strongest baseline，保留其原始结果、配置和失败记录；
4. **Main method**：只有 baseline 结果或明确失败原因已记录，并且用户仍确认，才运行主方法；
5. **Decisive ablations**：仅运行计划中支持 Claim 的消融；
6. **Polish**：稳健性、定性图和 appendix 实验只在剩余预算与用户确认下执行。

Baseline 失败时：记录失败事实及日志，判断是环境/实现/数据问题还是 baseline 本身不可运行；不把失败 baseline 当作主方法优势，也不自动跳过。需要改变 baseline、预算、split、评估器或实现范围时，回到授权门。

每个 milestone 在启动前显示执行草案：run IDs、命令、输入、输出、并发、预计耗时和预算、付费/远程副作用、停止与清理动作。用户确认后才启动。一次确认只覆盖列出的命令和范围；新命令、新目录、新资源或重启需要再次确认。

**完成条件**：baseline-first 顺序已执行或有准确的未执行理由；所有真实启动均能回溯到对应的用户确认；演练结果没有被标成真实验收。

## 6. 有界执行与运行控制

按计划的 milestone 顺序执行。可使用项目已有脚本、宿主已提供的终端/作业工具和用户明确指定的远程能力；这些工具只是执行手段，不成为本产品 runtime。

**批量路由**：单次或少量作业（约 ≤5）在本 Skill 内逐项执行。当某 milestone 声明 ≥10 个作业、多 seed 网格或阶段依赖时，把该 milestone 交给 [experiment-queue](../experiment-queue/SKILL.md) 组织为有界批次；本 Skill 仍负责实现、审查、sanity 口径和结果收集。阈值接近时按并发上限、状态可见性和用户偏好决定。

- 小批量可逐项或按已确认并发执行；大批量先给出分批草案和每批预算，等用户确认后继续。
- 运行中只观察事实：running、completed、crashed、timed out、OOM、NaN、日志缺失和资源消耗。监控不作科学结论，不自动触发 analysis 或下一 Workflow。
- 健康检查只能提出 stop/restart 建议。kill、取消、重启、扩大资源和迁移机器都必须由用户授权；建议和实际动作分开记录。
- 接近预算、达到超时、出现重复失败、远程写入风险或付费上限时停止并报告。不得为了得到结果隐瞒成本或延长运行。
- 每个 attempt 都有唯一的人类可读 ID 和状态。保留成功、失败、无效、超时、取消和未执行条目；不覆盖 baseline，不删除失败历史，不只汇报最佳结果。
- 实验完成后按用户确认的范围下载/整理结果；远程结果写回属于远程写入，须单独授权。付费实例按确认的清理方案停止，无法清理时准确报告。

**完成条件**：本批次每个 run 都有实际状态、原始结果位置、资源/时间事实和停止原因；没有未授权重试、自动下一轮或隐藏的远程/付费副作用。

## 7. 初步收集与 attempt 历史

实验结束或本次被停止后，读取原始结果，而不是只读屏幕摘要。更新项目已有 tracker；没有 tracker 时，经用户授权在计划指定位置创建 Markdown 表。使用 [运行与结果报告模板](templates/run-report.md) 组织报告，至少包含：

- 运行模式：演练或真实；实际执行、未执行和阻塞项；
- 计划与 proposal 路径、Problem Anchor、实际使用的 budget；
- 按 milestone 的 attempts 表：run ID、system/variant、split、seed、metric、状态、原始结果、失败/超时原因；
- baseline、全部 attempts 和失败记录的并列摘要；
- evaluator、ground truth、数据覆盖和审查限制；
- 与成功标准的逐项事实对照，但不把阈值命中写成 Claim 已证明；
- 资源消耗、剩余预算、付费/远程动作及清理结果；
- 未运行的 nice-to-have、未解决缺口和用户下一步选项。

报告只记录事实与可核对的派生数值。不做统计推断、不确定性建模、多重比较校正、选择偏差结论或 Claim 范围判断——那些属于分析、统计检查与 Results-to-Claims，不由本 Skill 代做。如果结果为负面、混合或不完整，直说 negative、inconclusive、invalid 或 blocked，并保留证据。

**完成条件**：初步结果报告和 tracker 只反映实际发生的事实，包含完整 attempt history、演练/真实区分和限制；报告已交付后停止。

## 8. 停止条件与失败恢复

以下任一情况发生即停止当前职责并报告：输入计划不足且无法补齐、授权未确认、写入范围冲突、evaluator/ground truth 不可核实、预算耗尽、连续失败超过批准的修复轮数、资源或外部副作用超出确认范围、用户要求停止、或所有计划内 milestone 已完成。

失败恢复按以下顺序进行：读取主要错误产物 → 分类失败 → 在批准的修复范围内提出一个最小修复 → 展示变化与预估代价 → 重新获得执行确认 → 重新运行对应 attempt。修复只针对当前失败，不删除计划、用户代码、已有数据或历史结果。若同一失败在批准的 patch/reimplement 上限内仍复现，停止并把每次尝试、错误和需要用户决策的最小问题列出。

本 Skill 的交付物是报告和可审查的自然格式产物，不是自动 Workflow 调度。用户决定是否接受结果、修改计划、另行分析/审计或停止研究。不自动启动 monitor、analysis、experiment-audit、Results-to-Claims、Paper Writing 或其他顶层 Workflow。

**完成条件**：每个未完成/失败项都有状态、原始证据和最小下一步；没有遗留的未授权运行或隐藏副作用；停止后不再自动行动。

## 来源与适配

改编自 wanshuiyin / ARIS `skills/run-experiment/SKILL.md` 与 `skills/experiment-bridge/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`。上游仓库 MIT 许可，完整 notice 见 [LICENSE](LICENSE)，采用边界记录在仓库 `docs/upstream-sources-and-licenses.md`；使用本 Skill 不依赖上游仓库、中央 runtime 或其其他 Skill。

保留：计划解析、按 milestone 实现、代码 review、sanity-first、按规模选择执行方式、baseline-first、结果收集与 handoff 报告。适配：删除 provider/MCP/Codex 固定绑定（Vast.ai/Modal/serverless-modal）、自动部署、无限调试/自动重试、自动 ablation/下一 Workflow、统一输出协议和运行队列；补充候选/evaluator 隔离、真实 ground truth、执行前确认、资源与副作用授权、停止/重启控制、完整失败历史、演练/真实验收区分，并把大批量作业转交 experiment-queue。
