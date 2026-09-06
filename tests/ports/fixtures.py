"""Only locally authored test bytes. NEVER a community port or release candidate.

Accepted cases always retain fixture-only/not-shippable origin, a reserved URL,
a synthetic all-zero commit, fixture reviewer, and a non-shipping LicenseRef.
Negative cases are mutations of these fixtures, never accepted external ports.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research_os.validation.ports import tree_digest

MARKER = "fixture-only/not-shippable"


def write_json(root: Path, path: str, value: object) -> dict[str, str]:
    return write_bytes(root, path, (json.dumps(value, sort_keys=True, indent=2) + "\n").encode())


def write_bytes(root: Path, path: str, data: bytes) -> dict[str, str]:
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return {"path": path, "sha256": hashlib.sha256(data).hexdigest()}


def sign_decision(root: Path, manifest: dict) -> None:
    decision_bundle = {
        key: manifest[key]
        for key in (
            "contract", "id", "origin", "source", "licensing", "snapshot", "baseline",
            "adapted", "original", "ledger", "evaluation", "review", "decision",
            "decision_principal", "product",
        )
    }
    admission_digest = hashlib.sha256(json.dumps(decision_bundle, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    decision_receipt = {
        "port_id": manifest["id"], "principal": manifest["decision_principal"],
        "decision": manifest["decision"], "reviewed_at": manifest["review"]["reviewed_at"],
        "product": manifest["product"], "admission_digest": admission_digest,
    }
    manifest["decision_evidence"] = write_json(root, "evidence/decision.json", decision_receipt)


def fixture(root: Path, decision: str = "adapt") -> dict:
    prefix = (MARKER + "\nLocal Research OS test bytes, not external repository code.\n").encode()
    before = {"unit.txt": prefix + b"baseline behavior\n", "keep.txt": prefix + b"unchanged\n",
              "delete.txt": prefix + b"removed\n"}
    after = before if decision == "preserve" else {
        "unit.txt": prefix + b"adapted behavior\n", "keep.txt": before["keep.txt"],
        "add.txt": prefix + b"added\n",
    }
    trees = {}
    for name, files in (("snapshot", before), ("baseline", before), ("adapted", after)):
        entries = []
        for path, data in sorted(files.items()):
            entry = write_bytes(root, f"evidence/{name}/{path}", data)
            entries.append({"path": path, "sha256": entry["sha256"]})
        trees[name] = {"path": f"evidence/{name}", "files": entries}
    source = {"status": "available", "url": "https://research-os.invalid/fixtures/local-only",
              "commit": "0" * 40, "path": "tests/ports/local-authored",
              "retrieved_at": "2026-09-06T00:00:00Z"}
    receipt = {key: source[key] for key in ("url", "commit", "path", "retrieved_at")}
    receipt.update({"origin": MARKER, "snapshot_sha256": tree_digest(trees["snapshot"]["files"])})
    source["evidence"] = write_json(root, "evidence/source.json", receipt)
    licensing = {
        "status": "available", "spdx": "LicenseRef-ResearchOS-Fixture-Only",
        "license": write_bytes(root, "evidence/LICENSE", prefix + b"Local test use only; not a third-party license.\n"),
        "notice": {"status": "included", "file": write_bytes(root, "evidence/NOTICE", prefix + b"Authored only for admission validator tests.\n")},
    }
    ledger = []
    for path in sorted(before.keys() | after.keys()):
        action = "add" if path not in before else "delete" if path not in after else "keep" if before[path] == after[path] else "modify"
        ledger.append({"action": action, "path": path, "reason": f"Locally authored {action} fixture"})
    evaluation = {
        "harness": write_bytes(root, "evidence/harness.txt", prefix + b"Stored receipt shape fixture; NOT an executed community evaluation.\n"),
        "environment": write_bytes(root, "evidence/environment.txt", prefix + b"Deterministic local receipt-fixture environment.\n"),
        "baseline": [], "adapted": [],
    }
    for index, side in enumerate(("baseline", "adapted")):
        for repetition in range(2):
            run = {"run_id": f"{side}-{repetition + 1}", "executed_at": f"2026-09-06T00:00:0{index * 2 + repetition + 1}Z",
                   "subject_sha256": tree_digest(trees[side]["files"]), "result": "pass"}
            receipt = dict(run, side=side, harness_sha256=evaluation["harness"]["sha256"],
                           environment_sha256=evaluation["environment"]["sha256"], origin=MARKER)
            detail = {
                "contract": {"name": "research-os/port-evaluation-detail", "version": "1.0.0"},
                "kind": "fixture-shape",
                "subject_sha256": run["subject_sha256"],
                "tree_sha256": run["subject_sha256"],
                "result": run["result"],
                "checks": [{"name": "fixture-shape", "pass": True}],
            }
            run["detail"] = write_json(root, f"evidence/evals/{run['run_id']}-detail.json", detail)
            run["evidence"] = write_json(root, f"evidence/evals/{run['run_id']}.json", receipt)
            evaluation[side].append(run)
    manifest = {
        "contract": {"name": "research-os/port", "version": "1.0.0"},
        "id": "local-test-port", "origin": MARKER, "source": source, "licensing": licensing,
        **trees, "original": {"behavior": write_bytes(root, "evidence/behavior.txt", prefix + b"Original baseline emits the baseline text.\n"), "dependencies": []},
        "ledger": ledger, "evaluation": evaluation,
        "review": {"principal": "fixture:local-reviewer", "reviewed_at": "2026-09-06T00:00:05Z", "rationale": "Local validator fixture only, not actual external review."},
        "decision": decision,
        "decision_principal": "person:local-fixture-owner",
        "decision_evidence": {"path": "evidence/decision.json", "sha256": "0" * 64},
        "product": None if decision == "reject" else write_bytes(root, "products/local-test.txt", after["unit.txt"]),
    }
    sign_decision(root, manifest)
    save(root, manifest)
    write_json(root, "inventory.json", {"contract": {"name": "research-os/port-inventory", "version": "1.0.0"}, "manifests": ["PORT.json"]})
    return manifest


def save(root: Path, manifest: dict) -> None:
    write_json(root, "PORT.json", manifest)


def release(root: Path, manifest: dict) -> dict:
    product = manifest["product"] or {"path": "products/rejected.txt", "sha256": "0" * 64}
    value = {"contract": {"name": "research-os/port-release", "version": "1.0.0"},
             "products": [product], "allowlist": [{"port_id": manifest["id"], **product}]}
    write_json(root, "release.json", value)
    return value
