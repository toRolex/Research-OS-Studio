from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.workflows.mathematical import (  # noqa: E402
    audit_lean_project,
    compare_trusted_statement,
    validate_formalization_metadata,
)
from tests.mathematical.test_lean_formalize import records, write_project  # noqa: E402


class LeanAuditTests(unittest.TestCase):
    def test_transitive_imports_and_build_sources_cannot_escape_lock_or_audit(
        self,
    ) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            solution = project / "ResearchOSMath/Solution.lean"
            solution.write_text("import ResearchOSMath.Helper\n" + solution.read_text())
            (project / "ResearchOSMath/Helper.lean").write_text(
                "import ResearchOSMath.Hidden Init\n"
            )
            (project / "ResearchOSMath/Hidden.lean").write_text(
                "axiom escape : False\ntheorem hidden : False := by sorry\n"
            )
            (project / "UnusedBuildTarget.lean").write_text(
                "axiom buildEscape : False\n"
            )
            metadata["allowed_imports"] = [
                "ResearchOSMath.Helper",
                "ResearchOSMath.Hidden",
            ]
            metadata["sources"][1]["sha256"] = (
                __import__("hashlib").sha256(solution.read_bytes()).hexdigest()
            )
            audit, issues = audit_lean_project(project, metadata)
            codes = {issue.code for issue in issues}
            self.assertIn("lean.sources.coverage", codes)
            self.assertIn("lean.sorry", codes)
            self.assertIn("lean.axiom.declared", codes)
            self.assertIn("lean.import", codes)
            self.assertTrue(
                {"ResearchOSMath/Hidden.lean", "UnusedBuildTarget.lean"}.issubset(
                    {source["path"] for source in audit["sources"]}
                )
            )

    def test_fixed_metadata_source_hashes_toolchain_and_comparator_validate(
        self,
    ) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            self.assertEqual(validate_formalization_metadata(project, metadata), [])
            comparator, issues = compare_trusted_statement(project, metadata)
            self.assertEqual(issues, [])
            self.assertEqual(comparator["status"], "match")
            audit, issues = audit_lean_project(project, metadata)
            self.assertEqual(issues, [])
            self.assertEqual(audit["verdict"], "pass")

    def test_sorry_admit_placeholder_and_unsafe_are_detected_outside_comments(
        self,
    ) -> None:
        statement, proof, review = records()
        tokens = (
            ("sorry", "sorry"),
            ("admit", "admit"),
            ("TODO", "placeholder"),
            ("unsafe", "unsafe"),
        )
        for token, expected in tokens:
            with self.subTest(token=token), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                metadata = write_project(project, statement, proof, review)
                path = project / "ResearchOSMath/Solution.lean"
                path.write_text(
                    path.read_text(encoding="utf-8") + f"\n{token}\n", encoding="utf-8"
                )
                metadata["sources"][1]["sha256"] = (
                    __import__("hashlib").sha256(path.read_bytes()).hexdigest()
                )
                _, issues = audit_lean_project(project, metadata)
                self.assertIn(f"lean.{expected}", [issue.code for issue in issues])
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            path = project / "ResearchOSMath/Solution.lean"
            path.write_text(
                path.read_text(encoding="utf-8") + "\n-- sorry TODO unsafe admit\n",
                encoding="utf-8",
            )
            metadata["sources"][1]["sha256"] = (
                __import__("hashlib").sha256(path.read_bytes()).hexdigest()
            )
            _, issues = audit_lean_project(project, metadata)
            self.assertFalse(
                {"lean.sorry", "lean.admit", "lean.placeholder", "lean.unsafe"}
                & {issue.code for issue in issues}
            )

    def test_unapproved_import_and_declared_axiom_fail_closed(self) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            path = project / "ResearchOSMath/Solution.lean"
            path.write_text(
                "import Mathlib\naxiom escape : False\n"
                + path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            metadata["sources"][1]["sha256"] = (
                __import__("hashlib").sha256(path.read_bytes()).hexdigest()
            )
            _, issues = audit_lean_project(project, metadata)
            codes = [issue.code for issue in issues]
            self.assertIn("lean.import", codes)
            self.assertIn("lean.axiom.declared", codes)

    def test_drifted_source_toolchain_dependency_and_claim_boundary_are_rejected(
        self,
    ) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            changed = copy.deepcopy(metadata)
            changed["sources"][0]["sha256"] = "0" * 64
            changed["toolchain"]["lean"] = "latest"
            changed["dependencies"] = [{"name": "mathlib", "revision": "main"}]
            changed["claim_boundary"] = "Lean proves the paper."
            codes = [
                issue.code
                for issue in validate_formalization_metadata(project, changed)
            ]
            self.assertIn("lean.source.digest", codes)
            self.assertIn("lean.toolchain.lock", codes)
            self.assertIn("lean.dependency.lock", codes)
            self.assertIn("lean.claim_boundary", codes)

    def test_metadata_rejects_paths_escaping_project(self) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            metadata["sources"][0]["path"] = "../outside.lean"
            issues = validate_formalization_metadata(project, metadata)
            self.assertIn("lean.source.path", [issue.code for issue in issues])

    def test_metadata_rejects_symlinked_sources_and_comparator_outside_lock(
        self,
    ) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            outside = project / "outside.lean"
            outside.write_text(
                (project / "ResearchOSMath/Challenge.lean").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            trusted = project / "ResearchOSMath/Challenge.lean"
            trusted.unlink()
            trusted.symlink_to(outside)
            codes = [
                issue.code
                for issue in validate_formalization_metadata(project, metadata)
            ]
            self.assertIn("lean.source.path", codes)
            metadata["comparator"]["trusted_file"] = "unlocked.lean"
            codes = [
                issue.code
                for issue in validate_formalization_metadata(project, metadata)
            ]
            self.assertIn("lean.comparator.source", codes)

    def test_metadata_rejects_custom_replay_command_fields(self) -> None:
        statement, proof, review = records()
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, statement, proof, review)
            metadata["replay"]["axiom_command"] = ["sh", "-c", "echo fake"]
            issues = validate_formalization_metadata(project, metadata)
            self.assertIn("lean.replay.config", [issue.code for issue in issues])


if __name__ == "__main__":
    unittest.main()
