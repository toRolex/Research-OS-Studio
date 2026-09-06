# Computational CPU reference experiment

This fixture is intentionally dependency-free and deterministic. It computes a constant-mean baseline over fixed local JSON bytes using Python's `math.fsum` and writes sorted JSON.

Run from repository root:

```sh
uv run python reference-projects/computational/experiment.py
```

Expected `result.json`:

```json
{
  "algorithm": "constant-mean-baseline",
  "count": 4,
  "mean": 2.5,
  "mean_squared_error": 1.25
}
```

The workflow test invokes this command as a real local CPU experiment, pins the resulting bytes, then analyzes them without re-running. A successful process is deliberately not treated as Claim support until `assess-result-to-claim` is separately invoked.

The contract handoff test starts in a temporary Git project with actual committed typed Project, Workstream, research-question and Claim Artifacts. It explicitly invokes and commits each experiment stage, checks all seven resulting Artifacts through the shared foundation/type validator, checks Claim/Evidence against the executable semantics schemas, and verifies provenance against real commit bytes. No workflow creates a commit or invents a Project. Use the design request template only after replacing its deliberately invalid pin markers with real values.

Only a `supports` verdict emits canonical Evidence; `does_not_support` and `inconclusive` emit `experiment-analysis@1.0.0` with `role: result-to-claim-assessment`, not an Assurance Assessment. Workflow reports and attempt ledgers are diagnostic records, not typed Artifact handoffs. Candidate targets become fixed handoffs only after an explicit user commit. The tests also reject substituted run/result bytes, mismatched Workstreams and forged provenance, retain failed partial results, and stop on user revocation.

Regression commands from the repository root:

```sh
uv run --frozen python -m unittest discover -s tests/workflows/computational -v
uv run --frozen python -m unittest discover -s tests/contracts/semantics -v
```
