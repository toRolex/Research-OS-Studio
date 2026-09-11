---
name: novelty-check
description: 查新：对已有候选的核心 Claim 主动检索 closest prior work，判断已覆盖、关键区别或证据缺口。用户问“有没有人做过”，或当前已授权的 Idea Discovery 需要核对候选新颖性时使用；不用于生成新方向或评判实验有效性。
argument-hint: "[候选描述或原始材料路径；可指定报告位置与检索范围]"
---

# Novelty Check

Check whether a proposed method/idea has already been done in the literature. Judge the claimed delta, not whether the topic has neighbors.

## Scope and authorization

- **Role:** model-invoked internal capability within the caller's authorized research scope; users may also explicitly invoke it standalone. Read the original candidate, not only a generator's summary. A parent Workflow is a caller, not permission to start another Workflow.
- **Inputs:** candidate description or source paths; core Claim and problem/setting; known references; search cutoff and any confidentiality/resource limits. Read existing project instructions and workspace navigation if present. Setup, a particular directory, and any research runtime are not prerequisites.
- **Resolve before work:** identify the candidate, cutoff (today unless specified), allowed public search terms, and output mode. If the actual claimed contribution is missing or contradictory, ask one focused question and stop; do not invent it. Keep the user's problem and Claim unchanged.
- **Resources:** use already available, authorized read/search tools. Follow host-specific tool routing. Public lookup does not authorize uploading private drafts, paying for services, installing tools, using new credentials, or remote writes. Request permission for any such escalation; denial ends that action. If search/full text is unavailable, retain the failed lookup and report the precise limitation rather than pretend the check ran.
- **Writes:** standalone returns the report in chat unless a destination is authorized; composed contributes only the novelty section of the caller's named canonical report (or returns the section for the caller to insert). Save fetched materials and reviewer input/output only in the authorized evidence location; otherwise retain URLs, inspected passages and responses in the report/chat. Reuse existing material without overwriting it; ask on file or section conflicts. Do not edit proposals, source Claims, code, datasets or experiment plans.
- **Budget:** use the caller's bounded search budget. Otherwise allow at most 24 search requests, 8 papers for decisive reading, and citation-following depth 1. Three distinct query formulations per Claim are counted across sources, not repeated automatically on every source; a query sent to two sources consumes two requests. Do one initial pass, then one targeted follow-up for closest-paper citations, recent work and decisive gaps. Stop at the first exhausted limit, retaining unexamined candidates and any resulting evidence gaps; request a specific extension rather than looping.

## Phase A: Extract Key Claims

1. Read the user's method description and its original supporting materials.
2. Identify 3–5 core technical claims that carry the claimed delta, or fewer when the candidate genuinely has fewer:
   - What is the method?
   - What problem does it solve?
   - What is the mechanism?
   - What makes it different from obvious baselines?
3. Separate established components, proposed mechanisms and findings still to be demonstrated. Record assumptions, data/task, comparison baseline and claimed scope. Judge both the individual claims and their combination.

**Complete when:** every claimed contribution maps back to the candidate and has a concrete overlap question; unresolved input ambiguity has been surfaced rather than filled in.

## Phase B: Multi-Source Literature Search

For EACH core claim, search across available, relevant sources within the budget:

1. **Web and scholarly search:** use specific technical terms from the claim. Try at least three formulations: mechanism terminology, problem/setting terminology, and synonyms or adjacent-field names. Search arXiv, scholarly indexes and primary venue/publisher collections where available. Record queries, sources, dates, filters and failures. If a source is unavailable, state which coverage is lost.
2. **Known paper collections:** check relevant conferences/journals and preprints through the cutoff. Include an unfiltered historical search so older prior art is not hidden by recency filters; check the six months ending at the cutoff on arXiv for relevant fields (or the equivalent active preprint source). Verify actual version dates: a paper's early identifier does not make its later revision eligible as historical evidence. Record date-filter parameters and any limitations rather than treating date keywords as a reliable filter. Report concurrent work and separate preprint dates from publication dates.
3. **Read potentially overlapping work:** first read the abstract and related work to triage, then inspect the actual method, assumptions, result/theorem, experiments and limitations that decide overlap. Follow relevant citations and citing work during the targeted follow-up. Read appendices or supplements when a decisive claim relies on them.
4. **Verify before judging:** use [source verification](references/source-verification.md) for every prior-work entry. Identity confirmation and content support are separate. Preserve candidates that could not be verified, labeled with the failure or missing material. Search hits are leads, not evidence of full reading.
5. **Compare:** for each closest work, map Claim → specific section/page/equation/table → overlap → key difference → remaining unknown. Test whether supposedly different terminology denotes the same mechanism. Compare both method and experimental setting; do not infer absence from an abstract's silence.

**Complete when:** each Claim has a supported closest-work comparison or a named evidence gap; the search log distinguishes attempted, successful and unavailable coverage and states what was actually read.

## Phase C: Independent Verification

