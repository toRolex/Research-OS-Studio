# Source verification

Shared identity and evidence check for `novelty-check` (every closest-prior entry before an overlap judgment) and `research-lit` (every candidate before synthesis). A failed check stays visible. Do not fabricate titles, identifiers, authors, venues, or full author lists from memory. Do not merge a preprint and a published version silently. A title match, a search snippet, or model memory does not confirm identity or support a claim. Search hits are leads, not evidence of a full reading.

Unknown fields stay unknown. Preserve discrepancies between versions instead of blending dates or results.

## Branch: labels

- **Closest-prior overlap (`novelty-check`).** Record the lookup in natural language: identity confirmed, unresolved match, temporarily unavailable, or malformed input. State the attempted URL and reason. Keep unverified candidates on the list, labeled with the failure or the missing material. Do not drop them.
- **Literature synthesis (`research-lit`).** Use only this vocabulary:

| Label | Meaning | Required record |
|---|---|---|
| **CANDIDATE / 候选来源** | A search result, supplied citation, or scout lead whose identity has not yet been checked. | Discovery location and known metadata; reason verification is deferred, if any. |
| **VERIFIED / 已核实来源** | An inspected primary publication/preprint record or trusted supplied original confirms the title, authors, identifier, and explainable year/version as the same work. | Identity basis and locator, date of check, edition, and any unresolved metadata fields. This label verifies identity, not every statement or scientific correctness. |
| **UNVERIFIED / 未核实来源** | An attempted identity check is insufficient or failed. | Precise reason: source unavailable, not found in searched sources, conflicting identity, pending transient failure, or malformed citation. |

`pending retry` is an unverified reason, not verified. A candidate deferred at budget exhaustion stays candidate. Preserve all three classes; do not count an access failure as a fabricated paper. Unattempted verification stays candidate, not verified.

## Identity

Shared steps, then the caller's branch:

1. Record title, authors, date/year, venue or preprint status, primary URL, and DOI/arXiv identifier only when actually found.
2. Resolve an arXiv ID against the arXiv record; a DOI against the publisher or DOI registration record. Compare actual title, authors, dates, and edition, not HTTP success. An existing but unrelated identifier fails the match. Where the DOI service is unsuitable, use a relevant disciplinary index or publisher record.
3. Match title, first author, and identifiers. Explain preprint versus published year or version differences instead of merging them. If identifiers fail, or the citation is title-only, search the exact title plus first author (and year, when known) through another available scholarly source. A fuzzy title match is a lead, not confirmation.
4. Cross-check a second trustworthy source when available, especially for ambiguous titles, publication status, or conflicting metadata. Record when only one source was inspected. Two indexes copying one record are not independent content evidence.
5. For a supplied original offline, `research-lit` may record `verified from supplied original; external cross-check not performed` only when the document itself establishes identity. An unattributed snippet or user note stays externally unverified. Its text can still support a clearly attributed supplied-material summary.

**Completion:** each candidate has the caller's label, the actual basis, the version, and unresolved fields. The inspected record is the cited work, or the mismatch is explicit.

## Branch: reading depth

Record separately what was retrieved and what was actually read, with URL or local path.

- **Overlap decision (`novelty-check`).** Scopes: search snippet; metadata/abstract; named sections; or full text including the relevant appendix. A successful download is not a full read. An abstract may triage. For any decisive overlap or delta, open the primary paper and inspect the mechanism, assumptions, stated result, and evidence. Read the dependent appendix or supplement. Keep a section/page, equation/theorem/table locator, and a short quoted passage or faithful paraphrase. State which candidate Claim it supports and under which setting. Abstract silence does not establish a key difference. Another paper's related-work sentence is a pointer, not a substitute. Preserve conflicting versions and evidence against the preferred judgment. If the difference rests on text not retrieved, mark it unknown.
- **Landscape extraction (`research-lit`).** Scopes: metadata only, abstract, first three pages, named sections/pages, or full text actually inspected. Before saying "X proved," "Y showed," "Z outperformed," or describing consensus, inspect the material that supports that exact claim. Title or topic similarity and another paper's paraphrase are not enough. For numbers, keep task, dataset, baseline, metric, configuration, and uncertainty actually reported; do not fill missing details. For theory, keep assumptions and scope; reading a theorem is not an independent proof. Attribute abstract-only results as **author-reported from abstract**. Full-text denial means those method or result details are unassessed, not that the work does not exist. A secondary note may explain the user's view; it does not become the authors' finding without their source.

The same paper can be identity-verified and unread, or read from an excerpt whose external identity is still open. Those are separate columns in a literature report. An overlap verdict cannot treat a first-three-pages or abstract-only pass as decisive when the delta is still open; record that pass as the `research-lit` reading scope and leave the overlap unknown until the novelty-check depth above is met.

**Completion (`research-lit` content):** every substantive report claim has a locator and a calibrated reading scope, or is explicitly an inference or unresolved question. Verified identity alone never clears content support.

## Branch: failure handling

Respect access limits. A paywall or denied permission is not authorization to bypass it. Do not install tools or add credentials to get through.

- **Overlap decision (`novelty-check`).** If full text, a supplement, metadata, or a required search source stays unavailable, state exactly how that limits the comparison. Ask for the specific missing material or permission, not an open-ended new project. Never convert "no hit," network failure, absent abstract detail, or missing reviewer access into "novel." Also keep supported differences and covered subclaims; do not flatten every partial limit into a blanket inconclusive outcome.
- **Literature synthesis (`research-lit`):**
  - **Not found:** record queries and sources checked. If budget remains, one targeted follow-up for title spelling, first author, or a distinctive phrase. "Not found here" is not "does not exist."
  - **Conflicting identity:** keep the original citation and the mismatching record separate. Do not replace the citation with a plausible paper.
  - **Rate limit, timeout, or access denial:** keep the actual error and source. Respect the run's retry limit (at most one retry per failed retrieval). Continue other authorized sources without hiding lost coverage.
  - **No tools:** verify only what trusted supplied originals establish. Label uncheckable citations unverified. Return a supplied-material synthesis or a specific request for sources. A planned search is not an executed search.
  - If repeated identity mismatches suggest unreliable discovery, flag that source and use the bounded follow-up for narrower queries. Access failures alone are not hallucinations.

**Completion:** remaining gaps name the exact missing record or passage and the smallest next retrieval or user input. Stop at the run's limits. Do not retry until a favorable status appears.
