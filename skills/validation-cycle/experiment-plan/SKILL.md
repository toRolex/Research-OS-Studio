---
name: experiment-plan
description: 将已有研究问题或稳定方法转成 claim-driven 实验计划，明确对照、消融、评价边界、预算与负结果含义；只规划，产出后停止。
disable-model-invocation: true
---

# Experiment Plan: Claim-Driven, Bounded Validation

将用户给定的问题、Proposal 或方法整理为 **claim → evidence → run order** 路线图。保留 ARIS 的主结果、贡献隔离、简洁性、frontier necessity 和失败诊断方法；计划服务证据而非预设论文成功。

## 调用与授权

这是 **user-invoked Workflow**：用户显式调用本 Skill 制定实验计划时使用。模型不自动启动它；本 Skill 也不调用其他 Workflow。输入可以是现成研究问题，不要求先运行 Discovery 或 refinement。用户若只给不稳定方向，输出缺口与待确认的假设，不替用户换题。

- **User** 决定研究问题、固定评价面、预算上限及输出位置，并另行决定是否授权执行。
- **Agent** 只读本次相关材料，设计比较、填写计划和待运行清单；不实现候选、不运行 sanity/baseline/评估、不配置环境。
- **写入范围**：仅用户允许的计划与 tracker 文件。默认在对话返回草稿；需落盘时沿用现有 Research Workspace，提出 `EXPERIMENT_PLAN.md` 与 `EXPERIMENT_TRACKER.md` 的具体路径并确认。已有文件先展示差异，未授权覆盖则保留原件。写入前复查目的文件；出现外部变化时重新确认。不修改代码、数据、评估器、Agent 配置或其他研究材料。
- **资源范围**：本次仅规划。用户允许的未来实验预算不等于本次执行授权。远程读取、付费检索或敏感数据外传需符合本次授权；缺少资料时标为待提供，不安装工具或申请算力。
- **停止条件**：完成计划与摘要即停止；关键数据、评价定义或硬预算未知时交付明确标为“待补全，不可执行”的草稿并停止。拒绝授权或工具权限被拒时保留已有材料并报告。

## Planning constants

- **MAX_PRIMARY_CLAIMS = 2** — prefer one dominant claim plus one supporting claim; explain any inseparable exception.
- **MAX_CORE_BLOCKS = 5** — keep the must-run experimental story compact.
- **MAX_BASELINE_FAMILIES = 3** — prefer a few strong baselines over many weak ones.
- **DEFAULT_SEEDS = 3** — propose 3 seeds when stochastic variance matters and budget allows; this is neither automatic authorization nor a guarantee of statistical power.

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
- **Compared systems**: strongest baselines, ablations and variants only
- **Metrics**: decisive metric first, secondary metrics second
- **Setup details**: backbone, frozen vs trainable parts, key hyperparameters, training budget, seeds
- **Success criterion**: pre-specified effect size and uncertainty requirement, not merely the best point estimate
- **Failure interpretation**: what a negative result means and what it does not mean
- **Table / figure target**: where the evidence should appear (a report is sufficient)

Special rules:

- A **simplicity check** compares the final method against an overbuilt variant or a tempting extra component intentionally rejected; deletion studies must preserve comparable tuning and evaluation.
- A **frontier necessity check** compares the chosen modern primitive against the strongest plausible simpler or older alternative. If intentionally non-frontier, say so and skip the block.
- Pre-specify sampling unit, repeated seeds (start from DEFAULT_SEEDS when stochastic variance matters and budget allows), paired comparisons and uncertainty reporting when relevant. Keep tuning on development data and reserve final evaluation; label post-hoc analyses exploratory. Account for selection and multiple comparisons instead of presenting the best seed as confirmatory evidence.
- Separate **valid negative** (valid evidence rules out the pre-specified meaningful gain or meets an explicit falsification rule), **inconclusive** (uncertainty still permits competing conclusions), **invalid** (protocol/data leakage/evaluator defect), and **operational failure** (crash/OOM/timeout). Missing a success threshold alone does not establish a negative; pre-specify how uncertainty and effect size distinguish negative from inconclusive. A valid negative limits the tested Claim; operational failure is not scientific falsification. Preserve all attempts, not only winners; missing metrics remain missing, never zero-valued success.
- For **each criterion (including baseline validity and budget compliance)**, identify the planned primary evidence: run IDs, actual or proposed raw-result location, metric/column or log section, comparison and decision rule. Record existing evidence separately with its source; future evidence stays **not collected**. File existence and model agreement do not establish that the criterion holds.

