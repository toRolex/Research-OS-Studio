# Citation workflow for drafting

Adapted from Orchestra Research’s `ml-paper-writing` and `references/citation-workflow.md`. This is the complete local citation decision sequence, not its Python citation manager. Use existing authorized tools; no API client, MCP server or account is a prerequisite.

## Search → Verify → Retrieve → Validate → Add

Apply all five steps to every citation introduced into the draft. Existing bibliography entries are candidates too, not proof that the cited statement is true.

### 1. Search

Start with the plan’s references, existing bibliography and papers already mentioned in the research material. Search for the exact title and author, then specific technique, baseline, problem or assumption terms when needed. Keep the actual query and candidate URL or local path in the drafting notes.

Use available authorized scholarly search: Semantic Scholar for discovery and citation links, DOI registries/publishers for identified works, arXiv for preprints, or OpenAlex for broader discovery. These are optional services, not tool names the host must have. Follow current host instructions for search and library/API usage. No result, tool failure or exhausted budget means a visible citation gap, not permission to install a tool, buy a service or guess.

**Done**: each intended citation has an identified candidate or a stated search gap.

### 2. Verify identity

Compare title, complete author list, year/version and DOI/arXiv identifier against two sources where available, including a primary landing page or the original paper. Do not accept the first search hit automatically. Confirm that different records describe the same work and version; a valid URL, HTTP success, XML entry or matching keyword alone is insufficient.

Separate a preprint from its published version. Prefer the version actually read that supports the statement; if switching to a published version, confirm the relevant content remains. No DOI is not evidence a work is nonexistent. If only one source can be checked, state that limitation rather than claiming two-source verification. Conflicting identities remain unresolved.

**Done**: identity and version checks have source locations and an explicit outcome; ambiguity is preserved.

### 3. Retrieve metadata

Retrieve bibliography metadata from the publisher, DOI content negotiation, official proceedings or arXiv record using available tools. A DOI can be registered outside CrossRef; a failure there does not justify inventing metadata. When machine-readable metadata is unavailable, transcribe only fields directly present in an inspected authoritative source and record that manual provenance.

Verify entry type, full authors, title, year, venue and identifier; preserve capitalization and valid escaping. Do not create fallback author “Unknown,” year zero, guessed journal, pages or a plausible DOI. Preserve existing project keys and bibliography conventions where consistent. A fetched entry still needs the context check below.

**Done**: all used fields have provenance; missing required metadata is explicitly unresolved.

### 4. Validate the cited statement

Read the relevant full-text passage, theorem, methods, result or table—not merely search snippets or keyword hits in the abstract. Record a page/section/table/theorem locator and the bounded statement it supports. Check assumptions, task, population, comparison, direction and strength of attribution.

A real paper can be the wrong source for a claim. If only the abstract is accessible, cite only what that abstract actually establishes and label the access limitation; unsupported details remain gaps. Numerical claims from a review should be traced to the original study when possible; otherwise mark them as secondary-source-only. Do not turn several related papers into a claim that none of them makes.

**Done**: each citation has a supporting passage and scope, or is excluded from factual support and listed as unresolved.

### 5. Add to the authorized draft

Use only resolved citations as support in the manuscript. Markdown may use ordinary links or the user’s citation style; LaTeX uses the existing template’s commands and bibliography backend. Do not switch to BibLaTeX/Biber or rename shared keys merely because the upstream guide recommends it.

For unresolved work, insert visible `[CITATION NEEDED: what must be checked]` at the affected sentence and record the specific missing identity, metadata or support check. Do not emit fake `\cite{PLACEHOLDER...}` keys or dummy BibTeX entries that look like genuine references. The surrounding claim must not remain asserted as established if it depends on that missing source.

When permitted, write a draft-local bibliography containing the cited verified entries. Preserve shared bibliography files and unrelated entries. Check duplicate works, multi-citation commands, retained keys, entry types and bibliography references; do not remove original entries as “cleaning” outside the write scope.

**Done**: every in-text key resolves to the correct verified entry; every unresolved use is visibly marked in both draft and notes, with its precise next action.

## Failure handling

| Condition | Action |
|---|---|
| No search result | Try exact title/author and a bounded alternate query; then report the gap |
| Identifier resolves to a different work | Reject the candidate; retain conflict details |
| DOI metadata unavailable | Try official proceedings or arXiv; use only inspected fields |
| Sources disagree | Preserve the discrepancy and ask which version is intended |
| Full text inaccessible | Report access limitation; support no details beyond what was read |
| Rate limit or missing tool | Respect limits; stop queries at the agreed budget and list unchecked items |
| Encoding/format mismatch | Fix only the authorized draft’s transcription; retain the existing template/backend |

## Drafting notes

For each cited statement keep: manuscript location, key/link, title/version, identity sources, metadata source, supporting passage and status. This can be a natural Markdown table in the existing report. It is not a citation database, receipt protocol or independent citation audit.
