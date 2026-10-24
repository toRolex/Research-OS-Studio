# Research OS pstack provenance notice

The `playbooks/continuation.md` playbook adapts continuation and safe pause/resume
mechanisms from the `pstack/` subtree of `cursor/plugins` at fixed revision
`88d47514b82e7c44f00f2b2a72ff6dd12158038c`.

Upstream source material includes `pstack/skills/poteto-mode/playbooks/autonomous-run.md`,
`pause-safely.md`, and `session-pickup.md`, with related recall/reflect/correct
mechanisms from `pstack/skills/{recall,reflect,correct}/SKILL.md`.

Upstream license: MIT, Copyright (c) 2026 Lauren Tan, from `pstack/LICENSE`.

适配范围：host-neutral continuation, checkpoints, safe pause/resume, and
restoration from durable project artifacts. Cursor commands, cloud-worker runtime,
fixed model bindings, and transcript-directory assumptions are not included.
The complete upstream MIT text is provided in `LICENSE-PSTACK` beside this notice
and playbook; installing `research-os` does not require installing
`research-improvement`. The existing `LICENSE` remains unchanged for its original
copyright holder.
