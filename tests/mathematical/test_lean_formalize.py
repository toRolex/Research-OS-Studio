from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.workflows.mathematical import (  # noqa: E402
    CommandResult,
    MathematicalWorkflowError,
    confirm_statement,
    create_independent_review,
    create_statement_candidate,
    run_lean_formalize,
    run_math_proof,
)
from research_os.workflows.mathematical.lean import extract_declaration_statement  # noqa: E402

BOUNDARY = "Kernel pass covers only the fixed Lean statement in the recorded trusted base; it does not establish natural-language alignment, paper correctness, research significance, or human acceptance."


def records() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    statement = create_statement_candidate(
        revision=1,
        quantifiers=["for every n"],
        hypotheses=[],
        domain="natural numbers",
        conclusion="n + 0 = n",
        rationale="Lean test.",
    )
    statement = confirm_statement(
        statement,
        principal="project:user",
        confirmation=f"CONFIRM STATEMENT r1 {statement['semantic_digest']}",
    )
    proof = run_math_proof(
        statement=statement,
        actor_principal="project:author",
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
                "approach": "identity",
                "argument": "Apply identity.",
                "outcome": "candidate-proof",
                "gaps": [],
            }
        ],
        max_attempts=1,
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name, value in (("statement.json", statement), ("proof.json", proof)):
            (root / name).write_text(
                json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        review = create_independent_review(
            project_root=root,
            statement=statement,
            proof=proof,
            reviewer_principal="project:reviewer",
            input_paths=["statement.json", "proof.json"],
            input_digests=[
                hashlib.sha256((root / name).read_bytes()).hexdigest()
                for name in ("statement.json", "proof.json")
            ],
            findings=[],
            verdict="pass",
        )
    return statement, proof, review


def write_project(
    root: Path,
    statement: dict[str, object],
    proof: dict[str, object],
    review: dict[str, object],
    *,
    solution_statement: str = "∀ n : Nat, n + 0 = n",
) -> dict[str, object]:
    for name, value in (("statement.json", statement), ("proof.json", proof)):
        (root / name).write_text(
            json.dumps(value, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    (root / "ResearchOSMath").mkdir(parents=True)
    trusted = "theorem fixed : ∀ n : Nat, n + 0 = n := by\n  intro n\n  exact Nat.add_zero n\n"
    solution = f"theorem fixed : {solution_statement} := by\n  intro n\n  exact Nat.add_zero n\n\n#print axioms fixed\n"
    (root / "ResearchOSMath/Challenge.lean").write_text(trusted, encoding="utf-8")
    (root / "ResearchOSMath/Solution.lean").write_text(solution, encoding="utf-8")
    (root / "lean-toolchain").write_text("leanprover/lean4:v4.19.0\n", encoding="utf-8")
    normalized = extract_declaration_statement(trusted, "fixed")
    metadata = {
        "contract": {"name": "research-os/lean-formalization", "version": "1.0.0"},
        "statement": {
            "revision": statement["revision"],
            "semantic_digest": statement["semantic_digest"],
        },
        "proof": {"run_digest": proof["run_digest"]},
        "review": {"review_digest": review["review_digest"]},
        "authorization": {
            "principal": "project:user",
            "revision": statement["revision"],
            "statement_digest": statement["semantic_digest"],
            "phrase": f"AUTHORIZE LEAN r1 {statement['semantic_digest']}",
        },
        "toolchain": {
            "lean": "leanprover/lean4:v4.19.0",
            "lake": "Lake version 5.0.0",
            "file": "lean-toolchain",
        },
        "dependencies": [],
        "sources": [
            {
                "path": "ResearchOSMath/Challenge.lean",
                "sha256": hashlib.sha256(trusted.encode()).hexdigest(),
            },
            {
                "path": "ResearchOSMath/Solution.lean",
                "sha256": hashlib.sha256(solution.encode()).hexdigest(),
            },
        ],
        "allowed_imports": [],
        "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"],
        "comparator": {
            "trusted_file": "ResearchOSMath/Challenge.lean",
            "solution_file": "ResearchOSMath/Solution.lean",
            "declaration": "fixed",
            "normalized_statement_sha256": __import__(
                "research_os.workflows.mathematical", fromlist=["canonical_digest"]
            ).canonical_digest(normalized),
        },
        "replay": {
            "command": ["lake", "build"],
            "independent_principal": "project:kernel-replayer",
        },
        "claim_boundary": BOUNDARY,
    }
    metadata["sources"].append(
        {
            "path": "lean-toolchain",
            "sha256": hashlib.sha256(
                (root / "lean-toolchain").read_bytes()
            ).hexdigest(),
        }
    )
    (root / "formalization.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


class LeanFormalizeTests(unittest.TestCase):
    def test_review_fail_and_inconclusive_block_before_tooling(self) -> None:
        from research_os.workflows.mathematical import canonical_digest

        for verdict in ("fail", "inconclusive"):
            with (
                self.subTest(verdict=verdict),
                tempfile.TemporaryDirectory() as directory,
            ):
                statement, proof, review = records()
                review["verdict"] = verdict
                review["review_digest"] = canonical_digest(
                    {
                        key: value
                        for key, value in review.items()
                        if key != "review_digest"
                    }
                )
                project = Path(directory)
                write_project(project, statement, proof, review)
                result = run_lean_formalize(
                    project=project,
                    statement=statement,
                    proof=proof,
                    review=review,
                    runner=lambda *args, **kwargs: self.fail(
                        "review rejection must precede tooling"
                    ),
                )
                self.assertEqual(result.exit_code, 1)
                self.assertEqual(result.report["result"], "not-verified")
                self.assertIn(
                    "lean.review.verdict",
                    {issue["code"] for issue in result.report["issues"]},
                )

    def test_prerequisites_require_confirmed_statement_candidate_proof_and_review(
        self,
    ) -> None:
        statement, proof, review = records()
        unconfirmed = dict(statement)
        unconfirmed["confirmation"] = None
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_project(project, statement, proof, review)
            with self.assertRaises(MathematicalWorkflowError):
                run_lean_formalize(
                    project=project, statement=unconfirmed, proof=proof, review=review
                )
            gap = dict(proof)
            gap["result"] = "proof-gap"
            gap["run_digest"] = __import__(
                "research_os.workflows.mathematical", fromlist=["canonical_digest"]
            ).canonical_digest(
                {key: value for key, value in gap.items() if key != "run_digest"}
            )
            with self.assertRaises(MathematicalWorkflowError):
                run_lean_formalize(
                    project=project, statement=statement, proof=gap, review=review
                )

    def test_explicit_authorization_is_exact_and_stale_authorization_fails(
        self,
    ) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            metadata["authorization"]["phrase"] = "yes"
            (project / "formalization.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            result = run_lean_formalize(
                project=project, statement=statement, proof=proof, review=review
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.report["result"], "not-verified")
            self.assertIn(
                "lean.authorization",
                [issue["code"] for issue in result.report["issues"]],
            )

    def test_statement_mismatch_is_distinct_from_kernel_not_verified(self) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_project(
                project,
                statement,
                proof,
                review,
                solution_statement="∀ n : Nat, 0 + n = n",
            )
            result = run_lean_formalize(
                project=project, statement=statement, proof=proof, review=review
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.report["result"], "statement-mismatch")
            self.assertEqual(result.report["stop_reason"], "workflow-complete")

    def test_source_revisions_are_bounded_and_cannot_replace_locked_sources(
        self,
    ) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            with self.assertRaises(MathematicalWorkflowError):
                run_lean_formalize(
                    project=project,
                    statement=statement,
                    proof=proof,
                    review=review,
                    max_attempts=1,
                    candidate_source_revisions=[
                        {"id": "a", "sources": {}},
                        {"id": "b", "sources": {}},
                    ],
                )
            result = run_lean_formalize(
                project=project,
                statement=statement,
                proof=proof,
                review=review,
                max_attempts=1,
                candidate_source_revisions=[
                    {
                        "id": "replacement",
                        "sources": {"ResearchOSMath/Solution.lean": "0" * 64},
                    }
                ],
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.report["stop_reason"], "execution-failed")
            self.assertIn(
                "lean.source.revision",
                [issue["code"] for issue in result.report["issues"]],
            )
            self.assertEqual(
                metadata["statement"]["semantic_digest"], statement["semantic_digest"]
            )

    def test_failed_single_candidate_with_unused_budget_is_execution_failure(
        self,
    ) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_project(project, statement, proof, review)
            bin_dir = project / "bin"
            bin_dir.mkdir()
            for name in ("lean", "lake"):
                executable = bin_dir / name
                executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                executable.chmod(0o755)

            def runner(argv, *, cwd, env=None, timeout=120):
                if argv[-1] == "--version" and Path(argv[0]).name == "lean":
                    return CommandResult(
                        tuple(argv),
                        str(cwd),
                        0,
                        "Lean (version leanprover/lean4:v4.19.0)\n",
                        "",
                    )
                if argv[-1] == "--version":
                    return CommandResult(
                        tuple(argv), str(cwd), 0, "Lake version 5.0.0\n", ""
                    )
                return CommandResult(tuple(argv), str(cwd), 1, "", "build failed")

            result = run_lean_formalize(
                project=project,
                statement=statement,
                proof=proof,
                review=review,
                max_attempts=3,
                runner=runner,
                environment={"PATH": str(bin_dir)},
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.report["stop_reason"], "execution-failed")
            self.assertEqual(
                result.report["budget"], {"max_attempts": 3, "attempts_used": 1}
            )

    def test_real_lake_version_commit_suffix_is_accepted(self) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_project(project, statement, proof, review)
            bin_dir = project / "bin"
            bin_dir.mkdir()
            for name in ("lean", "lake"):
                executable = bin_dir / name
                executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                executable.chmod(0o755)

            def runner(argv, *, cwd, env=None, timeout=120):
                if argv[-1] == "--version" and Path(argv[0]).name == "lean":
                    stdout = "Lean (version 4.19.0, fixture)\n"
                elif argv[-1] == "--version":
                    stdout = "Lake version 5.0.0-6caaee8 (Lean version 4.19.0)\n"
                elif str(argv[-1]).endswith("Probe.lean"):
                    stdout = 'ROS_TYPE_JSON:"forall Nat Eq Nat.add"\nROS_CONSTANTS_JSON:["Nat","Nat.add","Eq"]\n\'fixed\' does not depend on any axioms\n'
                else:
                    stdout = "Build completed successfully.\n"
                return CommandResult(tuple(argv), str(cwd), 0, stdout, "")

            result = run_lean_formalize(
                project=project,
                statement=statement,
                proof=proof,
                review=review,
                runner=runner,
                environment={"PATH": str(bin_dir)},
            )
            self.assertEqual(result.exit_code, 0, result.report)
            self.assertEqual(result.report["result"], "verified")

    def test_malformed_lake_version_suffixes_fail_closed(self) -> None:
        invalid_versions = (
            "Lake version 5.0.1-6caaee8 (Lean version 4.19.0)",
            "Lake version 5.0.0-6caaee (Lean version 4.19.0)",
            "Lake version 5.0.0-6CAAEE8 (Lean version 4.19.0)",
            "Lake version 5.0.0-rc1 (Lean version 4.19.0)",
            "Lake version 5.0.0-6caaee8 (Lean version 4.18.0)",
            "Lake version 5.0.0-6caaee8 (unexpected metadata)",
            "Lake version 5.0.0-6caaee8 trailing text",
        )
        for lake_version in invalid_versions:
            with (
                self.subTest(lake_version=lake_version),
                tempfile.TemporaryDirectory() as directory,
            ):
                statement, proof, review = records()
                project = Path(directory)
                write_project(project, statement, proof, review)
                bin_dir = project / "bin"
                bin_dir.mkdir()
                for name in ("lean", "lake"):
                    executable = bin_dir / name
                    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                    executable.chmod(0o755)

                def runner(argv, *, cwd, env=None, timeout=120):
                    if argv[-1] != "--version":
                        self.fail("invalid Lake version must block before build")
                    stdout = (
                        "Lean (version 4.19.0, fixture)\n"
                        if Path(argv[0]).name == "lean"
                        else f"{lake_version}\n"
                    )
                    return CommandResult(tuple(argv), str(cwd), 0, stdout, "")

                result = run_lean_formalize(
                    project=project,
                    statement=statement,
                    proof=proof,
                    review=review,
                    runner=runner,
                    environment={"PATH": str(bin_dir)},
                )
                self.assertEqual(result.exit_code, 3)
                self.assertEqual(result.report["stop_reason"], "tooling-blocked")
                self.assertIn(
                    "lean.lake.runtime",
                    {issue["code"] for issue in result.report["issues"]},
                )

    def test_successful_chain_records_build_axioms_and_independent_replay(self) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_project(project, statement, proof, review)
            bin_dir = project / "bin"
            bin_dir.mkdir()
            for name in ("lean", "lake"):
                executable = bin_dir / name
                executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                executable.chmod(0o755)

            calls: list[tuple[str, ...]] = []

            def runner(argv, *, cwd, env=None, timeout=120):
                calls.append(tuple(argv))
                if argv[-1] == "--version" and Path(argv[0]).name == "lean":
                    stdout = "Lean (version leanprover/lean4:v4.19.0)\n"
                elif argv[-1] == "--version":
                    stdout = "Lake version 5.0.0\n"
                elif str(argv[-1]).endswith("Probe.lean"):
                    stdout = 'ROS_TYPE_JSON:"forall Nat Eq Nat.add"\nROS_CONSTANTS_JSON:["Nat","Nat.add","Eq"]\n\'fixed\' does not depend on any axioms\n'
                elif any(str(item).endswith("Solution.lean") for item in argv):
                    stdout = "'fixed' does not depend on any axioms\n"
                else:
                    stdout = "Build completed successfully.\n"
                return CommandResult(tuple(argv), str(cwd), 0, stdout, "")

            result = run_lean_formalize(
                project=project,
                statement=statement,
                proof=proof,
                review=review,
                runner=runner,
                environment={"PATH": str(bin_dir)},
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.report["result"], "verified")
            self.assertEqual(result.report["verdict"], "pass")
            self.assertEqual(
                result.report["kernel_replay"]["principal"], "project:kernel-replayer"
            )
            receipt = result.report["kernel_replay"]
            self.assertEqual(receipt["project_digest"], receipt["input_digest"])
            self.assertEqual(receipt["input_digest"], receipt["output_digest"])
            self.assertTrue(receipt["tooling"]["available"])
            self.assertEqual(result.report["claim_boundary"], BOUNDARY)
            digest_input = dict(result.report)
            report_digest = digest_input.pop("report_digest")
            self.assertEqual(
                report_digest,
                __import__(
                    "research_os.workflows.mathematical", fromlist=["canonical_digest"]
                ).canonical_digest(digest_input),
            )
            self.assertGreaterEqual(
                sum(
                    1
                    for call in calls
                    if call[-2:] == ("lake", "build") or call[-1] == "build"
                ),
                2,
            )


if __name__ == "__main__":
    unittest.main()
