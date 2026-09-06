from __future__ import annotations

import base64
import concurrent.futures
import hashlib
import io
import json
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from research_os.remote import RemoteAdapter, RemoteConfig, RemoteExecutor
from research_os.remote.__main__ import main
from research_os.remote.adapter import SSHTransport
from research_os.remote.config import ConfigurationError
from research_os.workflows.computational.budget import BudgetUsage
from research_os.workflows.computational.execution import AttemptContext

DATA = b'{"result": 42}\n'
SHA = hashlib.sha256(DATA).hexdigest()
BUDGET = BudgetUsage(seconds=1, attempts=3, rounds=3)


class TrustedTransport:
    def __init__(self, backend="ssh"):
        self.backend = backend
        self.calls = []
        self.state = "running"
        self.mode = None
        self.job = None

    def __call__(self, request, timeout):
        self.calls.append(request)
        op = request["operation"]
        token = request.get("token")
        result = {
            "protocol": "research-os/remote-wire/1",
            "operation": op,
            "token": token,
            "return_code": None,
        }
        if op == "probe":
            return dict(result, state="available", remote_epoch_seconds=time.time())
        if op == "submit":
            self.job = {"backend": self.backend, "token": token}
            if self.backend == "slurm":
                self.job.update(job_id="1234", job_name="ros-" + token)
            else:
                self.job["process"] = {
                    "pid": 1234,
                    "start_ticks": "999",
                    "boot_id": "01234567-0123-0123-0123-0123456789ab",
                }
            if self.mode == "lost_submit":
                raise subprocess.TimeoutExpired("trusted fake accepted", 1)
            return dict(result, state="submitted", job=dict(self.job))
        result["job"] = dict(self.job)
        if self.mode == "identity":
            result["job"]["token"] = "f" * 64
        if op == "status":
            result.update(
                state=self.state,
                return_code=0
                if self.state == "succeeded"
                else 1
                if self.state in {"failed", "cancelled", "timed_out"}
                else None,
            )
        elif op == "cancel":
            result["state"] = "cancel_requested"
        else:
            result.update(
                state="retrieved",
                path=request["path"],
                data=base64.b64encode(DATA).decode(),
                sha256=SHA,
                size_bytes=len(DATA),
            )
            if self.mode == "digest":
                result["sha256"] = "0" * 64
        return result


