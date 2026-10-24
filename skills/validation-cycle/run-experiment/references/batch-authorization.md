# Batch Authorization Reference

This is the run-experiment installation's self-contained guide to consuming an existing batch authorization. In a full Research OS suite, the authoritative shared policy is `skills/general/research-os/references/batch-authorization.md`; this copy keeps standalone installs usable and must stay aligned with that policy.

The actual ledger is the project's `research-log.md`. The workspace `compute-policy.md` is only a starting policy and never authorizes a run. Read the existing authorization and attempts; append to the active batch rather than replacing prior history.

## Required batch fields

Confirm the record identifies the batch, plan, execution mode, user's confirmation and its source, confirmation time, and `authorization_status: 本批已确认`. The confirmed scope must identify the plan, writable paths and environment. Each applicable budget must be finite, non-negative and unit-bearing:

- `cost_limit` and `currency`;
- `compute_limit` and `compute_unit` (`cpu-core-hour` or `gpu-device-hour`);
- integer `run_limit` and `run_count_basis: planned-run`;
- `per_attempt_cost_limit` and `per_attempt_compute_limit`, each no greater than its cumulative limit;
- integer `concurrency_limit` and `retry_limit`;
- `valid_for_hours` and timezone-bearing ISO8601 `valid_until`.

Do not accept `unlimited`, negative values, NaN, or missing units. Mark non-applicable fields with a reason. Missing or ambiguous authorization data blocks the affected run; do not infer defaults or fill gaps.

## Before each attempt

One coordinator keeps the ledger and starts work. Check each condition before launch:

1. The batch is marked confirmed and its confirmation basis points to the user's original instruction, not the default policy.
2. Current time is before `valid_until`; the authorized scope includes this plan, write area, environment, command and side effects.
3. The attempt's worst-case cost and compute fit within the per-attempt caps.
4. Recorded use + worst-case reservations for running jobs + this attempt's worst-case use fit within each cumulative cap. Exact equality is allowed.
5. Count `planned-run` slots by distinct run IDs; retries reuse the same run ID. Check the active concurrency and remaining retry limit. Failed, timed-out and invalid attempts consume compute and cost; retries do not create new planned-run slots, but still consume the attempt's resources.
6. Unknown consumption remains reserved, never treated as zero. If a running reservation cannot be verified, stop before launching another job.

Append a `worst_case_estimate` and `started_at` before launch. Record `finished_at`, actual consumption and result only from original command/job evidence; missing measurements remain `unknown`, and uncovered consumption remains reserved. Keep each attempt's identity, raw logs, exit evidence and artifact locations linked in the log.

## Hard stops

Stop before launch when authorization is missing, expired, out of scope, over any per-attempt or cumulative cap, over concurrency or retry limits, or when consumption cannot be reconciled. Never delete or overwrite existing experiment results under ordinary batch authorization; ask for separate explicit approval for that destructive action. Recovery rereads the actual authorization and original job state; it does not extend `valid_until`.

This reference describes how to verify and account for authorization. It does not authorize a command, remote access, upload/download, paid resource, cleanup, or new credential beyond the user's confirmed scope.
