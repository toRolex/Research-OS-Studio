---
name: experiment-audit
description: 实验完整性审计。用户要求审计实验是否真实完整，或已授权的 Validation／写作流程在形成 Claim 前需要独立核对时使用。
disable-model-invocation: true
---
<!-- argument-hint: "[协议、代码、配置、运行日志、原始结果、evaluator/ground truth 与 Claims 的路径；可指定报告位置和审查范围]" -->

# Experiment Audit

独立的、只读的实验完整性审查：判断**报告的实验是否真实、完整、可核对，以及是否按预先声明的协议执行**。它不执行实验，不修代码，不产生新结果。

## 核心原则：执行者只收集路径，独立审查者判定

- **执行者**只定位本次可读的材料路径和审查范围，不预先读取、总结、解释或筛选内容，也不参与完整性判定。
- **独立审查者**直接读取代码、evaluator、真值来源、配置、日志、原始结果和 Claims 本身，不使用执行者摘要、分数、排行榜或模型共识代替原始证据。
- 独立审查者不可用或不在本次授权内时，明确标注 **single-agent assessment; independent verification not performed**；不得冒充第二审查者，不得把自我检查记作独立判定。

## 角色与边界
Gate: write-path | before=report-write | approval=explicit-user | source=SKILL.md#角色与边界

- **角色**：默认是当前 Validation 或写作职责内的 显式调用或已授权正文级联 discipline；用户也可点名 standalone。父 Workflow 的调用是 caller，不是启动其他 Workflow 的许可。
- **输入**：用户明确给出的 protocol/计划、代码与配置、数据说明、每次 attempt 的日志和输出、分析材料、evaluator/ground truth、候选 Claims 及其声明范围。优先读原始文件和实际生成物；摘要、截图、表格或二手报告只能作为待核对线索。
- **解决范围**：先列出本次实际可读的材料、研究问题、实验单元、协议版本、尝试范围和 Claim scope。材料缺失、相互矛盾或无法区分版本时标为 `unknown`/`blocked`，不凭路径、文件名、时间或叙述推断。
- **资源**：仅使用已有且获授权的读取、解析和比较能力。缺少运行环境、依赖、远程存储或付费服务时报告缺口；不安装环境、不上传私有材料、不扩大资源授权。
- **写入**：默认在对话中返回 Markdown 报告。只有本次明确给出目标路径时才写入；复用已有报告前先读取，冲突时展示拟改范围并询问。不得改代码、协议、数据、evaluator、真值、结果、Claims 或论文正文。
- **停止**：不启动、重跑、取消、修复、筛选、删除或扩展实验，不修改 ground truth，不自动调用分析、Results-to-Claims、写作或其他 Workflow。需要新运行或材料修复时只提出单独授权的下一步。

## 审查流程

### 1. 建立材料账本

为每个输入建立可读的材料表：路径或来源、实际读取范围、所属 Project/Workstream（如有）、版本或提交、生成时间、关联 attempt、文件类型和可核对性。没有明确版本、范围或身份的字段写 `unknown`；不自行补齐统一 hash、digest、receipt 或 JSON 包装。

按类别清单逐项定位（只记路径，不预读内容）：

- 评价脚本：`*eval*`、`*metric*`、`*test*`、`*benchmark*`；
- 结果文件：`results/`、`outputs/`、`logs/` 下的原始 stdout/stderr、JSON、CSV、表格、缓存；
- 真值来源：评价脚本中数据加载指向的数据集、标签、答案或参考实现；
- 运行记录：实验日志、attempt 目录、失败/超时/取消记录；
- 声明：候选 Claims、报告、计划的 claim 文本及其声明范围；
- 配置：metric 定义、seed、阈值、数据划分、资源预算。

列出协议声明的：

- hypothesis、任务/数据边界、baseline、metric/estimand、比较和成功标准；
- 允许修改与必须保持不变的代码、配置、数据、seed、评估器和输出位置；
- 资源/时间预算、停止规则、重试规则、排除规则和计划的 attempt；
- evaluator、ground truth、分析脚本与报告所声称的证据链。

**完成条件**：每个可审查对象都有原始位置和读取状态；缺失对象、冲突声明及无法建立的关联已单独列出。

### 2. Protocol conformance：逐项比对声明与执行

只根据实际代码、命令、配置、日志和输出比对协议，逐项记录 `conforms`、`deviates` 或 `unknown`：

1. 执行的 commit、代码路径、依赖/环境、命令参数与协议版本；
2. 数据、预处理、样本划分、输入文件、seed、随机性控制和实验单元；
3. baseline、模型/方法配置、允许修改范围、指标实现、阈值与停止规则；
4. 资源消耗、超时、OOM、崩溃、重试、手工介入、提前停止和预算边界；
5. 输出清单、失败/部分结果、排除项、选择规则与最终报告覆盖。

