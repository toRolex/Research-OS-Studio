---
name: setup-research-os
description: Install or update Research OS project files only after an explicit user request.
---

# Setup Research OS

Run only after explicit user invocation. Install the selected canonical skills, contracts, templates, validators, and generated platform projections into the current project as ordinary project files.

## Required inputs

- Exact Research OS source version and full source Git commit.
- Explicit project directory.
- Explicit operation: new install, named update environment, or historical restore.
- Platform capability profile used to generate each requested projection.

## Rules

1. Preflight every destination before writing. Preserve byte-identical files. If any existing file differs, stop without partial installation.
2. Never install a plugin, symlink, global runtime, automatic updater, Research OS-specific project runtime, `pyproject.toml`, dependency lockfile, or environment activation state.
3. Record a project-local install manifest containing the source revision and SHA-256 of every installed file.
4. Updates are explicit and non-destructive. Write a named versioned environment and require a separate explicit activation decision; never rewrite old runs, fixed Artifacts, Assessments, Publications, or prior environments.
5. Generate requested host projections from canonical skills. Pin the canonical skill, Adapter, capability-profile versions and digests.
6. Workflows remain explicit user entrypoints and cannot be model-invoked. Disciplines remain workflow-internal and are not exposed as normal user entrypoints.
7. If a platform cannot express every required control, return structured `BLOCKED`, write nothing, list no automatic next workflow, and stop.
8. New install and update source bytes must be read from the exact full Git commit, not from the mutable checkout. Historical restore accepts only a full 40-character Git commit, reads that fixed tree without changing the source project, verifies its current or supported legacy manifest, rejects non-regular files, and writes only to a new output directory.
9. Never start another workflow. Report installed, preserved, blocked, or restored files and stop with zero automatic next steps.

See `references/leaf-install-implementation-notes.md` for the implementation boundary and decisions.