**完成条件**：每个 block 的所有字段与逐 criterion evidence 对应完整；正、负、不确定、无效及运行失败的含义可区分。

### Phase 4: Turn the Plan Into an Execution Order

Specify future milestones; do not execute them:

1. **Sanity stage** — data pipeline and metric correctness; include a quick overfit or toy split only if it fits the authorized scope. If it would alter fixed data or training settings, use sufficient existing protocol checks instead, or block pending a separately approved sanity design. Label any dedicated sanity attempt and exclude it from confirmatory results.
2. **Baseline stage** — reproduce the strongest baseline(s) unchanged before candidate optimization
3. **Main method stage** — final method on the primary setting
4. **Decision stage** — decisive ablations for novelty, simplicity and frontier necessity
5. **Polish stage** — robustness, qualitative figures, appendix extras

For each milestone estimate compute, turnaround time, stop/go gate, risk and mitigation. **Baseline-first**: candidate runs require a valid baseline on the same evaluation surface, with original configuration and raw evidence retained. An earlier baseline may be reused only when its protocol and evidence are actually comparable; a literature number alone is insufficient. Baseline failure blocks main runs rather than encouraging optimization against an unreliable reference.

Separate **must-run** from **nice-to-have**. State per-run and total hard limits:

- run count (including seeds, sanity and retries), wall time including startup/evaluation, CPU/GPU time, memory/storage, data preparation, human effort, monetary cost and remote/API use as applicable; explicit zero or not-applicable is preferable to an unbounded blank.
- Show arithmetic and distinguish estimates from user-approved ceilings.
- Define resource accounting: occupied vs active GPU time, CPU cores × hours, whether existing data/cache counts toward storage, and cleanup time inside the wall-time cap.
- Count failed attempts against the budget; unused headroom authorizes neither retries nor new variants.
- Record who may stop a future job and what authorization is required, without stopping any job now.

If the minimum discriminating suite exceeds a ceiling, reduce optional work or present a smaller hypothesis with user approval; do not quietly increase budget or remove the decisive control. Gate on missing resources, invalid baseline, exhausted budget or protocol changes; new decisions go to the user, not an automatic loop.

**完成条件**：baseline-first 依赖、每阶段 gate、总预算算式与硬上限清楚；所有必须实验能纳入上限，否则明确不可执行及需用户决定之处。

### Phase 5: Write the Outputs and Stop

Read [计划与 tracker 模板](templates/experiment-plan.md) now. Fill every applicable section; explain any omitted block. Preserve natural-format evidence paths instead of wrapping them in a central schema. Follow the user's language preference; code, paths and metric names retain their original form.

Present the full draft in the conversation, or write only the authorized destinations under the write rules above ([调用与授权](#调用与授权)). The tracker is a human-readable list of proposed runs, not a scheduler; initial status is **NOT RUN** or **BLOCKED**, and planned evidence is not a result. Future execution may record successful, negative, invalid, crashed and timed-out attempts there without deleting history.

Finish with:

- Must-run blocks and first three **proposed** runs (not launch commands executed)
- Highest-risk assumption, unresolved decisions and whether the plan is complete enough for execution authorization
- Actual output paths, or “仅对话草稿，未落盘”
- “未启动实验、未配置环境；执行需用户另行授权”

**完成条件**：逐 Claim、逐 criterion 与全部 run 对照过计划和 tracker，预算一致；每个缺口可定位；输出后停止，不进入执行、自动改进或写作。

## 来源

改编自 ARIS by wanshuiyin；随发行保留 [MIT 许可](LICENSE)。来源版本、作者与复制范围集中记录于仓库来源说明；使用本 Skill 无需访问产品仓库或上游。
