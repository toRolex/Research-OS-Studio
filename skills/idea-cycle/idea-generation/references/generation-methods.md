# Generation methods

Adapted from ARIS idea-creator: complete landscape operations and substantive generation prompt, with resource, input and role boundaries changed for this Skill. MIT notice is co-located.

## Landscape from existing materials

Map the research area to understand what exists and where the gaps are.

1. **Scan local paper library first**: Check `papers/` and `literature/` in the project directory for existing PDFs. Read the relevant methods, results and limitations of supplied papers (record any unread sections) to build a baseline understanding before searching online. This avoids re-discovering what the user already knows.

2. **Optional authorized literature expansion** using an available host search tool (otherwise stay within the supplied material set):
   - Top venues in the last 2 years (NeurIPS, ICML, ICLR, ACL, EMNLP, etc.)
   - Recent arXiv preprints (last 6 months)
   - Use 5+ different query formulations
   - Read abstracts and introductions of the top 10-15 papers

3. **Build a landscape map**:
   - Group papers by sub-direction / approach
   - Identify what has been tried and what hasn't
   - Note recurring limitations mentioned in "Future Work" sections
   - Flag any open problems explicitly stated by multiple papers

4. **Identify structural gaps**:
   - Methods that work in domain A but haven't been tried in domain B
   - Contradictory findings between papers (opportunity for resolution)
   - Assumptions that everyone makes but nobody has tested
   - Scaling regimes that haven't been explored
   - Diagnostic questions that nobody has asked

## Generation prompt

Give each generator the actual material paths/text, original question, non-goals, constraints, assigned lens and candidate-card fields. This is generation, not a reviewer call.

```text
You are a researcher brainstorming research ideas.

Research direction: [user's direction]

Here is the current landscape:
[insert the material-grounded landscape here in this prompt text; no bundle file is required]

Key gaps identified:
[insert the material-grounded gap summary here in this prompt text]

Generate 1–2 concrete research ideas through the assigned lens; the coordinator targets 8–10 across the bounded fan-out. For each idea:
1. One-sentence summary
2. Core hypothesis (what you expect to find and why)
3. Minimum viable experiment (what's the cheapest way to test this?)
4. Expected contribution type: empirical finding / new method / theoretical result / diagnostic
5. Risk level: LOW (likely works) / MEDIUM (50-50) / HIGH (speculative)
6. Estimated effort: days / weeks / months

Prioritize ideas that are:
- Testable within the user's declared compute, data and time constraints (unknown resources stay unknown)
- Likely to produce a clear positive OR negative result (both can be informative; publishability remains unassessed)
- Simple at the core: one mechanism, few moving parts — an idea a colleague
  could restate after hearing it once. If the novelty only appears once a
  second module or an extra gate is added, that is packaging, not novelty.
- Aware of the supplied materials above — awareness, not avoidance. Differentiation
  is a separate novelty assessment's job, not a constraint on brainstorming.

"Apply X to Y" is legitimate when the application would reveal something
non-obvious — judge it by what it reveals, not by the template. A direct,
well-executed attack on a central problem is a valid idea when nobody has
executed it well; do not steer around crowded areas — proximity to strong
work is a sign the problem matters, not that it is taken.

Be genuinely creative: surprising connections, inverted assumptions,
questions nobody thought to ask. Creativity is a new angle on a problem
that matters — not an obscure corner nobody visits, and not extra modules
stacked until something looks new. Generate first, filter later — the
filters come after you, and they are strict enough. A bold, creative idea
with a named risk beats a hedged, complicated one with none. A great idea
is one where the answer matters regardless of which way it goes.
```

## Consolidation

1. Union every returned candidate, including named risks, estimates and failed/partial lens results. Preserve original cards before consolidation.
2. Compare problem object, mechanism/hypothesis and discriminating test. Merge only genuinely equivalent hypotheses with equivalent tests; retain all distinct assumptions, evidence anchors and lens origins in the representative. Keep uncertain near-duplicates separate.
3. Record a mapping from every original card to retained representative or temporary out-of-scope entry. Cite the matching details, not a similarity score invented after the fact.
4. Apply only known user constraints: confirmed unavailable data, or a supported minimum resource requirement above the authorized ceiling. An uncertain compute estimate, complexity concern or suspected prior work is an annotation, not a veto. Preserve the original idea with a reopening condition.
5. Attach prior-work uncertainty, so-what (why either sign matters), effort note and strongest anticipated objection. These are generator notes, not independent review. Forward the entire feasible non-duplicate pool with original materials, not only a favored shortlist.
6. Keep ranking advisory only when the user provided an objective ordering field; otherwise preserve lens/generation order. Generation ends here, before independent novelty/quality decisions and before running any pilot.
