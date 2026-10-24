# ML/AI Reviewer Expectations

Adapted from Orchestra Research `ml-paper-writing/references/reviewer-guidelines.md` (MIT). This reference tells the writer what ML/AI reviewers look for, so the draft can pre-empt predictable weaknesses. Scoring scales and timelines upstream were edition-specific examples and are not current rules; read the target edition's own reviewer guide before quoting a scale. Responding to actual reviews is the separate user-invoked `rebuttal` entry (ticket #29) and is **not** started by this workflow.

Read this file before the independent review step and when diagnosing a reviewer-style objection.

## The four assessment dimensions

All major ML/AI venues assess a paper across these dimensions. Write and self-check against each.

**Quality (technical soundness)** — are claims supported by the analysis and experiments actually present? Are proofs correct? Are experiments controlled? Are baselines fair and recent? Was methodology sound? Pre-empt with complete proofs or honest gaps, non-strawman baselines, reported variance with its method, and a documented tuning procedure.

**Clarity (writing and organization)** — is the paper clear and well organized? Can an expert reproduce it? Is notation consistent and defined? Is it self-contained? Pre-empt with consistent terminology, definitions at first use, reproducible detail, and an explicit signposting sentence for each section.

**Significance (impact)** — does the result matter to the community, and will others build on it? Pre-empt by articulating the problem's importance, connecting to recognized themes, and comparing meaningfully (not just numerically) to existing approaches. Significance claims about deployment or societal reach need a source or must be framed as bounded motivation.

**Originality (novelty)** — is there a new insight, and how does it differ from the closest prior work? Note that originality does not require a wholly new method: a novel evaluation or an explanation of why existing methods work can be original, when the evidence supports it. Pre-empt with an explicit relation to the closest prior work, not a claim of being first. "First" claims require independently checked prior work.

## Reviewer behavior the entry points follow

Reviewers form a judgement from the title, abstract, introduction and figures before reaching the methods. That makes the entry points disproportionately load-bearing without asserting any fixed reading percentage:

- The abstract must carry the contribution, difficulty, approach, actual evidence and a supported result.
- The introduction must front-load the contribution and preview scope.
- Figure 1 should convey the core idea or most compelling result.
- The methods and appendix support the decision; they do not rescue a buried contribution.

## Scoring calibration

Venues use different scales (for example a 1–6 recommendation scale, or separate soundness/presentation/contribution plus an overall score and confidence). Upstream's numeric labels and "top X% of accepted papers" bands are historical examples. Use the current edition's own reviewer instructions, and in self-review record the scale you actually applied.

When a fresh reviewer is used in this workflow, the reviewer reports a score on the scale the current guide defines, or records that the scale was unavailable.

## Common reviewer concerns and pre-emption

**Technical**

| Concern | Pre-empt with |
|---|---|
| "Baselines too weak" | state-of-the-art and recent baselines; cite the work being compared to |
| "Missing ablations" | systematic ablation of the design choices the claim depends on |
| "No error bars" | report the actual std dev/error/interval, with the method |
| "Hyperparameters not tuned" | documented tuning process, search ranges, matched budget for baselines |
| "Claims not supported" | every claim traced to a result that actually tests it |
| "Compute unclear" | recorded worker type, count, time and total |

**Novelty**

| Concern | Pre-empt with |
|---|---|
| "Incremental" | precise statement of what is new relative to the closest prior work |
| "Similar to [paper X]" | explicit comparison to X in related work |
| "Straightforward extension" | the non-obvious design decisions and their evidence |

**Clarity**

| Concern | Pre-empt with |
|---|---|
| "Hard to follow" | structure, signposting, one point per paragraph |
| "Notation inconsistent" | a notation table and a consistent symbol set |
| "Missing details" | a reproducibility appendix with the experiment's actual settings |
| "Figures unclear" | self-contained captions, legible axes, correct uncertainty display |

**Significance**

| Concern | Pre-empt with |
|---|---|
| "Limited impact" | a bounded, sourced account of the consequence of the result |
| "Narrow evaluation" | evaluation across the settings the claim actually covers |
| "Only works in a restricted setting" | state the scope and what it means for the claim |

## Pre-submission reviewer simulation

Before declaring the draft ready, answer these for the current manuscript and record the answers:

**Quality** — would I trust these results if I saw them? Is every claim supported by evidence? Are baselines fair and recent?
**Clarity** — can someone reproduce this from the paper? Is the writing clear outside this subfield? Are terms and notation defined?
**Significance** — why should the community care? What can be done with this work? Is the problem important?
**Originality** — what specifically is new? How does it differ from the closest related work? Is the contribution non-trivial?

This simulation is author-side self-review. It never substitutes for the fresh-context independent review required by the workflow, and it does not establish acceptance.

## Boundary

Reading this file does not authorize contact with reviewers, submission, rebuttal drafting, or a claim about how a specific reviewer will score. Reviewer feedback in the user's possession is handled by the separate `rebuttal` entry at the user's explicit request.
