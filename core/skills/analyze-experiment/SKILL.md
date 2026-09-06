---
name: analyze-experiment
description: Analyze only pinned bytes from one completed experiment run without performing any additional run, then stop.
---

# Analyze Experiment

User invocation only. Require a successful `experiment-run` Artifact selected by full Git commit and SHA-256, then read the recorded result bytes from that same commit and verify their SHA-256. Validate shared contracts, provenance bytes and fixed Project/Workstream binding; propagate the exact binding and canonical `{activity, inputs}` provenance into the analysis. Use the experiment's already-fixed metrics and criteria. Report findings, per-criterion outcomes, uncertainty, insufficiency, and negative results without beautification.

This workflow has no executor, command, retry, submission, or budget-expansion seam. Snapshot project files around analysis and fail if analysis mutates project state. Never rerun, resubmit, regenerate, tune, or silently repair the experiment; request a separately authorized workflow if more data is needed.

Produce a candidate `experiment-analysis` Artifact declaring `additional_runs_performed: false` and a report. Do not create Claim support. List optional next steps and stop.
