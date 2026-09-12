# Experiment Plan

**Problem / Hypothesis**: [anchored problem, mechanism, predicted direction and scope]
**Method Thesis**: [one sentence]
**Date**: [today]
**Inputs**: [actual source paths or user-provided context; known facts vs assumptions]
**Planning status**: [ready for execution authorization / blocked draft — neither means execution approved]
**Output scope**: [authorized plan / tracker destinations, or conversation only]

## Claim Map

| Claim | Why It Matters | Anti-claim / Falsifying Observation | Minimum Convincing Evidence | Linked Blocks |
|-------|----------------|-----------------------------------|-----------------------------|---------------|
| C1 | ... | ... | ... | B1, B2 |

## Fixed Evaluation and Candidate Scope

- Candidate files/components and allowed hyperparameter ranges (existing vs proposed):
- Allowed future result locations:
- Fixed dataset version / splits / preprocessing / ground-truth source:
- Fixed evaluator / metric definition, direction, units, aggregation:
- Fixed selection rule, seeds/pairing, comparison budget:
- Evaluation owner, candidate implementer and actual access separation (or not enforced):
- Protocol defect/change handling and required approval:

## Paper Storyline

For non-paper projects these are core/supplementary evidence targets.

- Main paper must prove:
- Appendix can support:
- Experiments intentionally cut and why:
- Frontier primitive central / absent and why:

## Experiment Blocks

Repeat for every kept block, including supplementary blocks.

### B1: [Name]

- Claim tested:
- Why this block exists:
- Competing explanations and discriminating predictions:
- Dataset / split / task:
- Compared systems / strong baselines / ablations:
- Metrics (decisive then secondary):
- Setup details (backbone, frozen/trainable parts, hyperparameters, budget, seeds):
- Success criterion (effect size, uncertainty and scope):
- Failure interpretation (valid negative / inconclusive / invalid / operational failure):
- Table / figure target:
- Priority: MUST-RUN / NICE-TO-HAVE

## Criterion Evidence Map

Planned locations are explicitly proposed, not existing evidence. Repeat a row for every criterion, including baseline validity and budget compliance. A raw file's existence is not a criterion verdict.

| Criterion | Claim / Block | Run IDs and Comparison | Required Primary Evidence / Location / Field | Decision Rule | Existing Evidence or Not Collected / Gap |
|-----------|---------------|------------------------|--------------------------------------------|---------------|------------------------------------------------|
| K1 | C1 / B1 | ... | proposed ... | ... | not collected |

## Run Order and Milestones

| Milestone | Goal | Runs | Decision Gate | Cost / Turnaround | Risk / Mitigation |
|-----------|------|------|---------------|-------------------|-------------------|
| M0 | sanity | ... | data and metric valid before M1 | ... | ... |
| M1 | unchanged baseline | ... | valid comparable raw evidence before M2 | ... | ... |
| M2 | main method | ... | ... | ... | ... |
| M3 | decisive ablations | ... | ... | ... | ... |
| M4 | optional polish | ... | ... | ... | ... |

## Compute and Data Budget

- Resource assumptions and actual user-approved limits (separate):
- Total estimated GPU-hours / CPU-hours and calculation:
- Total run count, seeds and retries (failed attempts count):
- Per-run / total wall-time limits including startup and evaluation:
- Memory / storage caps:
- Data preparation needs and access/license gaps:
- Human evaluation needs, effort and consent if applicable:
- Monetary ceiling and remote / paid API use (zero if none):
- Biggest bottleneck:
- Stop conditions, future job-stop authority and unapproved actions:
- Must-run feasibility; optional work omitted to fit limits:

## Statistical and Validity Plan

- Sampling unit, pairing, seeds/repetitions and uncertainty reporting:
- Tuning vs held-out final evaluation; selection/multiple-comparison handling:
- Evidence retention for all attempts, missing metrics and invalid runs:
- What negative evidence limits; what remains untested:

## Risks and Mitigations

- [Risk]:
- [Mitigation]:
- [Unresolved decision, affected block and who must decide]:

## Final Checklist

- [ ] Main paper tables / core report comparisons are covered
- [ ] Novelty is isolated by a discriminating control
- [ ] Simplicity is defended or its inapplicability is explained
- [ ] Frontier contribution is justified or explicitly not claimed
- [ ] Nice-to-have runs are separate from must-run runs
- [ ] Every criterion has primary evidence requirements and a decision rule
- [ ] Candidate scope and fixed evaluation surface are disjoint
- [ ] Sanity and valid baseline gate candidate runs
- [ ] Tracker totals, hard limits, negative interpretations and blockers agree

---

# Experiment Tracker

Place in the second authorized file; if conversation-only, keep as a separate section. Expand seeds into individual run IDs or an explicit counted range, so totals are auditable. All rows below are planned, never completed evidence.

| Run ID | Milestone | Purpose / Criterion | System / Variant | Split / Seed | Metrics | Priority | Status | Planned Raw Evidence / Notes |
|--------|-----------|---------------------|------------------|--------------|---------|----------|--------|------------------------------|
| R001 | M0 | sanity / ... | ... | ... | ... | MUST | NOT RUN | proposed ... |

## Handoff

- Must-run blocks:
- Highest-risk assumption:
- First three proposed runs:
- Plan / tracker paths, or conversation-only:
- Outstanding authorization / blockers:
- Experiments not started; environment unchanged. Stop here.
