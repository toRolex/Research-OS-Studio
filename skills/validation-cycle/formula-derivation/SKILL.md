---
name: formula-derivation
description: 推导公式并组织理论主线。对象或假设未固定、需要完整推导包时使用。
disable-model-invocation: true
---
<!-- argument-hint: "[问题目标与现有公式或笔记；可指定输出位置与尝试预算]" -->

# Formula Derivation: Research Theory Line Construction

Build an honest derivation package, not a fake polished theorem story.

## Invocation, Authorization, and Completion
Gate: write-authorization | before=package-write | approval=explicit-user | source=SKILL.md#invocation-authorization-and-completion

This is a model-invoked generation Skill, also available when a user explicitly names it. In **standalone** mode, produce the derivation package at the agreed project path. In **composed** mode, contribute the same complete content to the caller's designated report section; do not create a second canonical report.

Before Step 1, establish the target, allowed local inputs, output path or section, and attempt budget from the request. If writing is not authorized, return the package in chat. A default filename is a suggestion, not permission to overwrite. Read existing destinations, preserve unrelated material and prior attempts, and ask before resolving conflicting edits. Only the agreed research-material destination may be changed; project instructions, environment, and unrelated files remain untouched.

Use the user's finite budget; otherwise attempt one derivation map and at most one alternative route, then report remaining blockers. Ambiguities that change the object, assumptions, or scope require clarification before manipulation. Once Step 2 fixes the target, retain it verbatim in the package. A reframe or added assumption is a separately labeled proposal: only explicit authorization permits developing that variant, and its status never counts as success of the original target.

Ordinary Markdown mathematics is sufficient. Lean, symbolic tools, network access, paid resources, and environment setup are not prerequisites or actions of this Skill. Use only available authorized local reading/writing capabilities; report unavailable inputs or capabilities instead of pretending to have checked them. Numerical examples, self-checks, and model agreement are not mathematical proof or formal verification.

Completion means every nontrivial step has its category and justification, or an explicit gap, and the final package records status and remaining risks. Return the actual destination (or chat-only result), unchanged target versus authorized variant, checks performed and checks not performed, then stop. Relationships below are recommendations only: do not automatically invoke proof-writer or another Workflow, and do not automatically start a separate review or repair process.

## Constants

- DEFAULT_DERIVATION_DOC = `DERIVATION_PACKAGE.md` in project root
- STATUS = `COHERENT AS STATED | COHERENT AFTER REFRAMING / EXTRA ASSUMPTION | NOT YET COHERENT`

## Context: $ARGUMENTS

## Goal

Produce exactly one of:
1. a coherent derivation package for the original target
2. a reframed derivation package with corrected object / assumptions / scope
3. a blocker report explaining why the current notes cannot yet support a coherent derivation

## Step classification

每个非平凡步只标一类。类别转换处单独标记。解释性段落不写成已证。

- **identity**：精确代数改写
- **proposition**：带条件的命题
- **approximation**：模型简化或替代量
- **interpretation**：公式的文字含义

## Workflow

授权门通过后，按 Step 1–8 顺序做。每步的完成条件满足才进入下一步。

### Step 1: Gather Derivation Context
Determine the target derivation file with this priority:
1. a file path explicitly specified by the user
2. a derivation draft already referenced in local notes
3. `DERIVATION_PACKAGE.md` in project root as the default target

Read the relevant local context:
- the chosen target derivation file, if it already exists
- any local theory notes, formula drafts, appendix notes, or files explicitly mentioned by the user

Extract: target formula / theory goal, current formula chain, assumptions, notation, known blockers, desired output mode (internal alignment note / paper-style theory draft / blocker report). 目标、对象、符号或假设有歧义时，先写明所用解释再推导。

**完成条件**：目标文件已按优先级确定；相关笔记已读或列为未读；上述各项均有出处或标为缺口，没有用默认对象填空。

### Step 2: Freeze the Target
State explicitly:
- what is being explained, derived, or supported
- whether the immediate goal is:
  - identity / algebra
  - proposition
  - approximation
  - interpretation
- what the derivation is expected to output in the end

Do not start symbolic manipulation before this is fixed.

**完成条件**：原始目标逐字保留；立即目标是 identity／proposition／approximation／interpretation 之一；期望产出已写明。未固定则停止，不开始符号操作。

### Step 3: Choose the Invariant Object
Identify the single quantity or conceptual object that should organize the derivation.

Typical possibilities include:
- objective / utility / loss
- total cost / energy / welfare
- conserved quantity / state variable
- expected metric / effective rate / effective cost

If the current notes start from a narrower quantity, decide explicitly whether it is:
- the true top-level object
- a proxy
- a local slice
- an approximation

Do not let a convenient proxy silently replace the actual conceptual object.

