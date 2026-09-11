# Operational ideation frameworks

Adapted from Orchestra brainstorming-research-ideas, preserving all ten framework workflows, examples and self-checks. Use the selection guide below to choose the relevant branch, then read that complete numbered framework.

**Scope of every framework:** build, compare, test, validate and re-run mean *describe a candidate verification plan*, not execute it. Statements about novelty, importance and publishability are questions/annotations, never a generator's elimination or acceptance authority. Examples illustrate heuristics rather than establish historical priority.

## Core Ideation Frameworks

### 1. Problem-First vs. Solution-First Thinking

Research ideas originate from two distinct modes. Knowing which mode you are in prevents a common failure: building solutions that lack real problems, or chasing problems without feasible approaches.

**Problem-First** (pain point → method):
- Start with a concrete failure, bottleneck, or unmet need
- Naturally yields impactful work because the motivation is intrinsic
- Risk: may converge on incremental fixes rather than paradigm shifts

**Solution-First** (new capability → application):
- Start with a new tool, insight, or technique seeking application
- Often drives breakthroughs by unlocking previously impossible approaches
- Risk: "hammer looking for a nail"—solution may lack genuine demand

**Workflow**:
1. Write down your idea in one sentence
2. Classify it: Is this problem-first or solution-first?
3. If problem-first → verify the problem matters (who suffers? how much?)
4. If solution-first → identify at least two genuine problems it addresses
5. For either mode, articulate the gap: what cannot be done today that this enables?

**Self-Check**:
- [ ] Can I name a specific person or community who needs this?
- [ ] Is the problem I am solving actually unsolved (not just under-marketed)?
- [ ] If solution-first, does the solution create new capability or just replicate existing ones?

---

### 2. The Abstraction Ladder

Every research problem sits at a particular level of abstraction. Deliberately moving up or down the ladder reveals ideas invisible at your current level.

| Direction | Action | Outcome |
|-----------|--------|---------|
| **Move Up** (generalize) | Turn a specific result into a broader principle | Framework papers, theoretical contributions |
| **Move Down** (instantiate) | Test a general paradigm under concrete constraints | Empirical papers, surprising failure analyses |
| **Move Sideways** (analogize) | Apply same abstraction level to adjacent domain | Cross-pollination, transfer papers |

**Workflow**:
1. State your current research focus in one sentence
2. Move UP: What is the general principle behind this? What class of problems does this belong to?
3. Move DOWN: What is the most specific, constrained instance of this? What happens at the extreme?
4. Move SIDEWAYS: Where else does this pattern appear in a different field?
5. For each new level, ask: Is this a publishable contribution on its own?

**Example**:
- **Current**: "Improving retrieval accuracy for RAG systems"
- **Up**: "What makes context selection effective for any augmented generation system?"
- **Down**: "How does retrieval accuracy degrade when documents are adversarially perturbed?"
- **Sideways**: "Database query optimization uses similar relevance ranking—what can we borrow?"

---

### 3. Tension and Contradiction Hunting

Breakthroughs often come from resolving tensions between widely accepted but seemingly conflicting goals. These contradictions are not bugs—they are the research opportunity.

**Common Research Tensions**:

| Tension Pair | Research Opportunity |
|-------------|---------------------|
| Performance ↔ Efficiency | Can we match SOTA with 10x less compute? |
| Privacy ↔ Utility | Can federated/encrypted methods close the accuracy gap? |
| Generality ↔ Specialization | When does fine-tuning beat prompting, and why? |
| Safety ↔ Capability | Can alignment improve rather than tax capability? |
| Interpretability ↔ Performance | Do mechanistic insights enable better architectures? |
| Scale ↔ Accessibility | Can small models replicate emergent behaviors? |

**Workflow**:
1. Pick your research area
2. List the top 3-5 desiderata (things everyone wants)
3. Identify pairs that are commonly treated as trade-offs
4. For each pair, ask: Is this trade-off fundamental or an artifact of current methods?
5. If artifact → the reconciliation IS your research contribution
6. If fundamental → characterizing the Pareto frontier is itself valuable

**Self-Check**:
- [ ] Have I confirmed this tension is real (not just assumed)?
- [ ] Can I point to papers that optimize for each side independently?
- [ ] Is my proposed reconciliation technically plausible, not just aspirational?

---

### 4. Cross-Pollination (Analogy Transfer)

Borrowing structural ideas from other disciplines is one of the most generative research heuristics. Many foundational techniques emerged this way—attention mechanisms draw from cognitive science, genetic algorithms from biology, adversarial training from game theory.

**Requirements for a Valid Analogy**:
- **Structural fidelity**: The mapping must hold at the level of underlying mechanisms, not just surface similarity
- **Non-obvious connection**: If the link is well-known, record it for independent novelty assessment; it may still reveal a new mechanism or boundary
- **Testable predictions**: The analogy should generate concrete hypotheses

