---
name: statistical-check
description: Check pinned analyses for estimand alignment, statistical assumptions, uncertainty, multiplicity, leakage, and claim-strength mismatches inside the current workflow.
---

# Statistical Check

Model-invoked discipline only. Inspect the calling workflow's fixed protocol, data description, analysis specification, outputs, and candidate interpretation. Do not collect data, rerun analysis, tune thresholds, choose a preferred endpoint, or rewrite the research question.

## Check procedure

1. Identify the population, sampling or experimental unit, estimand, estimator, comparison, endpoint, and decision criterion exactly as declared. Report any mismatch before considering numerical significance.
2. Check independence, exchangeability, missingness, censoring, distributional assumptions, preprocessing, exclusions, leakage, stopping rules, seed aggregation, and whether the effective sample size matches the unit of inference.
3. Check effect sizes and uncertainty intervals before thresholded significance. Record multiplicity across outcomes, subgroups, models, seeds, checkpoints, and analysis variants; reject post-hoc selection presented as preregistered.
4. Distinguish descriptive, associational, predictive, and causal conclusions. Mark language stronger than the design or evidence permits.
5. For every finding, cite the pinned byte scope and state whether it changes validity, precision, generalizability, or only presentation.

Return structured findings with `pass`, `fail`, or `blocked`; never synthesize a scalar quality score. A pass means only that this bounded statistical check found no disqualifying issue. It cannot change research semantics or budget, create Evidence support, revise a Claim, confer human acceptance, authorize advancement, or invoke another workflow.