**完成条件**：一个不变对象已点名，并标为 top-level／proxy／local slice／approximation；替代对象只能作为单独标注的变体提案。

### Step 4: Normalize Assumptions and Notation
Restate:
- all assumptions
- all symbols
- regime boundaries or special cases
- which quantities are fixed, adaptive, or state dependent

Identify:
- hidden assumptions
- undefined notation
- scope ambiguities
- whether the current formula chain already mixes exact steps with approximations

Preserve the user's original notation unless a cleanup is necessary for coherence.
If you adopt a cleaner internal formulation, keep that as a derivation device rather than silently replacing the user's target.

**完成条件**：每个假设与符号都有出处；隐含假设、未定义符号与范围歧义已列出；精确步与近似混用处已标记。

### Step 5: Classify the Derivation Steps
按 [Step classification](#step-classification) 给每个非平凡步分类。

**完成条件**：每个非平凡步都有一类，类别转换处已单独标记。

### Step 6: Build a Derivation Map
Choose a derivation strategy, for example:
- definition -> substitution -> simplification
- primitive law -> intermediate variable -> target expression
- global quantity -> perturbation -> decomposition
- exact model -> approximation -> interpretable closed form
- general dynamic object -> simplified slice -> local theorem -> return to general case

Then write a derivation map:
- target formula or theory line
- required intermediate identities or lemmas
- which assumptions each nontrivial step uses
- where approximations enter
- where special-case and general-case regimes diverge or collapse

If the derivation needs a decomposition, derive it from the chosen global quantity.
Do not make a split appear magically from one local variable itself.

**完成条件**：推导图列出目标、中间步、每步用到的假设、近似进入点与特例／一般情形分歧；分解能追溯到不变对象。

### Step 7: Write the Derivation Document
Keep the delivery mode and authorization established before Step 1:
- No write authorization: return the full package in chat; create no files.
- Composed with write authorization: update only the caller-designated report section, preserve everything else, and do not create a second canonical report.
- Standalone with write authorization: write to the agreed file; read existing files first, update only the relevant section, preserve prior attempts, and avoid duplicated content.

The default filename only suggests a destination; do not reselect paths or expand authorization here. The full package structure below applies equally to chat and report sections; adjust heading levels when embedding into an existing report.

Do NOT write directly into paper sections or appendix `.tex` files unless the user explicitly asks for that target.

写入只发生在授权门已允许的目的地。按 [derivation package](templates/derivation-package.md) 填节。

**完成条件**：模板各节已填，或未写入原因已记录；每个缺口、失败路线与开放风险都在包内。

### Step 8: Final Verification
Treat status as tentative until this check is complete. Any unresolved load-bearing gap or unsupported approximation requires `NOT YET COHERENT`, even when the rest of the exposition reads smoothly. Apply this rule separately to the original target and each explicitly authorized variant; a coherent variant cannot upgrade the original target.

Before finishing the target derivation file, verify:
- the target is explicit
- the invariant object is stable across the derivation
- every assumption used is stated
- each formula step is correctly labeled as identity / proposition / approximation / interpretation
- the derivation does not silently switch objects
- special cases and general cases still belong to one theory line
- boundaries and non-claims are stated

If the derivation still lacks a coherent object, stable assumptions, or an honest path from premises to result, downgrade the status and write a blocker report instead of forcing a clean story.

**完成条件**：原始目标与每个已授权变体各有一个 STATUS；承重缺口或无支持近似使原始目标为 `NOT YET COHERENT`；检查项逐条有结果或未完成原因。然后停止：不自动调用 `proof-writer`、审查或修复。

## Package and output modes

Write the package with [derivation package](templates/derivation-package.md). The same skeleton applies to chat, an authorized file, and a composed report section; adjust heading levels when embedding. Output-mode branches in that template decide which sections are filled versus left as an explicit blocker. A default filename is a suggestion, not a new write grant.

## Relationship to `proof-writer`

对象或假设未固定时留在本 Skill。对象、假设与记号都已固定、任务是严格证明或反驳该命题时，用 `proof-writer`。

## Chat Response

After writing the target derivation file, respond briefly with:
- status
- whether the target survived unchanged or had to be reframed
- what file was updated

## Key Rules

- Never fabricate a coherent derivation if the object, assumptions, or scope do not support one.
- Prefer proposing a reframe over overclaiming; developing it requires explicit authorization.
- Separate assumptions, identities, propositions, approximations, and interpretations.
- Keep one invariant object across special and general cases whenever possible.
- Treat simplified constant-parameter cases as analysis slices, not as the conceptual main object.
- If uncertainty remains, mark it explicitly in `Open Risks`; do not hide it in polished prose.
- Coherence matters more than elegance.
