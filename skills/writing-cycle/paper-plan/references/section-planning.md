# Section-by-section and figure planning

Adapted from ARIS paper-plan Steps 2–4; see LICENSE-ARIS.txt. These are planning worksheets, not instructions to draft the paper or create figures. Read after the Claim—Evidence matrix. Every numerical/page example below is illustrative, not project evidence or current venue policy. Preserve supported scope and negative results.

**IMPORTANT**: The section count is FLEXIBLE (5-8 sections). Choose what fits the content best. The templates below are starting points, not rigid constraints.

**Empirical/Diagnostic paper:**
```
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Method / Setup (1.5 pages)
4. Experiments (3 pages)
5. Analysis / Discussion (1 page)
6. Conclusion (0.5 pages)
```

**Theory + Experiments paper:**
```
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Preliminaries & Modeling (1.5 pages)
4. Experiments (1.5 pages)
5. Theory Part A (1.5 pages)
6. Theory Part B (1.5 pages)
7. Conclusion (0.5 pages)
— Total: 9 pages
```
Theory papers often need 7 sections (splitting theory into estimation + optimization, or setup + analysis). These allocations are illustrative, not a venue rule. Allocate within the verified limit, including every item that the venue counts; leave explicit slack instead of padding to the maximum.

Theory papers should:
- Include **proof sketch** locations (not just theorem statements)
- Plan a **comparison table** of prior theoretical bounds vs. this paper's bounds
- Identify which proofs go in appendix vs. main body

**Method paper:**
```
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Method (2 pages)
4. Experiments (2.5 pages)
5. Ablation / Analysis (1 page)
6. Conclusion (0.5 pages)
```

### Step 3: Section-by-Section Planning

For each section, specify:

```markdown
### §0 Abstract
- **What we achieve**: [the paper's specific contribution, not field-level background]
- **Why it matters / is hard**: [why this problem is important and non-trivial]
- **How we do it**: [approach in one sentence]
- **Evidence**: [what supports the claim]
- **Most remarkable result**: [strongest quantitative or theoretical result]
- **Estimated length**: 150-250 words
- **Self-contained check**: can a reader understand this without the paper?

### §1 Introduction
- **Opening hook**: [1-2 sentences that motivate the problem]
- **Gap / challenge**: [what's missing in prior work, and why prior work is insufficient]
- **One-sentence contribution**: [the main takeaway of the paper]
- **Approach overview**: [what we do differently]
- **Key questions**: [the research questions this paper answers]
- **Contributions**: [2-4 numbered bullets, specific and falsifiable, matching Claims-Evidence Matrix]
- **Results preview**: [the strongest result or comparison to surface early]
- **Hero figure**: [describe what Figure 1 should show — MUST include clear comparison if applicable]
- **Estimated length**: 1.5 pages
- **Key citations**: [3-5 papers to cite here]
- **Front-loading check**: [would a skim reader know the main claim before reaching the method?]

### §2 Related Work
- **Subtopics**: [2-4 categories of related work]
- **Positioning**: [how this paper differs from each category]
- **Planning target**: enough space for substantive synthesis (often 3-4 paragraphs); adjust to the verified venue budget rather than enforcing a one-page minimum.
- **Organization rule**: organize by methodological family / assumption / question, not paper-by-paper
- **Must NOT be just a list** — synthesize, compare, and position

### §3 Method / Setup / Preliminaries
- **Notation**: [key symbols and their meanings]
- **Problem formulation**: [formal setup]
- **Method description**: [algorithm, model, or experimental design]
- **Formal statements**: [theorems, propositions if applicable]
- **Proof sketch locations**: [which key steps appear here vs. appendix]
- **Estimated length**: 1.5-2 pages

### §4 Experiments / Main Results
- **Figures planned**:
  - Fig 1: [description, type: bar/line/table/architecture, WHAT COMPARISON it shows]
  - Fig 2: [description]
  - Table 1: [what it shows, which methods/baselines compared]
- **Data source**: [original results, data, proof, or observation with exact location; missing sources remain DATA_NEEDED]

### §5 Conclusion
- **Restatement**: [contributions rephrased, not copy-pasted from intro]
- **Limitations**: [honest assessment — reviewers value this]
- **Future work**: [1-2 concrete directions]
- **Estimated length**: 0.5 pages
```

### Step 4: Figure Plan

List every figure and table:

```markdown
## Figure Plan

| ID | Type | Description | Data Source | Priority |
|----|------|-------------|-------------|----------|
| Fig 1 | Hero/Architecture | System overview + comparison | existing method description; schematic, not measured evidence | HIGH |
| Fig 2 | Line plot | Training curves comparison | figures/exp_A.json | HIGH |
| Fig 3 | Bar chart | Ablation results | figures/ablation.json | MEDIUM |
| Table 1 | Comparison table | Main results vs. baselines | figures/main_results.json | HIGH |
| Table 2 | Theory comparison | Prior bounds vs. ours | exact prior theorem and project proof locations with assumptions; DATA_NEEDED if absent | HIGH (theory papers) |
```

**CRITICAL for Figure 1 / Hero Figure**: Describe in detail what the figure should contain, including:
- Which methods are being compared
- What measured difference the available evidence supports (or what concept a schematic explains)
- Caption draft that clearly states the comparison
- Why the figure helps a skim reader understand the paper before reading the full method


## Planning completion

For every section and figure, add Claim IDs, evidence locations, uncertainty, missing inputs, and main/appendix placement. For a theory-only paper, use theorem dependencies and proof coverage rather than inventing an experiments section. For empirical or qualitative work, use the actual measurement/observation protocol and justified scope. Section counts and lengths are flexible, not a requirement to add claims. Figure plans specify actual conditions, comparator, units, error-bar meaning, and editable/reproducible source expected from later work; no rendering occurs here.
