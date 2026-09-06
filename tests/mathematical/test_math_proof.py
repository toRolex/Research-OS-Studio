from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.workflows.mathematical import (  # noqa: E402
    MathematicalWorkflowError,
    confirm_statement,
    create_statement_candidate,
    revise_statement,
    run_math_proof,
    validate_math_proof,
    validate_statement,
)


from research_os.workflows.mathematical.records import canonical_digest  # noqa: E402


def confirmed_statement() -> dict[str, object]:
    statement = create_statement_candidate(
        revision=1,
        quantifiers=["for every natural number n"],
        hypotheses=[],
        domain="natural numbers",
        conclusion="n + 0 = n",
        rationale="Fixed test statement.",
    )
    return confirm_statement(
        statement,
        principal="project:user",
        confirmation=f"CONFIRM STATEMENT r1 {statement['semantic_digest']}",
    )


def candidate_attempt(identifier: str = "A1") -> dict[str, object]:
    return {
        "id": identifier,
        "approach": "right identity",
        "argument": "Nat.add_zero supplies the exact equality.",
        "outcome": "candidate-proof",
        "gaps": [],
    }


def lemma_map() -> list[dict[str, object]]:
    return [
        {
            "id": "L1",
            "statement": "zero is a right identity for natural addition",
            "depends_on": [],
            "status": "proved",
        }
    ]


