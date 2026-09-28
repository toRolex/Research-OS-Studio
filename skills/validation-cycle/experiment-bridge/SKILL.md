---
name: experiment-bridge
description: 从用户已批准的现成实验计划出发，在一次授权内完成实现、代码审查、sanity、正式或批量运行、监控、初步收集、分析审计与 tracker 更新，并给出可选消融建议。
disable-model-invocation: true
---
<!-- argument-hint: "[已批准的实验计划/tracker/proposal 路径；说明演练或真实执行、可修改范围与资源上限]" -->

# Experiment Bridge

用户已批准的现成计划，在一次授权内按阶段组合内部能力。这是 **user-invoked Workflow**：只由用户显式调用。输入可以是现成计划，不要求先运行 `experiment-plan`。

能力、阶段、报告章节见 [composition map](references/composition-map.md)。正文只写何时组合、交哪一节、与子 skill 的差额。子 skill 的执行细则以子 skill 为准。

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
- 本次确认的**运行数**（planned run 名额的计数差额见第 4 节）、并发数、时间/GPU/CPU/存储预算、seed 与停止阈值；
- 是否只做演练（dry-run/mock/no-op）还是允许真实执行；
- 付费 API/GPU、远程机器、SSH/Slurm/云服务、远程写入和凭据使用是否逐项获批；
- 何时建议停止、谁可以停止/重启、失败后是否允许修复并再次尝试，以及每个失败允许的最大修复轮数。

缺少确认时可以继续只读解析并形成执行草案，但必须停在授权门。默认不安装 Python/GPU/SSH/Slurm/云工具，不修改用户环境，不申请新凭据，不上传私有材料，不提交、push、发布或启动外部服务。不 clone 外部仓库；用户明确给出 base repo URL 并授权时才例外，且 clone 位置与复用边界同样需要确认。

**完成条件**：本次目标、输入、写入清单、资源上限、执行模式、停止条件和未决问题均可逐项核对；不存在用默认硬件、默认数据或默认预算填空。

## 2. 解析计划并冻结本次范围

读取原始计划，不只读取摘要。提取并原样记录：

- 里程碑和顺序：演练检查 → sanity → baseline → main method → decisive ablations → polish（消融默认见第 4 节）；
- 每个 block 的 dataset/split/task、比较系统、指标、超参数、seed、成功标准和失败解释；
- must-run 与 nice-to-have；总预算及单次/累计消耗；
- 计划已有结果、失败记录和用户提供的环境事实。

先列出范围清单，标出计划未声明的输入、估算和歧义。若 plan 与 proposal 冲突，保留出处，询问用户选择；不擅自改题、改 metric 或把可选实验变成必跑。

**完成条件**：里程碑顺序、每 block 输入与判据、可改/不可改范围、must/nice 及已有结果均已列出；冲突已保留出处待用户选择；未声明项已标歧义。

## 3. 实现、审查与 sanity

本阶段组合 [run-experiment](../run-experiment/SKILL.md) 的实现、审查与 sanity。执行细则留在该 skill。

- **何时**：授权门通过，且本次确认包含实现或 sanity。
- **交哪一节**：实现范围、审查结果、sanity 状态。
- **差额**：修复轮数上限与第 4 节执行修复共用同一计数（见第 4 节）。独立 reviewer 不可用时，该节标“独立代码审查未执行”。

**完成条件**：该节已填，或缺口已标明；sanity 状态为通过、失败、无效、超时或阻塞之一。

## 4. 正式与批量运行

执行细则留在 [run-experiment](../run-experiment/SKILL.md)；有界批次的波次、OOM 与恢复留在 [experiment-queue](../experiment-queue/SKILL.md)。

