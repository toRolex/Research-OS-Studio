# Run Status Record

**Observation time:** [timestamp and timezone]
**Invoked by:** [user / parent Workflow name]
**Target run:** [job name or id, working directory, start time if observed]

## Primary status

- **Status:** [running / completed / crashed / not started / unknown]
- **Evidence:** [locator plus the observed fact that establishes it]
- **Limits:** [what would change this status; any missing terminal evidence]

## Surfaces observed

| Surface | Locator | Observed at | Result |
|---|---|---|---|
| [process / scheduler / log / status / artifact] | [path or query] | [time] | [fact only] |
| | | | |

## Progress and output facts

| Fact | Value | Locator |
|---|---|---|
| Latest progress counter (step/epoch/total) | [value, or “not emitted”] | |
| Last output timestamp | | |
| Expected output path | [exists / absent / not specified] | |
| Recorded exit code | [value, or “not recorded”] | |
| Recorded resources or cost | [values the run logged, or “not observed”] | |

## Not observed

[Requested or expected surfaces that were unreadable, absent or stale, and how this
limits the record. State “none” only after checking the target run's surfaces.]

## Handoff

- This record contains observations only: no result interpretation, comparison, ranking
  or research conclusion.
- Training-quality diagnosis, if needed, is the separate `training-health-check`
  capability and was not started here.
- No stop, restart, retry or other job-control action was performed; the job remains
  under the user's control.
- Output: [chat only / written to the authorized path].