**High-Yield Source Fields for ML Research**:

| Source Field | Transferable Concepts |
|-------------|----------------------|
| Neuroscience | Attention, memory consolidation, hierarchical processing |
| Physics | Energy-based models, phase transitions, renormalization |
| Economics | Mechanism design, auction theory, incentive alignment |
| Ecology | Population dynamics, niche competition, co-evolution |
| Linguistics | Compositionality, pragmatics, grammatical induction |
| Control Theory | Feedback loops, stability, adaptive regulation |

**Workflow**:
1. Describe your problem in domain-agnostic language (strip the jargon)
2. Ask: What other field solves a structurally similar problem?
3. Study that field's solution at the mechanism level
4. Map the solution back to your domain, preserving structural relationships
5. Generate testable predictions from the analogy
6. Validate: Does the borrowed idea actually improve outcomes?

---

### 5. The "What Changed?" Principle

Strong ideas often come from revisiting old problems under new conditions. Advances in hardware, scale, data availability, or regulations can invalidate prior assumptions and make previously impractical approaches viable.

**Categories of Change to Monitor**:

| Change Type | Example | Research Implication |
|------------|---------|---------------------|
| **Compute** | GPUs 10x faster | Methods dismissed as too expensive become feasible |
| **Scale** | Trillion-token datasets | Statistical arguments that failed at small scale may now hold |
| **Regulation** | EU AI Act, GDPR | Creates demand for compliant alternatives |
| **Tooling** | New frameworks, APIs | Reduces implementation barrier for complex methods |
| **Failure** | High-profile system failures | Exposes gaps in existing approaches |
| **Cultural** | New user behaviors | Shifts what problems matter most |

**Workflow**:
1. Pick a well-known negative result or abandoned approach (3-10 years old)
2. List the assumptions that led to its rejection
3. For each assumption, ask: Is this still true today?
4. If any assumption has been invalidated → re-run the idea under new conditions
5. Frame the contribution: "X was previously impractical because Y, but Z has changed"

---

### 6. Failure Analysis and Boundary Probing

Understanding where a method breaks is often as valuable as showing where it works. Boundary probing systematically exposes the conditions under which accepted techniques fail.

**Types of Boundaries to Probe**:
- **Distributional**: What happens with out-of-distribution inputs?
- **Scale**: Does the method degrade at 10x or 0.1x the typical scale?
- **Adversarial**: Can the method be deliberately broken?
- **Compositional**: Does performance hold when combining multiple capabilities?
- **Temporal**: Does the method degrade over time (concept drift)?

**Workflow**:
1. Select a widely-used method with strong reported results
2. Identify the implicit assumptions in its evaluation (dataset, scale, domain)
3. Systematically violate each assumption
4. Document where and how the method breaks
5. Diagnose the root cause of each failure
6. Propose a fix or explain why the failure is fundamental

**Self-Check**:
- [ ] Am I probing genuine boundaries, not just confirming known limitations?
- [ ] Can I explain WHY the method fails, not just THAT it fails?
- [ ] Does my analysis suggest a constructive path forward?

---

### 7. The Simplicity Test

Before accepting complexity, ask whether a simpler approach suffices. Fields sometimes over-index on elaborate solutions when a streamlined baseline performs competitively.

**Warning Signs of Unnecessary Complexity**:
- The method has many hyperparameters with narrow optimal ranges
- Ablations show most components contribute marginally
- A simple baseline was never properly tuned or evaluated
- The improvement over baselines is within noise on most benchmarks

**Workflow**:
1. Identify the current SOTA method for your problem
2. Strip it to its simplest possible core (what is the one key idea?)
3. Specify how to build that minimal version with careful engineering (design only here)
4. Specify a fair comparison: same compute budget, same tuning effort
5. If the gap is small → the contribution is the simplicity itself
6. If the gap is large → you now understand what the complexity buys

**Contribution Framing**:
- "We show that [simple method] with [one modification] matches [complex SOTA]"
- "We identify [specific component] as the critical driver, not [other components]"

---

### 8. Stakeholder Rotation

Viewing a system from multiple perspectives reveals distinct classes of research questions. Each stakeholder sees different friction, risk, and opportunity.

**Stakeholder Perspectives**:

| Stakeholder | Key Questions |
|-------------|---------------|
| **End User** | Is this usable? What errors are unacceptable? What is the latency tolerance? |
| **Developer** | Is this debuggable? What is the maintenance burden? How does it compose? |
| **Theorist** | Why does this work? What are the formal guarantees? Where are the gaps? |
| **Adversary** | How can this be exploited? What are the attack surfaces? |
| **Ethicist** | Who is harmed? What biases are embedded? Who is excluded? |
| **Regulator** | Is this auditable? Can decisions be explained? Is there accountability? |
| **Operator** | What is the cost? How does it scale? What is the failure mode? |

