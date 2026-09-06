---
name: citation-reference-audit
description: Audit pinned citations and external-reference receipts for identity, metadata, byte fixation, and contextual support inside the current workflow.
---

# Citation Reference Audit

Model-invoked discipline only. Work from the calling workflow's enumerated citation occurrences, bibliography records, pinned local bytes, and external-reference receipts. Do not browse, fetch, replace references, edit the manuscript, or treat an unfixed URL as evidence.

## Audit procedure

1. Match every citation occurrence to exactly one reference identity and every bibliography entry to at least one intended occurrence. Flag aliases, duplicates, missing entries, and ambiguous versions.
2. Verify authorship, title, venue or repository, date, version, persistent identifier, source URL, retrieval record, content digest, and license or usage evidence when required.
3. Read the cited fixed bytes and compare the manuscript's local proposition with what the source actually states, under its assumptions, population, definitions, and limitations.
4. Distinguish existence, metadata correctness, and contextual support. Passing one layer cannot excuse failure in another; a secondary citation cannot silently stand in for a claimed primary result.
5. Report retractions, corrections, version drift, inaccessible required bytes, quotation errors, and scope inflation with citation occurrence and fixed source scope.

Return per-reference and per-occurrence `pass`, `fail`, or `blocked` findings. Missing fixed evidence is `blocked`, not guessed. This discipline cannot fetch missing material, change research semantics or budget, confer human acceptance, alter a Claim, authorize advancement or Publication freeze, or invoke another workflow.
