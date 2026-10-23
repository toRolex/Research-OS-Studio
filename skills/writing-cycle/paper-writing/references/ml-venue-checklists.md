# ML/AI Venue Requirements and Pre-Submission Checklist

Adapted from Orchestra Research `ml-paper-writing/references/checklists.md` (MIT). The item *structure* below is retained because it is the professional method; the year-specific page limits, deadlines, scoring scales and policy wordings are historical upstream examples and **not** current rules. Before relying on any requirement, read the target edition's own author guide, CFP, style files and checklist and record the URLs and access date (see [`../../paper-drafting/references/venue-and-format.md`](../../paper-drafting/references/venue-and-format.md)).

Read this file when the user names an ML/AI venue, asks what a checklist requires, or when the workflow reaches the pre-submission step.

## Official rules first

1. Fix venue, year, track/article type and stage (review / preprint / camera-ready) from the request.
2. Find that edition's official author instructions, template, required statements and checklist; follow links from the official site.
3. Record which items below apply, which are confirmed by the official source, and which are unknown.
4. A past-year table or a third-party template does not confirm a current rule. Unknown stays unknown.

## Universal pre-submission checklist shape

This is the cross-venue checklist an ML/AI paper is measured against. Use it as the writing target; confirm the exact wording and the yes/no/NA response format with the current official checklist.

### Content

- [ ] Abstract within the venue's word/character limit
- [ ] Main content within the page limit; references and appendix handled per current rules
- [ ] Every headline claim matches a result actually present in the paper
- [ ] Each experiment states the claim it supports
- [ ] Limitations section present and specific
- [ ] All figures/tables have self-contained captions
- [ ] Related work situates the contribution rather than listing papers

### Technical and statistical

- [ ] Baselines appropriate, recent and fairly compared
- [ ] Error bars or intervals on quantitative comparisons, with the calculation method named
- [ ] Number of runs/seeds stated
- [ ] Hyperparameters and selection procedure documented
- [ ] Compute resources documented
- [ ] Ablations/controls present for the main design choices
- [ ] Negative or unfavorable results represented where they bear on the claim

### Reproducibility

- [ ] Code/data availability stated, or the reason for withholding
- [ ] Environment and exact reproduction commands documented
- [ ] Data splits and preprocessing documented
- [ ] Model checkpoints documented where applicable
- [ ] Any released artifact has a datasheet/model card describing training data, limitations and licensing

### Formatting and anonymity

- [ ] Correct venue + year template used unmodified
- [ ] Margins, fonts, spacing unchanged
- [ ] Double-blind rules met: no author names, acknowledgments, grant numbers, identifying repository URLs; own work cited in third person
- [ ] References complete and resolved
- [ ] PDF compiles cleanly and all figures render

### Ethics, impact and disclosure

- [ ] Broader/negative societal impact considered and stated where required
- [ ] Data/code/asset licenses cited (name, version, URL, terms)
- [ ] Human-subjects work: IRB/consent status, participant instructions, compensation stated (anonymized at submission)
- [ ] Safeguards/controlled release described for high-risk models or scraped data
- [ ] LLM/AI use disclosed to the degree the venue requires

## Venue-shape profiles

Different ML/AI venues emphasise different items. Treat these as checklists of the *kinds* of requirements to verify, not as current policy.

### NeurIPS-shaped

- A mandatory paper checklist with yes/no/NA answers and short justifications, outside the page limit. Items recur around: claims alignment; limitations; theory and proofs; reproducibility; data and code access; experimental details; statistical significance; compute resources; ethics; broader impacts; safeguards; license respect; asset documentation; human subjects; IRB; LLM declaration.
- Honest limitation acknowledgment is explicitly not penalized by reviewers (upstream reviewer instruction; verify in the current edition's reviewer guide).
- Lay summary / broader-impact material for accepted papers, when the current edition asks for it.

### ICML-shaped

- A Broader Impact Statement at the end of the paper, before references, outside the page limit: positive impacts, negative impacts, who may be affected, mitigation.
- Reproducibility checklist: data splits, hyperparameters, search ranges, selection method, compute, code availability.
- Statistical reporting: error bars on comparisons, std dev vs std error named, number of runs, significance tests between methods.
- Anonymization: no names, acknowledgments, grant numbers, identifying repository URLs, first-person citation of own work.

### ICLR-shaped

- LLM-use disclosure when an LLM played a significant role in ideation or writing; ordinary grammar/editing/code-completion assistance typically falls outside. Describe the precise role in the section the current guide names.
- Reproducibility statement referencing code/data/checkpoints, when requested.
- Ethics statement, when requested.
- Reciprocal reviewing obligations, when the edition imposes them.

### ACL-family-shaped (ACL/EMNLP/NAACL)

- A Limitations section that does not count toward the page limit; content: strong assumptions, scope, failure conditions, generalization concerns.
- Responsible-NLP items: bias/fairness, dual-use.
- Multilingual considerations when applicable: language diversity, translation validity.
- Human evaluation when applicable: annotator details, agreement metrics, compensation.
- Ethics statement where required.

### AAAI-shaped

- Strict adherence to the official style file; no layout modifications to fit content.

### COLM-shaped

- Language-model focus; the introduction and related work are framed for that audience.

## Page limits

Upstream recorded: NeurIPS 2025 9 pages; ICML 2026 8 (+1 camera-ready); ICLR 2026 9 (+1); ACL 2025 8 long; AAAI 2026 7 (+1); COLM 2025 9 (+1); references/appendix typically unlimited. **These are historical examples, not current limits.** Read the target edition's own rules and record the actual limits before claiming compliance. Never compress content by editing the style file, margins or fonts.

## Templates and licensing

- This Skill ships no conference template, style file, `.bib`/`.bst` or example PDF, and grants no license to any external asset. Upstream templates include third-party LPPL/algorithm packages and files whose redistribution terms are not covered by the repository MIT license, so they are not vendored here.
- Use the template the user already has, in the form its license allows; otherwise obtain the current official template through the user's own authorized channel and check its included license before copying it into the project.
- When a user template conflicts with the current official rules, show the conflict and let the user decide; record the decision and any remaining noncompliance rather than silently choosing.

## Checklist use

- The checklist is a writing target and a self-check. Marking every box does not establish that a scientific claim is true, that the paper is accepted, or that the authors have agreed to submit.
- An item that cannot be satisfied from the existing material is a visible gap in the report, not an invented answer. Do not answer "yes" on the user's behalf for ethics, consent, license or disclosure items.
