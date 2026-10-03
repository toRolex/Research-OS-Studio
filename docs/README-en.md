<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-ondark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo-onlight.png">
    <img alt="Research OS Studio" src="assets/logo-onlight.png" width="75%">
  </picture>

  <p>Agent Skills suite designed for research workflows</p>

  <p>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
    <a href="../skills/README.md"><img src="https://img.shields.io/badge/skills-39-green.svg" alt="Skills"></a>
    <a href="user-acceptance-guide.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
    <a href="https://github.com/toRolex/Research-OS-Studio/stargazers"><img src="https://img.shields.io/github/stars/toRolex/Research-OS-Studio.svg?style=social" alt="GitHub stars"></a>
  </p>

  <p>
    <a href="#research-os-studio">English</a> · <a href="../README.md">中文说明</a>
  </p>
</div>

> **Breaking (v2):** the old read-only entry `ask-research-os` has been removed. There is no compatibility period. To ask where to start, use `/research-os` route-only (for example `/research-os 我该从哪开始`). It recommends a next step and does not start work, use the network, or write files.

---

## Architecture and Workflow

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/workflow-dark.jpg">
    <source media="(prefers-color-scheme: light)" srcset="assets/workflow-light.jpg">
    <img alt="Research OS Studio System Architecture Workflow" src="assets/workflow-light.jpg" width="100%">
  </picture>
</div>

---

## Research OS Studio

