# Proof Package

包结构、Goal、STATUS 和三种输出模式只在本文件。写到哪里由 skill 的 Step 5 决定。嵌入已有报告时只改标题层级。

## Goal

恰好产出下面三种输出模式之一。

## STATUS

`PROVABLE AS STATED | PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION | NOT CURRENTLY JUSTIFIED`

原命题和每个已授权变体各记一个。肯定 STATUS 只有 `PROVABLE AS STATED`，以及已授权变体自己的已证状态。

## Claim
[exact statement; original wording retained]

## Status
[上面三种取值之一]

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

## Output modes

### Provable as stated
Fill every section above with a complete proof. Status of the original claim is `PROVABLE AS STATED`. End the proof with the completion marker only in this branch.

### Original claim too strong
Keep the original claim's status `NOT CURRENTLY JUSTIFIED`. Distinguish a demonstrated counterexample (false as stated) from an incomplete attempt (unresolved, not a claim of falsity). Propose corrections without changing the fixed target. Only if the user explicitly authorizes a variant, also write:
- why the original statement is not justified
- the corrected claim
- the minimal extra assumption if one exists
- a proof of the corrected claim, with its own status

### Cannot be completed honestly
Write:
- `Status: NOT CURRENTLY JUSTIFIED`
- the exact blocker: missing lemma, invalid implication, hidden assumption, or counterexample direction
- what extra assumption, lemma, or derivation would be needed to finish the proof
- a corrected weaker statement if one is available, labeled as a proposal rather than a proved variant
