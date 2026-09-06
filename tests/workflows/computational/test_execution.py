from __future__ import annotations

import os
import signal
import sys
import tempfile
import time
import unittest
from pathlib import Path

from unittest.mock import patch

from research_os.workflows.computational import BudgetUsage, execute_local_command
from research_os.workflows.computational import execution
from research_os.workflows.computational.execution import AttemptContext


@unittest.skipUnless(
    sys.platform in {"darwin", "linux"}, "POSIX process-group fixtures"
)
class LocalExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name)

    def execute(self, script: str, *, seconds: float = 0.6):
        return execute_local_command(
            self.project,
            AttemptContext(1, 1, (sys.executable, "-c", script)),
            BudgetUsage(seconds=seconds, attempts=1, rounds=1),
        )

    def child_fixture(self, *, ignore_term: bool = False, parent_exits: bool = False):
        # Only trusted inline fixtures run. The child closes all stdio and has a
        # finite lifetime even on the vulnerable implementation.
        child = (
            "import os, pathlib, signal, time; "
            + ("signal.signal(signal.SIGTERM, signal.SIG_IGN); " if ignore_term else "")
            + "pathlib.Path('child.pid').write_text(str(os.getpid())); "
            "time.sleep(1.5); pathlib.Path('marker').write_bytes(b'leaked')"
        )
        return (
            "import pathlib, subprocess, sys, time\n"
            f"subprocess.Popen([sys.executable, '-c', {child!r}], "
            "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
            "while not pathlib.Path('child.pid').exists(): time.sleep(0.005)\n"
            "print('parent-ready', flush=True)\n"
            "print('partial-error', file=sys.stderr, flush=True)\n"
            + ("sys.exit(0)\n" if parent_exits else "time.sleep(20)\n")
        )

    def assert_no_delayed_marker(self) -> None:
        pid_path = self.project / "child.pid"
        self.assertTrue(pid_path.exists(), "fixture child must have started")
        time.sleep(1.7)
        self.assertFalse(
            (self.project / "marker").exists(),
            "descendant survived executor return and wrote delayed marker",
        )

    def test_normal_exit_preserves_binary_streams_and_exit_status(self) -> None:
        for code in (0, 7):
            with self.subTest(code=code):
                receipt = self.execute(
                    f"import os; os.write(1, b'out\\x00\\xff'); "
                    f"os.write(2, b'err\\xfe'); raise SystemExit({code})"
                )
                self.assertEqual(
                    receipt.outcome, "succeeded" if code == 0 else "failed"
                )
                self.assertEqual(receipt.return_code, code)
                self.assertEqual(receipt.stdout, b"out\x00\xff")
                self.assertEqual(receipt.stderr, b"err\xfe")
                self.assertGreater(receipt.usage.seconds, 0)
                self.assertIsNone(receipt.detail)

    def test_timeout_kills_term_ignoring_leader_and_child(self) -> None:
        script = (
            "import signal; signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            + self.child_fixture(ignore_term=True)
        )
        started = time.monotonic()
        receipt = self.execute(script)
        elapsed = time.monotonic() - started
        self.assertEqual(receipt.outcome, "timed_out")
        self.assertIsNone(receipt.return_code)
        self.assertGreater(receipt.usage.seconds, 0.7)
        self.assertAlmostEqual(receipt.usage.seconds, elapsed, delta=0.1)
        self.assertLess(elapsed, 2)
        self.assertEqual(receipt.stdout, b"parent-ready\n")
        self.assert_no_delayed_marker()

    def test_parent_exit_still_kills_term_ignoring_child(self) -> None:
        receipt = self.execute(
            self.child_fixture(ignore_term=True, parent_exits=True), seconds=3
        )
        self.assertEqual(receipt.outcome, "succeeded")
        self.assert_no_delayed_marker()

    def test_timeout_retains_output_emitted_during_term_cleanup(self) -> None:
        receipt = self.execute(
            "import os, signal, time\n"
            "def stop(sig, frame):\n"
            " os.write(1, b'cleanup-out\\n'); os.write(2, b'cleanup-err\\n'); "
            "raise SystemExit(0)\n"
            "signal.signal(signal.SIGTERM, stop)\n"
            "os.write(1, b'partial-out\\n'); os.write(2, b'partial-err\\n')\n"
            "time.sleep(20)\n"
        )
        self.assertEqual(receipt.outcome, "timed_out")
        self.assertIsNone(receipt.return_code)
        self.assertEqual(receipt.stdout, b"partial-out\ncleanup-out\n")
        self.assertEqual(receipt.stderr, b"partial-err\ncleanup-err\n")

    def test_spawn_errors_are_blocked_not_command_failure(self) -> None:
        for command in ((str(self.project / "missing"),), ("bad\x00argv",)):
            with self.subTest(command=command):
                receipt = execute_local_command(
                    self.project,
                    AttemptContext(1, 1, command),
                    BudgetUsage(seconds=1, attempts=1, rounds=1),
                )
                self.assertEqual(receipt.outcome, "blocked")
                self.assertIsNone(receipt.return_code)
                self.assertIn("spawn failed", receipt.detail)
                self.assertTrue(receipt.stderr)
                self.assertGreater(receipt.usage.seconds, 0)

    def test_unsupported_group_cleanup_blocks_before_spawn(self) -> None:
        with (
            patch.object(execution.sys, "platform", "unsupported"),
            patch.object(execution.subprocess, "Popen") as spawn,
        ):
            receipt = self.execute("raise AssertionError('must not execute')")
        spawn.assert_not_called()
        self.assertEqual(receipt.outcome, "blocked")
        self.assertIn("process-group cleanup unavailable", receipt.detail)
        self.assertEqual(receipt.usage.seconds, 0)

    def test_cleanup_signal_errors_preserve_timeout_and_partial_streams(self) -> None:
        real_killpg = os.killpg

        def fail_term(pgid, sig):
            if sig == signal.SIGTERM:
                raise PermissionError("fixture TERM denied")
            return real_killpg(pgid, sig)

        with patch.object(execution.os, "killpg", side_effect=fail_term):
            receipt = self.execute(self.child_fixture())
        self.assertEqual(receipt.outcome, "timed_out")
        self.assertIsNone(receipt.return_code)
        self.assertEqual(receipt.stdout, b"parent-ready\n")
        self.assertEqual(receipt.stderr, b"partial-error\n")
        self.assertIn("cleanup unconfirmed", receipt.detail)
        self.assertIn("fixture TERM denied", receipt.detail)
        self.assert_no_delayed_marker()

    def test_cleanup_failure_cannot_report_success_or_ordinary_failure(self) -> None:
        for code in (0, 7):
            with (
                self.subTest(code=code),
                patch.object(
                    execution.os, "killpg", side_effect=PermissionError("denied")
                ),
            ):
                receipt = self.execute(
                    f"import sys; print('output'); print('error', file=sys.stderr); "
                    f"sys.exit({code})"
                )
            self.assertEqual(receipt.outcome, "blocked")
            self.assertIsNone(receipt.return_code)
            self.assertEqual(receipt.stdout, b"output\n")
            self.assertEqual(receipt.stderr, b"error\n")
            self.assertIn("TERM: denied", receipt.detail)
            self.assertIn("KILL: denied", receipt.detail)

    def test_caller_process_group_is_never_signalled(self) -> None:
        real_spawn = execution._LocalProcess
        processes = []

        def spawn(*args, **kwargs):
            process = real_spawn(*args, **kwargs)
            processes.append(process)
            return process

        with (
            patch.object(execution, "_LocalProcess", side_effect=spawn),
            patch.object(execution.os, "getpgrp", side_effect=lambda: processes[0].pid),
            patch.object(execution.os, "killpg") as killpg,
        ):
            receipt = self.execute("print('safe')")
        killpg.assert_not_called()
        self.assertEqual(receipt.outcome, "blocked")
        self.assertIn("unsafe process group", receipt.detail)
        self.assertEqual(receipt.stdout, b"safe\n")

    def test_spawn_time_is_deducted_from_command_allowance(self) -> None:
        clock = time.monotonic_ns()
        # Spawn is modeled as having spent the entire allowance. Real fixture
        # startup must not receive a fresh one-second communicate budget.
        with patch.object(
            execution,
            "monotonic_ns",
            side_effect=[clock, clock + 2_000_000_000] + [clock + 2_100_000_000] * 10,
        ):
            receipt = self.execute("import time; time.sleep(0.2)", seconds=1)
        self.assertEqual(receipt.outcome, "timed_out")
        self.assertEqual(receipt.usage.seconds, 2.1)

    def test_cleanup_drain_error_preserves_timeout_snapshot_and_reaps(self) -> None:
        real_communicate = execution.subprocess.Popen.communicate
        calls = []

        def communicate(process, *args, **kwargs):
            calls.append(process)
            if len(calls) == 2:
                raise OSError("fixture drain failed")
            return real_communicate(process, *args, **kwargs)

        with patch.object(execution._LocalProcess, "communicate", new=communicate):
            receipt = self.execute(
                "import sys, time; print('partial', flush=True); "
                "print('original-error', file=sys.stderr, flush=True); time.sleep(20)"
            )
        self.assertEqual(receipt.outcome, "timed_out")
        self.assertEqual(receipt.stdout, b"partial\n")
        self.assertEqual(receipt.stderr, b"original-error\n")
        self.assertIn("output drain: fixture drain failed", receipt.detail)
        with self.assertRaises(ChildProcessError):
            os.waitpid(calls[0].pid, os.WNOHANG)

    def test_reap_error_is_explicit_without_losing_command_output(self) -> None:
        real_wait = execution._LocalProcess.wait
        real_communicate = execution.subprocess.Popen.communicate
        drains = []

        def communicate(process, *args, **kwargs):
            result = real_communicate(process, *args, **kwargs)
            drains.append(result)
            return result

        def wait(process, *args, **kwargs):
            if len(drains) == 2:
                raise OSError("fixture reap failed")
            return real_wait(process, *args, **kwargs)

        with (
            patch.object(execution._LocalProcess, "wait", new=wait),
            patch.object(execution._LocalProcess, "communicate", new=communicate),
        ):
            receipt = self.execute("print('completed')")
        self.assertEqual(receipt.outcome, "blocked")
        self.assertIsNone(receipt.return_code)
        self.assertEqual(receipt.stdout, b"completed\n")
        self.assertIn("leader reap: fixture reap failed", receipt.detail)

    def test_kill_error_is_reported_and_direct_child_is_reaped(self) -> None:
        real_killpg = os.killpg

        def killpg(pgid, sig):
            result = real_killpg(pgid, sig)
            if sig == signal.SIGKILL:
                raise PermissionError("fixture KILL failure")
            return result

        with patch.object(execution.os, "killpg", side_effect=killpg):
            receipt = self.execute(
                "import os, signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                "print(os.getpid(), flush=True); time.sleep(20)"
            )
        self.assertEqual(receipt.outcome, "timed_out")
        self.assertIn("KILL: fixture KILL failure", receipt.detail)
        with self.assertRaises(ChildProcessError):
            os.waitpid(int(receipt.stdout), os.WNOHANG)

    def test_group_leader_is_not_reaped_before_last_group_signal(self) -> None:
        real_killpg = os.killpg
        observations = []

        def killpg(pgid, sig):
            # WNOWAIT observes the child without stealing executor ownership.
            try:
                os.waitid(os.P_PID, pgid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            except ChildProcessError:
                observations.append("already reaped")
            return real_killpg(pgid, sig)

        with patch.object(execution.os, "killpg", side_effect=killpg):
            receipt = self.execute("print('done')")
        self.assertEqual(receipt.outcome, "succeeded")
        self.assertEqual(observations, [], "PGID must stay reserved until last signal")

    def test_cleanup_interrupt_still_kills_and_reaps_before_propagating(self) -> None:
        real_sleep = time.sleep
        interrupted = False

        def sleep(seconds):
            nonlocal interrupted
            if seconds == 0.15 and not interrupted:
                interrupted = True
                raise KeyboardInterrupt("fixture interruption")
            real_sleep(seconds)

        with patch.object(execution, "sleep", side_effect=sleep):
            with self.assertRaisesRegex(KeyboardInterrupt, "fixture interruption"):
                self.execute(self.child_fixture(ignore_term=True))
        self.assert_no_delayed_marker()

    def test_sigchld_auto_reaping_blocks_before_spawn(self) -> None:
        with (
            patch.object(execution.signal, "getsignal", return_value=signal.SIG_IGN),
            patch.object(execution, "_LocalProcess") as spawn,
        ):
            receipt = self.execute("raise AssertionError('must not execute')")
        spawn.assert_not_called()
        self.assertEqual(receipt.outcome, "blocked")

    def test_missing_waitid_blocks_before_spawn(self) -> None:
        with (
            patch.object(execution.os, "waitid", None),
            patch.object(execution, "_LocalProcess") as spawn,
        ):
            receipt = self.execute("raise AssertionError('must not execute')")
        spawn.assert_not_called()
        self.assertEqual(receipt.outcome, "blocked")

    def test_parent_exit_with_inherited_pipe_still_times_out(self) -> None:
        script = self.child_fixture(ignore_term=True, parent_exits=True).replace(
            "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL",
            "stdout=None, stderr=None",
        )
        receipt = self.execute(script)
        self.assertEqual(receipt.outcome, "timed_out")
        self.assertEqual(receipt.stdout, b"parent-ready\n")
        self.assertEqual(receipt.stderr, b"partial-error\n")
        self.assert_no_delayed_marker()

    @unittest.skipUnless(sys.platform == "darwin", "Darwin zombie-only EPERM")
    def test_zombie_group_probe_failure_is_not_cleanup_success(self) -> None:
        real_run = execution.subprocess.run

        def run(argv, *args, **kwargs):
            if argv[0] == "/bin/ps":
                raise execution.subprocess.TimeoutExpired(argv, 0.2)
            return real_run(argv, *args, **kwargs)

        with patch.object(execution.subprocess, "run", side_effect=run):
            receipt = self.execute("print('completed')")
        self.assertEqual(receipt.outcome, "blocked")
        self.assertIn("state probe failed", receipt.detail)
        self.assertEqual(receipt.stdout, b"completed\n")

    def test_communicate_interrupt_keeps_identity_until_group_cleanup(self) -> None:
        real_select = execution.subprocess._PopenSelector.select
        interrupted = False
        real_killpg = os.killpg
        observations = []
        processes = []
        real_spawn = execution._LocalProcess

        def spawn(*args, **kwargs):
            process = real_spawn(*args, **kwargs)
            processes.append(process)
            return process

        def select(selector, timeout=None):
            nonlocal interrupted
            if not interrupted:
                interrupted = True
                deadline = time.monotonic() + 2
                while (
                    not (self.project / "child.pid").exists()
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.005)
                time.sleep(0.05)
                raise KeyboardInterrupt("communicate fixture interruption")
            return real_select(selector, timeout)

        def killpg(pgid, sig):
            try:
                os.waitid(os.P_PID, pgid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            except ChildProcessError:
                observations.append("already reaped")
            return real_killpg(pgid, sig)

        with (
            patch.object(execution, "_LocalProcess", side_effect=spawn),
            patch.object(execution.subprocess._PopenSelector, "select", new=select),
            patch.object(execution.os, "killpg", side_effect=killpg),
        ):
            with self.assertRaisesRegex(KeyboardInterrupt, "communicate fixture"):
                self.execute(self.child_fixture(ignore_term=True, parent_exits=True))
        self.assert_no_delayed_marker()
        with self.assertRaises(ChildProcessError):
            os.waitpid(processes[0].pid, os.WNOHANG)
        self.assertEqual(observations, [])

    def test_kill_interrupt_retries_cleanup_and_preserves_original_exception(
        self,
    ) -> None:
        real_killpg = os.killpg
        pids = []
        interrupted = False

        def killpg(pgid, sig):
            nonlocal interrupted
            pids.append(pgid)
            if sig == signal.SIGKILL and not interrupted:
                interrupted = True
                raise KeyboardInterrupt("KILL fixture interruption")
            return real_killpg(pgid, sig)

        with patch.object(execution.os, "killpg", side_effect=killpg):
            with self.assertRaisesRegex(KeyboardInterrupt, "KILL fixture"):
                self.execute(self.child_fixture(ignore_term=True))
        self.assert_no_delayed_marker()
        with self.assertRaises(ChildProcessError):
            os.waitpid(pids[0], os.WNOHANG)

    def test_timeout_reaps_direct_child(self) -> None:
        receipt = self.execute(
            "import os, time; print(os.getpid(), flush=True); time.sleep(20)"
        )
        self.assertEqual(receipt.outcome, "timed_out")
        pid = int(receipt.stdout)
        with self.assertRaises(ChildProcessError):
            os.waitpid(pid, os.WNOHANG)

    def test_parent_exit_does_not_leave_background_child(self) -> None:
        receipt = self.execute(self.child_fixture(parent_exits=True), seconds=3)
        self.assertEqual(receipt.outcome, "succeeded")
        self.assertEqual(receipt.return_code, 0)
        self.assertEqual(receipt.stdout, b"parent-ready\n")
        self.assert_no_delayed_marker()

    def test_timeout_kills_descendant_with_closed_stdio(self) -> None:
        receipt = self.execute(self.child_fixture())
        self.assertEqual(receipt.outcome, "timed_out")
        self.assertIsNone(receipt.return_code)
        self.assertEqual(receipt.stdout, b"parent-ready\n")
        self.assertEqual(receipt.stderr, b"partial-error\n")
        self.assert_no_delayed_marker()
