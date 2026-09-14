---
name: proof-writer
description: 为固定命题撰写严谨证明：当用户需要证明定理、引理、命题或推论，补全证明，写证明，证明某个命题，补齐缺失步骤、形式化证明草图，或判断所声称证明在给定假设下能否完成时使用；不替代只读证明审查。
argument-hint: "[定理陈述与假设；可指定输出位置与尝试预算]"
---

# Proof Write: Rigorous Theorem / Lemma Drafting

Write a mathematically honest proof package, not a polished fake proof.

## Invocation, Authorization, and Completion

This is a model-invoked generation Skill, also available when a user explicitly names it. In **standalone** mode, produce the proof package at the agreed project path. In **composed** mode, contribute the same complete content to the caller's designated report section; do not create a second canonical report.

Before Step 1, establish the exact claim, allowed local inputs, output path or section, and attempt budget from the request. If writing is not authorized, return the package in chat. A default filename is a suggestion, not permission to overwrite. Read existing destinations, preserve unrelated material and prior attempts, and ask before resolving conflicting edits. Only the agreed research-material destination may be changed; project instructions, environment, and unrelated files remain untouched.

Use the user's finite budget; otherwise attempt one proof strategy and at most one alternative route, then report remaining blockers. Clarify ambiguities affecting quantifiers, assumptions, or scope before proving. Freeze the original claim and assumptions verbatim in the package. A weaker claim or added assumption is a separately labeled proposal: only explicit authorization permits proving that variant, and its status never counts as proof of the original claim. Internal normalization must be demonstrably equivalent under the frozen assumptions.

Ordinary Markdown mathematics is sufficient. Lean, symbolic tools, network access, paid resources, and environment setup are not prerequisites or actions of this Skill. Use only available authorized local reading/writing capabilities; report unavailable inputs or capabilities instead of pretending to have checked them. Numerical examples, self-checks, and model agreement are not mathematical proof or formal verification.

Completion means every nontrivial implication has a justification, or an explicit gap, and the final package records status and remaining risks. Return the actual destination (or chat-only result), original claim versus authorized variant, checks performed and checks not performed, then stop. Do not automatically invoke formula-derivation or another Workflow, and do not automatically start a separate review, repair, or long-running proof process.

## Constants

- DEFAULT_PROOF_DOC = `PROOF_PACKAGE.md` in project root
- STATUS = `PROVABLE AS STATED | PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION | NOT CURRENTLY JUSTIFIED`

## Context: $ARGUMENTS

## Goal

Produce exactly one of:
1. a complete proof of the original claim
2. a corrected claim plus a proof of the corrected claim
3. a blockage report explaining why the claim is not currently justified

## Inputs

Extract and normalize:
- exact theorem / lemma / proposition / corollary statement
- explicit assumptions
- notation and definitions
- any user-provided proof sketch, partial proof, or intended strategy
- nearby lemmas or claims in local notes, appendix files, or theorem drafts if the request points to them
- desired output style if specified: concise, appendix-ready, or full-detail

If notation or assumptions are ambiguous, state the exact interpretation you are using before proving anything.

## Workflow

### Step 1: Gather Proof Context
Determine the target proof file with this priority:
1. a file path explicitly specified by the user
2. a proof draft already referenced in local notes or theorem files
3. `PROOF_PACKAGE.md` in project root as the default target

Read the relevant local context:
- the chosen target proof file, if it already exists
- theorem notes, appendix drafts, or files explicitly mentioned by the user

Extract:
- exact claim
- assumptions
- notation
- proof sketch or partial proof
- nearby lemmas that the draft may depend on

### Step 2: Normalize the Claim
Restate:
- the exact claim being proved
- all assumptions, separately from conclusions
- all symbols used in the claim

Identify:
- hidden assumptions
- undefined notation
- scope ambiguities
- whether the available sketch proves the full claim or only a weaker variant

Preserve the user's original theorem statement; any changed statement remains a separately labeled proposal until explicitly authorized.
If you use a stronger normalization or cleaner internal formulation only to make the proof easier, keep that as an internal proof device rather than silently replacing the original claim.

### Step 3: Feasibility Triage
Before writing a proof, record a **tentative** feasibility classification, not a proof-success verdict. Select exactly one final status only after Step 6; a positive final status requires the complete argument, with no unresolved load-bearing gap:
- `PROVABLE AS STATED`
- `PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION`
- `NOT CURRENTLY JUSTIFIED`

Check explicitly:
- does the conclusion actually follow from the listed assumptions?
- is any cited theorem being used outside its conditions?
- is the claim stronger than what the available argument supports?
- is there an obvious counterexample, boundary case, or quantifier failure?

If the claim is not provable as stated, do NOT fabricate a proof.
Do NOT silently strengthen assumptions or narrow the theorem's scope just to make the proof work.