Research OS Studio decomposes research into well-defined workflows. The AI assists within explicit authorization boundaries to generate candidate solutions, code, and drafts, while experiment design, result validation, and progression decisions remain in your control.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Design Principles](#core-design-principles)
- [39 Skills Inventory](#39-skills-inventory)
- [Typical Research Workflows](#typical-research-workflows)
- [Safety and Control Principles](#safety-and-control-principles)
- [FAQ](#faq)
- [Documentation](#documentation)
- [License](#license)

---

## Quick Start

### 1. Install Skills

Run the following command in your research project root directory:

```bash
# List all discoverable skills
npx skills@latest add toRolex/Research-OS-Studio --list

# Install all skills to current project
npx skills@latest add toRolex/Research-OS-Studio --all
```

### 2. Workspace Setup

After installation, run the setup command in your Agent:

```bash
/setup-research-os
```

This command inspects your existing project structure and suggests configuration options. It presents a complete draft before writing any changes, never overwrites existing research materials, and does not install system-level packages.

### 3. Choose a Skill

If you are unsure which skill fits your current stage, ask the unified entry and keep the request read-only:

```bash
/research-os where should I start
```

That selects route-only. It recommends a skill from your topic or existing materials, modifies no files, does not use the network, and never starts a workflow. The old entry `ask-research-os` has been removed. If you already know the skill, invoke it directly, or let `/research-os` open the matching playbook.

---

## Core Design Principles

- **Pure Agent Skills**: Installs directly without separate CLIs, Python packages, or background services.
- **Three Research Cycles**:
  1. **Idea Cycle**: Literature search, multi-angle ideation, novelty verification, independent review, and proposal convergence.
  2. **Validation Cycle**: Empirical track handles experiment planning, monitoring, statistical analysis, and audits; theoretical track covers derivations, proof drafting, review, and repairs.
  3. **Writing Cycle**: Paper drafting, academic plotting, LaTeX compilation checks, citation and claim consistency audits, rebuttal preparation, and venue adaptation.
- **Human in the Loop**: Top-level workflows stop upon completion and never transition to subsequent stages without explicit instruction.
- **Native File Formats**: Outputs deliverables directly as Markdown, LaTeX, scripts, and data files.

---

## 39 Skills Inventory

The suite contains 39 standalone skills. Invocation is explicit except for setup:
- **Explicit except setup**: the user names the skill, or a parent playbook reads it by path. The model does not trigger it from the description.
- **`setup-research-os`**: the only skill that may later be suggested by the model. That flip belongs to the setup ticket and has not landed; it is still explicit.

| Category | Skill Name | Invocation | Description |
|---|---|---|---|
| **General** | [setup-research-os](../skills/general/setup-research-os/SKILL.md) | Explicit | Interactive workspace initialization; model suggestion not flipped yet |
| | [research-os](../skills/general/research-os/SKILL.md) | Explicit | Unified orchestrator; read-only requests use route-only and have no side effects |
| **Idea Cycle** | [idea-discovery](../skills/idea-cycle/idea-discovery/SKILL.md) | Explicit | Full ideation workflow: literature search, ideation, novelty check, review, proposal |
| | [research-lit](../skills/idea-cycle/research-lit/SKILL.md) | Explicit | Literature search and synthesis with source verification |
| | [idea-generation](../skills/idea-cycle/idea-generation/SKILL.md) | Explicit | Multi-angle research candidate generation with filtering logs |
| | [creative-thinking-for-research](../skills/idea-cycle/creative-thinking-for-research/SKILL.md) | Explicit | Cognitive shifts and orthogonal exploration for ideation bottlenecks |
| | [novelty-check](../skills/idea-cycle/novelty-check/SKILL.md) | Explicit | Search closest prior work to verify proposal novelty |
| | [idea-review](../skills/idea-cycle/idea-review/SKILL.md) | Explicit | Independent reviewer perspective identifying proposal weaknesses |
| | [idea-refinement](../skills/idea-cycle/idea-refinement/SKILL.md) | Explicit | Refines proposals into minimal viable and frontier routes |
| **Validation** | [experiment-plan](../skills/validation-cycle/experiment-plan/SKILL.md) | Explicit | Creates bounded experiment plans with hypotheses, baselines, and budgets |
| | [experiment-bridge](../skills/validation-cycle/experiment-bridge/SKILL.md) | Explicit | Full experiment workflow: implementation, test runs, monitoring, analysis, audit |
| | [run-experiment](../skills/validation-cycle/run-experiment/SKILL.md) | Explicit | Executes experiment code within approved scope and tracks status |
| | [experiment-queue](../skills/validation-cycle/experiment-queue/SKILL.md) | Explicit | Manages batch experiment queues and resource allocation |
| | [monitor-experiment](../skills/validation-cycle/monitor-experiment/SKILL.md) | Explicit | Monitors running processes and hardware state without inference |
| | [training-health-check](../skills/validation-cycle/training-health-check/SKILL.md) | Explicit | Diagnoses training issues such as NaNs, OOMs, or stalled loss |
| | [analyze-results](../skills/validation-cycle/analyze-results/SKILL.md) | Explicit | Evaluates statistical distributions and uncertainty across runs |
| | [experiment-audit](../skills/validation-cycle/experiment-audit/SKILL.md) | Explicit | Audits code logic, evaluation metrics, and result authenticity |
| | [result-to-claim](../skills/validation-cycle/result-to-claim/SKILL.md) | Explicit | Extracts bounded scientific claims supported by empirical data |
| | [formula-derivation](../skills/validation-cycle/formula-derivation/SKILL.md) | Explicit | Mathematical derivations recording assumptions, steps, and error bounds |
| | [proof-writer](../skills/validation-cycle/proof-writer/SKILL.md) | Explicit | Drafts formal proofs while tracking incomplete attempts and gaps |
| | [proof-review](../skills/validation-cycle/proof-review/SKILL.md) | Explicit | Read-only check for proof structure, lemmas, and counterexamples |
| | [proof-repair](../skills/validation-cycle/proof-repair/SKILL.md) | Explicit | Targeted repair of proof gaps within authorized scope |
| | [proof-orchestrator](../skills/validation-cycle/proof-orchestrator/SKILL.md) | Explicit | Manages long-horizon proofs with optional Lean formalization |
| **Writing Cycle** | [paper-writing](../skills/writing-cycle/paper-writing/SKILL.md) | Explicit | General paper writing workflow: planning, plotting, drafting, compiling, auditing |
| | [ml-paper-writing](../skills/writing-cycle/ml-paper-writing/SKILL.md) | Explicit | ML paper writing covering seeds, error bars, compute, and limitations |
| | [systems-paper-writing](../skills/writing-cycle/systems-paper-writing/SKILL.md) | Explicit | Systems paper writing covering design alternatives and benchmarks |
| | [paper-plan](../skills/writing-cycle/paper-plan/SKILL.md) | Explicit | Outlines paper structure and builds Claim-Evidence matrices |
| | [paper-drafting](../skills/writing-cycle/paper-drafting/SKILL.md) | Explicit | Drafts academic manuscripts grounded in experimental data |
| | [academic-plotting](../skills/writing-cycle/academic-plotting/SKILL.md) | Explicit | Generates academic figures with reproducible plotting scripts |
| | [paper-compile](../skills/writing-cycle/paper-compile/SKILL.md) | Explicit | Runs build checks against your local LaTeX toolchain |
| | [paper-compile-repair](../skills/writing-cycle/paper-compile-repair/SKILL.md) | Explicit | Fixes LaTeX compilation errors after showing a diff for confirmation |
| | [citation-audit](../skills/writing-cycle/citation-audit/SKILL.md) | Explicit | Audits citation identity, metadata, and in-text context accuracy |
| | [apply-citation-fixes](../skills/writing-cycle/apply-citation-fixes/SKILL.md) | Explicit | Updates BibTeX entries or in-text citation keys upon confirmation |
| | [paper-claim-audit](../skills/writing-cycle/paper-claim-audit/SKILL.md) | Explicit | Verifies consistency between manuscript claims and underlying data |
| | [claim-stress-test](../skills/writing-cycle/claim-stress-test/SKILL.md) | Explicit | Simulates critical reviewer perspectives to challenge weak points |
| | [research-improvement](../skills/writing-cycle/research-improvement/SKILL.md) | Explicit | Multi-stage review and repair loops for code, claims, and drafts |
| | [rebuttal](../skills/writing-cycle/rebuttal/SKILL.md) | Explicit | Breaks reviewer comments into distinct concerns and drafts responses |
| | [resubmit-pipeline](../skills/writing-cycle/resubmit-pipeline/SKILL.md) | Explicit | Adapts manuscripts to new conference templates while preserving history |
| | [paper-talk](../skills/writing-cycle/paper-talk/SKILL.md) | Explicit | Generates presentation slide outlines and scripts from the paper |

---

## Typical Research Workflows

### 1. Idea Discovery
```text
Provide research direction
      ↓
/idea-discovery
  ├─ Search literature and track citations (research-lit)
  ├─ Generate candidate ideas (idea-generation & creative-thinking)
  ├─ Search prior work and check novelty (novelty-check)
  ├─ Review and identify weaknesses (idea-review)
  └─ Refine and converge route (idea-refinement)
      ↓
Delivers RESEARCH_PROPOSAL.md (Stops, awaiting user decision)
```

### 2. Validation
```text
State hypothesis or target theorem
      ↓
Empirical Track                      Theoretical Track
/experiment-plan                    formula-derivation (Derivations)
      ↓                                   ↓
/experiment-bridge                  proof-writer (Draft proofs)
  ├─ Test execution & monitoring          ↓
  ├─ Health checks & diagnostics     proof-review (Logic review)
  └─ Code & result integrity audit        ↓
      ↓                             /proof-repair (Targeted repair)
/result-to-claim (Extract claims)         ↓
      ↓                             /proof-orchestrator (Lean assistant)
Delivers audit & claim report       Delivers complete proof logs
```

### 3. Writing Cycle
```text
Provide data or theoretical findings
      ↓
Manuscript Drafting
  ├─ General papers: /paper-writing
  ├─ Machine learning: /ml-paper-writing
  └��� Systems: /systems-paper-writing
      ↓
Targeted Audits and Real Compilation
  ├─ LaTeX compilation checks & fixes (paper-compile / /paper-compile-repair)
  ├─ Citation verification & fixes (citation-audit / /apply-citation-fixes)
  ├─ Full manuscript data consistency (paper-claim-audit)
  └─ Reviewer stress tests (claim-stress-test)
      ↓
Post-submission and Derivatives
  ├─ Rebuttal response: /rebuttal
  ├─ Venue adaptation: /resubmit-pipeline
  └─ Academic talk: /paper-talk
      ↓
Delivers manuscript & auxiliary materials (Stops)
```

---

## Safety and Control Principles

1. **No System Alterations**: The suite does not install or modify Python, Lean, LaTeX, CUDA drivers, or cloud credentials. It reports missing tools and adapts cleanly.
2. **No Automatic Chaining**: Top-level workflows stop after delivering their artifacts. They do not trigger subsequent stages without user direction.
3. **Prior Confirmation**: Operations that involve heavy computation, file rewriting, or paid APIs require explicit user confirmation.

---

## FAQ

**Q: Will installing this suite alter my existing project files?**  
A: No. The `setup-research-os` command inspects your workspace and displays all proposed edits before writing anything.

**Q: Which AI clients are supported?**  
A: Any client supporting the Agent Skills format is compatible, including Claude Code, Codex, Cursor, Gemini CLI, Kimi CLI, and Pi.

---

## Documentation

- [User Acceptance Guide](user-acceptance-guide.md): Manual acceptance steps and boundary checks
- [Product Map](../skills/general/research-os/references/PRODUCT-MAP.md): Skill definitions and boundaries
- [Skills Directory](../skills/README.md): Structure and compatibility guide
- [Upstream Sources and Licenses](upstream-sources-and-licenses.md): Third-party attribution and licenses

---

## License

This project is licensed under the [MIT License](../LICENSE). See [Upstream Sources and Licenses](upstream-sources-and-licenses.md) for third-party attributions.
