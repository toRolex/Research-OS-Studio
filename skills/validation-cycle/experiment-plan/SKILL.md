---
name: experiment-plan
description: 将已有研究问题或稳定方法转成 claim-driven 实验计划，明确对照、消融、评价边界、预算与负结果含义；只规划，产出后停止。
disable-model-invocation: true
---

# Experiment Plan: Claim-Driven, Bounded Validation

将用户给定的问题、Proposal 或方法整理为 **claim → evidence → run order** 路线图。计划服务证据而非预设论文成功。

Gates: none

## 委托合同依赖

- 单装包随本叶携带 [委托合同分发摘录](references/mandate.md)，覆盖目标、权限、额度、完成/停止与验收的必需规则；完整规范的唯一权威仍是 `skills/general/research-os/references/mandate.md`。
- 分发摘录缺失、与完整规范冲突或本次动作超出摘录时，标为 `blocked` 并停止受影响动作；不得从开发仓库路径或其他叶推断授权。

## 委托继承

- 目标、权限、研究额度、完成与停止语义以 research-os mandate 为唯一权威；只读或只建议时不落盘。
- 内部级联不重置授权；计划写盘按委托允许的位置继续。未来实验预算不等于执行授权。
- 完成计划即停止；关键数据、评价定义或硬预算未知时交付 **BLOCKED 草稿**，不编造数值。

本 Skill 可由用户独立显式调用，或由入口在有效研究委托覆盖规划职责、材料、输出范围与额度时按路径级联，不要求再次点名。模型不因描述自行触发；本 Skill 只制定计划，完成后返回用户或调用者，不调用其他 Workflow 或启动实验。输入可以是现成研究问题，不要求先运行 Discovery 或 refinement。用户若只给不稳定方向，输出缺口与待确认的假设，不替用户换题。

- **User** 决定研究问题、固定评价面、预算上限及输出位置，并另行决定是否授权执行。
- **Agent** 只读本次相关材料，设计比较、填写计划和待运行清单；不实现候选、不运行 sanity/baseline/评估、不配置环境。
- **写入范围**：仅用户允许的计划与 tracker 写域。默认在对话返回草稿；已授权写域内的新文件直接写入，不再为普通文件路径重复确认。先读同名目标；写域不明、外部变化、覆盖既有成果或目标替换时停止相应动作并确认。沿用现有 Research Workspace，不修改代码、数据、评估器、Agent 配置或其他研究材料。
- **资源范围**：本次仅规划。用户允许的未来实验预算不等于本次执行授权。远程读取、付费检索或敏感数据外传需符合本次授权；缺少资料时标为待提供，不安装工具或申请算力。
- **停止条件**：完成计划与摘要即停止；关键数据、评价定义或硬预算未知时交付明确标为“待补全，不可执行”的草稿并停止。拒绝授权或工具权限被拒时保留已有材料并报告。
- 需要运行批次时，仅在用户明确确认后按工作区授权流程记录该批 `research-log.md`；实际启动由 run-experiment 核验并继承这份授权，不逐 milestone 再索权。仅有计划不代表运行获批。

## Planning constants

- **MAX_PRIMARY_CLAIMS = 2** — prefer one dominant claim plus one supporting claim; explain any inseparable exception.
- **MAX_CORE_BLOCKS = 5** — keep the must-run experimental story compact.
- **MAX_BASELINE_FAMILIES = 3** — prefer a few strong baselines over many weak ones.
- **DEFAULT_SEEDS = 3** — propose 3 seeds when stochastic variance matters and budget allows; this is neither automatic authorization nor a guarantee of statistical power.
- **对照按问题选**：机器学习用计划声明中的训练 baseline；数学计算采用计划声明的对照（最小对照、已知值、证书重放或独立实现检查），不硬套训练 baseline。

## Workflow

**完成条件的两条分支**：下列每阶段的要求逐项满足，或逐项标为缺口并注明受影响 block、所需材料及待决策人。存在关键缺口时，以 **BLOCKED 草稿**完成规划，后续字段只填可确定部分；预算未知就保留未知，不为了满足“完整”而编造数值。只有全部关键项确定、彼此一致且必须实验符合硬上限时，才能标为“可供执行授权”。两者均不表示已授权执行。

### Phase 0: Load the Proposal Context

Read the relevant user-supplied proposal, review summary and refinement report if present. Locate them through the project's existing navigation, not a required directory layout. Without these files, derive the same information from the user's prompt:

- **Problem Anchor** and hypothesis: mechanism, expected direction and conditions under which it could be falsified
- **Dominant contribution**, optional supporting contribution
- **Critical reviewer concerns**
- **Data / compute / timeline constraints** and existing environment capabilities
- **Which frontier primitive is central, if any**

Distinguish observed project facts, user-provided constraints and proposed assumptions. Missing tools, unavailable data, uncertain dataset rights or unknown evaluator behavior are gaps, not facts to invent. Ask only the decisions needed to make the plan determinate; otherwise mark the affected blocks blocked.

