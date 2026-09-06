"""Migrated walking-skeleton guarantees at the new application boundary."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from research_os.cli import CodexHostReceipt, run
from tests.integration.package_support import installed_cli
from research_os.core import (
    ApplicationFailure,
    DISCIPLINE_IDS,
    WORKFLOW_IDS,
    _verify_bundled_port_attestation,
)


def run_cli(*args, cwd=None, env=None):
    return subprocess.run([sys.executable, "-m", "research_os.cli", *args],
                          cwd=cwd or ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "src"), **(env or {})},
                          text=True, capture_output=True)


def report(result):
    return json.loads(result.stdout)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def charter_request(project, name="request.json"):
    value = {"contract": {"name": "research-os/artifact", "version": "1.1.0"},
             "target": {"kind": "git", "path": "question.json"},
             "type": {"name": "research-question", "version": "1.0.0"},
             "spec": {"question": "A fixed question", "boundaries": ["local only"],
                      "success_criteria": [], "budget": {}, "invariants": []}}
    write_json(project / "question.json", value)
    write_json(project / name, {"inputs": [{"path": "question.json", "sha256": hashlib.sha256((project / "question.json").read_bytes()).hexdigest()}]})


class WalkingSkeletonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"
        self.project.mkdir()

    def snapshot(self):
        return {p.relative_to(self.project).as_posix(): p.read_bytes()
                for p in self.project.rglob("*") if p.is_file()}

    def setup(self):
        result = installed_cli("setup-research-os", "--project", str(self.project))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def args(self, adapter=False):
        return (["adapter", "codex", "research-charter"] if adapter else ["research-charter"]) + [
            "--project", str(self.project), "--input", "request.json",
            "--output", "artifacts/charter.json", "--report", "reports/charter.json",
        ] + (["--confirm", "RUN research-charter"] if adapter else [])

    def host_run(self, host):
        stream = StringIO()
        with redirect_stdout(stream):
            code = run(self.args(True), codex_host=host)
        return code, json.loads(stream.getvalue())

    def test_setup_idempotent_all_workflows_no_runtime_or_lock(self):
        custom = self.project / ".claude/skills/research-charter/notes.txt"
        custom.parent.mkdir(parents=True)
        custom.write_text("keep")
        self.setup()
        before = self.snapshot()
        self.setup()
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.project / ".research-os/runtime").exists())
        self.assertFalse((self.project / "uv.lock").exists())
        claude_manifest = json.loads(
            (self.project / ".research-os/projections/claude-code/manifest.json").read_bytes()
        )
        self.assertEqual(set(claude_manifest["workflow_entries"]), set(WORKFLOW_IDS))
        self.assertEqual(set(claude_manifest["discipline_entries"]), set(DISCIPLINE_IDS))
        self.assertEqual(claude_manifest["projection_scope"], "complete")
        self.assertEqual(claude_manifest["excluded_canonical_skills"], [])
        self.assertEqual(claude_manifest["blocked_capabilities"], [])
        for name in WORKFLOW_IDS:
            text = (self.project / ".claude/skills" / name / "SKILL.md").read_text()
            self.assertIn("disable-model-invocation: true", text)
        for name in DISCIPLINE_IDS:
            text = (self.project / ".claude/skills" / name / "SKILL.md").read_text()
            self.assertIn("user-invocable: false", text)
            self.assertNotIn("disable-model-invocation", text)

        codex_manifest = json.loads(
            (self.project / ".research-os/projections/codex/manifest.json").read_bytes()
        )
        self.assertEqual(set(codex_manifest["workflow_entries"]), set(WORKFLOW_IDS))
        self.assertEqual(codex_manifest["discipline_entries"], [])
        self.assertEqual(codex_manifest["projection_scope"], "workflow-only")
        self.assertEqual(codex_manifest["blocked_capabilities"], ["discipline_private_visibility"])
        self.assertEqual(
            {item["name"] for item in codex_manifest["excluded_canonical_skills"]},
            set(DISCIPLINE_IDS),
        )
        for name in WORKFLOW_IDS:
            policy = self.project / ".agents/skills" / name / "agents/openai.yaml"
            self.assertIn("allow_implicit_invocation: false", policy.read_text())
        for name in DISCIPLINE_IDS:
            self.assertFalse((self.project / ".agents/skills" / name).exists())
        self.assertEqual(custom.read_text(), "keep")

    def test_install_rejects_bundle_without_or_drifting_port_release_attestation(self):
        from research_os import __version__
        from research_os.core import ADAPTERS, CORE, REFERENCES, TEMPLATES
        from research_os.install import SourceBundle

        files = {}
        for prefix, root in (
            ("core", CORE),
            ("templates", TEMPLATES),
            ("adapters", ADAPTERS),
            ("reference-projects", REFERENCES),
        ):
            for path in root.rglob("*"):
                if path.is_file():
                    files[f"{prefix}/{path.relative_to(root).as_posix()}"] = path.read_bytes()
        raw = files.pop("core/port-release-attestation.json")
        missing = SourceBundle(__version__, "a" * 40, files)
        object.__setattr__(missing, "source_verified", True)
        with self.assertRaises(ApplicationFailure):
            _verify_bundled_port_attestation(missing)

        files["core/port-release-attestation.json"] = raw
        catalog = json.loads(files["core/catalog.json"])
        discipline = next(item for item in catalog["skills"] if item["kind"] == "discipline")
        path = f"core/skills/{discipline['id']}/SKILL.md"
        files[path] += b"\ndrift\n"
        drifted = SourceBundle(__version__, "a" * 40, files)
        object.__setattr__(drifted, "source_verified", True)
        with self.assertRaises(ApplicationFailure):
            _verify_bundled_port_attestation(drifted)

    def test_setup_conflict_is_atomic(self):
        path = self.project / ".agents/skills/research-charter/agents/openai.yaml"
        path.parent.mkdir(parents=True)
        path.write_text("custom")
        before = self.snapshot()
        result = installed_cli("setup-research-os", "--project", str(self.project))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(before, self.snapshot())

    def test_setup_symlink_is_rejected(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.project / ".claude").symlink_to(outside, target_is_directory=True)
        result = installed_cli("setup-research-os", "--project", str(self.project))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(list(outside.iterdir()), [])

    def test_charter_candidate_and_dynamic_validation(self):
        self.setup()
        charter_request(self.project)
        result = run_cli(*self.args())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(report(result)["automatic_next_workflow"])
        self.assertEqual(report(result)["status"], "stopped")
        validation = run_cli("validate", "--project", str(self.project), "artifacts/charter.json")
        self.assertEqual(validation.returncode, 0, validation.stdout)
        self.assertEqual(report(validation)["validator"], {"name": "artifact", "version": "1.1.0"})
        self.assertEqual(len(report(validation)["evidence"]), 2)
        self.assertFalse((self.project / "publications").exists())

    def test_verified_host_exactly_once_matches_direct(self):
        self.setup()
        charter_request(self.project)
        requests = []
        def host(request, invoke):
            requests.append(request)
            result = invoke()
            with self.assertRaises(RuntimeError):
                invoke()
            return CodexHostReceipt(request.digest(), result["status"], result["stop_reason"], 0)
        code, value = self.host_run(host)
        self.assertEqual(code, 0, value)
        self.assertEqual(len(requests), 1)
        self.assertFalse(requests[0].automatic_next_workflow)
        artifact = (self.project / "artifacts/charter.json").read_bytes()
        saved_report = (self.project / "reports/charter.json").read_bytes()
        (self.project / "artifacts/charter.json").unlink()
        (self.project / "reports/charter.json").unlink()
        direct = run_cli(*self.args())
        self.assertEqual(report(direct), value)
        self.assertEqual(artifact, (self.project / "artifacts/charter.json").read_bytes())
        self.assertEqual(saved_report, (self.project / "reports/charter.json").read_bytes())

    def test_host_failure_no_fallback_and_late_callback_closed(self):
        self.setup()
        charter_request(self.project)
        callbacks = []
        def host(request, invoke):
            callbacks.append(invoke)
            return object()
        code, value = self.host_run(host)
        self.assertEqual(code, 1, value)
        self.assertFalse((self.project / "artifacts").exists())
        with self.assertRaises(RuntimeError):
            callbacks[0]()

    def test_host_cannot_replace_the_explicit_request(self):
        self.setup()
        charter_request(self.project)
        def host(request, invoke):
            value = json.loads((self.project/'question.json').read_bytes())
            value['spec']['question'] = 'unauthorized replacement'
            write_json(self.project/'question.json',value)
            write_json(self.project/'request.json',{'inputs':[{'path':'question.json','sha256':hashlib.sha256((self.project/'question.json').read_bytes()).hexdigest()}]})
            return invoke()
        code, value = self.host_run(host)
        self.assertEqual(code,1,value)
        self.assertFalse((self.project/'artifacts/charter.json').exists())

    def test_host_cannot_retry_failed_core_invocation(self):
        self.setup()
        attempts = []
        def host(request, invoke):
            for _ in range(2):
                try:
                    invoke()
                except Exception as exc:
                    attempts.append(type(exc).__name__)
            raise FileNotFoundError("request.json")
        code, _ = self.host_run(host)
        self.assertEqual(code, 2)
        self.assertEqual(attempts, ["FileNotFoundError", "RuntimeError"])

    def test_offline_blocks_even_injected_host(self):
        self.setup()
        charter_request(self.project)
        before = self.snapshot()
        with patch.dict(os.environ, {"RESEARCH_OS_OFFLINE": "1"}):
            code, value = self.host_run(lambda *_: self.fail("host invoked offline"))
        self.assertEqual(code, 3, value)
        self.assertFalse(value["execution"]["direct_cli_fallback"])
        self.assertEqual(before, self.snapshot())
        for adapter in ("claude-code", "codex"):
            result = run_cli("adapter", adapter, "research-charter", *self.args()[1:],
                             "--confirm", "RUN research-charter", env={"RESEARCH_OS_OFFLINE": "1"})
            self.assertEqual(result.returncode, 3, result.stdout)

    def test_host_receipt_and_projection_drift_fail(self):
        self.setup()
        charter_request(self.project)
        def dishonest(request, invoke):
            result = invoke()
            return CodexHostReceipt("0" * 64, result["status"], result["stop_reason"], 0)
        self.assertEqual(self.host_run(dishonest)[0], 1)
        (self.project / "artifacts/charter.json").unlink()
        (self.project / "reports/charter.json").unlink()
        def drift(request, invoke):
            result = invoke()
            (self.project / ".agents/skills/research-charter/agents/openai.yaml").write_text("drift")
            return CodexHostReceipt(request.digest(), result["status"], result["stop_reason"], 0)
        code, value = self.host_run(drift)
        self.assertEqual(code, 1)
        self.assertEqual(value["issues"][0]["code"], "codex.projection_changed")

    def test_output_race_preserves_concurrent_file(self):
        self.setup()
        charter_request(self.project)
        path = self.project / "artifacts/charter.json"
        def race(request, invoke):
            path.parent.mkdir()
            path.write_text("concurrent")
            return invoke()
        code, _ = self.host_run(race)
        self.assertEqual(code, 1)
        self.assertEqual(path.read_text(), "concurrent")
        self.assertFalse((self.project / "reports/charter.json").exists())

    def test_existing_outputs_preflight_before_host(self):
        self.setup()
        path = self.project / "artifacts/charter.json"
        path.parent.mkdir()
        path.write_text("keep")
        code, _ = self.host_run(lambda *_: self.fail("host invoked"))
        self.assertEqual(code, 1)
        self.assertEqual(path.read_text(), "keep")

    def test_paths_overlap_symlink_and_pin_drift_no_writes(self):
        charter_request(self.project)
        arguments = self.args()
        arguments[arguments.index("--report") + 1] = "artifacts/charter.json"
        self.assertEqual(run_cli(*arguments).returncode, 1)
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.project / "artifacts").symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(run_cli(*self.args()).returncode, 0)
        self.assertEqual(list(outside.iterdir()), [])
        (self.project / "artifacts").unlink()
        (self.project / "question.json").write_text("{}")
        self.assertEqual(run_cli(*self.args()).returncode, 1)
        self.assertFalse((self.project / "artifacts").exists())

    def test_validation_usage_fail_and_projection_parity(self):
        self.setup()
        for name, raw in (("invalid.json", b'{}'), ("malformed.json", b'{no')):
            (self.project / name).write_bytes(raw)
            direct = run_cli("validate", "--project", str(self.project), name)
            self.assertEqual(direct.returncode, 1)
            for adapter in ("claude-code", "codex"):
                projected = run_cli("adapter", adapter, "validate", "--project", str(self.project), name)
                self.assertEqual(projected.returncode, direct.returncode)
                self.assertEqual(report(projected), report(direct))
        for path in ("missing.json", "../escape.json"):
            self.assertEqual(run_cli("validate", "--project", str(self.project), path).returncode, 2)

    def test_workflow_only_codex_validation_rejects_excluded_discipline_injection(self):
        self.setup()
        for relative in (
            ".agents/skills/statistical-check/SKILL.md",
            ".agents/skills/evil/SKILL.md",
        ):
            injected = self.project / relative
            injected.parent.mkdir(parents=True, exist_ok=True)
            injected.write_text("injected discipline")
            artifact = self.project / "invalid.json"
            artifact.write_text("{}")
            result = run_cli(
                "adapter", "codex", "validate", "--project", str(self.project), "invalid.json"
            )
            self.assertEqual(result.returncode, 3, result.stdout)
            self.assertTrue(
                {"projection.excluded", "projection.inventory"}
                & {item["code"] for item in report(result)["issues"]}
            )
            injected.unlink()
            if relative.startswith(".agents/skills/evil"):
                injected.parent.rmdir()

    def test_projection_conflicts_and_symlinks(self):
        out = self.project / "projection"
        path = out / ".claude/skills/research-charter/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("custom")
        result = installed_cli("generate-projection", "claude-code", "--output", str(out))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(path.read_text(), "custom")
        self.assertFalse((out / "manifest.json").exists())
        path.unlink()
        path.symlink_to(self.project / "missing")
        self.assertEqual(installed_cli("generate-projection", "claude-code", "--output", str(out)).returncode, 1)


if __name__ == "__main__":
    unittest.main()
