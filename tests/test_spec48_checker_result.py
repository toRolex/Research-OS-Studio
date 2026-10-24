"""A-F1: existing positive nodes must reject real crashes and malformed reports."""
import importlib
import subprocess
import sys
import unittest
from unittest.mock import patch

from spec48_checker_result import parse_checker_result

GREEN_NODES = {
    49: ("CounterRelationship", "test_current_tree_has_no_new_breakage"),
    50: ("EntryDiscovery", "test_full_checker_green_with_no_new_failures"),
    51: ("ArenaCheckerRegressionTests", "test_current_tree_has_no_new_breakage"),
    54: ("Registration", "test_current_tree_has_no_new_breakage"),
    56: ("CheckerContract", "test_builtin_checker_registers_ticket56_contract"),
    57: ("MigrationContract", "test_checker_adds_no_new_problem_beyond_recorded_historical_breaks"),
    58: ("CheckerCounterexamples", "test_current_tree_has_no_new_breakage"),
}
OK = "OK: 41 个 Skill（U 40 / M 1），调用策略与门声明通过\n"


class CheckerResultBoundaries(unittest.TestCase):
    def test_valid_failure_preserves_target_diagnostic(self):
        diagnostic = "  - skills/example/SKILL.md: target contract missing"
        result = subprocess.CompletedProcess([], 1, f"FAIL: 1 个问题\n{diagnostic}\n", "")
        self.assertEqual(parse_checker_result(result), [diagnostic])

    def test_malformed_failure_is_not_a_counterexample_result(self):
        for output in (
            "", "FAIL: 0 个问题\n", "FAIL: 2 个问题\n  - only one\n",
            "FAIL: 1 个问题\nmissing diagnostic prefix\n",
            "HISTORY PASS: fake.tar.gz\nFAIL: 1 个问题\n  - target\n",
        ):
            with self.subTest(output=output), self.assertRaises(AssertionError):
                parse_checker_result(subprocess.CompletedProcess([], 1, output, ""))

    def test_only_explicit_history_status_grammar_is_ignored(self):
        history = "HISTORY UNVERIFIED: example.tar.gz (UNAVAILABLE; 摘要不认证来源/安全)\n"
        self.assertEqual(parse_checker_result(subprocess.CompletedProcess([], 0, history + OK, "")), [])

    def run_original_node(self, ticket, result):
        module = importlib.import_module(f"test_spec48_ticket{ticket}")
        cls, name = GREEN_NODES[ticket]
        case = getattr(module, cls)(name)
        with patch.object(module.subprocess, "run", return_value=result):
            getattr(case, name)()

    def test_seven_positive_nodes_reject_a_real_python_crash(self):
        crash = subprocess.run(
            [sys.executable, "-c", "raise RuntimeError('checker crashed before checking')"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(crash.returncode, 1)
        self.assertEqual(crash.stdout, "")
        self.assertIn("Traceback", crash.stderr)
        for ticket in GREEN_NODES:
            with self.subTest(ticket=ticket), self.assertRaises(AssertionError):
                self.run_original_node(ticket, crash)

    def test_seven_positive_nodes_reject_incomplete_or_failed_reports(self):
        for code, stdout, stderr in (
            (0, "", ""), (0, "OK: fake\n", ""), (0, OK, "unexpected stderr"),
            (1, "", ""), (1, "FAIL: 0 个问题\n", ""),
            (1, "FAIL: 1 个问题\n  - target contract missing\n", ""),
            (2, OK, ""), (-9, "", ""),
        ):
            result = subprocess.CompletedProcess([], code, stdout, stderr)
            for ticket in GREEN_NODES:
                with self.subTest(ticket=ticket, code=code, stdout=stdout), self.assertRaises(AssertionError):
                    self.run_original_node(ticket, result)

    def test_seven_positive_nodes_accept_a_normal_structure_report(self):
        result = subprocess.CompletedProcess([], 0, OK, "")
        for ticket in GREEN_NODES:
            with self.subTest(ticket=ticket):
                self.run_original_node(ticket, result)
