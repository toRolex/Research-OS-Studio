from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.workflows.mathematical import (  # noqa: E402
    MathematicalWorkflowError,
    confirm_statement,
    create_independent_review,
    create_statement_candidate,
    revise_statement,
    run_math_proof,
    validate_independent_review,
)
from research_os.workflows.mathematical.records import canonical_digest  # noqa: E402


def records() -> tuple[dict[str, object], dict[str, object]]:
    statement = create_statement_candidate(
        revision=1,
        quantifiers=["for every n"],
        hypotheses=[],
        domain="natural numbers",
        conclusion="n + 0 = n",
        rationale="Review test.",
    )
    statement = confirm_statement(
        statement,
        principal="project:user",
        confirmation=f"CONFIRM STATEMENT r1 {statement['semantic_digest']}",
    )
    proof = run_math_proof(
        statement=statement,
        actor_principal="project:proof-author",
        examples=[],
        counterexamples=[],
        lemma_map=[
            {
                "id": "L1",
                "statement": "right identity",
                "depends_on": [],
                "status": "proved",
            }
        ],
        attempts=[
            {
                "id": "A1",
                "approach": "identity lemma",
                "argument": "Apply right identity.",
                "outcome": "candidate-proof",
                "gaps": [],
            }
        ],
        max_attempts=1,
    )
    return statement, proof


def rehash(review: dict[str, object]) -> None:
    review["isolation_receipt"]["input_manifest_digest"] = canonical_digest(
        review["isolation_receipt"]["inputs"]
    )
    review["review_digest"] = canonical_digest(
        {key: value for key, value in review.items() if key != "review_digest"}
    )


class MathReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.statement, self.proof = records()
        self.paths = ["statement.json", "proof.json"]
        self.digests = []
        for path, record in zip(self.paths, (self.statement, self.proof), strict=True):
            data = (json.dumps(record, indent=2) + "\n").encode()
            (self.root / path).write_bytes(data)
            self.digests.append(hashlib.sha256(data).hexdigest())

    def create(self, **overrides: object) -> dict[str, object]:
        kwargs = dict(
            project_root=self.root,
            statement=self.statement,
            proof=self.proof,
            reviewer_principal="project:reviewer",
            input_paths=self.paths,
            input_digests=self.digests,
            findings=[],
            verdict="pass",
        )
        kwargs.update(overrides)
        return create_independent_review(**kwargs)

    def codes(self, review: object, **overrides: object) -> list[str]:
        kwargs = dict(
            project_root=self.root, statement=self.statement, proof=self.proof
        )
        kwargs.update(overrides)
        return [issue.code for issue in validate_independent_review(review, **kwargs)]

    def test_review_receipt_fixes_real_bytes_and_separates_acceptance(self) -> None:
        review = self.create()
        self.assertEqual(self.codes(review), [])
        receipt = review["isolation_receipt"]
        self.assertEqual(receipt["mode"], "fresh-context-fixed-inputs")
        self.assertIs(receipt["fresh_context"], True)
        self.assertIs(receipt["history_access"], False)
        self.assertFalse(receipt["conversation_history_included"])
        self.assertFalse(receipt["hidden_state_included"])
        self.assertEqual(receipt["reviewer_principal"], "project:reviewer")
        self.assertEqual(receipt["proof_actor_principal"], "project:proof-author")
        self.assertEqual(receipt["user_principal"], "project:user")
        self.assertEqual(receipt["statement_revision"], 1)
        self.assertEqual(receipt["statement_digest"], self.statement["semantic_digest"])
        self.assertEqual([item["sha256"] for item in receipt["inputs"]], self.digests)
        self.assertEqual(
            [item["role"] for item in receipt["inputs"]],
            ["statement", "candidate-proof"],
        )
        self.assertFalse(review["human_acceptance"])
        self.assertEqual(review["dimension"], "independent_review")

    def test_self_review_user_review_and_context_carryover_are_rejected(self) -> None:
        for principal in (
            "project:proof-author",
            " project:proof-author ",
            "project:user",
            " project:user ",
            "",
        ):
            with (
                self.subTest(principal=principal),
                self.assertRaises(MathematicalWorkflowError),
            ):
                self.create(reviewer_principal=principal)
        for policy in (
            dict(conversation_history_included=True),
            dict(hidden_state_included=True),
            dict(fresh_context=False),
            dict(history_access=True),
            dict(fresh_context=1),
            dict(history_access=0),
            dict(conversation_history_included=None),
        ):
            with (
                self.subTest(policy=policy),
                self.assertRaises(MathematicalWorkflowError),
            ):
                self.create(**policy)

    def test_manifest_requires_exact_existing_statement_and_proof(self) -> None:
        (self.root / "unrelated.json").write_text("{}")
        unrelated = hashlib.sha256(b"{}").hexdigest()
        for paths, digests in (
            (["statement.json"], self.digests[:1]),
            (["statement.json", "statement.json"], [self.digests[0]] * 2),
            (["statement.json", "missing.json"], self.digests),
            (["statement.json", "unrelated.json"], [self.digests[0], unrelated]),
            (self.paths + ["unrelated.json"], self.digests + [unrelated]),
            (self.paths, [self.statement["semantic_digest"], self.proof["run_digest"]]),
            (self.paths, ["g" * 64, self.digests[1]]),
            (self.paths, ["0" * 63, self.digests[1]]),
        ):
            with (
                self.subTest(paths=paths, digests=digests),
                self.assertRaises(MathematicalWorkflowError),
            ):
                self.create(input_paths=paths, input_digests=digests)

    def test_manifest_paths_reject_escape_aliases_symlinks_and_nonfiles(self) -> None:
        (self.root / "link.json").symlink_to(self.root / "statement.json")
        (self.root / "linked-dir").symlink_to(self.root, target_is_directory=True)
        (self.root / "directory").mkdir()
        for path in (
            str(self.root / "statement.json"),
            "../statement.json",
            "./statement.json",
            "a/../statement.json",
            "a//statement.json",
            "statement.json/",
            "statement.json#fragment",
            "statement.json?query",
            "C:\\statement.json",
            "link.json",
            "linked-dir/statement.json",
            "directory",
            "",
            " statement.json",
            "statement.json\x00",
        ):
            with self.subTest(path=path), self.assertRaises(MathematicalWorkflowError):
                self.create(input_paths=[path, "proof.json"])

    def test_validator_rechecks_actual_bytes_not_rehashed_manifest_claims(self) -> None:
        review = self.create()
        (self.root / "statement.json").write_text(json.dumps(self.statement))
        self.assertIn("review.inputs.bytes", self.codes(review))
        forged = copy.deepcopy(review)
        forged["isolation_receipt"]["inputs"][0]["sha256"] = hashlib.sha256(
            (self.root / "statement.json").read_bytes()
        ).hexdigest()
        rehash(forged)
        self.assertEqual(self.codes(forged), [])
        (self.root / "proof.json").unlink()
        self.assertIn("review.inputs.file", self.codes(forged))

    def test_rehashed_hostile_receipts_still_fail_validation(self) -> None:
        review = self.create()
        changes = (
            ("fresh_context", False),
            ("history_access", True),
            ("history_access", 0),
            ("reviewer_principal", "project:other"),
            ("proof_actor_principal", "project:other"),
            ("user_principal", "project:other"),
            ("statement_revision", 2),
            ("statement_digest", "0" * 64),
            ("unlisted_context", "history.json"),
        )
        for key, value in changes:
            with self.subTest(key=key, value=value):
                forged = copy.deepcopy(review)
                forged["isolation_receipt"][key] = value
                rehash(forged)
                self.assertTrue(self.codes(forged))
        for field, value in (
            ("path", "../statement.json"),
            ("sha256", "z" * 64),
            ("role", "candidate-proof"),
            ("revision", 2),
            ("target", {"kind": "git", "path": "other.json"}),
        ):
            with self.subTest(field=field):
                forged = copy.deepcopy(review)
                forged["isolation_receipt"]["inputs"][0][field] = value
                rehash(forged)
                self.assertTrue(self.codes(forged))

    def test_review_is_invalid_for_new_revision_including_same_semantics(self) -> None:
        review = self.create()
        revised = revise_statement(
            self.statement, domain="integers", rationale="User revision."
        )
        revised = confirm_statement(
            revised,
            principal="project:user",
            confirmation=f"CONFIRM STATEMENT r2 {revised['semantic_digest']}",
        )
        self.assertIn("review.subject", self.codes(review, statement=revised))
        same_semantics = copy.deepcopy(self.statement)
        same_semantics["revision"] = 2
        same_semantics["confirmation"] = None
        same_semantics = confirm_statement(
            same_semantics,
            principal="project:user",
            confirmation=f"CONFIRM STATEMENT r2 {same_semantics['semantic_digest']}",
        )
        self.assertIn("review.subject", self.codes(review, statement=same_semantics))
        changed = copy.deepcopy(self.proof)
        changed["run_digest"] = "0" * 64
        self.assertIn("review.subject", self.codes(review, proof=changed))

    def test_missing_subject_or_invalid_candidate_cannot_be_reviewed(self) -> None:
        review = self.create()
        self.assertIn("review.subject.missing", self.codes(review, statement=None))
        self.assertIn("review.subject.missing", self.codes(review, proof=None))
        proof = copy.deepcopy(self.proof)
        proof["lemma_map"][0]["status"] = "gap"
        with self.assertRaises(MathematicalWorkflowError):
            self.create(proof=proof)

    def test_boolean_proof_revision_cannot_alias_integer_statement_revision(
        self,
    ) -> None:
        self.proof["statement"]["revision"] = True
        self.proof["run_digest"] = canonical_digest(
            {key: value for key, value in self.proof.items() if key != "run_digest"}
        )
        data = json.dumps(self.proof).encode()
        (self.root / "proof.json").write_bytes(data)
        self.digests[1] = hashlib.sha256(data).hexdigest()
        with self.assertRaises(MathematicalWorkflowError) as raised:
            self.create()
        self.assertIn(
            "proof.statement", [issue.code for issue in raised.exception.issues]
        )

    def test_boolean_review_subject_revision_cannot_alias_fixed_revision(self) -> None:
        for revision in (True, False):
            with self.subTest(revision=revision):
                review = self.create()
                review["subject"]["statement_revision"] = revision
                rehash(review)
                self.assertIn("review.subject", self.codes(review))

    def test_receipt_or_findings_tampering_breaks_digest(self) -> None:
        review = self.create()
        review["isolation_receipt"]["conversation_history_included"] = True
        self.assertIn("review.isolation", self.codes(review))
        self.assertIn("review.digest", self.codes(review))


if __name__ == "__main__":
    unittest.main()
