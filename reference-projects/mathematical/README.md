# Fixed mathematical reference project

This dependency-free Lake project fixes the theorem `∀ n : Nat, n + 0 = n` in both trusted and solution sources. `statement.json`, `proof.json`, and `review.json` retain the ordinary-mathematics path. `formalization.json` binds those records to exact source hashes, Lean/Lake versions, allowed imports, permitted axioms, the statement comparator, and an independent replay principal.

Release verification must run with the pinned toolchain and `RESEARCH_OS_REQUIRE_LEAN=1`. In that environment the mathematical tests require real `lake build`, kernel axiom audit, statement comparison, and independent replay to pass. On a workstation without Lean/Lake, the workflow returns exit code 3 and `tooling-blocked`; that result is accurate local evidence but does not satisfy the release gate.
