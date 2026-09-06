#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Deterministic, offline text-discipline port evaluation.

This harness never executes upstream commands or code. It evaluates untrusted
source text and adapted canonical skill text as data against fixed safety and
research-control invariants.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

FORBIDDEN_UPSTREAM = (
    "allowed-tools:",
    "auto_proceed",
    "never stop",
)
REQUIRED_ADAPTED = (
    "Model-invoked discipline only.",
)
CONTROL_BOUNDARIES = (
    "budget",
    "accept",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(kind: str, subject: Path, expected_digest: str) -> dict[str, object]:
    raw = subject.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8")
    checks: list[dict[str, object]] = [
        {"name": "subject-digest", "pass": actual == expected_digest},
        {"name": "nonempty-utf8", "pass": bool(text.strip())},
    ]
    if kind == "baseline-text":
        checks.extend(
            [
                {"name": "substantive-procedure", "pass": len(text.splitlines()) >= 20},
                {"name": "research-operation", "pass": any(token in text.lower() for token in ("audit", "analy", "proof", "citation", "training", "system"))},
            ]
        )
    elif kind == "baseline-comparator":
        value = json.loads(text)
        checks.extend(
            [
                {"name": "fixed-modules", "pass": isinstance(value.get("challenge_module"), str) and isinstance(value.get("solution_module"), str)},
                {"name": "fixed-theorems", "pass": isinstance(value.get("theorem_names"), list) and len(value["theorem_names"]) >= 1 and len(set(value["theorem_names"])) == len(value["theorem_names"])},
                {"name": "axiom-allowlist", "pass": value.get("permitted_axioms") == ["propext", "Quot.sound", "Classical.choice"]},
            ]
        )
    elif kind == "adapted-discipline":
        lowered = text.lower()
        checks.extend(
            [
                {"name": "model-only-boundary", "pass": all(token in text for token in REQUIRED_ADAPTED)},
                {"name": "user-control-boundary", "pass": all(token in lowered for token in CONTROL_BOUNDARIES)},
                {"name": "no-upstream-provider-policy", "pass": not any(token in lowered for token in FORBIDDEN_UPSTREAM)},
                {"name": "structured-procedure", "pass": "## " in text and len(text.splitlines()) >= 15},
            ]
        )
    else:
        raise ValueError(f"unsupported evaluation kind: {kind}")
    return {
        "contract": {"name": "research-os/port-evaluation-detail", "version": "1.0.0"},
        "kind": kind,
        "subject_sha256": actual,
        "result": "pass" if all(item["pass"] for item in checks) else "fail",
        "checks": checks,
    }


def main() -> int:
    if len(sys.argv) != 6:
        raise SystemExit("usage: evaluate_port.py KIND SUBJECT EXPECTED_SHA256 TREE_SHA256 OUTPUT")
    kind, subject, expected_digest, tree_digest, output = sys.argv[1:]
    result = evaluate(kind, Path(subject), expected_digest)
    result["tree_sha256"] = tree_digest
    Path(output).write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
