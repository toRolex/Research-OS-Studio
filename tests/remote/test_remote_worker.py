from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from research_os.remote import RemoteConfig
from research_os.remote import worker


class WorkerTests(unittest.TestCase):
    """Trusted local executable fixtures only; never invoke ssh or a real scheduler."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        self.capture = self.root / "calls.jsonl"
        self.states = self.root / "states.json"
        self.states.write_text(json.dumps({"squeue": "", "sacct": ""}))
        executable = f"#!{Path(sys.executable).resolve()}\nimport json,sys,pathlib\nname=pathlib.Path(sys.argv[0]).name\nwith pathlib.Path({str(self.capture)!r}).open('a') as f: f.write(json.dumps({{'name':name,'argv':sys.argv,'stdin':sys.stdin.read() if name=='sbatch' else ''}})+'\\n')\nprint('1234' if name=='sbatch' else json.loads(pathlib.Path({str(self.states)!r}).read_text()).get(name,''),end='')\n"
        for name in ("sbatch", "squeue", "sacct", "scancel"):
            path = self.bin / name
            path.write_text(executable)
            path.chmod(0o700)
        self.environment = patch.dict(
            os.environ, {"PATH": str(self.bin) + os.pathsep + os.environ["PATH"]}
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.git("init", "-q")
        self.git("config", "user.name", "Trusted Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        script = b"import pathlib,sys; pathlib.Path('result.json').write_text(sys.argv[1]); print('log')\n"
        (self.checkout / "experiment.py").write_bytes(script)
        self.git("add", "experiment.py")
        self.git("commit", "-qm", "pinned local fixture")
        revision = self.git("rev-parse", "HEAD").stdout.decode().strip()
        self.config = RemoteConfig(
            "slurm",
            "never-contacted.invalid",
            str(self.checkout),
            revision,
            {"experiment.py": hashlib.sha256(script).hexdigest()},
            slurm={"partition": "cpu", "cpus_per_task": "1"},
        )
        self.token = "a" * 64
        self.request = {
            "config": self.config.as_dict(),
            "operation": "submit",
            "token": self.token,
            "seconds": 1,
            "deadline_epoch_seconds": time.time() + 30,
            "context": {
                "command": [
                    str(Path(sys.executable).resolve()),
                    "experiment.py",
                    "literal;$(false)' argument",
                ],
                "cwd": ".",
                "environment": {},
            },
            "worker_source": Path(worker.__file__).read_text(),
        }

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.checkout), *args], capture_output=True, check=True
        )

    def submit(self):
        result = worker.handle(self.request)
        self.job = result["job"]
        self.directory = self.checkout / ".research-os/remote-jobs" / self.token
        return result

    def operation(self, name, **extra):
        return worker.handle(dict(self.request, operation=name, job=self.job, **extra))

    def set_state(self, queue, accounting):
        self.states.write_text(json.dumps({"squeue": queue, "sacct": accounting}))

    def test_fake_slurm_submit_exact_argv_and_immutable_snapshot(self):
        (self.checkout / "experiment.py").write_text(
            "raise RuntimeError('dirty bytes must not execute')"
        )
        result = self.submit()
        self.assertEqual(result["state"], "submitted")
        self.assertEqual(result["job"]["job_id"], "1234")
        calls = [json.loads(line) for line in self.capture.read_text().splitlines()]
        self.assertEqual([c["name"] for c in calls], ["sbatch"])
        self.assertIn("--no-requeue", calls[0]["argv"])
        self.assertIn("--partition=cpu", calls[0]["argv"])
        self.assertIn("--time=1", calls[0]["argv"])
        self.assertNotIn("--wrap", calls[0]["argv"])
        worker.supervise(self.directory)
        status = json.loads((self.directory / "result.json").read_text())
        self.assertEqual(status["state"], "succeeded")
        data = (self.directory / "work/result.json").read_text()
        self.assertEqual(data, self.request["context"]["command"][-1])
        self.set_state("", f"1234|ros-{self.token}|COMPLETED|0:0\n")
        self.assertEqual(self.operation("status")["state"], "succeeded")
        artifact = self.operation("artifact", path="result.json")
        self.assertEqual(artifact["sha256"], hashlib.sha256(data.encode()).hexdigest())
        self.assertEqual(self.operation("log", path="stdout")["state"], "retrieved")
        with self.assertRaises(FileExistsError):
            worker.handle(self.request)
        self.assertEqual(
            sum(
                json.loads(line)["name"] == "sbatch"
                for line in self.capture.read_text().splitlines()
            ),
            1,
        )

    def test_scheduler_unknown_ambiguous_and_identity_mismatch(self):
        self.submit()
        fixtures = [
            ("", ""),
            ("1234|wrong|RUNNING\n", ""),
            (
                f"1234|ros-{self.token}|RUNNING\n",
                f"1234|ros-{self.token}|COMPLETED|0:0\n",
            ),
            ("", f"1234|ros-{self.token}|PREEMPTED|0:0\n"),
            ("", f"1234|ros-{self.token}|COMPLETED|1:0\n"),
            ("", f"1234|ros-{self.token}|COMPLETED|0:0\n"),
            ("", f"1234|ros-{self.token}|RUNNING|0:0\n" * 2),
        ]
        for queue, accounting in fixtures:
            with (
                self.subTest(queue=queue, accounting=accounting),
                self.assertRaises((ValueError, FileNotFoundError)),
            ):
                self.set_state(queue, accounting)
                self.operation("status")

    def test_cancel_ack_is_pending_until_accounting_proves_terminal(self):
        self.submit()
        self.set_state(f"1234|ros-{self.token}|RUNNING\n", "")
        self.assertEqual(self.operation("cancel")["state"], "cancel_requested")
        calls = [json.loads(line) for line in self.capture.read_text().splitlines()]
        self.assertEqual(calls[-1]["argv"][1:], ["--", "1234"])
        self.set_state("", f"1234|ros-{self.token}|CANCELLED by 501|0:15\n")
        self.assertEqual(self.operation("status")["state"], "cancelled")

    def test_worker_walltime_and_cancel_without_client_polling(self):
        for token, cancel in (("b" * 64, False), ("c" * 64, True)):
            with self.subTest(cancel=cancel):
                request = dict(
                    self.request,
                    token=token,
                    seconds=0.04,
                    context={
                        "command": [
                            str(Path(sys.executable).resolve()),
                            "-c",
                            "import time; time.sleep(10)",
                        ],
                        "cwd": ".",
                        "environment": {},
                    },
                )
                worker.handle(request)
                directory = self.checkout / ".research-os/remote-jobs" / token
                if cancel:
                    worker.save(directory / "cancel.request", {"token": token}, True)
                worker.supervise(directory)
                receipt = json.loads((directory / "result.json").read_text())
                self.assertEqual(
                    receipt["state"], "cancelled" if cancel else "timed_out"
                )
                self.assertNotEqual(receipt["return_code"], 0)
                self.assertLess(receipt["seconds"], 1)

    def test_snapshot_digest_failure_precedes_sbatch(self):
        config = dict(self.config.as_dict(), inputs={"experiment.py": "f" * 64})
        with self.assertRaises(ValueError):
            worker.handle(dict(self.request, config=config))
        self.assertFalse(self.capture.exists())

    def test_worker_retrieval_rejects_symlink_and_large_file(self):
        self.submit()
        work = self.directory / "work"
        (work / "bad").symlink_to(self.states)
        with self.assertRaises(ValueError):
            self.operation("artifact", path="bad")
        (work / "big").write_bytes(b"x" * (self.config.max_transfer_bytes + 1))
        with self.assertRaises(ValueError):
            self.operation("artifact", path="big")

    def test_expired_queued_job_never_starts(self):
        self.request["deadline_epoch_seconds"] = time.time() - 1
        self.submit()
        worker.supervise(self.directory)
        receipt = json.loads((self.directory / "result.json").read_bytes())
        self.assertEqual(receipt["state"], "timed_out")
        self.assertFalse((self.directory / "child.json").exists())
        self.assertFalse((self.directory / "work/result.json").exists())

    def test_supervisor_write_failure_cleans_up_child(self):
        self.request["context"]["command"] = [
            str(Path(sys.executable).resolve()),
            "-c",
            "import time; time.sleep(60)",
        ]
        self.submit()
        original_save = worker.save
        original_popen = worker.subprocess.Popen
        children = []

        def launch(*args, **kwargs):
            child = original_popen(*args, **kwargs)
            children.append(child)
            return child

        def fault(path, value, *args):
            if path.name == "child.json":
                raise OSError("injected disk full")
            return original_save(path, value, *args)

        with (
            patch.object(worker, "save", fault),
            patch.object(worker.subprocess, "Popen", launch),
        ):
            worker.supervise(self.directory)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        with self.assertRaises(ProcessLookupError):
            os.kill(children[0].pid, 0)
        self.assertEqual(
            json.loads((self.directory / "result.json").read_bytes())["state"],
            "unknown",
        )

    def test_ssh_worker_identity_cancel_and_completion_with_trusted_process(self):
        config = dict(self.config.as_dict(), backend="ssh", slurm={})
        self.request["config"] = config
        process_identity = {
            "pid": 4321,
            "start_ticks": "100",
            "boot_id": "01234567-0123-0123-0123-0123456789ab",
        }

        class TrustedProcess:
            pid = 4321

        original_popen = worker.subprocess.Popen

        def launch(argv, **kwargs):
            return (
                TrustedProcess()
                if "supervise" in argv
                else original_popen(argv, **kwargs)
            )

        with (
            patch.object(worker.subprocess, "Popen", side_effect=launch),
            patch.object(worker, "identity", return_value=process_identity),
        ):
            self.submit()
            self.assertEqual(self.operation("status")["state"], "running")
            self.assertEqual(self.operation("cancel")["state"], "cancel_requested")
        self.assertTrue((self.directory / "cancel.request").exists())
        worker.supervise(self.directory)
        receipt = self.operation("status")
        self.assertEqual(receipt["state"], "cancelled")
        self.assertNotEqual(receipt["return_code"], 0)
        self.assertEqual(receipt["job"]["process"], process_identity)
        self.assertEqual(self.operation("log", path="stderr")["state"], "retrieved")

    def test_ssh_missing_or_reused_supervisor_never_proves_completion(self):
        self.request["config"] = dict(self.config.as_dict(), backend="ssh", slurm={})
        process_identity = {
            "pid": 4321,
            "start_ticks": "100",
            "boot_id": "01234567-0123-0123-0123-0123456789ab",
        }

        class TrustedProcess:
            pid = 4321

        original_popen = worker.subprocess.Popen

        def launch(argv, **kwargs):
            return (
                TrustedProcess()
                if "supervise" in argv
                else original_popen(argv, **kwargs)
            )

        with (
            patch.object(worker.subprocess, "Popen", side_effect=launch),
            patch.object(worker, "identity", return_value=process_identity),
        ):
            self.submit()
        for operation in ("status", "cancel"):
            with (
                patch.object(
                    worker, "identity", side_effect=FileNotFoundError("process gone")
                ),
                self.assertRaises(FileNotFoundError),
            ):
                self.operation(operation)
            with (
                patch.object(
                    worker,
                    "identity",
                    return_value=dict(process_identity, start_ticks="101"),
                ),
                self.assertRaises(ValueError),
            ):
                self.operation(operation)
        self.assertFalse((self.directory / "cancel.request").exists())

    def test_fifo_retrieval_fails_without_blocking(self):
        self.submit()
        os.mkfifo(self.directory / "work/fifo")
        with self.assertRaises(ValueError):
            self.operation("artifact", path="fifo")

    def test_cancel_remains_available_when_accounting_fails(self):
        self.submit()
        self.set_state(f"1234|ros-{self.token}|RUNNING\n", "")
        original = worker.run

        def broken_accounting(argv, **kwargs):
            if argv[0] == "sacct":
                return subprocess.CompletedProcess(argv, 1, b"", b"accounting offline")
            return original(argv, **kwargs)

        with patch.object(worker, "run", side_effect=broken_accounting):
            with self.assertRaises(ValueError):
                self.operation("status")
            receipt = self.operation("cancel")
        self.assertEqual(receipt["state"], "cancel_requested")
        calls = [json.loads(line) for line in self.capture.read_text().splitlines()]
        self.assertEqual(calls[-1]["name"], "scancel")
        self.assertEqual(calls[-1]["argv"][1:], ["--", "1234"])
        self.set_state("1234|wrong|RUNNING\n", "")
        with self.assertRaises(ValueError):
            self.operation("cancel")

    def test_scheduler_tools_missing_is_blocked_probe(self):
        with patch.object(worker.shutil, "which", return_value=None):
            receipt = worker.handle(dict(self.request, operation="probe"))
        self.assertEqual(receipt["state"], "blocked")
        self.assertIn("sbatch", receipt["detail"])


if __name__ == "__main__":
    unittest.main()
