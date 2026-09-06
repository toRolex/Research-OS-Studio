from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.workflows.mathematical import (  # noqa: E402
    audit_lean_project,
    compare_trusted_statement,
    run_lean_formalize,
    validate_independent_review,
    validate_math_proof,
    validate_statement,
)

PROJECT = ROOT / "reference-projects" / "mathematical"


def copy_fixture(target: Path) -> None:
    target.mkdir()
    for path in PROJECT.rglob("*"):
        if path.is_file() and ".lean-runs" not in path.parts:
            destination = target / path.relative_to(PROJECT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())


class ReferenceFixtureTests(unittest.TestCase):
    def test_fixed_records_and_static_audits_are_reproducible(self) -> None:
        statement = json.loads((PROJECT / "statement.json").read_text(encoding="utf-8"))
        proof = json.loads((PROJECT / "proof.json").read_text(encoding="utf-8"))
        review = json.loads((PROJECT / "review.json").read_text(encoding="utf-8"))
        metadata = json.loads(
            (PROJECT / "formalization.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_statement(statement, require_confirmed=True), [])
        self.assertEqual(validate_math_proof(proof, statement=statement), [])
        self.assertEqual(
            validate_independent_review(
                review, project_root=PROJECT, statement=statement, proof=proof
            ),
            [],
        )
        comparator, comparator_issues = compare_trusted_statement(PROJECT, metadata)
        self.assertEqual(comparator_issues, [])
        self.assertEqual(comparator["status"], "match")
        audit, audit_issues = audit_lean_project(PROJECT, metadata)
        self.assertEqual(audit_issues, [])
        self.assertEqual(audit["verdict"], "pass")
        manifest = PROJECT / "lake-manifest.json"
        self.assertTrue(manifest.is_file())
        self.assertIn(
            "lake-manifest.json",
            {source["path"] for source in metadata["sources"]},
        )

    def test_locked_manifest_tampering_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory) / "fixture"
            copy_fixture(runtime)
            manifest = runtime / "lake-manifest.json"
            manifest.write_text(
                manifest.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            metadata = json.loads(
                (runtime / "formalization.json").read_text(encoding="utf-8")
            )
            _, audit_issues = audit_lean_project(runtime, metadata)
            self.assertIn("lean.source.digest", {issue.code for issue in audit_issues})

    def test_release_mode_requires_real_lean_pass_and_local_mode_never_fakes_it(
        self,
    ) -> None:
        statement = json.loads((PROJECT / "statement.json").read_text(encoding="utf-8"))
        proof = json.loads((PROJECT / "proof.json").read_text(encoding="utf-8"))
        review = json.loads((PROJECT / "review.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory) / "fixture"
            copy_fixture(runtime)
            result = run_lean_formalize(
                project=runtime,
                statement=statement,
                proof=proof,
                review=review,
            )
        if os.environ.get("RESEARCH_OS_REQUIRE_LEAN") == "1":
            self.assertEqual(result.exit_code, 0, json.dumps(result.report, indent=2))
            self.assertEqual(result.report["result"], "verified")
            self.assertEqual(result.report["audit"]["verdict"], "pass")
            self.assertEqual(result.report["kernel_replay"]["verdict"], "pass")
            self.assertGreaterEqual(result.report["commands_recorded"], 8)
        else:
            self.assertIn(result.exit_code, {0, 3})
            if result.exit_code == 3:
                self.assertEqual(result.report["verdict"], "blocked")
                self.assertEqual(result.report["stop_reason"], "tooling-blocked")
                self.assertNotEqual(result.report["result"], "verified")
            else:
                self.assertEqual(result.report["result"], "verified")


if __name__ == "__main__":
    unittest.main()
