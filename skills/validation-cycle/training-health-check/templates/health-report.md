# Training Health Report

**Observation time:** [timestamp and timezone]
**Invoked by:** [user / parent Workflow name]
**Target run:** [job name or id, framework if relevant, window covered]
**Window:** [first–last step/epoch or timestamp actually inspected]
**Thresholds used:** [defaults, or the user's stated thresholds/expected schedule]

## Observation surfaces and adequacy

| Surface | Locator | Range covered | Adequacy |
|---|---|---|---|
| [log / metrics file / resource record] | [path] | [steps or timestamps] | [sufficient / partial / missing] |
| | | | |

Gaps: [missing ranges, truncation, unreadable encoding, absent eval entries, or “none
found after checking the expected surfaces”.]

## Per-signal findings

| Signal | Evidence locator | Observed values / window | Finding |
|---|---|---|---|
| NaN / Inf | | | |
| Divergence | | | |
| OOM | | | |
| Stagnation | | | |
| Log completeness | | | |
| [optional secondary signal] | | | |

## Diagnosis

- **Result:** [no anomaly detected / anomaly detected / insufficient observation / indeterminate]
- **Basis:** [signals checked, window, and the evidence that decides the result]
- **Severity / terminality:** [terminal / quality-only / not applicable]
- **Uncertainty:** [what the observations cannot show, including unexamined ranges]

`no anomaly detected` means only that the checked signals show no anomaly in this window;
it is not a scientific verdict, not proof of convergence, and not support for a Claim.

## Recommendation (advice only)

- **Recommended:** [continue / stop and investigate / collect more observations /
  extend the window / fix the observation]
- **Why:** [maps to the diagnosis]
- **What would change this:** [additional observation or user-provided context]
- **Preserve:** [log window, run identifier and observed values the user should keep]

## Handoff

- No research results, Claims or paper content were produced.
- No stop, kill, restart, retry or requeue was performed; job control remains with the
  user, whose explicit authorization is required for any such action.
- Output: [chat only / written to the authorized path].
