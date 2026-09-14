# Health Signals

A catalog for diagnosing training observations. Patterns are examples, not a parser
contract: read the run's own log and metric format first. Defaults below are starting
points the user may override; state any threshold actually used.

## Observation completeness (check first)

| Check | Passes when | If it fails |
|---|---|---|
| Surface exists and is readable | File/resource exists, non-empty, decodes in its stated encoding | `insufficient observation`; name the path and error |
| Numbering contiguous | Step/epoch indices advance without unexplained skips | Report the gaps and their size; do not bridge them silently |
| No truncation | The tail is a complete record, not a half-written line | Treat the last partial record as absent |
| Expected entries present | Eval/checkpoint records appear on the run's own stated cadence | Mark the missing range; adequacy becomes partial |
| Timestamps sound | Monotonic, and recency matches the expected cadence | A stalled clock or stale tail is itself evidence |

A missing or corrupt log is an observability problem: the diagnosis is
`insufficient observation` (recommend `fix the observation`), never `no anomaly detected`.

## Signals

### NaN / Inf

- **Look for:** `nan`, `inf`, `-inf`, `NaN`, `Inf` in loss, gradient norm, learning rate
  or metric records; framework-specific spellings.
- **Confirm:** it belongs to this run and this window, and is a real value, not a masked
  or sentinel entry the framework prints for skipped steps.
- **Classify:** any real NaN/Inf in loss or gradient is `anomaly detected` (terminal
  severity). Keep the exact line and step.
- **If not observed:** say the log carries no gradient/loss values, rather than reporting
  healthy.

### Divergence

- **Look for:** loss increasing over a sustained window, or growing beyond the run's
  normal fluctuation scale.
- **Default window:** at least 3–5 consecutive records, or a clear monotonic trend over
  the window, whichever the run's cadence supports.
- **Distinguish:** isolated spikes within normal variance are not divergence; a single
  rising point after a step change (data, LR, batch size) may be the schedule, not a fault.
- **Classify:** sustained increase with no expected cause is `anomaly detected`.
  Too few records to establish a trend is `indeterminate` / `insufficient observation`.

### OOM (out of memory)

- **Look for:** allocation failures in the log (`out of memory`, `OutOfMemory`, CUDA/MPS
  OOM messages), a kill signal (e.g. exit from SIGKILL / signal 9), scheduler-reported
  OOM, or a process death immediately after a memory rise.
- **Confirm:** the failure is attributable to this run, not a neighbor job; note whether
  it is reproducible at the same step or resource setting.
- **Classify:** an OOM is `anomaly detected` and usually terminal for the attempt.
  Distinguish from a warning that was caught and recovered.
- **Boundary:** the process-level fact that a job died belongs to `monitor-experiment`;
  this skill diagnoses the OOM cause visible in the training log.

### Stagnation

- **Look for:** loss or the target eval metric showing no improvement beyond the run's
  noise scale over a sustained window.
- **Default window:** use the run's own evaluation or checkpoint cadence; require enough
  points that a plateau is distinguishable from normal late-training slowdown.
- **Distinguish:** a short plateau during warmup or before an LR change is expected; a
  metric that is still improving slowly is not stagnation.
- **Classify:** a sustained flat/declining metric with no expected schedule cause is
  `anomaly detected` (non-terminal, quality). Insufficient window is
  `insufficient observation`.

### Optional secondary signals

Report only when the observations carry them: sudden loss spikes (>~10× normal
variation), exploding or vanishing gradient norm, LR schedule deviation, or metrics
moving opposite to the expected direction. Classify each with its window and evidence.

## Decision table (recommendation, never an action)

| Observation | Diagnosis | Recommendation |
|---|---|---|
| NaN/Inf in loss or gradient | anomaly (terminal) | Stop and investigate (user action) |
| Sustained divergence with no expected cause | anomaly (terminal) | Stop and investigate (user action) |
| OOM / kill signal in the training log | anomaly (terminal) | Stop and investigate (user action); preserve the log window |
| Sustained stagnation, no schedule cause | anomaly (quality) | Investigate; consider adjusting the run under a new authorized plan |
| Loss decreasing, metrics improving | no anomaly in window | Continue; observe again later |
| Flat but not diverging, short window | indeterminate | Extend the window / collect more observations |
| Noisy, cannot establish a trend | indeterminate | Extend the window / collect more observations |
| Log missing, truncated or unreadable | insufficient observation | Fix the observation, then re-check |

This table produces advice. The skill never edits the job, and never stops, kills,
restarts or requeues it; those actions require the user's explicit authorization.

## Thresholds the user may override

Window length, noise scale, spike factor and stagnation tolerance all depend on the run.
When the user provides a baseline expectation, expected schedule or explicit threshold,
use it and record it. Otherwise state the default used and treat borderline results as
`indeterminate` rather than forcing a verdict.
