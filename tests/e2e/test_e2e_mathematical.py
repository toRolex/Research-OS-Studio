"""Ordinary proof does not require Lean; release Lean never uses a fake tool."""
import os
import unittest

from tests.e2e.support import InstalledProject, artifact, digest


class MathematicalReleaseTests(InstalledProject, unittest.TestCase):
    def test_e2e_mathematical_ordinary_proof_review_pdf_publication(self):
        self.setup_installed_project()
        self.api("from pathlib import Path; import json; "
                 "from research_os.workflows.mathematical import create_statement_candidate, confirm_statement; "
                 "s=create_statement_candidate(revision=1, quantifiers=['for every natural n'], hypotheses=[], "
                 "domain='natural numbers', conclusion='n + 0 = n', rationale='right additive identity'); "
                 "s=confirm_statement(s, principal='alice', confirmation=f\"CONFIRM STATEMENT r1 {s['semantic_digest']}\"); "
                 "Path('statement-spec.json').write_text(json.dumps(s))")
        self.add("statement.json", artifact("statement.json", "mathematical-statement", self.read("statement-spec.json")))
        self.invoke("math-proof", {
            "statement_input": self.input_pin("statement.json"), "output": "proof.json", "report": "proof-report.json",
            "actor_principal": "alice", "examples": [], "counterexamples": [],
            "lemma_map": [{"id": "L1", "statement": "right additive identity", "depends_on": [], "status": "proved"}],
            "attempts": [{"id": "A1", "approach": "definition of addition", "argument":
                "Addition on natural numbers is defined recursively on the second operand. Its base equation is n + 0 = n, for every natural n; no induction step or additional hypothesis is needed.",
                "outcome": "candidate-proof", "gaps": []}], "max_attempts": 1,
        })
        self.assertFalse((self.root / "formalization.json").exists())
        self.validate("statement.json")
        self.validate("proof.json")
        self.add("proof.json")
        # Explicit fixture decisions; the adapter consumes validated typed inputs,
        # replays only their pinned bytes and does not claim actual model isolation.
        statement_record_ref = self.add("review-statement.json", self.read("statement.json")["spec"], role="material")
        proof_record_ref = self.add("review-proof.json", self.read("proof.json")["spec"], role="material")
        def project_record(path, kind, record_ref, inputs):
            self.write("projection-request.json", dict(kind=kind, target={"kind": "git", "path": path},
                record_ref=record_ref, project_ref=self.project_ref, workstream_ref=self.workstream_ref, inputs=inputs))
            self.api("from pathlib import Path; import json; "
                     "from research_os.workflows.mathematical.projections import project_record; "
                     "request=json.loads(Path('projection-request.json').read_bytes()); "
                     "result=project_record(Path(request['record_ref']['target']['path']).read_bytes(), **request); "
                     f"Path({path!r}).write_text(json.dumps(result, indent=2)+'\\n')")
            return self.add(path)
        statement_ref = project_record("typed-statement.json", "math-statement-projection", statement_record_ref, {})
        proof_ref = project_record("typed-proof.json", "math-proof-projection", proof_record_ref, {"statement": statement_ref})
        self.write("validation-context.json", {"project": self.project_ref, "evidence": [],
                                               "records": [m["ref"] for m in self.members]})
        self.validate("typed-statement.json", context=True)
        self.validate("typed-proof.json", context=True)
        self.write("review-request.json", {"statement_ref": statement_ref, "proof_ref": proof_ref})
        self.api("from pathlib import Path; import json; "
                 "from research_os.cli import load_validation_context; "
                 "from research_os.workflows.mathematical.projections import create_typed_review; "
                 "context=load_validation_context(Path.cwd(), 'validation-context.json'); "
                 "context.pop('evidence_by_digest'); "
                 "request=json.loads(Path('review-request.json').read_bytes()); "
                 "r=create_typed_review(**request, **context, reviewer_principal='bob', findings=[], verdict='pass'); "
                 "Path('review.json').write_text(json.dumps(r, indent=2)+'\\n')")
        review = self.read("review.json")
        self.assertFalse(review["human_acceptance"])
        self.assertNotEqual(review["reviewer_principal"], review["proof_actor_principal"])
        self.assertEqual({item["sha256"] for item in review["isolation_receipt"]["inputs"]},
                         {digest(self.root / "review-statement.json"), digest(self.root / "review-proof.json")})
        review_record_ref = self.add("review.json", role="material")
        review_ref = project_record("typed-review.json", "math-review-projection", review_record_ref,
                                    {"statement": statement_ref, "proof": proof_ref})
        self.write("validation-context.json", {"project": self.project_ref, "evidence": [],
                                               "records": [m["ref"] for m in self.members]})
        self.validate("typed-review.json", context=True)
        for path in ("typed-statement.json", "typed-proof.json", "typed-review.json"):
            direct = self.cli("validate", "--project", str(self.root), path, "--context", "validation-context.json")
            for adapter in ("claude-code", "codex"):
                adapted = self.cli("adapter", adapter, "validate", "--project", str(self.root), path,
                                   "--context", "validation-context.json")
                self.assertEqual(direct, adapted)
        # Missing fixed context and byte/version corruption fail, never API-fallback.
        self.cli("validate", "--project", str(self.root), "typed-review.json", code=1)
        invalid = self.read("typed-review.json")
        invalid["spec"]["record_digest"] = "0" * 64
        self.write("invalid-review.json", invalid)
        self.cli("validate", "--project", str(self.root), "invalid-review.json", "--context", "validation-context.json", code=1)
        invalid["type"]["version"] = "2.0.0"
        self.write("invalid-review.json", invalid)
        result = self.cli("validate", "--project", str(self.root), "invalid-review.json", "--context", "validation-context.json", code=1)
        self.assertIn("type.unsupported", {i["code"] for i in result["issues"]})
        self.claim_ref = self.add("claim.json", artifact("claim.json", "claim", {
            "project": self.project_ref, "workstream": self.workstream_ref, "statement": "For every natural n, n + 0 = n.",
            "scope": "whole_subject", "conditions": ["Recursive definition of natural-number addition"],
            "limitations": ["Ordinary mathematical argument, not formal verification"],
        }))
        self.evidence_ref = self.add("evidence.json", artifact("evidence.json", "evidence", {
            "project": self.project_ref, "workstream": self.workstream_ref, "description": "Fixed ordinary proof and fixture review",
        }, relations=[{"relation": "supports", "claim": self.claim_ref, "scope": "whole_subject",
                       "method": "Review of recursive definition", "conditions": ["Natural numbers"]}],
            provenance=[{"activity": "ordinary proof review", "inputs": [review_ref]}]))
        self.validate("evidence.json")
        self.publish("mathematical-theoretical", "For every natural n, n + 0 = n, by the defining base equation of addition.")
        self.assertEqual(self.invocations, ["math-proof"])

    def test_e2e_mathematical_real_lean_reports_blocked_or_verified(self):
        self.setup_installed_project()
        self.api("from pathlib import Path; import research_os, shutil; "
                 "source=Path(research_os.__file__).parent/'_reference_projects/mathematical'; "
                 "shutil.copytree(source, 'lean-reference')")
        self.write("lean-reference/request.json", {
            "statement_input": {"path": "statement.json", "sha256": digest(self.root / "lean-reference/statement.json")},
            "proof_input": {"path": "proof.json", "sha256": digest(self.root / "lean-reference/proof.json")},
            "review_input": {"path": "review.json", "sha256": digest(self.root / "lean-reference/review.json")},
            "report": "lean-report.json",
        })
        from tests.e2e.support import execute
        result = execute(["uv", "run", "--no-project", str(self.environment / "bin/research-os"),
                          "workflow", "lean-formalize", "--project", str(self.root / "lean-reference"),
                          "--request", "request.json"], self.root, check=False)
        import json
        report = json.loads(result.stdout)
        self.assertIn(result.returncode, (0, 3), report)
        if result.returncode == 3:
            self.assertEqual(report["verdict"], "blocked", report)
            self.assertEqual(report["stop_reason"], "tooling-blocked", report)
            self.assertEqual(report["result"], "not-verified", report)
            if os.environ.get("RESEARCH_OS_REQUIRE_LEAN") == "1":
                self.fail("Release gate BLOCKED: real fixed Lean build/audit/comparator/kernel replay unavailable")
            self.skipTest("BLOCKED release gate: real Lean unavailable; blocked behavior verified, not a Lean PASS")
        self.assertEqual(report["result"], "verified", report)
        self.assertEqual(report["audit"]["verdict"], "pass", report)
        self.assertEqual(report["kernel_replay"]["verdict"], "pass", report)


if __name__ == "__main__":
    unittest.main()