When an authorized independent reviewer is available, request one read-only verification in a fresh context; prefer a different model when already available, without requiring a provider. For long inputs, give paths to the original candidate and accessible source materials, plus the complete Phase-B candidate list and comparison dossier. Otherwise include the complete relevant material directly. The reviewer must inspect primary passages, not rubber-stamp the executor's summary.

Ask: “Is this method novel? What is the closest prior work? What is the delta?” Include the verdict limits below verbatim. Request evidence locators, missing reads and the strongest counterexample. Preserve the actual briefing and full response in the authorized report/evidence location. Reconcile disagreements against source passages, retaining unresolved disagreements; model agreement is not scientific evidence.

If an independent reviewer is unavailable or outside authorization, label the output **single-agent assessment; independent verification not performed**. This limits review assurance, not the ability to make a source-supported judgment. Do not impersonate a second reviewer or repeatedly seek a more favorable verdict.

**Complete when:** the actual response has been considered and retained, or the missing independent verification is explicitly recorded.

### The verdict limits

Copy this block **verbatim** into the reviewer's briefing; Phase D uses it too.

```text
=== NOVELTY VERDICT LIMITS (these bound how you judge, never how widely you search within authorization) ===
Search thoroughly; judge calibrated. Two failures waste months equally:
passing an idea a published paper already contains, and killing a viable idea
because the territory has neighbors.
1. Proximity is information, not a verdict. Someone working nearby goes in the
   report; it is not by itself a reason to reject.
2. ABANDON has exactly one qualification: a specific published paper already
   contains this result — name that paper and the inspected evidence covering
   the core contribution under matching assumptions. No named paper, no ABANDON.
3. Crowded-but-deltaed is PROCEED: state the delta in one sentence a reviewer
   could verify. Thin or contested delta is PROCEED WITH CAUTION — say what
   would make it carry, not why it should die. CAUTION is not a safe middle:
   if the evidence is sufficient and you cannot name the specific thing that
   makes the delta thin, the verdict is PROCEED.
4. Concurrent or competing work is not a veto. That is a race — report it and
   let the user decide whether to run it.
5. A direct attack on a central problem is legitimate novelty when nobody has
   executed it well. "This area is hot" does not mean "this area is taken."
6. This check is an early assessment, never a proof of novelty or correctness.
   Within sufficient evidence, when torn between two verdicts, choose the more
   permissive one. Missing decisive evidence instead means EVIDENCE GAP: name
   what is missing, why it matters, and the smallest lookup or user input that
   would resolve it. Stop at the agreed budget; reassess when that evidence arrives.
Say plainly when an idea clears the check. Do not manufacture overlap.
```

## Phase D: Novelty Report

Output a readable Markdown report using [the report template](templates/novelty-report.md). The template organizes this check, not a machine schema. In composed mode, nest it inside the authorized novelty section rather than creating a duplicate deliverable.

- State **PROCEED**, **PROCEED WITH CAUTION**, **ABANDON**, or **EVIDENCE GAP**, with a Claim-level rationale. A specific covered subclaim does not kill a novel combination or finding; an unknown decisive core claim prevents overall clearance, while resolved subclaims retain their judgments.
- ABANDON is advice about the stated novelty claim, not permission to delete an idea or prohibit useful replication. A preprint competitor is reported as concurrent/competing evidence with dates; do not silently relabel it a published veto.
- EVIDENCE GAP is a bounded current outcome, not permanent “inconclusive”: list the exact missing source/passage/input, its decision consequence and the next retrieval needed. On new evidence, update the affected comparisons and give a decisive recommendation when sufficient.
- Explain the key differentiator and what a reviewer would cite as prior work. A numeric novelty score is optional only if requested; it never substitutes for the comparison. If used, anchor 5/10 to a defensible delta with clear neighbors and reserve 1–3 for results a named published paper already contains.
- Suggested positioning is one honest, verifiable delta sentence, not a rewritten topic. Distinguish a proposed finding from a demonstrated result.

**Complete when:** the report contains original Claim scope, search coverage, concrete sources and reading status, evidence-located comparisons, a calibrated recommendation, unresolved gaps and review limitations. Then stop. The user decides whether to retain, revise or abandon the candidate; this skill neither changes the topic nor starts experiments, refinement or another Workflow.

## Interpretation rules

- Two failures waste months equally: a false novelty claim, and a viable idea abandoned because the territory has neighbors. Be honest in both directions — and when an idea clears the check, say so plainly.
- Novelty can live in the combination or the finding even when every individual claim rates LOW — judge the idea, not each claim in isolation. Known parts arranged to reveal something unknown can be novel; identify the specific unknown rather than assume the combination is new.
- “Applying X to Y” earns novelty by what the application reveals — a non-obvious interaction, failure mode, or insight. Judge the revelation, not the template.
- Check both the method AND the experimental setting for novelty. If the method is not novel but the FINDING would be, say so explicitly. A proposed finding remains unproven until supported outside this check.

Adapted from ARIS by wanshuiyin; bundled [MIT license](LICENSE). Source revision and adoption details are recorded in the repository's centralized source document; that document is maintenance information, not an execution dependency.