**完成条件**：研究问题、输入来源、约束与缺口逐项列明；每个假设可识别为已给定或待确认。

### Phase 1: Freeze the Claims and Evaluation Surface

Before proposing experiments, write:

- **Primary claim**: the main mechanism-level contribution
- **Supporting claim**: optional, only if it directly strengthens the main story
- **Anti-claim to rule out**: e.g. gains only from more parameters, a larger search space, or a decorative modern component
- **Minimum convincing evidence**: what would make each claim believable to a strong reviewer?

Keep within MAX_PRIMARY_CLAIMS unless multiple claims are inseparable. Specify the falsifying observation as well as the expected improvement.

Define two disjoint boundaries for future execution:

1. **Candidate scope** — exact existing files or proposed implementation locations and permitted components/hyperparameter ranges. Label proposed paths as not yet created. Include allowed output locations; a broad project directory is not a substitute for a specific edit scope.
2. **Fixed evaluation surface** — dataset version and split, ground-truth source, preprocessing, evaluation code/protocol, metric formula/direction/units/aggregation, selection rule, seeds or pairing, and comparison budget. Candidate code may produce predictions, not redefine labels, evaluator, denominator or success threshold. Hidden tests remain with their owner; request a public protocol rather than reading private answers. If there is no ground truth, name the justified alternative (e.g. blinded human rubric), its limitations and required authorization.

Before calling the plan ready for execution authorization, bind the actual project location, data/protocol identifiers, existing way to set each seed or run parameter within candidate scope, and proposed evidence destinations. Unavailable bindings are blockers, not invented executable commands.

Where the project lacks actual access separation, say that this is a planned responsibility boundary, not enforced isolation. Evaluator defects require stopping the affected comparison and user approval of a new protocol; all systems must be re-evaluated under that protocol, retaining old results as non-comparable.

**完成条件**：每个 Claim 有支持和反驳条件；候选可改范围与固定评价面不重叠，缺失项阻止该计划被称为可执行。

### Phase 2: Build the Experimental Storyline

Use a compact set of blocks (within MAX_CORE_BLOCKS); delete those not needed:

1. **Main anchor result** — does the method solve the actual bottleneck?
2. **Novelty isolation** — does the dominant contribution itself matter?
3. **Simplicity / elegance check** — can a bigger or more fragmented version be avoided?
4. **Frontier necessity check** — if an LLM / VLM / Diffusion / RL-era component is central, is it the right tool?
5. **Failure analysis or qualitative diagnosis** — what does the method still miss?

For each block choose **Main paper** (essential), **Appendix** (non-blocking) or **Cut** (not worth the budget). Without a paper target, use core evidence / supplementary evidence / cut with the same meaning. Prefer one strong baseline family over many weak baselines (within MAX_BASELINE_FAMILIES). If a stronger modern baseline exists, use it rather than padding the list; mark an unverified baseline claim as such.

Make the **discriminating experiment** explicit: list competing explanations and their different predictions. Prefer the cheapest comparison that can change the decision. Match data, tuning opportunity and compute as appropriate; if budgets differ, separate the efficiency and unconstrained-quality claims. A comparison that cannot distinguish the explanations cannot establish the mechanism.

**完成条件**：每个保留 block 指向 Claim、竞争解释与可区分的观察；主证据、补充证据和删去项及理由齐全。

### Phase 3: Specify Each Experiment Block

For every kept block, fully specify:

- **Claim tested** and **why this block exists**
- **Dataset / split / task**
- **Compared systems / validation route**: choose and state the route. For training, compare the strongest relevant baselines, ablations and variants. For math/non-training work, name the mathematical control, known value, certificate replay or independent check; 不要求训练 baseline。
- **Metrics**: decisive metric first, secondary metrics second
- **Setup details**: training blocks state backbone, frozen vs trainable parts, key hyperparameters, training budget and seeds; math/non-training blocks state only applicable environment, exact inputs and check procedure, with training fields not applicable.
- **Success criterion**: pre-specified effect size and uncertainty requirement, not merely the best point estimate
- **Failure interpretation**: what a negative result means and what it does not mean
- **Table / figure target**: where the evidence should appear (a report is sufficient)

Special rules:

- Simplicity check 与 frontier necessity check 的比较对象见 [block checks](references/block-checks.md)。保留了对应 block 时按该文件填写；非 frontier 方法跳过 frontier block。
- Pre-specify sampling unit, repeated seeds (start from DEFAULT_SEEDS when stochastic variance matters and budget allows), paired comparisons and uncertainty reporting when relevant. Keep tuning on development data and reserve final evaluation; label post-hoc analyses exploratory. Account for selection and multiple comparisons instead of presenting the best seed as confirmatory evidence.
- Separate **valid negative** (valid evidence rules out the pre-specified meaningful gain or meets an explicit falsification rule), **inconclusive** (uncertainty still permits competing conclusions), **invalid** (protocol/data leakage/evaluator defect), and **operational failure** (crash/OOM/timeout). Missing a success threshold alone does not establish a negative; pre-specify how uncertainty and effect size distinguish negative from inconclusive. A valid negative limits the tested Claim; operational failure is not scientific falsification. Preserve all attempts, not only winners; missing metrics remain missing, never zero-valued success.
- For **each applicable criterion** (including training-baseline validity on the training route and budget compliance), identify primary evidence: run IDs, actual or proposed raw-result location, metric/column or log section, comparison and decision rule. For math/non-training work, evidence instead points to the named certificate, known value, invariant or independent check; training-baseline validity is not required. Record existing evidence separately with its source; future evidence stays **not collected**. File existence and model agreement do not establish that the criterion holds.

