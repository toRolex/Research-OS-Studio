"""Count every discovered test; emit durable inventory and actual execution totals.

Usage: uv run --frozen python tests/e2e/run_suite.py [--e2e | --collect-only]
       --output /absolute/evidence/directory
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


class CountingResult(unittest.TextTestResult):
    """Count successful callbacks, not method count minus subtest events."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_count = 0
        self.failed_subtests = 0
        self.fixture_errors = 0
        self._started = set()
        self._failed = set()

    @property
    def failed_methods(self):
        return len(self._failed)

    def startTest(self, test):
        self._started.add(test.id())
        super().startTest(test)

    def addSuccess(self, test):
        self.passed_count += 1
        super().addSuccess(test)

    def addFailure(self, test, err):
        self._failed.add(test.id())
        super().addFailure(test, err)

    def addError(self, test, err):
        if test.id() in self._started:
            self._failed.add(test.id())
        else:
            self.fixture_errors += 1
        super().addError(test, err)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.failed_subtests += 1
            self._failed.add(test.id())
        super().addSubTest(test, subtest, err)


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--e2e", action="store_true")
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-output", type=Path)
    args = parser.parse_args()
    if args.reference_output is not None:
        os.environ["RESEARCH_OS_E2E_OUTPUT"] = str(args.reference_output.resolve())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    all_tests = list(flatten(suite))
    all_ids = [test.id() for test in all_tests]
    modules = {test.__class__.__module__ for test in all_tests}
    expected = {".".join(path.relative_to(ROOT).with_suffix("").parts)
                for path in (ROOT / "tests").rglob("test*.py")}
    errors = [*loader.errors]
    if expected - modules:
        errors.append("omitted modules: " + ", ".join(sorted(expected - modules)))
    if len(all_ids) != len(set(all_ids)):
        errors.append("duplicate test IDs")
    if len(all_tests) < 371:
        errors.append("collection below the 371-test integration baseline")
    inventory = {"collected": len(all_tests), "test_files": len(expected),
                 "test_ids": all_ids, "collection_errors": errors}
    (output / "collection.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(json.dumps({key: value for key, value in inventory.items() if key != "test_ids"}), flush=True)
    if errors:
        return 1
    if args.collect_only:
        return 0
    selected = [test for test in all_tests if not args.e2e or test.id().startswith("tests.e2e.")]
    result = unittest.TextTestRunner(verbosity=2, resultclass=CountingResult).run(unittest.TestSuite(selected))
    summary = {"collected": len(all_tests), "selected": len(selected), "executed": result.testsRun,
               "passed": result.passed_count, "failed_methods": result.failed_methods,
               "failed_subtests": result.failed_subtests, "fixture_errors": result.fixture_errors,
               "failures": len(result.failures), "errors": len(result.errors),
               "skipped": [{"test": test.id(), "reason": reason} for test, reason in result.skipped],
               "expected_failures": len(result.expectedFailures), "unexpected_successes": len(result.unexpectedSuccesses),
               "release_authorized": False,
               "note": "Test success is not repository/ports/Lean/host release acceptance; inspect independent gates."}
    (output / "results.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if result.wasSuccessful() and result.testsRun == len(selected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