- **何时 · 消融**：decisive ablations 默认不执行。只有本次确认的运行清单点名它时才跑；否则第 7 节只给建议。
- **何时 · 批量**：某 milestone 的作业数 ≤5，或并发上限与逐作业状态在 run-experiment 内可见：留在 run-experiment。作业数 ≥10、多 seed 网格，或阶段依赖：交给 experiment-queue。6–9：并发上限或逐作业状态不可见就走 queue，否则留在 run-experiment。
- **交哪一节**：run-experiment 交 attempts 与停止原因；queue 交批次清单、波次状态与 attempt 汇总。
- **差额 · 运行名额**：每个已确认 planned run 占用一个名额，无论 attempt 成功、失败、无效或超时，除非用户明确只按成功运行计数。已确认运行数优先于计划总预算。已确认修复轮数内的重跑复用该 planned run 的名额；超出需再次确认扩大运行数。修复轮数按每个不同失败计数，同时约束第 3 节代码审查修复与本节执行修复。

**完成条件**：本批次每个 run 都有实际状态、原始结果位置、资源/时间事实和停止原因；真实启动可回溯到对应确认。

## 5. 监控、健康、收集

- **监控**：有运行中的作业时，组合 [monitor-experiment](../monitor-experiment/SKILL.md)，每次调用一次。交运行事实章节。差额：`completed` 在本报告里只是 run fact，科学判断留第 6 节。
- **健康**：有训练观测时，组合 [training-health-check](../training-health-check/SKILL.md)。交健康章节。差额：停止与重启仍由用户执行，本 Workflow 只收录建议。
- **初步收集**：读取原始结果，更新已授权 tracker。交 attempts 事实表。统计与 Claim 留第 6 节。

**完成条件**：三节各有证据定位，或对应能力未组合并已标明；演练结果没有被标成真实验。

## 6. 分析审计与 tracker 更新

- **分析**：已有完整结果时，组合 [analyze-results](../analyze-results/SKILL.md)。交分析章节。差额：它的报告嵌进本报告，不另建主报告。
- **审计**：形成 Claim 前需要核对时，组合 [experiment-audit](../experiment-audit/SKILL.md)。交审计章节。差额：独立审查者不可用时该节标 `single-agent assessment; independent verification not performed`。
- **Tracker**：把实际状态写回用户授权的 tracker。已有文件先读，冲突时展示差异并询问。

**完成条件**：分析与审计章节各有结论、定位与缺口，或未组合并已标明；tracker 只反映实际发生的事实。

## 7. 可选消融建议与停止

主结果为正向，且消融未列入本次确认的运行清单时，写 claim-driven 消融建议：针对哪个组件、做什么对照、预期何种判别性观察、估计资源与停止条件。主结果为负向或不确定时，跳过并写明理由。建议留在报告里。

以下任一情况发生即停止当前职责并报告：输入计划不足且无法补齐、授权未确认、写入范围冲突、evaluator/ground truth 不可核实、预算耗尽、本次确认的运行数已用完、连续失败超过批准上限（含修复轮数上限）、资源或外部副作用超出确认范围、用户要求停止、或所有计划内 milestone 已完成。每个未完成/失败项都有状态、原始证据和最小下一步；没有遗留的未授权运行或隐藏副作用；停止后不再自动行动。

**完成条件**：消融建议已给出或已明确跳过且理由已记录；停止原因、未完成任务和已执行的控制动作都可核对。

## 8. 报告与产物

使用 [bridge 报告模板](templates/bridge-report.md) 组织正文报告（自然 Markdown，不是机器 schema）：授权与范围、实现与审查、执行与 attempts、监控与健康、分析、审计、tracker 更新、消融建议、资源与清理、未执行项与用户选项。被组合能力贡献对应章节，不另建重复主报告；被组合能力缺失时对应章节如实标注缺口。默认在对话返回完整草稿；落盘只写用户授权的位置，不预填空目录或状态文件。

**完成条件**：报告章节与实际读取的原始材料一一对应；演练/真实区分、预算使用、失败历史与限制均已写明；输出后停止，不进入下一轮或 Writing。