### Step 4: Build a Dependency Map
Choose a proof strategy, for example:
- direct
- contradiction
- induction
- construction
- reduction to a known result
- coupling / probabilistic argument
- optimization inequality chaining

Then write a dependency map:
- main claim
- required intermediate lemmas
- named theorems or inequalities that will be cited
- which assumptions each nontrivial step depends on
- boundary cases that must be handled separately

If one step is substantial, isolate it as a lemma instead of burying it in one sentence.

### Step 5: Write the Proof Document
Keep the delivery mode and authorization established before Step 1:
- No write authorization: return the full package in chat; create no files.
- Composed with write authorization: update only the caller-designated report section, preserve everything else, and do not create a second canonical report.
- Standalone with write authorization: write to the agreed file; read existing files first, update only the relevant claim section, preserve prior attempts, and avoid duplicated content.

The default filename only suggests a destination; do not reselect paths or expand authorization here. The full package structure below applies equally to chat and report sections; adjust heading levels when embedding into an existing report.

Do NOT write directly into paper sections or appendix `.tex` files unless the user explicitly asks for that target.

The proof package must include:
- exact claim
- explicit assumptions
- proof status
- announced strategy
- dependency map
- numbered major steps
- justification for every nontrivial implication

Mathematical rigor requirements:
- never use "clearly", "obviously", "it can be shown", "by standard arguments", or "similarly" to hide a gap
- define every constant and symbol before use
- check quantifier order carefully
- handle degenerate and boundary cases explicitly, or state why they are excluded
- if invoking a standard fact, state its name and why its assumptions are satisfied here
- use `$...$` for inline math and `$$...$$` for display equations
- never write math in plain text
- if the proof uses an equivalent normalization that is stronger in appearance than the user's original theorem statement, label it explicitly as a proof device and keep the original claim separate

### Step 6: Final Verification
Before finishing the target proof file, verify:
- the theorem statement exactly matches what was actually shown
- every assumption used is stated
- every nontrivial implication is justified
- every inequality direction is correct
- every cited result is applicable under the stated assumptions
- edge cases are handled or explicitly excluded
- no hidden dependence on an unproved lemma remains

If a key step still cannot be justified, downgrade the status and write a blockage report instead of forcing a proof.

## Required File Structure

Write the target proof file using this structure:

```md
# Proof Package

## Claim
[exact statement]

## Status
[Select one exact STATUS value; attach separate statuses to original and authorized variant.]

## Assumptions
- ...

## Notation
- ...

## Proof Strategy
[chosen approach and why]

## Dependency Map
1. Main claim depends on ...
2. Lemma A depends on ...
3. Step k uses ...

## Proof
Step 1. ...
Step 2. ...
...
[Only for a complete proof of the stated claim: Therefore the claim follows. ∎]
[Otherwise: stop at the last justified step and identify the gap; do not add a completion marker.]

## Corrections or Missing Assumptions
- [only if needed]

## Proof Gaps, Failed Routes, and Lessons
- Gap: exact unresolved implication or lemma, assumptions needed, and consequence for the original claim; write `none identified` only when justified.
- Failed route: actual strategy attempted, precise failure point and reason; if none, say `none attempted` rather than inventing a history.
- Reusable lesson: a concrete future check, including its scope of applicability.
- Proposed next action: missing lemma, evidence, or user decision; not an automatic retry or repair.

## Open Risks
- [remaining fragile points, if any]
```

## Output Modes

### If the claim is provable as stated
Write the full file structure above with a complete proof.

### If the original claim is too strong
Keep the original claim's status `NOT CURRENTLY JUSTIFIED`; distinguish a demonstrated counterexample (false as stated) from an incomplete attempt (unresolved, not a claim of falsity). Propose corrections without changing the fixed target. Only if the user explicitly authorizes a variant, write:
- why the original statement is not justified
- the corrected claim
- the minimal extra assumption if one exists
- a proof of the corrected claim

### If the proof cannot be completed honestly
Write:
- `Status: NOT CURRENTLY JUSTIFIED`
- the exact blocker: missing lemma, invalid implication, hidden assumption, or counterexample direction
- what extra assumption, lemma, or derivation would be needed to finish the proof
- a corrected weaker statement if one is available

## Chat Response

After writing the target proof file, respond briefly with:
- status
- whether the original claim survived unchanged
- what file was updated

## Key Rules

- Never fabricate a missing proof step.
- Prefer proposing a weaker claim over overclaiming; developing it requires explicit authorization.
- Separate assumptions, derived facts, heuristics, and conjectures.
- Preserve the user's original theorem statement unless you explicitly mark a corrected claim or an internal normalization.
- If the statement is false as written, say so explicitly and give a counterexample or repaired statement.
- If uncertainty remains, mark it explicitly in `Open Risks`; do not hide it inside polished prose.
- Correctness matters more than brevity.
