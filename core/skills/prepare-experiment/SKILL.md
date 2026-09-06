---
name: prepare-experiment
description: Build, test, and check a pinned experiment design within a hard bounded preparation budget, then stop.
---

# Prepare Experiment

User invocation only. Require an `experiment-design` Artifact whose selected path, full Git commit, SHA-256, shared contract, type, and exact type version are verified. Verify canonical provenance bytes and real fixed Project/Workstream binding; preserve those references in preparation. Build, test, and inspect its implementation without changing the fixed hypothesis, dataset, controls, metrics, criteria, or budget.

`ordinary` mode performs one attempt and stops at the first failure. Check explicit user revocation before each attempt; stop as `user_stopped` and retain prior attempts. `bounded_autonomy` may try the user-supplied bounded repair/check sequence while all six counters remain within their limits. Count resources programmatically before and after every attempt. Never add budget.

Append every attempt, command argv, environment-key list, outcome, resource receipt, stdout, and stderr to immutable ledger entries. Preserve failures and partial logs. Produce a candidate `experiment-preparation` Artifact plus report; never start `run-experiment`. List optional next steps and stop.
