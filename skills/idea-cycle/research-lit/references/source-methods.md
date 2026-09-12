# Literature source methods

## Existing materials

### Reference-manager library

When a requested library is already accessible through an authorized connector:

1. Search by the research topic and its aliases.
2. Read relevant collections/folders.
3. Extract annotations and PDF highlights for relevant papers; these show what the user considered important, not independently established facts.
4. Retrieve citation data; export BibTeX only when requested, without modifying the collection.
5. For each entry retain title, authors, year, venue, annotations, tags, collection and stable item locator.

Completion: relevant results and actual access failures are recorded, with user annotations distinguished from paper passages. Detect tools from the host's available capabilities; a mention of Zotero does not make a connector exist.

### Research notes / Obsidian

When the requested notes are readable:

1. Search notes by topic and tags.
2. Read the user's summaries and insights, not only titles.
3. Follow relevant note links within the citation-depth and material budget.
4. Retain note title/path, insights, linked sources and available frontmatter (paper URL, status, rating).

Completion: the user's processed understanding is represented with its note locator; a rating or summary is not relabeled as verification of the original paper. Read-only access is sufficient; no automatic vault note creation.

### Local papers

1. Prefer an explicit user library, then a library recorded in project instructions/navigation; otherwise inspect project `papers/` and `literature/` if present. Do not scan unrelated home directories.
2. Compare candidates against library/index results. Identifiers establish duplicates; filenames only prioritize screening.
3. Prioritize filename relevance and first-page content; screen up to 20 relevant papers unless the caller set another bound.
4. Read the first three pages for title, authors, year, core contribution and direct/tangential relevance. Record shorter, unreadable or scanned documents accurately; use an existing authorized reader/OCR capability, not an installation step.
5. Keep deeper reading for the selected papers carrying the synthesis. A library hit already seen through a manager may still require reading its local PDF.

Completion: the report distinguishes screened introductions from inspected methods/results. If no library contributed, list checked locations and suggest supplying a path or material; do not create directories to conceal the absence.

## External sources

These are source roles, not required integrations. Use requested sources only when the host actually exposes an authorized way to access them. Consult current official documentation before using unfamiliar tool/API syntax; do not copy runtime helpers from another installation.

| Source role | Method and distinctive value | Interpretation boundary |
|---|---|---|
| arXiv / relevant preprint collection | Search technical terms; retrieve title, abstract, author list, categories and actual submission/version dates. Keep accessible text links; metadata lookup needs no PDF save. | Preprint identity does not establish peer review or experimental validity. |
| Semantic Scholar / scholarly index | Search published journal/conference collections as well as preprints; collect venue, DOI, citation links and available abstract/TLDR. Include venue-only papers absent from arXiv. | Index metadata is a lead for primary verification; generated TLDR is not a paper passage. Citation counts need source/date, not model memory. |
| Progressive reader (e.g. DeepXiv) | Search → brief → document outline/head → the relevant sections, especially methods and experiments. Deepen only the most relevant papers. | Each stage has a different reading depth; a brief is not full-text reading. Retain section locators. |
| Broad web/content search (e.g. Exa or host equivalent) | Search both research-paper collections and the wider web for code, blogs, documentation and alternate terminology; retain content highlights and URLs. | Blogs/docs are labeled non-paper sources; inspect the original paper before attributing a scientific result. |
| Assisted literature scout | Decompose sub-problems, aliases, neighboring tasks and benchmark variants for wider discovery; use the briefing below if an authorized scout is available. The executor can apply the same search angles sequentially. | Scout output supplies candidates. It does not verify identity, read papers on the executor's behalf without evidence, or replace factual checking. |
| OpenAlex / cross-disciplinary citation graph | Find works beyond CS, citation connections, topic classifications, institutions and funding where relevant to the question. | Merge source-specific metadata with explicit origin; no index is universally more accurate or current. Resolve conflicts against primary publication records. |

### Assisted scout briefing

Provide the actual topic, cutoff, source restrictions, confidentiality boundary and a share of the existing search budget:

> You are a research literature scout. Search for papers on the stated question from multiple angles: sub-problems, aliases, neighboring tasks and benchmark/setting variants. Prefer genuinely relevant work over keyword adjacency. Include suitable venues, journals, surveys, recent preprints, foundational work and papers with code. For each candidate return exact title, full author list if available, year, exact venue or preprint label, arXiv ID, DOI, code URL and a one-sentence contribution, leaving unknown fields unknown. Also return actual queries, source URLs, filters, failures and what you read. Stay within the assigned request limit; return fewer papers rather than inventing entries to meet a quota. Do not modify project files or make acceptance/novelty judgments.

Completion: actual scout output has been received and its candidates verified under the same rules as all other sources, or the missing capability is reported. Broad discovery remains useful without a particular provider.

### Merge discipline

- arXiv/index/progressive-reader matches: compare arXiv ID, DOI, title, authors and version. Retain one paper family with labeled editions and all discovery locations.
- Prefer primary published metadata when citing a confirmed publication; preserve preprint text/version links when those were actually read. An index venue field alone does not establish equivalent contents.
- Broad web matches: compare canonical URLs and title/author metadata; keep non-paper sources distinct.
- Scout matches: reconcile supplied identifiers with records, retaining uniquely discovered candidates and unresolved mismatches. Do not inherit its citation counts.
- Cross-disciplinary graph matches: retain useful institutions/funding/topics with source attribution rather than overwriting conflicting metadata silently.

Completion: duplicates are consolidated without losing version differences or user notes; uncertain near-matches remain visible.

## Saving materials

Only when requested and the destination is authorized:

1. Download the top 3–5 relevant accessible papers (default maximum five); skip already-held identical editions.
2. Use the approved library path, respect source rate limits and stop on access denial; do not bypass paywalls or add credentials.
3. Confirm each returned file is a readable paper matching the intended identity. A nonempty response, file size or `.pdf` suffix alone may be a login/error page.
4. Keep original metadata and note actual paths, editions and failed downloads in the report. Preserve existing files on conflicts.

Completion: each attempted save has an actual success/failure outcome. Saving is optional and does not authorize wiki ingest, memory updates, remote collection writes or a new research workflow.
