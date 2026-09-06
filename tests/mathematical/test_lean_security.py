from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_os.workflows.mathematical import (
    CommandResult,
    run_lean_formalize,
    audit_lean_project,
)
from tests.mathematical.test_lean_formalize import records, write_project


def fixture_runner(argv, *, cwd, env=None, timeout=120):
    if argv[-1] == "--version":
        text = (
            "Lean (version 4.19.0, fixture)"
            if Path(argv[0]).name == "lean"
            else "Lake version 5.0.0"
        )
    elif str(argv[-1]).endswith("Probe.lean"):
        text = 'ROS_TYPE_JSON:"forall Nat Eq Nat.add"\nROS_CONSTANTS_JSON:["Nat","Nat.add","Eq"]\n\'fixed\' does not depend on any axioms\n'
    else:
        text = "Build completed successfully."
    return CommandResult(tuple(argv), str(cwd), 0, text, "")


class LeanSecurityTests(unittest.TestCase):
    def execute(self, project, runner=fixture_runner, **kwargs):
        statement, proof, review = records()
        write_project(project, statement, proof, review)
        bin_dir = project / "bin"
        bin_dir.mkdir()
        for name in ("lean", "lake"):
            path = bin_dir / name
            path.write_text("#!/bin/sh\nexit 0\n")
            path.chmod(0o755)
        return run_lean_formalize(
            project=project,
            statement=statement,
            proof=proof,
            review=review,
            runner=runner,
            environment={"PATH": str(bin_dir)},
            **kwargs,
        )

    def test_kernel_types_not_lexical_statement_determine_alignment(self):
        with tempfile.TemporaryDirectory() as directory:

            def mismatch(argv, **kwargs):
                result = fixture_runner(argv, **kwargs)
                if "solution-Probe.lean" in str(argv[-1]):
                    return CommandResult(
                        result.argv,
                        result.cwd,
                        0,
                        result.stdout.replace("Nat.add", "evil.add"),
                        "",
                    )
                return result

            result = self.execute(Path(directory), mismatch)
            self.assertEqual(result.report["result"], "statement-mismatch")

    def test_axioms_must_belong_to_exact_target(self):
        with tempfile.TemporaryDirectory() as directory:

            def unrelated(argv, **kwargs):
                result = fixture_runner(argv, **kwargs)
                return CommandResult(
                    result.argv,
                    result.cwd,
                    result.returncode,
                    result.stdout.replace("'fixed'", "'unrelated'"),
                    result.stderr,
                )

            result = self.execute(Path(directory), unrelated)
            self.assertEqual(result.exit_code, 1)
            self.assertIn(
                "lean.axiom.output",
                {issue["code"] for issue in result.report["issues"]},
            )

    def test_build_mutation_cannot_be_restored_at_later_stage(self):
        with tempfile.TemporaryDirectory() as directory:

            def mutation(argv, **kwargs):
                result = fixture_runner(argv, **kwargs)
                if argv[-1] == "build":
                    (kwargs["cwd"] / "ResearchOSMath/Solution.lean").write_text(
                        "theorem fixed : True := by trivial\n"
                    )
                return result

            result = self.execute(Path(directory), mutation)
            self.assertEqual(result.exit_code, 1)
            self.assertNotEqual(result.report["result"], "verified")
            self.assertTrue(
                Path(result.report["history_path"], "command-0003.json").exists()
            )

    def test_history_is_append_only_and_snapshots_survive_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            result = self.execute(
                project,
                lambda argv, **kwargs: CommandResult(
                    tuple(argv), str(kwargs["cwd"]), 1, "", "failure"
                ),
            )
            history = Path(result.report["history_path"])
            before = {
                str(path): path.read_bytes()
                for path in history.rglob("*")
                if path.is_file()
            }
            statement, proof, review = records()
            second = run_lean_formalize(
                project=project,
                statement=statement,
                proof=proof,
                review=review,
                environment={"PATH": ""},
            )
            self.assertNotEqual(second.report["history_path"], str(history))
            self.assertEqual(
                before,
                {
                    str(path): path.read_bytes()
                    for path in history.rglob("*")
                    if path.is_file()
                },
            )
            self.assertTrue(
                (
                    history / "candidate-0001/source/ResearchOSMath/Solution.lean"
                ).is_file()
            )

    def test_isolated_probe_failure_cannot_inherit_original_success(self):
        with tempfile.TemporaryDirectory() as directory:
            origin = Path(directory).resolve()

            def isolated_failure(argv, **kwargs):
                result = fixture_runner(argv, **kwargs)
                if (
                    str(argv[-1]).endswith("Probe.lean")
                    and kwargs["cwd"].resolve() != origin
                ):
                    return CommandResult(
                        result.argv, result.cwd, 1, "", "isolated kernel failure"
                    )
                return result

            result = self.execute(origin, isolated_failure)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.report["kernel_replay"]["verdict"], "fail")

    def test_equal_custom_type_names_are_not_semantic_equivalence(self):
        with tempfile.TemporaryDirectory() as directory:

            def custom(argv, **kwargs):
                result = fixture_runner(argv, **kwargs)
                return CommandResult(
                    result.argv,
                    result.cwd,
                    result.returncode,
                    result.stdout.replace('["Nat","Nat.add","Eq"]', '["CustomDomain"]'),
                    result.stderr,
                )

            result = self.execute(Path(directory), custom)
            self.assertEqual(result.exit_code, 1)
            self.assertIn(
                "lean.comparator.trusted_base",
                {issue["code"] for issue in result.report["issues"]},
            )

    def test_boolean_metadata_revisions_and_exit_codes_fail_closed(self):
        for field in ("statement", "authorization"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                metadata = write_project(project, *records())
                metadata[field]["revision"] = True
                _, issues = audit_lean_project(project, metadata)
                self.assertIn("lean.revision.type", {issue.code for issue in issues})
        with tempfile.TemporaryDirectory() as directory:

            def boolean_exit(argv, **kwargs):
                result = fixture_runner(argv, **kwargs)
                return CommandResult(
                    result.argv, result.cwd, False, result.stdout, result.stderr
                )

            result = self.execute(Path(directory), boolean_exit)
            self.assertEqual(result.exit_code, 1)
            self.assertNotEqual(result.report["result"], "verified")

    def test_unsupported_dependencies_and_compiled_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, *records())
            metadata["dependencies"] = [{"name": "external", "revision": "a" * 40}]
            path = project / "Cached.olean"
            path.write_bytes(b"compiled")
            metadata["sources"].append(
                {
                    "path": path.name,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
            _, issues = audit_lean_project(project, metadata)
            self.assertIn(
                "lean.dependencies.unsupported", {issue.code for issue in issues}
            )
            self.assertIn("lean.source.compiled", {issue.code for issue in issues})

    def test_unlisted_closure_is_retained_on_coverage_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            statement, proof, review = records()
            write_project(project, statement, proof, review)
            (project / "Hidden.lean").write_text(
                "theorem hidden : True := by trivial\n"
            )
            result = run_lean_formalize(
                project=project, statement=statement, proof=proof, review=review
            )
            self.assertEqual(result.exit_code, 1)
            self.assertTrue(
                Path(
                    result.report["history_path"], "submitted-source/Hidden.lean"
                ).is_file()
            )

    def test_dependency_manifest_cannot_disagree_with_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            metadata = write_project(project, *records())
            path = project / "lake-manifest.json"
            path.write_text(
                json.dumps(
                    {"packages": [{"name": "hidden", "type": "git", "rev": "a" * 40}]}
                )
            )
            metadata["sources"].append(
                {
                    "path": path.name,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
            _, issues = audit_lean_project(project, metadata)
            self.assertIn(
                "lean.dependencies.manifest", {issue.code for issue in issues}
            )


if __name__ == "__main__":
    unittest.main()
