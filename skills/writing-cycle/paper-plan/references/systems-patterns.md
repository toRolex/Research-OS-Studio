> Planning-only adaptation of Orchestra systems-paper-writing/references/writing-patterns.md (LICENSE-Orchestra.txt). All four frameworks, selection guide, composition and anti-patterns are retained. Paper-specific illustrative histories are excluded; operational verbs below mean organizing existing research into a plan, never running research. Comparative templates apply only when actual evidence supports the comparison. A failure or inconclusive result can be the thesis.

# Writing Patterns for Systems Papers

Four reusable structural patterns for organizing systems papers, with concrete examples from published work.

---

## Pattern 1: Gap Analysis

**When to use**: You have identified specific, enumerable shortcomings in existing systems that your work addresses one-by-one.

**Structure**:
```text
Introduction:
  G1: [Existing systems assume X, but workloads show Y]
  G2: [Existing approach cannot handle scenario Z]
  G3: [No existing system provides property W]
  ...
  "We present [System], which addresses G1–Gn through A1–An."

Design:
  A1 → addresses G1: [Design component with rationale]
  A2 → addresses G2: [Design component with rationale]
  A3 → addresses G3: [Design component with rationale]
  ...

Evaluation:
  Experiment for G1/A1: [Metric showing A1 fixes G1]
  Experiment for G2/A2: [Metric showing A2 fixes G2]
  ...
```

**Key property**: Creates a **traceable contract** — reviewers can verify that every claimed gap has a corresponding solution and evaluation.

### How to Apply This Pattern

1. List all limitations of existing work as G1–Gn (typically 3–5)
2. For each Gi, locate the existing answering component Ai; if absent, record a design/evidence gap
3. In the contribution list, state: "We identify G1–Gn and address them through A1–An"
4. In the evaluation plan, map existing tests to each Gi→Ai pair; missing tests remain gaps
5. Use a summary table in Introduction or Related Work showing the gap-answer mapping

---

## Pattern 2: Observation-Driven

**When to use**: You have access to production data, workload traces, or empirical measurements that reveal surprising properties motivating your design.

**Structure**:
```text
Background & Motivation:
  Observation 1: [Data finding with figure/table]
    → Insight 1: [What this means for design]
  Observation 2: [Data finding with figure/table]
    → Insight 2: [What this means for design]
  Observation 3: [Data finding with figure/table]
    → Insight 3: [What this means for design]

Design:
  Insight 1 → Component A: [Design driven by O1]
  Insight 2 → Component B: [Design driven by O2]
  Insight 3 → Component C: [Design driven by O3]

Evaluation:
  Show system handles the patterns identified in O1–O3
```

**Key property**: Observations ground the motivation in inspectable evidence; sampling, measurement, and scope limitations remain open to challenge.

### How to Apply This Pattern

1. Locate 2–4 findings already supported by your production data or traces; distinguish observations from proposed explanations
2. Present each as "Observation N" with supporting figure/table
3. Below each observation, state the design insight it implies
4. In Design, reference back: "Motivated by O1 (§2), we design..."
5. In Evaluation, use workloads that exhibit the observed patterns

---

## Pattern 3: Contribution List

**When to use**: Your system has multiple distinct contributions that span different technical areas (new abstraction + new algorithm + new implementation + new evaluation methodology).

**Structure**:
```text
Introduction:
  "This paper makes the following contributions:
  1. [Contribution type]: [Description] (§N)
  2. [Contribution type]: [Description] (§M)
  3. [Contribution type]: [Description] (§P)
  4. [Contribution type]: [Description] (§Q)"

Each section directly addresses one or more numbered contributions.

Evaluation:
  Each experiment validates a specific contribution.
```

**Key property**: Reviewers can **count and verify** contributions. Clear section cross-references make the paper navigable.

### How to Apply This Pattern

1. List contributions as numbered items (3–7 is typical)
2. Tag each with a type: Analysis, Design, Algorithm, System, Evaluation
3. Cross-reference sections: "(§N)"
4. Ensure each contribution is **testable** — a reviewer should be able to verify it from the paper
5. In evaluation, map experiments back to contribution numbers

---

## Pattern 4: Thesis Formula

**When to use**: Your paper has a single, strong central claim that can be expressed as a comparative statement.

**Structure** (Irene Zhang's formula):
```text
Thesis: "X is better for applications Y running in environment Z"

Introduction: State the thesis clearly
Background: Define Y and Z, explain why they matter
Design: Explain how X achieves its advantage
Evaluation: Test the scoped comparison of X with baselines for Y in Z
  - Show X beats baselines on Y
  - Show X works in environment Z
  - Show X's advantage comes from its design choices (ablation)
```

**Key property**: The entire paper serves a **single, memorable claim**. Reviewers can assess the paper by checking if the thesis is adequately supported.

### How to Apply This Pattern

1. Distill your contribution to one sentence: "[System] is better for [application] in [environment] because [insight]"
2. 在所选摘要蓝图的贡献/论点槽位陈述 thesis；槽位顺序遵循[计划模板的摘要选择规则](../templates/paper-plan.md#叙事与结构)，不固定为第 3 句
3. In Introduction: use it as the culmination of the gap analysis
4. In Design: show how each component serves the thesis
5. In Evaluation: locate tests of the thesis with appropriate baselines and workloads, marking missing tests
6. In Conclusion: restate the thesis with evidence from evaluation

### Combining the Thesis Formula with Other Patterns

The thesis formula is **compositional** — it works as the top-level structure while other patterns fill in the details:

- Thesis + Gap Analysis: "X is better for Y in Z because it addresses G1–Gn"
- Thesis + Observation-Driven: "X is better for Y in Z; we discovered this through O1–O3"
- Thesis + Contribution List: "X is better for Y in Z; our contributions include C1–Cn"

---

## Pattern Selection Guide

| Your Situation | Recommended Pattern | Reason |
|---------------|-------------------|--------|
| Clear list of shortcomings in prior work | Gap Analysis | Traceable, easy for reviewers |
| Have production data or traces | Observation-Driven | Evidence-grounded motivation |
| Multiple distinct technical contributions | Contribution List | Countable, verifiable |
| One strong comparative claim | Thesis Formula | Focused, memorable |
| Complex system with data + gaps | Thesis + Gap + Observation | Combine for maximum impact |

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Feature Dump
Listing system features without connecting them to problems or claims. Fix: use Gap Analysis or Thesis Formula to give every feature a purpose.

### Anti-Pattern 2: Solution Looking for a Problem
Presenting the design before establishing why it is needed. Fix: use Observation-Driven to ground the design in real data.

### Anti-Pattern 3: Vague Contributions
"We propose a novel system for X" — not testable, not verifiable. Fix: use Contribution List with specific, measurable claims.

### Anti-Pattern 4: Missing Alternatives
Presenting design choices as the only option. Fix: for every major decision, discuss at least one alternative and why it was rejected (Irene Zhang's rule).
