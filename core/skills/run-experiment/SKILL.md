---
name: run-experiment
description: Execute a prepared pinned experiment in ordinary or explicitly bounded-autonomy mode, preserving every attempt, then stop.
---

# Run Experiment

User invocation only. Require pinned `experiment-design` and successful `experiment-preparation` Artifacts passing shared contracts, provenance-byte checks and identical fixed Project/Workstream bindings. Preserve those bindings in the run. Check user revocation before each attempt and stop as `user_stopped` without losing history. Execute argv commands without a shell. `ordinary` mode stops after the first failed, blocked, timed-out, or result-missing attempt. `bounded_autonomy` may retry only the user-supplied sequence and only while elapsed seconds, USD cost, tokens, GPU-hours, attempts, and rounds stay within hard limits.

Preflight cumulative preparation-plus-run counters and hard-stop before over-budget work. Non-time counters require an explicit complete usage receipt; never infer missing cost, tokens, or GPU-hours as measured usage. If an executor reports excess consumption, preserve the attempt and stop as budget exhausted. Never blindly resubmit an unknown remote job. Reject a pre-existing expected-result path, snapshot partial or successful result bytes into the immutable attempt ledger, and never overwrite an earlier attempt. If a failed attempt leaves a partial result, preserve it and stop before retrying as `partial_result_requires_user_action`; a later successful no-op must never reuse failed bytes.

A zero exit status is only execution success. It does not establish a Claim, assurance pass, or human acceptance. Produce a candidate `experiment-run` Artifact and report, list optional next steps, and stop without analyzing.