**完成条件**：每个 block 按其训练或数学/非训练路线写齐适用字段与逐 criterion evidence；训练路线明确 strongest baseline 和 baseline validity，数学/非训练路线明确对照或证书检查且不要求训练 baseline；正、负、不确定、无效及运行失败的含义可区分。

### Phase 4: Turn the Plan Into an Execution Order

Specify future milestones; do not execute them. Choose the comparison/validation route from the research question:

1. **Sanity stage** — check data pipeline and metric correctness for training, or the mathematical object and checker for math/non-training work. Use a toy split/quick overfit only when training settings and authorized scope permit it. Label dedicated sanity attempts and exclude them from confirmatory evidence.
2. **Training branch — baseline-first** — reproduce the strongest baseline relevant to the claim unchanged before candidate optimization. Candidate runs require a valid baseline on the same evaluation surface, with original configuration and raw evidence retained. Reuse an earlier baseline only when its protocol and evidence are actually comparable; a literature number alone is insufficient. An invalid or missing required baseline blocks candidate runs.
3. **Math/non-training branch — comparison or certificate check** — name the mathematical control (for example a known value, analytic invariant, minimal counterexample, certificate replay, or independent implementation) and its exact evidence and decision rule. When no candidate is trained, backbone, training recipe, strongest training baseline, and its gate are not required (不要求训练 baseline). An unavailable or invalid certificate/check blocks only the claim that depends on it and remains `unknown` until resolved.
4. **Main method / candidate stage** — final method on the primary setting when applicable; otherwise perform only the declared mathematical/non-training checks.
5. **Decision stage** — decisive ablations for novelty, simplicity and frontier necessity when applicable; for other work, use the declared comparison to decide among pre-specified explanations.
6. **Polish stage** — robustness, qualitative figures and appendix extras when applicable.

For each applicable milestone estimate compute, turnaround time, stop/go gate, risk and mitigation. Preserve baseline-first for training studies; do not transfer that gate to math/non-training work. A failed comparison or certificate check does not become evidence of success.

Separate **must-run** from **nice-to-have**. State per-run and total hard limits:

- run count (including seeds, sanity and retries), wall time including startup/evaluation, CPU/GPU time, memory/storage, data preparation, human effort, monetary cost and remote/API use as applicable; explicit zero or not-applicable is preferable to an unbounded blank.
- Show arithmetic and distinguish estimates from user-approved ceilings.
- Define resource accounting: occupied vs active GPU time, CPU cores × hours, whether existing data/cache counts toward storage, and cleanup time inside the wall-time cap.
- Count failed attempts against the budget; unused headroom authorizes neither retries nor new variants.
- Record who may stop a future job and what authorization is required, without stopping any job now.

If the minimum discriminating suite exceeds a ceiling, reduce optional work or present a smaller hypothesis with user approval; do not quietly increase budget or remove the decisive control. Gate on missing resources, invalid baseline, exhausted budget or protocol changes; new decisions go to the user, not an automatic loop.

**完成条件**：训练路线的 baseline-first 依赖或数学/非训练路线的对照/证书 gate、每阶段条件、总预算算式与硬上限清楚；适用的必须运行能纳入上限，否则明确不可执行及需用户决定之处。

### Phase 5: Write the Outputs and Stop

Read [计划与 tracker 模板](templates/experiment-plan.md) now. Fill every applicable section; explain any omitted block. Preserve natural-format evidence paths instead of wrapping them in a central schema. Follow the user's language preference; code, paths and metric names retain their original form.

Present the full draft in the conversation, or write only the authorized destinations under the write rules above ([委托继承](#委托继承)). The tracker is a human-readable list of proposed runs, not a scheduler; initial status is **NOT RUN** or **BLOCKED**, and planned evidence is not a result. Future execution may record successful, negative, invalid, crashed and timed-out attempts there without deleting history.

Finish with:

- Must-run blocks and first three **proposed** runs (not launch commands executed)
- Highest-risk assumption, unresolved decisions and whether the plan is complete enough for execution authorization
- Actual output paths, or “仅对话草稿，未落盘”
- “未启动实验、未配置环境；执行需用户另行授权”

**完成条件**：逐 Claim、逐 criterion 与全部 run 对照过计划和 tracker，预算一致；每个缺口可定位；输出后停止，不进入执行、自动改进或写作。
