# ML Experiment Reporting

Body-level method for the experiments, reproducibility and limitations parts of an ML/AI paper. Adapted from Orchestra Research `ml-paper-writing` (`SKILL.md`, `references/checklists.md`, `references/reviewer-guidelines.md`, MIT). This is writing and checking discipline over material the user already has: it never runs, reruns, tunes or repairs an experiment, and it never invents a missing value.

Read this file before writing or revising any experiment, result, ablation, compute, reproducibility or limitations passage.

## 1. Every experiment carries an argument

For each experiment reported, state at the point of the result:

- the claim it tests, in one sentence ("This experiment tests whether …");
- how that claim connects to the headline contribution;
- the setting actually used (dataset/split, model/configuration, metric, budget);
- what the reader should observe ("the error bars on the three seeds show that …"), without asserting more than the numbers show.

An experiment with no claim is decoration; a claim with no experiment is a gap. Numbered experiment order follows the argument, and the strongest evidence is placed where reviewers actually read.

## 2. Baselines and comparisons

- Use the strongest reference points the material actually contains: state-of-the-art and recent work, not strawmen. A baseline named in the plan but never run is a gap, not a result.
- Compare under matched conditions: same data split, preprocessing, metric definition, tuning budget and compute class. When conditions differ, say so explicitly instead of writing a headline delta.
- Report comparison direction and units (`↑` higher is better, `↓` lower is better) and keep decimal precision consistent across a table.
- Bold the best value per metric as a reading aid, and never let bolding or a small delta stand in for a significance claim.
- The user's own earlier results, reimplementations and reported numbers from other papers are different sources; label which is which and do not merge them into one column.

## 3. Runs, seeds and uncertainty

This is the discipline reviewers fail papers on most often; report it from real logs only.

- Number of runs/seeds: state the exact count per configuration. A single run is a single run; it is not a mean and not a significance test.
- Error bars: report the actual uncertainty quantity the material has (standard deviation, standard error, min/max, confidence interval, or a statistical test) and name the calculation method and the underlying unit (seeds, folds, samples). "Error bars" without a stated method is incomplete.
- Distinguish population standard deviation from standard error of the mean. They answer different questions and are not interchangeable.
- When the material only contains one seed for some cells, mark those cells as single-run in the table/caption and in the traceability notes; fill the remaining cells from what exists. Do not average seeds that were not run and do not report a best seed as the result.
- Aggregation: state what is averaged, over how many units, after which filtering, and how failures were treated. Report a spread alongside a mean; a mean with hidden variance is a gap.
- Significance: only report a test the material actually contains, with its assumptions and multiple-comparison handling. Correlated runs are not independent evidence. When the plan asserts significance and the material has none, the claim is narrowed or deferred, not asserted.
- Numeric claims in the abstract/introduction must match the tables, including whether the number is a mean or a single run.

## 4. Hyperparameters and selection

- List the hyperparameters that matter for reproduction, and for each state search range and the selection procedure (grid, random, Bayesian, validation-based early stopping).
- Distinguish the configuration used to select hyperparameters from the held-out data used to report the final number; tuning on test data invalidates the comparison.
- If baselines were not tuned under a comparable budget, record that asymmetry rather than hiding it.
- Report the final design decisions in the main paper; keep the full search log as supporting material, and only add it as an appendix when it is genuinely needed to support a claim.

## 5. Data and splits

- Specify data source, version/date, licensing/permission status, preprocessing, filtering, deduplication and the exact train/validation/test split or cross-validation scheme.
- State whether the test set was used to make any decision. Once a split is used for selection it is no longer a clean test set, and the paper says so.
- Record dataset construction for any dataset this work releases: collection process, consent/labeling where applicable, known biases and limitations.

## 6. Compute reporting

Reviewers and checklist items ask for compute, so report it as fact from actual logs:

- compute worker type (CPU/GPU/accelerator model and count), memory, and storage where relevant;
- wall-clock time per representative run and total project compute (hours or GPU-hours) over the runs actually performed;
- the execution environment that affects the number (framework/version, precision, distributed configuration);
- the provider or cluster only when it is material to interpreting the result. Cost is not a scientific result.

If the material does not contain these, mark a visible gap such as `[COMPUTE NEEDED: GPU type/count and total hours]`; never estimate a plausible figure.

## 7. Ablations and controls

- An ablation removes or varies one factor to show what the method depends on. State the hypothesis for each ablation and keep the surrounding setting fixed.
- Include the ablations the plan committed to, including negative/neutral ones. An ablation whose result hurts the story is reported in a table; it is not deleted and it is not reframed as a "trade-off" unless the evidence supports that framing.
- Distinguish ablation from sensitivity analysis (varying a value) and from a baseline comparison (different method).

## 8. Reproducibility and artifact availability

- Provide or point to exact commands, environment specification, data access and checkpoints appropriate to the contribution. Say plainly when something cannot be released and why.
- Reproducibility statements describe what was actually done and released, not what could be done in principle.
- A reproducibility appendix is not a substitute for stating the setting of each experiment inline.

## 9. Negative, failed and invalid results

- Keep failed runs, divergences, OOMs, timeouts and invalid attempts in the record. In the paper, report the outcomes that affect interpretation; in the report, list all of them.
- Do not silently drop a configuration because it lost. Exclusions are legitimate only under a stated protocol (for example, a pre-registered failure criterion), and the protocol is written down.
- A crashed or invalid run is not evidence for or against the claim.

## 10. Limitations (dedicated section)

ML/AI venues require or strongly expect a limitations passage; write it as a real section, not a disclaimer.

- Name the strong assumptions the method or analysis relies on and where they are likely to fail.
- State scope constraints: domains, languages, scales, regimes, and evaluation types not covered.
- Identify performance-influencing factors the study did not control.
- Explain, where honest, why the named limitations do not invalidate the bounded core claim, without turning the section into a defense.
- Point at the limitation beside the affected claim as well; the reader should not have to reach the end of the paper to learn the scope.
- A limitation that contradicts a headline claim is a scope decision for the user, not a sentence to soften.

## 11. Tables and figures as evidence

- Tables: use the template/booktabs conventions when the venue provides them; include direction symbols and units; right-align numeric columns; keep precision consistent; caption must define every symbol and the uncertainty quantity.
- Figures: captions stand alone and state what is plotted, the aggregation/seeds, and the uncertainty band. Mark annotated figures whose shape is a design choice, not data.
- No title inside a figure; no unlabeled axis; no truncated axis that exaggerates a difference; colorblind-safe palettes and grayscale legibility where the venue expects them.
- Chart and table numbers must match the traceability table and the abstract exactly.

## 12. Incomplete reports

The user's material is often incomplete. The correct output is a reviewable draft with visible holes:

- Place `[EVIDENCE NEEDED: what is missing and which claim it affects]` at the exact sentence, cell or caption, and repeat it in the report with the minimal material needed.
- Phrases such as "we report the mean over N seeds" are only written when N runs exist. Otherwise write the single-run wording or the gap marker.
- Do not substitute a default (for example "3 seeds", "8×A100") for a missing fact, and do not infer compute from model class.
- If a planned experiment was never run, the corresponding claim is narrowed to what the run evidence supports or deferred to the user.

## 13. What this reference never authorizes

Reading this file grants no experiment, environment, download, purchase or remote-write permission. It does not authorize changing a metric, dropping a baseline, weakening a claim, or editing the user's source results. Those are user decisions recorded in the report, not silent edits.