class MathProofTests(unittest.TestCase):
    def test_candidate_requires_exact_confirmation_bound_to_revision_and_digest(
        self,
    ) -> None:
        candidate = create_statement_candidate(
            revision=1,
            quantifiers=["for every n"],
            hypotheses=["n is a natural number"],
            domain="natural numbers",
            conclusion="n + 0 = n",
            rationale="Test confirmation binding.",
        )
        self.assertEqual(validate_statement(candidate), [])
        self.assertEqual(
            validate_statement(candidate, require_confirmed=True)[0].code,
            "statement.unconfirmed",
        )
        with self.assertRaises(MathematicalWorkflowError):
            confirm_statement(candidate, principal="project:user", confirmation="yes")
        confirmed = confirm_statement(
            candidate,
            principal="project:user",
            confirmation=f"CONFIRM STATEMENT r1 {candidate['semantic_digest']}",
        )
        self.assertEqual(validate_statement(confirmed, require_confirmed=True), [])

    def test_semantic_change_creates_revision_and_discards_old_confirmation(
        self,
    ) -> None:
        first = confirmed_statement()
        second = revise_statement(
            first,
            domain="integers",
            rationale="The user explicitly selected the integer-domain revision.",
        )
        self.assertEqual(second["revision"], 2)
        self.assertEqual(second["supersedes"], first["semantic_digest"])
        self.assertIsNone(second["confirmation"])
        self.assertNotEqual(second["semantic_digest"], first["semantic_digest"])
        self.assertEqual(
            validate_statement(second, require_confirmed=True)[0].code,
            "statement.unconfirmed",
        )
        with self.assertRaises(MathematicalWorkflowError):
            confirm_statement(
                second,
                principal="project:user",
                confirmation=first["confirmation"]["phrase"],
            )
        with self.assertRaises(MathematicalWorkflowError):
            revise_statement(first, rationale="Only formatting changed.")

    def test_examples_counterexamples_and_failure_history_are_retained(self) -> None:
        statement = confirmed_statement()
        run = run_math_proof(
            statement=statement,
            actor_principal="project:proof-author",
            examples=[{"input": "0", "observation": "works"}],
            counterexamples=[
                {"input": "-1", "observation": "outside the declared domain"}
            ],
            lemma_map=lemma_map(),
            attempts=[
                {
                    "id": "A1",
                    "approach": "direct rewrite",
                    "argument": "A first argument was attempted and retained.",
                    "outcome": "failed",
                    "gaps": ["the rewrite rule was not justified"],
                }
            ],
            max_attempts=3,
        )
        self.assertEqual(run["result"], "proof-gap")
        self.assertEqual(run["stop_reason"], "counterexample-found")
        self.assertEqual(run["attempts"][0]["outcome"], "failed")
        self.assertEqual(
            run["proof_gaps"][0]["gap"], "the rewrite rule was not justified"
        )
        self.assertEqual(validate_math_proof(run, statement=statement), [])

    def test_attempt_budget_is_hard_and_budget_exhaustion_is_not_a_proof_result(
        self,
    ) -> None:
        statement = confirmed_statement()
        attempts = [
            {
                "id": "A1",
                "approach": "induction",
                "argument": "base only",
                "outcome": "proof-gap",
                "gaps": ["successor case"],
            },
            {
                "id": "A2",
                "approach": "rewriting",
                "argument": "rewrite unavailable",
                "outcome": "failed",
                "gaps": ["missing lemma"],
            },
        ]
        run = run_math_proof(
            statement=statement,
            actor_principal="project:proof-author",
            examples=[],
            counterexamples=[],
            lemma_map=lemma_map(),
            attempts=attempts,
            max_attempts=2,
        )
        self.assertEqual(run["result"], "proof-gap")
        self.assertEqual(run["stop_reason"], "budget-exhausted")
        self.assertEqual(run["budget"], {"max_attempts": 2, "attempts_used": 2})
        with self.assertRaises(MathematicalWorkflowError):
            run_math_proof(
                statement=statement,
                actor_principal="project:proof-author",
                examples=[],
                counterexamples=[],
                lemma_map=lemma_map(),
                attempts=attempts,
                max_attempts=1,
            )

    def test_candidate_proof_stops_without_invoking_or_requiring_lean(self) -> None:
        statement = confirmed_statement()
        run = run_math_proof(
            statement=statement,
            actor_principal="project:proof-author",
            examples=[{"input": "3", "observation": "3 + 0 = 3"}],
            counterexamples=[],
            lemma_map=lemma_map(),
            attempts=[candidate_attempt()],
            max_attempts=2,
        )
        self.assertEqual(run["result"], "candidate")
        self.assertEqual(run["stop_reason"], "workflow-complete")
        self.assertNotIn("lean", str(run).lower())
        self.assertEqual(run["next_steps"][0], "request independent proof review")

    def test_candidate_cannot_hide_unclosed_gaps_or_lemma_obligations(self) -> None:
        for source in (
            "lemma-gap",
            "lemma-open",
            "candidate-gap",
            "earlier-gap",
            "empty-gap",
        ):
            with self.subTest(source=source):
                lemmas = lemma_map()
                attempts = [candidate_attempt()]
                if source.startswith("lemma-"):
                    lemmas[0]["status"] = source.removeprefix("lemma-")
                elif source == "candidate-gap":
                    attempts[0]["gaps"] = ["successor case remains unproved"]
                else:
                    attempts.insert(
                        0,
                        {
                            **candidate_attempt("A0"),
                            "outcome": "proof-gap",
                            "gaps": []
                            if source == "empty-gap"
                            else ["unclosed earlier gap"],
                        },
                    )
                history = copy.deepcopy(attempts)
                run = run_math_proof(
                    statement=confirmed_statement(),
                    actor_principal="project:proof-author",
                    examples=[],
                    counterexamples=[],
                    lemma_map=lemmas,
                    attempts=attempts,
                    max_attempts=3,
                )
                self.assertEqual(run["result"], "proof-gap")
                self.assertEqual(run["stop_reason"], "proof-gap")
                self.assertEqual(run["attempts"], history)
                self.assertTrue(run["proof_gaps"])
                self.assertEqual(validate_math_proof(run), [])

    def test_rehashed_candidate_cannot_bypass_proof_gap_validation(self) -> None:
        run = run_math_proof(
            statement=confirmed_statement(),
            actor_principal="project:proof-author",
            examples=[],
            counterexamples=[],
            lemma_map=lemma_map(),
            attempts=[candidate_attempt()],
            max_attempts=2,
        )
        for source in (
            "lemma",
            "attempt",
            "aggregate",
            "missing-candidate",
            "counterexample",
            "stop",
        ):
            with self.subTest(source=source):
                forged = copy.deepcopy(run)
                if source == "lemma":
                    forged["lemma_map"][0]["status"] = "gap"
                elif source == "attempt":
                    forged["attempts"][0]["gaps"] = ["unproved"]
                elif source == "aggregate":
                    forged["proof_gaps"] = [{"attempt": "A1", "gap": "unproved"}]
                elif source == "missing-candidate":
                    forged["attempts"][0]["outcome"] = "failed"
                elif source == "counterexample":
                    forged["counterexamples"] = [{"input": "counterexample"}]
                else:
                    forged["stop_reason"] = "user-stopped"
                forged["run_digest"] = canonical_digest(
                    {key: value for key, value in forged.items() if key != "run_digest"}
                )
                self.assertIn(
                    "proof.result.inconsistent",
                    [issue.code for issue in validate_math_proof(forged)],
                )

    def test_counterexample_attempt_blocks_later_candidate_without_losing_history(
        self,
    ) -> None:
        attempts = [
            {**candidate_attempt("A0"), "outcome": "counterexample"},
            candidate_attempt(),
        ]
        run = run_math_proof(
            statement=confirmed_statement(),
            actor_principal="project:proof-author",
            examples=[],
            counterexamples=[],
            lemma_map=lemma_map(),
            attempts=attempts,
            max_attempts=3,
        )
        self.assertEqual(run["result"], "proof-gap")
        self.assertEqual(run["stop_reason"], "counterexample-found")
        self.assertEqual(run["attempts"], attempts)
        run.update(result="candidate", stop_reason="workflow-complete")
        run["run_digest"] = canonical_digest(
            {key: value for key, value in run.items() if key != "run_digest"}
        )
        self.assertIn(
            "proof.result.inconsistent",
            [issue.code for issue in validate_math_proof(run)],
        )

    def test_boolean_statement_revision_and_attempt_budgets_are_rejected(self) -> None:
        for value in (True, False):
            with self.subTest(value=value):
                statement = confirmed_statement()
                statement["revision"] = value
                self.assertIn(
                    "statement.revision",
                    [issue.code for issue in validate_statement(statement)],
                )
                with self.assertRaises(MathematicalWorkflowError):
                    run_math_proof(
                        statement=confirmed_statement(),
                        actor_principal="project:proof-author",
                        examples=[],
                        counterexamples=[],
                        lemma_map=lemma_map(),
                        attempts=[candidate_attempt()],
                        max_attempts=value,
                    )
                run = run_math_proof(
                    statement=confirmed_statement(),
                    actor_principal="project:proof-author",
                    examples=[],
                    counterexamples=[],
                    lemma_map=lemma_map(),
                    attempts=[candidate_attempt()],
                    max_attempts=1,
                )
                for field in ("max_attempts", "attempts_used"):
                    forged = copy.deepcopy(run)
                    forged["budget"][field] = value
                    forged["run_digest"] = canonical_digest(
                        {
                            key: item
                            for key, item in forged.items()
                            if key != "run_digest"
                        }
                    )
                    self.assertIn(
                        "proof.budget",
                        [issue.code for issue in validate_math_proof(forged)],
                    )

    def test_lemma_map_rejects_unknown_dependencies_and_cycles(self) -> None:
        statement = confirmed_statement()
        invalid_maps = [
            [
                {
                    "id": "L1",
                    "statement": "x",
                    "depends_on": ["missing"],
                    "status": "open",
                }
            ],
            [
                {"id": "L1", "statement": "x", "depends_on": ["L2"], "status": "open"},
                {"id": "L2", "statement": "y", "depends_on": ["L1"], "status": "open"},
            ],
        ]
        for invalid in invalid_maps:
            with self.subTest(invalid=invalid):
                with self.assertRaises(MathematicalWorkflowError):
                    run_math_proof(
                        statement=statement,
                        actor_principal="project:proof-author",
                        examples=[],
                        counterexamples=[],
                        lemma_map=invalid,
                        attempts=[candidate_attempt()],
                        max_attempts=1,
                    )

    def test_digest_detects_rewriting_retained_history(self) -> None:
        statement = confirmed_statement()
        run = run_math_proof(
            statement=statement,
            actor_principal="project:proof-author",
            examples=[],
            counterexamples=[],
            lemma_map=lemma_map(),
            attempts=[candidate_attempt()],
            max_attempts=1,
        )
        changed = copy.deepcopy(run)
        changed["attempts"][0]["argument"] = "silently rewritten"
        self.assertIn(
            "proof.digest",
            [issue.code for issue in validate_math_proof(changed, statement=statement)],
        )


if __name__ == "__main__":
    unittest.main()