每个偏差单独记录，即使它看似有利或没有改变数值；把"协议未声明"与"没有发生"区分开。protocol conformance 不能证明结果真实，也不能把事后采用的配置写成 preregistered。**一条证据线通过不替另一条通过。**

**完成条件**：每一项可观察的协议要求都有比对结论、材料定位和影响范围；未能观察的项明确保持 `unknown`。

### 3. Independent experiment integrity：直接读 primary artifacts

不先接受 evaluator 或执行者的结论，沿 A–F 从原始材料重建事实。判断问题与单项 FAIL／WARN 见 [完整性检查细则](references/integrity-checks.md)。检查面：

- **A.** Ground truth provenance
- **B.** Score normalization
- **C.** Result existence 与数字对应
- **D.** Dead code
- **E.** Scope
- **F.** Evaluation type
- **尝试完整性**
- **代码—运行对应**

在**不运行新实验**的前提下，用已存在的原始输出和透明计算步骤核对派生统计、聚合、排序、不确定性与图表；不能从材料完成重算时保留 `unknown`，不以模型心算或报告数字代替结果。

将每项事实分成 `observed`（primary artifact 直接显示）、`derived`（由已读材料透明推得）、`reported`（只在摘要/报告中出现）和 `unsupported`（现有材料不能支持）。只有前两类可作为审查依据；`reported` 必须回溯，`unsupported` 不得升级为通过。

**完成条件**：代码、evaluator/ground truth、每个结果和每个 attempt 都有直接读取状态；所有无法回溯的数字、遗漏或疑似 phantom result 已定位并标注。

### 4. 交叉检查与发现分级

将两条证据线分别汇总，禁止用一条线的结论覆盖另一条线。至少检查：

- evaluator 是否独立、完整、未被被评对象或执行者事后修改；
- ground truth 是否真实存在、来源清楚、覆盖声明任务，且不是 fake ground truth；
- 每个 reported result 是否有对应 primary bytes、输入、配置和 attempt；
- 失败、部分输出、负结果、异常和排除是否可见且理由一致；
- 代码、配置、日志、输出和报告是否属于同一实际运行，而非拼接材料；
- 报告是否遗漏比较、seed、checkpoint、数据子集或不利条件；
- Claim 是否超出 population、setting、metric、时间范围或实验设计所能支持的 scope。

对每个 Claim 逐条读取原文、条件、population/setting、时间范围、比较对象和证据引用，比较它与实际数据、评估器、attempt 集合及实验设计的范围；把"在该固定设置观察到"与"普遍有效、因果有效、优于所有方法、已复现或已证明"分开。

分级如下：

- `blocker`：关键 primary artifact、ground truth、attempt 身份或结果来源不可得，导致该审查范围不能判定；或存在明显伪造/不可核对证据链。
- `major`：evaluator/ground truth 不独立、结果与代码/运行不对应、关键失败被隐藏，或 Claim 明显超范围，足以改变结论可信度。
- `minor`：局部记录缺失、可复核性受损或有限范围偏差，不足以单独推翻核心结果。
- `note`：不影响当前判定的可读性、维护或未来复核建议。

每个发现包含：严重级别、证据类别（protocol conformance 或 independent integrity）、具体材料定位、观察事实、受影响的结果/Claim、为何影响审查、保守结论及需要用户另行授权的最小补救。不输出综合分数或用"整体质量"掩盖分项发现。

**完成条件**：每个发现都写明信号来源，并绑定实际读到的 primary artifact 或明确缺失项；两条证据线均有独立结论。

### 5. 报告与判定

返回自然 Markdown，使用 [审计报告模板](templates/audit-report.md) 组织：

1. `审查范围与材料账本`；
2. `Protocol conformance`（逐项结论与偏差）；
3. `Independent experiment integrity`（A–F、attempt、代码/结果对应的结论与定位）；
4. `发现`（按严重级别）；
5. `按 Claim 的支持边界`；
6. `缺失材料与未完成检查`；
7. `停止与建议`。

整体判定只允许：

- **PASS**：两条证据线在声明范围内均无 `blocker`/`major`，且关键 primary artifacts 可读；这不是研究结论、复现保证或人类接受。
- **FAIL**：已提供的材料明确违反协议或完整性约束，存在至少一个 `blocker`/`major`。
- **BLOCKED**：关键材料缺失或不可读，无法完成范围内的独立审查；不得因没有发现而写 PASS。

**完成条件**：审查范围、两条证据线、发现分级，以及整体 PASS／FAIL／BLOCKED 都已写出。齐了才停。Standalone 在对话或用户指定文件返回；composed 只贡献调用者指定 canonical report 的审计章节。
