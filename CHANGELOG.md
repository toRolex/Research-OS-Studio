# research-os-studio

## 2.0.0

### Major Changes

- [`77bee0d`](https://github.com/toRolex/Research-OS-Studio/commit/77bee0d08f09393aba1c7a9efd704861c4fd04d8) Thanks [@toRolex](https://github.com/toRolex)! - Major v2 release of Research OS Studio:

  - Route-only skill-layer orchestration: a single entry routes to the three top-level workflows (Idea Discovery, Validation, Paper Writing and Improvement), with no automatic cross-stage progression
  - Explicit authorization gates: the default compute policy is not an execution grant, so batch size, density and side-effect boundaries require explicit pre-authorization (ADR 0006)
  - Explicit invocation contract and host mapping (ADR 0007), with host-native invocation documented for pi, Claude Code and Codex
  - Breaking: `ask-research-os` removed; hidden skills now require host-native commands; workflows no longer promise unconditional continuation or a publication-ready manuscript
  - Domain glossary: `CONTEXT.md` renamed to `GLOSSARY.md` with tightened Workflow / Internal Skill / Claim / Evidence terms
  - Maintainable `workflow-v2.svg` diagrams replacing raster references, with unconditional stage transitions removed
  - Bounded three-host acceptance evidence archived under `docs/acceptance/`; 39 skills, 74 tests and a clean static security scan

## 1.0.0

### Major Changes

- [`0d6b42f`](https://github.com/toRolex/Research-OS-Studio/commit/0d6b42fc23b819c277f043730ca7dee55642539d) Thanks [@toRolex](https://github.com/toRolex)! - Initial major release of Research OS Studio:

  - 39 self-contained agent skills across General, Idea Cycle, Validation Cycle, and Writing Cycle
  - Human-in-the-loop workflows with bounded execution and zero unauthorized cross-stage progression
  - Direct installation via standard Skills CLI (`npx skills add toRolex/Research-OS-Studio --all`)
  - Comprehensive static validation and integrity check scripts
  - Documentation and guides in English and Chinese