class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve()
        self.transport = TrustedTransport()
        self.config = RemoteConfig(
            "ssh", "cluster.example", "/srv/pinned", "a" * 40, {"input.json": SHA}
        )
        self.adapter = RemoteAdapter(
            self.project, self.config, transport=self.transport
        )
        self.context = AttemptContext(1, 1, ("python3", "experiment.py"))

    def submit(self):
        receipt = self.adapter.submit(self.context, BUDGET)
        self.assertEqual(receipt.state, "submitted", receipt.detail)
        return receipt

    def test_no_config_all_capabilities_block_without_transport(self):
        adapter = RemoteAdapter(
            self.project, None, transport=lambda *a: self.fail("called")
        )
        for receipt in (
            adapter.probe(),
            adapter.submit(self.context, BUDGET),
            adapter.status(1),
            adapter.cancel(1),
            adapter.log(1, "stdout", "out"),
            adapter.retrieve_artifact(1, "out", SHA, "out"),
        ):
            self.assertEqual(receipt.exit_code, 3)
            self.assertEqual(receipt.state, "blocked")
            self.assertEqual(receipt.real_environment, "NOT_EVALUATED")

    def test_missing_ssh_executable_is_blocked_no_intent(self):
        config = RemoteConfig.from_mapping(
            dict(self.config.as_dict(), ssh_executable="/nonexistent/ssh")
        )
        adapter = RemoteAdapter(self.project, config)
        self.assertEqual(adapter.submit(self.context, BUDGET).exit_code, 3)
        self.assertEqual(adapter.records(), [])

    def test_probe_available_is_not_real_lifecycle_pass(self):
        receipt = self.adapter.probe()
        self.assertEqual(receipt.state, "available")
        self.assertEqual(receipt.as_dict()["real_environment"], "NOT_EVALUATED")

    def test_ssh_lifecycle_and_pinned_retrieval(self):
        submitted = self.submit()
        self.assertEqual(self.adapter.status(1).state, "running")
        self.assertEqual(self.adapter.log(1, "stdout", "logs/live").state, "retrieved")
        self.assertEqual(
            self.adapter.retrieve_artifact(1, "result.json", SHA, "premature").state,
            "blocked",
        )
        self.transport.state = "succeeded"
        self.assertEqual(self.adapter.status(1).state, "succeeded")
        receipt = self.adapter.retrieve_artifact(
            1, "result.json", SHA, "results/final.json"
        )
        self.assertEqual(receipt.state, "retrieved", receipt.detail)
        self.assertEqual((self.project / "results/final.json").read_bytes(), DATA)
        self.assertEqual(receipt.job, submitted.job)
        self.assertTrue(receipt.evidence["digest_verified"])
        events = self.adapter.records()
        self.assertEqual(events[0]["kind"], "intent")
        self.assertEqual(events[0]["value"]["configuration"]["revision"], "a" * 40)
        self.assertEqual(
            events[0]["value"]["context"]["command"], list(self.context.command)
        )
        self.assertEqual(len({event["token"] for event in events}), 1)

    def test_slurm_lifecycle_cancel_is_not_complete(self):
        transport = TrustedTransport("slurm")
        config = RemoteConfig.from_mapping(
            dict(self.config.as_dict(), backend="slurm", slurm={"partition": "cpu"})
        )
        self.adapter = RemoteAdapter(self.project, config, transport=transport)
        receipt = self.submit()
        self.assertEqual(receipt.job["job_id"], "1234")
        self.assertEqual(self.adapter.cancel(1).state, "cancel_requested")
        self.assertEqual(
            self.adapter.submit(AttemptContext(2, 2, ("true",)), BUDGET).state,
            "unknown",
        )
        transport.state = "cancelled"
        terminal = self.adapter.status(1)
        self.assertEqual(terminal.state, "cancelled")
        self.assertNotEqual(terminal.exit_code, 0)
        self.assertEqual(
            self.adapter.retrieve_artifact(1, "out", SHA, "out").state, "blocked"
        )

    def test_unknown_latches_even_after_later_success(self):
        self.submit()
        self.transport.state = "unknown"
        self.assertEqual(self.adapter.status(1).state, "unknown")
        self.transport.state = "succeeded"
        self.assertEqual(self.adapter.status(1).state, "unknown")
        reconstructed = RemoteAdapter(
            self.project, self.config, transport=self.transport
        )
        self.assertEqual(
            reconstructed.submit(AttemptContext(2, 2, ("true",)), BUDGET).state,
            "unknown",
        )
        self.assertEqual(
            sum(c["operation"] == "submit" for c in self.transport.calls), 1
        )

    def test_unknown_allows_pinned_cancel_but_does_not_clear_latch(self):
        self.submit()
        self.transport.state = "unknown"
        self.assertEqual(self.adapter.status(1).state, "unknown")
        receipt = self.adapter.cancel(1)
        self.assertEqual(receipt.state, "unknown")
        self.assertEqual(receipt.evidence["state"], "cancel_requested")
        self.assertEqual(self.transport.calls[-1]["operation"], "cancel")
        self.assertEqual(
            self.adapter.submit(AttemptContext(2, 2, ("true",)), BUDGET).state,
            "unknown",
        )

    def test_clock_skew_blocks_before_submit(self):
        trusted = self.transport

        def skewed(request, timeout):
            result = trusted(request, timeout)
            if request["operation"] == "probe":
                result["remote_epoch_seconds"] += 3600
            return result

        adapter = RemoteAdapter(self.project, self.config, transport=skewed)
        self.assertEqual(adapter.submit(self.context, BUDGET).state, "blocked")
        self.assertFalse(any(c["operation"] == "submit" for c in trusted.calls))

    def test_lost_acknowledgement_never_resubmits_same_or_next_attempt(self):
        self.transport.mode = "lost_submit"
        self.assertEqual(self.adapter.submit(self.context, BUDGET).state, "unknown")
        for number in (1, 2):
            adapter = RemoteAdapter(self.project, self.config, transport=self.transport)
            self.assertEqual(
                adapter.submit(AttemptContext(number, number, ("true",)), BUDGET).state,
                "unknown",
            )
            self.assertEqual(adapter.status(1).state, "unknown")
        self.assertEqual(
            sum(c["operation"] == "submit" for c in self.transport.calls), 1
        )

    def test_receipt_write_crash_preserves_intent_barrier(self):
        from research_os.remote import adapter as module

        original = module._exclusive

        def fault(path, data):
            if path.name == "event-00000002.json":
                raise OSError("disk full after accepted")
            return original(path, data)

        with patch.object(module, "_exclusive", fault):
            self.assertEqual(self.adapter.submit(self.context, BUDGET).state, "unknown")
        self.assertEqual(
            self.adapter.submit(AttemptContext(2, 2, ("true",)), BUDGET).state,
            "unknown",
        )
        self.assertEqual(
            sum(c["operation"] == "submit" for c in self.transport.calls), 1
        )

    def test_concurrent_submit_has_one_side_effect(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(lambda _: self.adapter.submit(self.context, BUDGET), range(2))
            )
        self.assertEqual(sum(r.state == "submitted" for r in results), 1)
        self.assertEqual(
            sum(c["operation"] == "submit" for c in self.transport.calls), 1
        )

    def test_job_identity_drift_hard_stops(self):
        self.submit()
        self.transport.mode = "identity"
        self.assertEqual(self.adapter.status(1).state, "unknown")
        self.assertEqual(self.adapter.cancel(1).state, "unknown")

    def test_same_attempt_cannot_change_command_after_success(self):
        self.submit()
        self.transport.state = "succeeded"
        self.adapter.status(1)
        self.assertEqual(
            self.adapter.submit(AttemptContext(1, 1, ("different",)), BUDGET).state,
            "unknown",
        )
        self.assertEqual(
            self.adapter.submit(AttemptContext(2, 2, ("different",)), BUDGET).state,
            "submitted",
        )

    def test_config_drift_and_corrupt_ledger_block(self):
        self.submit()
        config = RemoteConfig.from_mapping(
            dict(self.config.as_dict(), host="different.example")
        )
        self.assertEqual(
            RemoteAdapter(self.project, config, transport=self.transport)
            .status(1)
            .state,
            "unknown",
        )
        (self.adapter.directory / "event-00000002.json").write_bytes(b"{")
        self.assertEqual(
            self.adapter.submit(AttemptContext(2, 2, ("true",)), BUDGET).state,
            "unknown",
        )

    def test_digest_mismatch_does_not_publish(self):
        self.submit()
        self.transport.state = "succeeded"
        self.adapter.status(1)
        self.transport.mode = "digest"
        receipt = self.adapter.retrieve_artifact(1, "out", SHA, "out")
        self.assertEqual(receipt.state, "unknown")
        self.assertFalse((self.project / "out").exists())

    def test_expected_digest_mismatch_does_not_publish(self):
        self.submit()
        self.transport.state = "succeeded"
        self.adapter.status(1)
        receipt = self.adapter.retrieve_artifact(1, "out", "f" * 64, "out")
        self.assertEqual(receipt.state, "unknown")
        self.assertFalse((self.project / "out").exists())

    def test_retrieval_never_overwrites_or_follows_symlink(self):
        self.submit()
        self.transport.state = "succeeded"
        self.adapter.status(1)
        (self.project / "out").write_bytes(b"preserve")
        self.assertEqual(
            self.adapter.retrieve_artifact(1, "out", SHA, "out").state, "unknown"
        )
        self.assertEqual((self.project / "out").read_bytes(), b"preserve")

    def test_path_traversal_rejected_before_transport(self):
        for path in (
            "../out",
            "/tmp/out",
            "a/../../out",
            ".git/config",
            "a//b",
            "a\\b",
        ):
            with self.subTest(path=path), self.assertRaises(ConfigurationError):
                self.adapter.retrieve_artifact(1, path, SHA, "out")
        self.assertEqual(self.transport.calls, [])

    def test_budget_no_unmetered_resources(self):
        for budget in (
            BudgetUsage(seconds=0, attempts=1, rounds=1),
            BudgetUsage(seconds=1, attempts=1, rounds=1, gpu_hours=1),
            BudgetUsage(seconds=1, attempts=1, rounds=1, cost_usd=1),
        ):
            self.assertEqual(self.adapter.submit(self.context, budget).state, "blocked")
        self.assertEqual(self.transport.calls, [])

    def test_executor_success_and_logs_protocol(self):
        self.transport.state = "succeeded"
        executor = RemoteExecutor(
            self.adapter, artifacts={"result.json": ("result.json", SHA)}
        )
        result = executor(self.project, self.context, BUDGET)
        self.assertEqual(result.outcome, "succeeded", result.detail)
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.stdout, DATA)
        self.assertEqual(result.stderr, DATA)
        self.assertEqual((self.project / "result.json").read_bytes(), DATA)
        self.assertEqual(
            result.usage.attempts, 0
        )  # Outer workflow charges exactly once.
        self.assertGreater(result.usage.seconds, 0)

    def test_executor_unknown_or_cancelled_is_blocked_not_retryable_failure(self):
        for state in ("unknown", "cancelled", "timed_out"):
            with self.subTest(state=state):
                transport = TrustedTransport()
                transport.state = state
                adapter = RemoteAdapter(
                    self.project,
                    self.config,
                    ledger_directory="ledger-" + state,
                    transport=transport,
                )
                result = RemoteExecutor(adapter)(self.project, self.context, BUDGET)
                self.assertEqual(result.outcome, "blocked")
                self.assertIsNone(result.return_code)
                self.assertNotIn("succeeded", result.detail)

    def test_executor_wait_budget_retains_identity_without_cancel_claim(self):
        executor = RemoteExecutor(self.adapter)
        result = executor(
            self.project, self.context, BudgetUsage(seconds=0.02, attempts=1, rounds=1)
        )
        self.assertEqual(result.outcome, "blocked")
        self.assertIsNotNone(executor.last_receipt.job)
        self.assertEqual(
            sum(c["operation"] == "submit" for c in self.transport.calls), 1
        )

    def test_cli_no_configuration_structured_exit_3(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--project", str(self.project), "probe"])
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(output.getvalue())["state"], "blocked")

    def test_cli_invalid_config_structured_exit_2(self):
        config = self.project / "bad.json"
        config.write_text('{"backend":"magic"}')
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(
                ["--project", str(self.project), "--config", str(config), "probe"]
            )
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["exit_code"], 2)

    def test_config_rejects_injection_and_unknown_fields(self):
        for change in (
            {"host": "-oProxyCommand=bad"},
            {"host": "host;touch bad"},
            {"user": "u@h"},
            {"root": "/tmp/../x"},
            {"ssh_executable": "ssh -o bad"},
            {"python_executable": "python3;bad"},
            {"slurm": {"wrap": "evil"}},
            {"port": True},
            {"timeout_seconds": float("nan")},
            {"unknown": 1},
        ):
            with self.subTest(change=change), self.assertRaises(ConfigurationError):
                RemoteConfig.from_mapping(dict(self.config.as_dict(), **change))

    def test_retrieval_parent_symlink_cannot_escape_project(self):
        self.submit()
        self.transport.state = "succeeded"
        self.adapter.status(1)
        outside = self.project / "outside"
        outside.mkdir()
        (self.project / "alias").symlink_to(outside, target_is_directory=True)
        receipt = self.adapter.retrieve_artifact(1, "out", SHA, "alias/out")
        self.assertEqual(receipt.state, "unknown")
        self.assertFalse((outside / "out").exists())

    def test_retrieval_write_failure_publishes_no_partial_file(self):
        self.submit()
        self.transport.state = "succeeded"
        self.adapter.status(1)
        import os

        original = os.fsync
        injected = False

        def fail_once(fd):
            nonlocal injected
            if not injected:
                injected = True
                raise OSError("injected output fsync failure")
            return original(fd)

        with patch("research_os.remote.adapter.os.fsync", side_effect=fail_once):
            receipt = self.adapter.retrieve_artifact(1, "out", SHA, "out")
        self.assertEqual(receipt.state, "unknown")
        self.assertFalse((self.project / "out").exists())
        self.assertEqual(list(self.project.glob(".remote-retrieval-*")), [])

    def test_adapter_descriptors_are_strict_versioned_json(self):
        root = Path(__file__).resolve().parents[2]
        for backend in ("ssh", "slurm"):
            directory = root / "adapters" / backend
            capability = json.loads((directory / "capability.json").read_bytes())
            schema = json.loads((directory / "config.schema.json").read_bytes())
            self.assertEqual(capability["version"], "1.0.0")
            self.assertEqual(
                capability["evidence"]["real_environment"], "NOT_EVALUATED"
            )
            self.assertEqual(
                set(capability["capabilities"]),
                {"submit", "status", "cancel", "log", "artifact"},
            )
            self.assertEqual(
                schema["$schema"], "https://json-schema.org/draft/2020-12/schema"
            )
        schema = json.loads((root / "adapters/ssh/config.schema.json").read_bytes())
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["properties"]), set(self.config.as_dict()))

    def test_retrieval_cannot_pollute_default_or_custom_ledger(self):
        for ledger in (".research-os/remote-attempts", "custom/history"):
            with self.subTest(ledger=ledger):
                transport = TrustedTransport()
                adapter = RemoteAdapter(
                    self.project,
                    self.config,
                    ledger_directory=ledger,
                    transport=transport,
                )
                adapter.submit(self.context, BUDGET)
                transport.state = "succeeded"
                adapter.status(1)
                before = {p.name: p.read_bytes() for p in adapter.directory.iterdir()}
                calls = len(transport.calls)
                for destination in (
                    ledger,
                    ledger + "/event-00000004.json",
                    ledger + "/nested/out",
                ):
                    self.assertEqual(
                        adapter.retrieve_artifact(1, "out", SHA, destination).exit_code,
                        2,
                    )
                    self.assertEqual(adapter.log(1, "stdout", destination).exit_code, 2)
                    with self.assertRaises(ConfigurationError):
                        RemoteExecutor(adapter, artifacts={"out": (destination, SHA)})
                self.assertEqual(len(transport.calls), calls)
                self.assertEqual(
                    {p.name: p.read_bytes() for p in adapter.directory.iterdir()},
                    before,
                )
                self.assertEqual(len(adapter.records()), 3)

    def test_false_failure_receipt_is_unknown_not_executor_exception(self):
        trusted = self.transport

        def contradictory(request, timeout):
            result = trusted(request, timeout)
            if request["operation"] == "status":
                result.update(state="failed", return_code=0)
            return result

        adapter = RemoteAdapter(self.project, self.config, transport=contradictory)
        result = RemoteExecutor(adapter)(self.project, self.context, BUDGET)
        self.assertEqual(result.outcome, "blocked")
        self.assertEqual(adapter.status(1).state, "unknown")

    def test_fake_ssh_executable_sees_safe_argv_and_json(self):
        executable = self.project / "trusted fake ssh"
        capture = self.project / "capture.json"
        executable.write_text(
            f"#!{Path(sys.executable).resolve()}\nimport sys,json,pathlib\nr=json.load(sys.stdin)\npathlib.Path({str(capture)!r}).write_text(json.dumps({{'argv':sys.argv,'request':r}}))\nprint(json.dumps({{'protocol':'research-os/remote-wire/1','operation':r['operation'],'token':r.get('token'),'state':'available'}}))\n"
        )
        executable.chmod(0o700)
        config = RemoteConfig.from_mapping(
            dict(self.config.as_dict(), ssh_executable=str(executable))
        )
        transport = SSHTransport(config)
        payload = {
            "operation": "probe",
            "config": config.as_dict(),
            "command": ["x; touch /BAD", "$(false)", "a'b\nnext"],
        }
        result = transport(payload, 1)
        self.assertEqual(result["state"], "available")
        captured = json.loads(capture.read_text())
        self.assertEqual(captured["request"]["command"], payload["command"])
        self.assertIn("StrictHostKeyChecking=yes", captured["argv"])
        remote_argv = shlex.split(captured["argv"][-1])
        self.assertEqual(remote_argv[:2], ["python3", "-c"])
        self.assertNotIn("touch /BAD", captured["argv"][-1])


if __name__ == "__main__":
    unittest.main()
