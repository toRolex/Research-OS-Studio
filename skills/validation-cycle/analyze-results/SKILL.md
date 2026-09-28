---
name: analyze-results
description: 分析已完成结果的统计可信度。用户问“结果怎么样／可信吗”，或已授权的 Validation 职责需要分析已完成结果时使用。
---
<!-- argument-hint: "[baseline、结果文件、attempt 记录与待答问题的路径；可指定报告位置]" -->

# Analyze Results

从 baseline、全部 attempts 和失败记录形成含不确定性与偏差限制的结果分析。它回答“已有结果实际显示了什么、支撑边界在哪里”，不回答“该做什么新实验”，更不把一次胜出写成结论。

## Scope and authorization

- **Role:** model-invoked internal capability within the caller's authorized research scope; users may also explicitly invoke it standalone. Read the original result files and attempt records, not only an executor's summary. A parent Workflow is a caller, not permission to start another Workflow.
- **Inputs:** the baseline (numbers plus where they came from), every attempt's raw outputs and run records (success, failure, crash, timeout, invalid, excluded), the configs and seeds behind each attempt, and the question the analysis should answer. Read existing project instructions and workspace navigation if present. Setup, a particular directory layout, a GPU scheduler, or any research runtime is not a prerequisite.
- **Resolve before work:** identify the baseline source, the attempt set, and the output mode. If the baseline is missing, the attempt set is ambiguous, or the question is contradictory, ask one focused question and stop; do not invent a baseline or fill the attempt set from a directory listing. Keep the user's research question unchanged.
- **Resources:** use already available, authorized read and compare tools, following host-specific tool routing. Simple descriptive computation (means, spreads, deltas) uses whatever the host already provides; do not install packages, environments, or analysis services. If a recomputation cannot be performed with available tools, keep the reported number as `reported` and record the gap rather than restating it as verified.
- **Writes:** standalone returns the report in chat unless the user authorizes a destination. Composed contributes only the analysis section of the caller's named canonical report (or returns the section for the caller to insert). Reuse existing material without overwriting it; ask on file or section conflicts. Do not edit result files, logs, configs, code, datasets, evaluators, or Claims.
- **Budget:** one bounded analysis pass per invocation. Read what establishes the inventory, the descriptive facts, and the credibility checks; prefer tails and targeted reads over loading whole logs. Stop at the first exhausted limit, retaining unexamined attempts and any resulting evidence gaps; request a specific extension rather than looping.
- **Stop:** 本次只交付分析报告。需要的新运行或材料修复只作为单独授权的下一步提出。

**完成条件**：baseline 出处、attempt 集合与输出模式已确定，或已提出一个聚焦问题并停止；写入范围与单次分析预算可核对。

## Phase 1: 建立结果账本

列出本次分析范围内的每一项，不预读内容做判断，只记位置与状态：

- baseline：数值、出处（复现的本地结果还是引用的外部数字）、对应的配置与数据划分。引用型 baseline 标注为 `reported`，直到在原始出处核对。
- 全部 attempts：成功、失败、崩溃、超时、无效、取消、重试、被排除的每一次，含标识、配置、seed、输出位置与运行记录。只保留 winner 的汇总必须回溯到原始 attempt 集合；找不到的 attempt 记为缺失，不用“应该跑过”填补。
- 每个结果文件的实际读取范围、所属 attempt、文件类型与可核对性。摘要、截图、表格或二手转述只作待核对线索。

**完成条件**：每个可分析对象都有原始位置和读取状态；缺失对象、矛盾声明及无法建立的关联已单独列出。

## Phase 2: 描述统计

只根据实际读到的原始输出报告数字，每个数字带定位。细节见 [可信度检查细则](references/statistical-checks.md)。

- 逐 attempt 报告 observed 数值；派生统计（均值、spread、delta、趋势）必须同时给出公式与输入，不以心算代替可核对计算。
- 均值与 spread 只用于真正可比的重复（同配置、同数据划分、同 metric 实现）；不可比的 runs 并列报告，不合并。
- 趋势陈述带样本量；outlier 只标记并保留，不删除、不平滑。
- 无法从材料完成重算的项保留 `unknown`，不把报告数字升级为已验证。

**完成条件**：每个报告数字都有原始定位与事实分级；不可重算项已明确保持 `unknown`。

## Phase 3: 可信度检查

沿以下检查面逐项给出结论与定位，禁止用一条线的通过覆盖另一条线：

每条细则见 [可信度检查细则](references/statistical-checks.md)。检查面是：重复与不确定性、选择偏差、多重比较、失败与无效记录、数字对应、范围诚实。事实分级用该文件的 `observed`／`derived`／`reported`／`unsupported`。

**完成条件**：细则里每一题都有结论或 `unknown`，并带材料定位与影响范围。

## Phase 4: 独立复核

有已授权的独立审查者时，在全新上下文中请求一次只读复核；已有不同模型可用时优先使用，不强制要求特定 provider。提供 baseline 出处、全部 attempt 输出与 Phase 1–3 案卷的路径——绝不只给执行者摘要。提问：“Do these results support the stated reading? What is the weakest link — uncertainty, selection, or scope?” 将实际 briefing 与完整回复保存在授权的报告位置。对照原始段落调和分歧，保留未解决的分歧；模型一致不是科学证据。

无独立审查者或超出授权时，标注输出 **single-agent assessment; independent verification not performed**。不冒充第二审查者，不反复寻求更有利的结论。

**完成条件**：每条分歧都有保留或改判；无独立审查者或超出授权时标明 single-agent。

## Phase 5: 报告与判定

Output a readable Markdown report using [报告模板](templates/analysis-report.md). The template organizes this analysis, not a machine schema. In composed mode, nest it inside the authorized analysis section rather than creating a duplicate deliverable.

- 严格分离 **Description**（观察到什么，带定位）、**Statistical evidence**（统计支撑是什么、不确定性与分母是什么）、**Claim**（在什么范围内可以说什么）。排名、单 metric winner、一次阳性结果都不单独构成科学结论。
- 每个 Claim 写清支持范围：固定设置、固定 metric、固定数据划分下的观察，还是可外推的判断；后者需要明确的额外依据，否则降级为观察陈述。
- EVIDENCE GAP 是有界的当前结果：列出确切缺失的材料、它影响哪个判断、最小的补证动作。缺失关键材料时不得给出肯定性结论。
- 报告结束后停止。用户决定是否调整 Claim、补实验或进入写作；本 Skill 不改变研究目标，不启动任何其他 Workflow。

**完成条件**：报告含结果账本、逐项数字与定位、统计证据与不确定性、偏差检查结论、Claim 支持边界、未决缺口与复核限制。然后停止。

## Interpretation rules

- 核对链只沿账本 → 原始输出 → 派生统计 → 报告回溯；顺向不升级。
