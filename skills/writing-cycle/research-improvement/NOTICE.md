# Research improvement upstream notice

`research-improvement` keeps the Research OS Studio bounded review/repair loop and
adds process/tool-improvement controls adapted from these MIT-licensed sources:

- Source: `cursor/plugins`, `pstack/` subtree
- Revision: `88d47514b82e7c44f00f2b2a72ff6dd12158038c`
- Mechanisms compared: `skills/reflect/SKILL.md`, `skills/correct/SKILL.md`,
  `skills/automate-me/SKILL.md`, `skills/recall/SKILL.md`,
  `skills/poteto-mode/playbooks/{autonomous-run,pause-safely,session-pickup}.md`,
  and `docs/guide/07-overnight.md`
- Adaptation: host-neutral continuation, quota accumulation, safe pause/resume,
  failure-path retention, and explicit confirmation for public suite changes and
  external trackers. Cursor `/loop`, cloud-agent runtime, fixed model roles,
  transcript paths, and automatic tracker writes were not copied.
- License: MIT, Copyright (c) 2026 Lauren Tan; full text is in `UPSTREAM-LICENSE.md`.

This notice records provenance and adaptation scope. It is not a runtime gate.