**Workflow**:
1. Describe your system or method in one paragraph
2. Assume each stakeholder perspective in turn (spend 5 minutes per role)
3. For each perspective, list the top 3 concerns or questions
4. Identify which concerns are unaddressed by existing work
5. Turn the unaddressed concerns into candidate research questions; impact remains a question for independent review

---

### 9. Composition and Decomposition

Novelty often emerges from recombination or modularization. Innovation frequently lies not in new primitives, but in how components are arranged or separated.

**Composition** (combining existing techniques):
- Identify two methods that solve complementary subproblems
- Ask: What emergent capability arises from combining them?
- Example: RAG + Chain-of-Thought → retrieval-augmented reasoning

**Decomposition** (breaking apart monolithic systems):
- Identify a complex system with entangled components
- Ask: Which component is the actual bottleneck?
- Example: Decomposing "fine-tuning" into data selection, optimization, and regularization reveals that data selection often matters most

**Workflow**:
1. List the 5-10 key components or techniques in your area
2. **Compose**: Pick pairs and ask what happens when you combine them
3. **Decompose**: Pick a complex method and isolate each component's contribution
4. For compositions: Does the combination create emergent capabilities?
5. For decompositions: Does isolation reveal a dominant or redundant component?

---

### 10. The "Explain It to Someone" Test

A strong research idea should be defensible in two sentences to a smart non-expert. This test enforces clarity of purpose and sharpens the value proposition.

**The Two-Sentence Template**:
> **Sentence 1** (Problem): "[Domain] currently struggles with [specific problem], which matters because [concrete consequence]."
> **Sentence 2** (Insight): "We [approach] by [key mechanism], which works because [reason]."

**If You Cannot Fill This Template**:
- The problem may not be well-defined yet → return to Framework 1
- The insight may not be clear yet → return to Framework 7 (simplify)
- The significance may not be established → return to Framework 3 (find the tension)

**Calibration Questions**:
- Would a smart colleague outside your subfield understand why this matters?
- Does the explanation stand without jargon?
- Can you predict what a skeptic's first objection would be?

---

## Bounded diverge / annotate / handoff

Retain the original integrated sequence as a generating aid within the main Skill's budget:

1. Diverge: list tensions (F3), changed assumptions (F5), failure boundaries (F6), a neighboring mechanism (F4), composition/decomposition (F9), and up/down/sideways variants (F2). Select branches relevant to the assigned lens; do not multiply the candidate budget implicitly.
2. Annotate: apply the Explain-It, Problem-First, Simplicity, Stakeholder and Feasibility checks to every candidate. Record unclear pitches, missing beneficiaries, unjustified complexity and uncertain resources. Only confirmed hard-constraint violations may leave the current feasible pool; every original card remains in the report.
3. Sharpen each retained card, not a self-selected winner: two-sentence pitch (F10), core tension (F3), abstraction level (F2), three possible discriminating tests, strongest objection and response, and a smallest pilot *design* within known resources. No pilot is run here.
4. Completion: each candidate has a pitch, problem/beneficiary, mechanism, uncertainty, test design, effort estimate and strongest objection, or an explicit missing item. Handoff the complete pool for separate assessment; the researcher makes the final adoption decision.

## Framework Selection Guide

Not sure which framework to start with? Use this decision guide:

| Your Situation | Start With |
|---------------|------------|
| "I don't know what area to work in" | Tension Hunting (F3) → What Changed (F5) |
| "I have a vague area but no specific idea" | Abstraction Ladder (F2) → Failure Analysis (F6) |
| "I have an idea but I'm not sure it's good" | Explain-It Test (F10) → Simplicity Test (F7) |
| "I have a good idea but need a fresh angle" | Cross-Pollination (F4) → Stakeholder Rotation (F8) |
| "I want to combine existing work into something new" | Composition/Decomposition (F9) |
| "I found a cool technique and want to apply it" | Problem-First Check (F1) → Stakeholder Rotation (F8) |
| "I want to challenge conventional wisdom" | Failure Analysis (F6) → Simplicity Test (F7) |

---

## Common Pitfalls in Research Ideation

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **Novelty without impact** | "No one has done X" but no one needs X | Apply Problem-First Check (F1) |
| **Incremental by default** | Idea is +2% on a benchmark | Climb the Abstraction Ladder (F2) |
| **Complexity worship** | Method has 8 components, each helping marginally | Apply Simplicity Test (F7) |
| **Echo chamber** | All ideas come from reading the same 10 papers | Use Cross-Pollination (F4) |
| **Stale assumptions** | "This was tried and didn't work" (5 years ago) | Apply What Changed (F5) |
| **Single-perspective bias** | Only considering the ML engineer's view | Use Stakeholder Rotation (F8) |
| **Premature convergence** | Committed to first idea without exploring alternatives | Run full Diverge phase |

---
