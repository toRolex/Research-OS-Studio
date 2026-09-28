# Derivation Package

Use this skeleton for chat, an authorized file, and a composed report section. Adjust heading levels when embedding. Do not write into paper sections or appendix `.tex` unless that destination was authorized before Step 1.

## Target
[what is being derived or explained; original wording retained]

## Status
[Select one exact STATUS value; attach separate statuses to the original target and each authorized variant.]

## Invariant Object
[top-level quantity organizing the derivation; label proxy / local slice / approximation if used]

## Assumptions
- ...

## Notation
- ...

## Derivation Strategy
[chosen route and why]

## Derivation Map
1. Target depends on ...
2. Intermediate step A uses ...
3. Approximation enters at ...

## Main Derivation
Step 1. ...
Step 2. ...
...

## Remarks and Interpretation
- ...

## Boundaries and Non-Claims
- ...

## Proof Gaps, Failed Routes, and Lessons
- Gap: exact unresolved step, assumptions it needs, and consequence for the target; write `none identified` only when justified.
- Failed route: actual approach attempted, where and why it stopped; if none, say `none attempted` rather than inventing a history.
- Reusable lesson: what to check or avoid next time, with the assumptions under which it applies.
- Proposed next action: missing input or intermediate derivation, for the user to decide; not an automatic retry.

## Open Risks
- ...

## Output modes

### Coherent as stated
Fill every section above. Status of the original target is `COHERENT AS STATED`.

### Close but not coherent yet
Keep the original target's status `NOT YET COHERENT` and propose the needed change. Only if the user explicitly authorizes a variant, also write:
- the exact mismatch
- the corrected invariant object, assumption, or scope
- the reframed derivation package, with its own status

### Cannot be made coherent honestly
Write:
- `Status: NOT YET COHERENT`
- the exact blocker: missing object, unstable assumptions, notation conflict, unsupported approximation, or a theorem-level claim without enough conditions
- what extra assumption, reframe, or intermediate derivation would be needed
