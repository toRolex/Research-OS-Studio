---
name: training-health-check
description: Diagnose health signals in a pinned training run without mutating, restarting, extending, or selecting the run inside the current workflow.
---

# Training Health Check

Model-invoked discipline only. Read only the digest-pinned training protocol, metric series, logs, checkpoints, resource observations, and failure records supplied by the calling workflow. Never connect to a live tracker, restart a job, change hyperparameters, select a checkpoint, or spend additional budget.

## Check procedure

1. Verify run identity, step and wall-clock ordering, expected metric names, checkpoint identities, and completeness of the observed interval. Treat gaps or mixed run identities as blockers to trend claims.
2. Inspect non-finite values, exploding or vanishing magnitudes, abrupt discontinuities, divergence, collapse, saturation, stalled progress, unstable oscillation, and train-validation separation.
3. Correlate metric anomalies with pinned evidence for learning-rate changes, data boundaries, gradient or parameter norms, throughput, memory pressure, restarts, and checkpoint recovery. Label correlation as correlation.
4. Distinguish a healthy observed interval from convergence or generalization. Absence of an observed anomaly is not proof that the run should continue or that the selected model is valid.
5. Return findings with severity, exact series range, supporting bytes, competing explanations, and the smallest separately authorized diagnostic action.

Use `blocked` for missing or noncomparable observations, `fail` for a health violation established by pinned evidence, and `pass` only for the bounded interval checked. The result cannot change research semantics or budget, confer human acceptance, select or continue a run, authorize advancement, or invoke another workflow.
