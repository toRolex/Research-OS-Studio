from __future__ import annotations

import os
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.workflows.mathematical import run_lean_formalize  # noqa: E402
from tests.mathematical.test_lean_formalize import records, write_project  # noqa: E402


class BlockedSemanticsTests(unittest.TestCase):
    def test_missing_lean_and_lake_are_structured_blocked_exit_three(self) -> None:
        statement, proof, review = records()
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            project = Path(directory)
            write_project(project, statement, proof, review)
            empty_path = project / "empty-bin"
            empty_path.mkdir()
            result = run_lean_formalize(
                project=project,
                statement=statement,
                proof=proof,
                review=review,
                environment={"PATH": str(empty_path)},
            )
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.report["verdict"], "blocked")
            self.assertEqual(result.report["result"], "not-verified")
            self.assertEqual(result.report["stop_reason"], "tooling-blocked")
            self.assertEqual(
                result.report["issues"][0]["code"], "lean.tooling.unavailable"
            )

    def test_version_mismatch_is_blocked_not_kernel_failure(self) -> None:
        statement, proof, review = records()
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            project = Path(directory)
            write_project(project, statement, proof, review)
            bin_dir = project / "bin"
            bin_dir.mkdir()
            for name in ("lean", "lake"):
                executable = bin_dir / name
                executable.write_text(
                    "#!/bin/sh\necho wrong-version\n", encoding="utf-8"
                )
                executable.chmod(0o755)
            result = run_lean_formalize(
                project=project,
                statement=statement,
                proof=proof,
                review=review,
                environment={"PATH": str(bin_dir)},
            )
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.report["stop_reason"], "tooling-blocked")
            self.assertIn(
                "lean.toolchain.runtime",
                [issue["code"] for issue in result.report["issues"]],
            )

    def test_ordinary_mathematical_tests_do_not_depend_on_system_lean(self) -> None:
        self.assertIsInstance(shutil.which("lean"), (str, type(None)))
        self.assertIsInstance(shutil.which("lake"), (str, type(None)))
        required = os.environ.get("RESEARCH_OS_REQUIRE_LEAN")
        self.assertIn(required, (None, "1"))
        if required == "1":
            self.assertIsNotNone(shutil.which("lean"))
            self.assertIsNotNone(shutil.which("lake"))


if __name__ == "__main__":
    unittest.main()
