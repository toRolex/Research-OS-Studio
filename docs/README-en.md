<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-ondark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo-onlight.png">
    <img alt="Research OS Studio" src="assets/logo-onlight.png" width="75%">
  </picture>

  <p>Agent Skills suite designed for research workflows</p>

  <p>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
    <a href="../skills/README.md"><img src="https://img.shields.io/badge/skills-41-green.svg" alt="Skills"></a>
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
  <img alt="Independent research entries with authorization gates and candidate outputs" src="assets/workflow-v2.svg" width="100%">
</div>

---

## Research OS Studio

Research OS Studio is a research-delegation suite: the main entry combines capabilities toward a user-owned goal within an explicit mandate. It can progress without ordinary stage-by-stage approvals; users retain control of goal replacement, authorization and quota boundaries, and external or destructive actions.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Design Principles](#core-design-principles)
- [Skills Inventory](#skills-inventory)
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

# For the discovery route, install `research-os` and its five Required capabilities together
npx skills@latest add toRolex/Research-OS-Studio --skill research-os research-lit idea-generation novelty-check idea-review idea-refinement --agent codex --copy -y
```

### 2. Workspace Setup

After installation, use your host's native invocation. All `/name` examples here are logical skill names, not universal commands: pi uses `/skill:name` (setup: `/skill:setup-research-os`; entry: `/skill:research-os where should I start`), Claude Code uses `/name`, and Codex uses `$name` or explicitly names the installed skill. Plain `/name` text in pi does not guarantee that a hidden explicit-only skill is loaded.

```bash
/setup-research-os
```

This command inspects your existing project structure and suggests configuration options. It presents a complete draft before writing any changes, never overwrites existing research materials, and does not install system-level packages.

### 3. Choose a Skill

If you are unsure which skill fits your current stage, ask the unified entry and keep the request read-only:

```bash
/research-os where should I start
```

That selects route-only. It recommends a skill from your topic or existing materials, modifies no files, does not use the network, and never starts a workflow. The old entry `ask-research-os` has been removed. If you already know the skill, invoke it directly, or let `/research-os` open the matching playbook. Designing an experiment uses experiment-plan; running an approved plan through analysis uses experiment-bridge. Both require the batch grant in the research log. The default policy written by setup is not permission to run.

Saved handoffs use three routes and no new state machine: `proof` resumes one fixed obligation, `improvement` runs the bounded review → repair → re-review loop, and `pickup` re-reads the saved handoff, `compute-policy.md`, and `research-log.md`. An expired authorization stays expired.

---

## Core Design Principles

- **Pure Agent Skills**: Installs directly without separate CLIs, Python packages, or background services.
- **Three Capability Areas (not a required sequence)**:
  1. **Idea Cycle**: Literature search, multi-angle ideation, novelty verification, independent review, and proposal convergence.
  2. **Validation Cycle**: Empirical track handles experiment planning, monitoring, statistical analysis, and audits; theoretical track covers derivations, proof drafting, review, and repairs.
  3. **Writing Cycle**: Paper drafting, academic plotting, LaTeX compilation checks, citation and claim consistency audits, rebuttal preparation, and venue adaptation.
- **Human in the Loop**: A research mandate establishes the goal, permitted scope and quota, and completion condition. The orchestrator may compose and reorder capabilities within that mandate without asking at ordinary stage transitions, output-path changes, or each repair. A read-only request stays read-only. Main-goal replacement waits for the goal owner's confirmation; work beyond authority or quota, external sends, destructive actions, and capability-specific hard gates stop only the affected work. Missing setup or an explicit budget does not block all work: begin with a bounded scope that does not assume ungranted resources. Delegate only when the active host actually supports subagents; otherwise do feasible work and report what could not be delegated.
- **Native File Formats**: Outputs deliverables directly as Markdown, LaTeX, scripts, and data files.

---

## Skills Inventory

The inventory below follows the current `skills/` tree; its size is not a product requirement. Research OS recipe names are routing labels, not additional installable skill slugs. Invocation is explicit except for setup:
- **Explicit except setup**: the user names the skill, or a parent playbook reads it by path. The model does not trigger it from the description.
- **`setup-research-os`**: the one skill a model may suggest. It is optional; a suggestion is not write authorization, and role setup is not a prerequisite to bounded research.

| Category | Skill Name | Invocation | Description |
|---|---|---|---|
| **General** | [setup-research-os](../skills/general/setup-research-os/SKILL.md) | Suggestable | Optional workspace bootstrap for live-model role mappings, a zero-grant default policy, and workspace seeds; a suggestion is not write authorization |
| | [research-os](../skills/general/research-os/SKILL.md) | Explicit | Unified research-delegation entry; route-only is read-only; Discovery and experiment-bridge are composable recipe names, not installable Skills; execution uniquely enters `run-experiment` and uses real host subagent capability when delegating |
| | [swarm](../skills/general/swarm/SKILL.md) | Explicit | Parallel exploration through real host subagents, with isolated outputs and explicit synthesis |
| | [interrogate](../skills/general/interrogate/SKILL.md) | Explicit | Read-only independent challenge of assumptions and conclusions |
| **Organization** | [arena](../skills/organization/arena/SKILL.md) | Explicit | Compares and integrates candidate outputs through an isolated, rubric-led process |
| **Idea Cycle** | [research-lit](../skills/idea-cycle/research-lit/SKILL.md) | Explicit | Literature search and synthesis with source verification |
| | [idea-generation](../skills/idea-cycle/idea-generation/SKILL.md) | Explicit | Multi-angle research candidate generation with filtering logs |
| | [creative-thinking-for-research](../skills/idea-cycle/creative-thinking-for-research/SKILL.md) | Explicit | Cognitive shifts and orthogonal exploration for ideation bottlenecks |
| | [novelty-check](../skills/idea-cycle/novelty-check/SKILL.md) | Explicit | Search closest prior work to verify proposal novelty |
| | [idea-review](../skills/idea-cycle/idea-review/SKILL.md) | Explicit | Independent reviewer perspective identifying proposal weaknesses |
| | [idea-refinement](../skills/idea-cycle/idea-refinement/SKILL.md) | Explicit | Refines proposals into minimal viable and frontier routes |
| **Validation** | [experiment-plan](../skills/validation-cycle/experiment-plan/SKILL.md) | Explicit | Creates bounded experiment plans with hypotheses, baselines, and budgets |
| | [run-experiment](../skills/validation-cycle/run-experiment/SKILL.md) | Explicit | Executes experiment code within approved scope and tracks status |
| | [experiment-queue](../skills/validation-cycle/experiment-queue/SKILL.md) | Explicit | Manages batch experiment queues and resource allocation |
| | [monitor-experiment](../skills/validation-cycle/monitor-experiment/SKILL.md) | Explicit | Monitors running processes and hardware state without inference |
| | [training-health-check](../skills/validation-cycle/training-health-check/SKILL.md) | Explicit | Diagnoses training issues such as NaNs, OOMs, or stalled loss |
| | [analyze-results](../skills/validation-cycle/analyze-results/SKILL.md) | Explicit | Evaluates statistical distributions and uncertainty across runs |
| | [experiment-audit](../skills/validation-cycle/experiment-audit/SKILL.md) | Explicit | Audits code logic, evaluation metrics, and result authenticity |
| | [result-to-claim](../skills/validation-cycle/result-to-claim/SKILL.md) | Explicit | Extracts bounded scientific claims supported by empirical data |
| | [formula-derivation](../skills/validation-cycle/formula-derivation/SKILL.md) | Explicit | Mathematical derivations recording assumptions, steps, and error bounds |
| | [create-formal-verification-skill](../skills/validation-cycle/create-formal-verification-skill/SKILL.md) | Explicit | Builds runnable formal checks with assumption and correspondence audits |
| | [maintain-formal-verification-skill](../skills/validation-cycle/maintain-formal-verification-skill/SKILL.md) | Explicit | Re-aligns and reruns formal checks after code changes |
| | [create-verification-skill](../skills/validation-cycle/create-verification-skill/SKILL.md) | Explicit | Builds runnable behavioral verification skills and evidence workflows |
| | [maintain-verification-skill](../skills/validation-cycle/maintain-verification-skill/SKILL.md) | Explicit | Updates behavioral verification workflows for changed product behavior |
| | [proof-writer](../skills/validation-cycle/proof-writer/SKILL.md) | Explicit | Drafts formal proofs while tracking incomplete attempts and gaps |
| | [proof-review](../skills/validation-cycle/proof-review/SKILL.md) | Explicit | Read-only check for proof structure, lemmas, and counterexamples |
| | [proof-repair](../skills/validation-cycle/proof-repair/SKILL.md) | Explicit | Targeted repair of proof gaps within authorized scope |
| **Writing Cycle** | [paper-writing](../skills/writing-cycle/paper-writing/SKILL.md) | Explicit | The single writing organizer; general, ML/AI, and Systems are professional options with on-demand references and templates shipped together |
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

These are example recipes, not mandatory stages or a fixed pipeline. The orchestrator can compose, reorder, or revisit capabilities according to the mandate, then stop when its completion condition is met.

### 1. Idea Discovery
```text
Provide a research direction
      ↓
/research-os I have a direction and no idea
      ↓
research-os Discovery recipe
  Select needed capabilities from goal gaps; start locally, reorder, or revisit
  ├─ Literature gap: research-lit
  ├─ Candidate gap: idea-generation (creative-thinking if useful)
  ├─ Prior work unchecked: novelty-check
  ├─ Independent challenge needed: idea-review
  └─ Convergence or Proposal needed: idea-refinement
      ↓
Deliver only the report and/or Proposal required by this mandate, then stop
```

Full Discovery is an optional recipe, not a required route. Existing results may satisfy or omit a responsibility; new evidence may reorder work or trigger a revisit. Leaf source, review, and anchor obligations remain in force. A missing required skill blocks only its affected work and must be reported. Goal replacement, over-authority, over-quota, or file conflict also blocks only the affected branch.

### 2. Validation
```text
State hypothesis or target theorem
      ↓
Empirical Track                      Theoretical Track
/experiment-plan                    formula-derivation (Derivations)
      ↓                                   ↓
/run-experiment                     proof-writer (Draft proofs)
  ├─ Test execution & monitoring          ↓
  ├─ Health checks & diagnostics     proof-review (Logic review)
  └─ Code & result integrity audit        ↓
      ↓                             /proof-repair (Targeted repair)
/result-to-claim (Extract claims)         ↓
      ↓                             /research-os proof recipe (proof-review methods on demand)
Delivers audit & claim report       Delivers complete proof logs
```

The theoretical route selects and alternates derivation, proof construction, fresh read-only review, finding repair, and optional formalization from evidence; these are not mandatory stages. `/research-os` is the sole owner of long-running mandate, rounds, quota, pause/resume, and stop control.

### 3. Writing Cycle
```text
Provide data or theoretical findings
      ↓
/research-os matches paper-writing from the materials
  ├─ General: general → paper-writing
  ├─ Machine learning: ml → paper-writing + ML reporting/reviewer/venue references
  └─ Systems design: systems → paper-writing + Systems methods/evaluation/venue references
      ↓
The leaf follows the active mandate rather than adding per-stage approval gates; read-only scope, goal changes, authority or quota overruns, external sends, and destructive actions remain gated
Parallel audits: paper-claim-audit, citation-audit, claim-stress-test
Proof manuscripts also read proof-review
      ↓
Delivers a candidate manuscript and audit report (stops)
Submission and upload are outside this route
paper-compile-repair and apply-citation-fixes remain distinct leaf skills; they may be invoked directly or cascaded by an authorized mandate, with each skill's exact-diff controls preserved
```

---

## Safety and Control Principles

1. **Environment ownership and scoped preparation**: Reuse existing resources. Project-local dependencies, tools, and caches may be prepared within a valid mandate's write scope and remaining quota; read-only capabilities do not prepare environments. Global installation/configuration, driver changes, credentials, and scheduler deployment require specific authority, not an ordinary research mandate. Report missing tools and unperformed checks honestly; stop the affected action when authority or resources are missing.
2. **Mandate, read-only scope, and hard gates**: Keep explicit entry and user-requested read-only scope. Within the mandate, ordinary reversible work and capability transitions proceed without repeated approval. Main-goal replacement waits for the goal owner's confirmation; authority or quota overrun, external sends, destructive changes, and specific safety gates stop before the side effect; only affected work is blocked.
3. **Quota-aware execution**: Missing setup or an explicit budget permits bounded work that does not assume ungranted resources. Heavy computation and paid external services proceed only within actual authorization and quota; missing or exceeded quota stops the affected work.

---

## FAQ

**Q: Will installing this suite alter my existing project files?**  
A: No. The `setup-research-os` command inspects your workspace and displays all proposed edits before writing anything.

**Q: What host capabilities are required?**

A host must actually discover and load Agent Skills for direct use. Delegated work additionally requires real subagent support in that host; verify its behavior rather than inferring it from a product name or successful file installation.

---

## Documentation

- [User Acceptance Guide](user-acceptance-guide.md): Manual acceptance steps and boundary checks
- [Product Map](../skills/general/research-os/references/PRODUCT-MAP.md): Skill definitions and boundaries
- [Skills Directory](../skills/README.md): Structure and compatibility guide
- [Upstream Sources and Licenses](upstream-sources-and-licenses.md): Third-party attribution and licenses

---

## License

This project is licensed under the [MIT License](../LICENSE). See [Upstream Sources and Licenses](upstream-sources-and-licenses.md) for third-party attributions.
