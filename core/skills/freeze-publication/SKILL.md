---
name: freeze-publication
description: Stage and explicitly confirm a closed empirical-computational or mathematical-theoretical Publication with fixed Manuscript, PDF, evidence and six-axis Assurance.
---

# Freeze Publication

## Invocation and authority

User-invoked workflow only. The platform projection enforces explicit invocation; the canonical Core remains provider-neutral. The user owns publication intent, scientific boundaries, formal acceptance and final freeze. A discipline may audit claims or citations only inside this workflow; it cannot accept, change a statement, loosen a gate, start Lean/experiments or invoke another workflow.

## Inputs

Read only the user-selected Project, Manuscript, members and Assessments, each fixed by actual SHA-256 and complete Git commit or canonical HTTPS target. Use the versioned contracts in `core/contracts/publication/` and the selected `templates/publication/` request. Empty templates are incomplete requests, not accepted examples.

Manuscript is a typed Artifact containing profile, Project, title, authors, body, contributions, important Claims, supporting Evidence, conditions, limitations, materials and external-reference refs. The PDF is its unique primary public text; the source Manuscript remains a separate typed member. Every member has a safe path, purpose, role, exact fixed reference and explicit dependencies. Materials are opaque original bytes, never implicitly upgraded to Claims or Assessments.

For computational outputs, preserve design/preparation/run/analysis/result-to-claim outputs and all used dependencies as fixed materials. For mathematical outputs, preserve statement, ordinary proof, review and optional formalization/toolchain/replay artifacts. Their semantic/run digests do not replace actual file-byte SHA-256. Candidate Evidence and standalone proof reviews require explicit canonical Evidence/Assessment records; no conversion may manufacture an assessor, commit, isolation receipt or human acceptance.

## Steps and completion criteria

1. **Prepare candidate.** Validate the typed Manuscript, preserve declared conditions and limitations, and generate the deterministic PDF from `manuscript_text` using `render_pdf`. The minimal renderer supports printable ASCII, newline and tab; unsupported glyphs fail rather than disappear. It interprets no markup, commands, URLs or embedded PDF instructions. Source and PDF must both be fixed before staging. Stop if any required material cannot be fixed.
2. **Stage.** Call `stage_publication(project, request, stage_path=...)`. Supply the complete selected member set, including Project/Workstream, provenance inputs, all Claim/Evidence dependencies, all selected Assessments and isolation inputs. No recursive fetching or implicit discovery. The stage path is exclusive; a revision uses a new path. Completion means a deterministic candidate manifest and successful preflight, not acceptance.
3. **Preflight.** Call `preflight(project, manifest)`. It rechecks actual working bytes against fixed Git blobs, validates closure and one primary PDF, and binds every receipt and Assessment. Six axes remain separate. Both profiles require active whole-Manuscript passes for structural conformance, independent review and human acceptance; computational additionally requires empirical reproducibility, mathematical requires mathematical argument review. `required_gates` may add subject/scope requirements but cannot remove the defaults. Lean is optional; when formal verification is claimed as required, add that gate explicitly. Missing, failed, inconclusive, not-applicable, stale or conflicting required evidence blocks freeze. Independent review requires a distinct bound reviewer and isolation receipt; human acceptance requires the Project user role.
4. **Final confirmation.** Present the entire staged manifest, preflight report, boundaries, external receipts and exact `confirmation_text(manifest)`: `FREEZE <publication> SHA256 <final-manifest-sha256>`. Ask the user to supply it exactly. No cached intent or previous revision's confirmation suffices. Do not synthesize the separate human-acceptance Assessment. Any changed field or byte requires re-stage, revalidation and renewed confirmation.
5. **Freeze once.** Call `freeze_publication(project, manifest, confirmation, principal)` only after actual user confirmation. It revalidates and writes an atomic no-replace snapshot under `publications/<name>/`: canonical manifest, closed copied files and freeze receipt. Existing files or directories are never overwritten, including empty destinations. Completion means the receipt identifies the exact final manifest digest and `verify_publication` passes.
6. **Stop.** Return candidate/frozen target, actual report, receipt and zero or more optional next steps; then stop. Do not submit a paper or invoke the next workflow. Retain failed staging evidence. A validation failure is exit code 1, not success or an external-prerequisite excuse.

## Profile policy and six-axis semantics

Profile version 1.0.0 uses four mandatory gates as a conservative publication policy: structural conformance validates shape, independent review prevents self-approval, human acceptance preserves user authority, and empirical reproducibility or mathematical argument review supplies the profile-specific research axis. These are separate scoped decisions, not a four-of-six score or proof that the other axes passed. All six keys are required to make omission explicit: `[]` means no Assessment included for that axis. An authored `not_applicable` Assessment is retained as that verdict; it is never synthesized, never a pass, and cannot satisfy a required gate. Optional Lean does not make formal verification mandatory for every mathematical paper. A publication claiming it as required must add the explicit formal-verification gate; any unknown, failed or inconclusive requirement blocks. The API never creates any Assessment, including passes used only in test fixtures.

## External references

Each versioned external-reference Artifact fixes target, purpose, required scope and retrieval receipt: retrieved time, identical resolved locator, actual content digest, fixed content, license evidence and retrieval log. Preserve minimum lawful bytes offline. Missing receipts or drift block. Do not silently substitute mirrors or newer content. The validator proves recorded byte/identity closure, not legal advice or scientific truth.

## After freeze

`verify_publication` reads the frozen package without depending on current upstream files. A second publication uses a new name and independently stages/confirms its content. `append_event` writes user-confirmed `supersede`, `retract` or `notice` under `publication-events/`, outside the package; supersede must identify a real different frozen Publication in the same Project. `stale_audit` appends actual changed/unavailable upstream-byte observations without changing original bytes or old Assessments. Repeating an identical event cannot overwrite its existing record.

## Integration seam

The public Python boundary is `research_os.publication`; shared CLI routing is owned by the integration leaf. This workflow does not claim that the legacy single-member CLI freeze already implements this staged contract. No commit, remote fetch, experiment or mathematical verification is automatically performed by Publication APIs.
