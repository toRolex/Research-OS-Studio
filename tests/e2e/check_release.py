"""Strict independent release gates; absent evidence never authorizes release."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
GATE_COMMANDS = (
    ("repository", ["research-os", "validate-repository", "--root", str(ROOT)]),
    ("ports", ["research-os", "validate-ports", "--root", str(ROOT)]),
    ("unified_manuscript_validator", ["python", "-m", "unittest", "tests.e2e.test_e2e_mathematical.MathematicalReleaseTests.test_e2e_mathematical_ordinary_proof_review_pdf_publication", "-v"]),
    ("lean", ["python", "-m", "unittest", "tests.e2e.test_e2e_mathematical.MathematicalReleaseTests.test_e2e_mathematical_real_lean_reports_blocked_or_verified", "-v"]),
)


def text(value):
    return value.decode(errors="replace") if isinstance(value, bytes) else value or ""


def evaluate_gates(output, commands=GATE_COMMANDS):
    """Retain partial evidence and continue independent gates after tool errors."""
    gates = {}
    for name, command in commands:
        try:
            result = subprocess.run(["uv", "run", "--frozen", *command], cwd=ROOT,
                                    env={**os.environ, "RESEARCH_OS_REQUIRE_LEAN": "1",
                                         "RESEARCH_OS_REQUIRE_MANUSCRIPT_CLI": "1"},
                                    capture_output=True, text=True, timeout=300)
            stdout, stderr = result.stdout, result.stderr
            status = "PASS" if result.returncode == 0 else "FAIL"
            if name == "lean" and "Release gate BLOCKED" in stderr:
                status = "BLOCKED"
            gates[name] = {"status": status, "exit_code": result.returncode}
        except (subprocess.TimeoutExpired, OSError) as exc:
            stdout = text(getattr(exc, "stdout", None))
            stderr = text(getattr(exc, "stderr", None))
            gates[name] = {"status": "ERROR", "exit_code": None,
                           "reason": f"{type(exc).__name__}: {exc}"}
        (output / f"{name}.stdout").write_text(stdout)
        (output / f"{name}.stderr").write_text(stderr)
    return gates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    gates = evaluate_gates(args.output)
    gates["ssh"] = {"status": "NOT_EVALUATED", "reason": "No declared real-environment lifecycle acceptance"}
    gates["slurm"] = {"status": "NOT_EVALUATED", "reason": "No declared real-environment lifecycle acceptance"}
    gates["live_host_execution"] = {"status": "BLOCKED", "reason": "No verified Claude Code / Codex isolation profile"}
    summary = {"release_authorized": False, "gates": gates}
    (args.output / "release-gates.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    # No publishing command or flag can waive remaining port/host/CLI gaps.
    return 1


if __name__ == "__main__":
    sys.exit(main())
