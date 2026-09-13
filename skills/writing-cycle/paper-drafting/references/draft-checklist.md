# Author drafting checklist

Apply every item to the requested draft. Record checked / not applicable with reason / unresolved with the missing material. Adapted from Orchestra’s section workflow, writing-guide checks, checklist content and four evaluation dimensions. This is author self-check, not an independent review or a submission gate.

## Claim coverage and technical quality

- Every claim in the supplied plan appears within the requested scope, or has an explicit unsupported/contradictory/deferred explanation. The title, abstract, contribution list, results, captions and conclusion express the same bounded finding.
- Every quantitative statement, comparison, table value and conclusion has an original-source locator. Recompute reported deltas from those values, with units, denominator, rounding, aggregation and comparison direction visible in the notes.
- Baselines use the described split, configuration, metric and budget. Include relevant unfavorable outcomes and failed/invalid attempts; report why exclusions are justified by the actual protocol.
- Number of runs/seeds, data splits, hyperparameters, search/selection procedure, uncertainty method and compute are reported when relevant and available. Missing details are gaps, not fabricated defaults or reasons to launch experiments.
- Each experiment paragraph states its claim, setting and observation. A single run does not become a significance test; a mechanism claim requires the evidence that actually distinguishes it from alternatives.
- Formal claims preserve assumptions, quantifiers, domains, notation and distinctions between proof, proof sketch and conjecture. Main-text/appendix restatements must agree with supplied source material. Missing proofs are explicit; this check does not establish mathematical correctness.

## Clarity, narrative and significance

- The existing contribution can be expressed in one sentence; the introduction explains What, Why and So What. Importance and originality claims have a source or are framed as the author’s bounded motivation, not guaranteed impact.
- The abstract gives the contribution, difficulty, approach, actual evidence and a supported result/guarantee. It is self-contained, with defined acronyms and no generic field-opening filler.
- The introduction follows the agreed plan, identifies a concrete gap and previews scope. Related work synthesizes method/assumption/question groups and explicitly explains the relationship to the draft’s work.
- Methods expose the actual implementation or derivation sufficiently for the requested draft; intuition accompanies formal statements. Supporting detail is located, not waved away with nonexistent supplementary files.
- Apply all seven reader-expectation principles and micro-level tips from the writing guide: subject/verb proximity, stress/topic position, old-before-new, one function per unit, action in verbs, context before new material; clarify pronouns, remove filler and inspect paragraph transitions.
- Terminology, abbreviations, notation, comparison direction and uncertainty remain unchanged by tone edits. No promotional synonym creates novelty; no style rule removes a truth-defining hedge, assumption or negative result.
- A skim reader can recover the supported contribution from title, abstract, introduction and captions. Existing figures/tables are readable, correctly labeled and self-contained; schematic illustrations are not described as empirical evidence.

## References and source integrity

- Every used citation has identity, version, metadata and passage-level context checks, or a visible citation gap. No guessed DOI, bibliography entry, author, year or unsupported attribution appears as verified.
- Citation keys, section labels, figure/table references and include paths resolve in the authorized draft. Check multiple keys per citation and any relevant appendix use; list missing dependencies instead of asserting compilation success.
- Table values and figure captions agree with raw results and scope. Style examples and their illustrative numbers have not leaked into the manuscript.

## Limitations, reporting and venue

Use the following reporting subjects from Orchestra’s checklist when applicable; they are prompts to inspect real materials, not universal current venue rules or a mandate to add research:

1. **Claims and limitations**: scope, assumptions, failures, robustness evidence and what remains unknown.
2. **Theory**: complete source proofs where supplied; missing obligations stay visible.
3. **Reproducibility and access**: actual instructions, environment descriptions, code/data/model availability and access restrictions; do not promise release or configure the environment.
4. **Experimental details**: splits, search ranges, selection method, seeds, uncertainty and compute from records.
5. **Ethics and broader impacts**: documented concerns, affected groups and mitigations; neither declare compliance nor invent risks/approvals to fill a checklist.
6. **Safeguards**: existing release/access controls for sensitive assets; no automatic release.
7. **Asset licenses and documentation**: actual creator, source/version, license and supplied documentation; do not infer permission from a URL.
8. **Human participants**: provided instructions, compensation, consent, risk assessment and IRB/equivalent records; ask when absent.
9. **LLM disclosure**: describe actual usage according to the current official policy and the user’s records; do not assume writing assistance is exempt.
10. **Domain-specific reporting**: e.g. language coverage, annotator details or agreement metrics for NLP; mark unrelated subjects not applicable.

For a named venue, confirm edition/stage, official-rule sources, allowed template, required sections and anonymity treatment. Unresolved official rules and user-template conflicts remain visible. Source text alone cannot confirm page count, font embedding, rendering or a successful PDF build.

## Handoff and stop

- All requested sections contain prose or precise visible gaps, not just an outline. Draft and notes identify every blocked item and the exact material/decision needed next.
- Only approved destinations changed; source Claims, Evidence, data, shared bibliography, templates and unrelated sections remain intact unless explicitly in scope.
- State exactly which checks ran and their limits. Independent claim/citation/proof audits, new experiments, plotting, compilation, resubmission and publication have not been triggered by drafting.
- Return the candidate manuscript, traceability notes and decisions; stop. A complete checklist is not proof of scientific validity, acceptance or submission readiness.
