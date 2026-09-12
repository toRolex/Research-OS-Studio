# Source verification

Apply this to every candidate before using it in the literature synthesis. A source's existence, metadata and support for a statement are different questions.

## Status vocabulary

| Label | Meaning | Required record |
|---|---|---|
| **CANDIDATE / 候选来源** | A search result, supplied citation or scout lead whose identity has not yet been checked. | Discovery location and known metadata; reason verification is deferred, if any. |
| **VERIFIED / 已核实来源** | An inspected primary publication/preprint record or trusted supplied original confirms the title, authors, identifier and explainable year/version as the same work. | Identity basis and locator, date of check, edition and any unresolved metadata fields. This label verifies identity, not every statement or scientific correctness. |
| **UNVERIFIED / 未核实来源** | An attempted identity check is insufficient or failed. | Precise reason: source unavailable, not found in searched sources, conflicting identity, pending transient failure, or malformed citation. |

Keep `pending retry` as an unverified reason, not verified. A candidate deferred at budget exhaustion stays candidate. Preserve all three classes in the report; no silent dropping or counting an access failure as a fabricated paper.

## Identity check

1. For an arXiv ID, inspect the corresponding arXiv record and compare actual title, authors and dates. An existing but unrelated ID fails the match.
2. For a DOI, inspect the publisher/registration record; compare metadata and edition, not just HTTP success. Where the DOI service is unsuitable, use a relevant disciplinary index or publisher record.
3. For a title-only citation, search exact phrases with the first author/year, then inspect the likely original record. Fuzzy title overlap supplies candidates, not confirmation.
4. Cross-check a second trustworthy source when available, especially for ambiguous titles, publication status or conflicting metadata. Record when only one source was inspected; do not pretend two indexes copying one record are independent content evidence.
5. For supplied originals offline, record `verified from supplied original; external cross-check not performed` only when the document itself establishes identity. An unattributed snippet or user note remains externally unverified. Reading its text can still support a clearly attributed supplied-material summary.

Unknown fields remain “unknown.” Never construct a DOI/arXiv ID, venue or full author list from memory. Preserve discrepancies between a preprint and published version instead of blending their dates or results.

Completion: each candidate has an identity label, actual basis, version and unresolved fields; the inspected record is demonstrably the cited work.

## Content support and reading scope

Record separately: metadata only, abstract, first three pages, named sections/pages, or full text actually inspected. Include the URL/local path and section/page/table/theorem locator, with a short supporting passage or precise paraphrase where useful.

Before saying “X proved,” “Y showed,” “Z outperformed” or describing consensus:

- Inspect the material that supports that exact claim. Title/topic similarity and another paper's related-work paraphrase are insufficient.
- For numerical comparisons retain task, dataset, baseline, metric, configuration and uncertainty information actually reported; mark missing details instead of supplying them.
- For theoretical statements retain assumptions and scope. Reading the theorem is not independent proof verification.
- Attribute abstract-only results as **author-reported from abstract**. Full-text access denied means unassessed method/results details, not nonexistent work.
- A secondary note may explain the user's view, but it cannot turn into the original authors' finding without checking their source.

Completion: every substantive report claim has a source locator and calibrated reading scope, or is explicitly an inference/unresolved question. Verified identity alone never clears content support.

## Failure and stop handling

- Not found: record queries/sources checked; use the one targeted follow-up for title spelling, first author or a distinctive phrase if budget remains. “Not found here” is not “does not exist.”
- Conflicting identity: retain the original citation and mismatching record separately; do not replace it silently with a plausible paper.
- Rate limit/timeout/access denial: retain the actual error and source. Respect retry limits and access restrictions; continue other authorized sources without hiding lost coverage.
- No tools: verify only what trusted supplied originals establish, label uncheckable citations unverified, and return a supplied-material synthesis or a specific request for sources. Planned searches are not executed searches.

Completion: remaining gaps name the exact missing record/passage and smallest next retrieval or user input. Report and stop at the run's limits rather than retrying until a favorable status appears.
