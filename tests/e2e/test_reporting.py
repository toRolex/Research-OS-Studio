"""Fault injection tests reporting only, never real-tool release acceptance."""
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tests.e2e import check_release, run_suite


class ReportingAcceptanceTests(unittest.TestCase):
    def test_two_failed_subtests_do_not_produce_negative_pass_count(self):
        class Failing(unittest.TestCase):
            def test_subtests(self):
                for value in (1, 2):
                    with self.subTest(value=value):
                        self.fail("deliberate reporting fixture")

        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=run_suite.CountingResult).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Failing))
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(result.passed_count, 0)
        self.assertEqual(result.failed_methods, 1)
        self.assertEqual(result.failed_subtests, 2)

    def test_setup_class_error_is_not_counted_as_executed_or_passed(self):
        class BrokenFixture(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                raise RuntimeError("deliberate reporting fixture")

            def test_not_reached(self):
                raise AssertionError("must not execute")

        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=run_suite.CountingResult).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(BrokenFixture))
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(result.passed_count, 0)
        self.assertEqual(result.fixture_errors, 1)

    def test_gate_timeout_keeps_partial_logs_and_evaluates_following_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            timeout = subprocess.TimeoutExpired(["fixture"], 1, output=b"partial output", stderr=b"partial error")
            completed = subprocess.CompletedProcess(["fixture"], 0, "{}", "")
            with patch.object(check_release.subprocess, "run", side_effect=[timeout, completed]):
                gates = check_release.evaluate_gates(output, [("first", ["fixture"]), ("second", ["fixture"])])
            self.assertEqual(gates["first"]["status"], "ERROR")
            self.assertEqual(gates["second"]["status"], "PASS")
            self.assertEqual((output / "first.stdout").read_text(), "partial output")
            self.assertIn("TimeoutExpired", gates["first"]["reason"])


if __name__ == "__main__":
    unittest.main()
