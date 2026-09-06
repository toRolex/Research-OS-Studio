# Port attribution and modifications

Research OS includes minimally adapted text disciplines derived from fixed source files. Upstream code and commands are not bundled or executed.

- `experiment-audit`, `statistical-check`, `training-health-check`, `environment-check`, `independent-proof-review`, `publication-claim-audit`, `citation-reference-audit`
  - Source: `https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git`
  - Fixed commit: `2349f63ccfd7502aae95ec987b4d0a4c65d69c52`
  - Copyright © 2026 wanshuiyin
  - License: MIT; see `auto-claude-code-research-in-sleep-MIT.txt`
  - Modified by Research OS: provider bindings, automatic progression, broad tool permissions, and mutable workflow actions were removed; fixed-input, bounded-verdict, user-control, and no-cross-workflow boundaries were added.

- `trusted-statement-comparison`
  - Source: `https://github.com/openai/ten-proofs.git`
  - Fixed commit: `94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`
  - Source path: `ComparatorChallenges/B_BinaryCodes.json`
  - License: Apache-2.0; see `ten-proofs-Apache-2.0.txt`
  - Modified by Research OS: the fixed comparator configuration informed a provider-neutral statement-comparison discipline. This does not bundle or claim to execute the upstream Lean comparator.

Full source snapshots, manifests, ledgers, evaluation details, and decision receipts remain in the repository `ports/` evidence tree. Installed distributions carry this attribution and the applicable license texts through `core/licenses/ports/`.
