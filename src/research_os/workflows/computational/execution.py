from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from time import monotonic_ns, sleep
from typing import Mapping, Protocol, Sequence

from .budget import BudgetUsage

_FULL_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_ATTEMPT_FILE = re.compile(r"^attempt-([0-9]{4,})\.")
_DIRECTORY_FLAGS = (
    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
)


@dataclass(frozen=True)
class AttemptContext:
    attempt: int
    round: int
    command: tuple[str, ...]
    cwd: str = "."
    environment: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.attempt < 1 or self.round < 1:
            raise ValueError("attempt and round numbers start at one")
        if not self.command or any(
            not isinstance(part, str) or not part for part in self.command
        ):
            raise ValueError(
                "command must be a non-empty sequence of non-empty strings"
            )
        _validate_relative_path(self.cwd, allow_dot=True)
        for key, value in self.environment.items():
            if not isinstance(key, str) or not key or "=" in key or "\x00" in key:
                raise ValueError(
                    "environment variable names must be non-empty and contain no '=' or NUL"
                )
            if not isinstance(value, str) or "\x00" in value:
                raise ValueError(
                    "environment variable values must be strings without NUL"
                )


@dataclass(frozen=True)
class ExecutionReceipt:
    outcome: str
    return_code: int | None
    usage: BudgetUsage
    stdout: bytes
    stderr: bytes
    detail: str | None = None

    def __post_init__(self) -> None:
        if self.outcome not in {"succeeded", "failed", "timed_out", "blocked"}:
            raise ValueError("unsupported execution outcome")
        if self.outcome == "succeeded" and self.return_code != 0:
            raise ValueError("succeeded execution requires return code zero")
        if self.outcome == "failed" and (
            self.return_code is None or self.return_code == 0
        ):
            raise ValueError("failed execution requires a non-zero return code")
        if self.outcome in {"timed_out", "blocked"} and self.return_code is not None:
            raise ValueError("non-completed execution cannot have a return code")
        if not isinstance(self.stdout, bytes) or not isinstance(self.stderr, bytes):
            raise TypeError("stdout and stderr must be bytes")


class Executor(Protocol):
    def __call__(
        self,
        project: Path,
        context: AttemptContext,
        remaining: BudgetUsage,
    ) -> ExecutionReceipt: ...


def execute_local_command(
    project: Path,
    context: AttemptContext,
    remaining: BudgetUsage,
) -> ExecutionReceipt:
    """Execute one argv-only local CPU command within the project boundary."""
    project = project.resolve(strict=True)
    cwd = _resolve_relative(project, context.cwd, allow_dot=True, strict=True)
    if not cwd.is_dir():
        raise NotADirectoryError(context.cwd)
    if remaining.attempts < 1 or remaining.rounds < 1:
        return ExecutionReceipt(
            outcome="blocked",
            return_code=None,
            usage=BudgetUsage(),
            stdout=b"",
            stderr=b"",
            detail="attempt or round budget unavailable",
        )
    if remaining.seconds <= 0:
        return ExecutionReceipt(
            outcome="timed_out",
            return_code=None,
            usage=BudgetUsage(),
            stdout=b"",
            stderr=b"",
            detail="no time budget remaining",
        )

    if not (
        sys.platform in {"darwin", "linux"}
        and os.name == "posix"
        and all(
            callable(getattr(os, name, None))
            for name in ("setsid", "killpg", "getpgrp", "waitid")
        )
        and all(
            hasattr(os, name) for name in ("WNOWAIT", "WEXITED", "WNOHANG", "P_PID")
        )
        and signal.getsignal(signal.SIGCHLD) != signal.SIG_IGN
    ):
        return ExecutionReceipt(
            outcome="blocked",
            return_code=None,
            usage=BudgetUsage(),
            stdout=b"",
            stderr=b"",
            detail="safe local process-group cleanup unavailable on this platform",
        )

    # Do not leak provider credentials or unrelated host state into experiments.
    # Callers must opt in to every non-PATH variable via context.environment.
    environment = {"PATH": os.environ.get("PATH", os.defpath)}
    environment.update(context.environment)
    started = monotonic_ns()
    try:
        process = _LocalProcess(
            list(context.command),
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return ExecutionReceipt(
            outcome="blocked",
            return_code=None,
            usage=BudgetUsage(seconds=(monotonic_ns() - started) / 1_000_000_000),
            stdout=b"",
            stderr=str(exc).encode("utf-8", errors="replace"),
            detail=f"local command spawn failed: {exc}",
        )

    stdout, stderr = b"", b""
    detail = None
    try:
        # Popen startup consumes the same wall-clock budget as execution.
        allowance = remaining.seconds - (monotonic_ns() - started) / 1_000_000_000
        stdout, stderr = process.communicate(timeout=max(0.0, allowance))
        outcome = "succeeded" if process.returncode == 0 else "failed"
        return_code = process.returncode
    except subprocess.TimeoutExpired as exc:
        outcome, return_code = "timed_out", None
        stdout, stderr = _as_bytes(exc.stdout), _as_bytes(exc.stderr)
        detail = "local command exceeded remaining seconds budget"
    except (OSError, ValueError) as exc:
        outcome, return_code = "blocked", None
        detail = f"local command communication failed: {exc}"
    except BaseException as original:
        try:
            _cleanup_local_process(process, stdout, stderr)
        except BaseException as cleanup_error:
            original.add_note(f"cleanup interrupted: {cleanup_error}")
        raise

    # Clean even a successful leader's group: background children may close
    # their stdio and outlive communicate() without triggering its timeout.
    stdout, stderr, errors = _cleanup_local_process(process, stdout, stderr)
    if errors:
        cleanup_detail = "process-group cleanup unconfirmed: " + "; ".join(errors)
        detail = f"{detail}; {cleanup_detail}" if detail else cleanup_detail
        if outcome != "timed_out":
            outcome, return_code = "blocked", None

    receipt = ExecutionReceipt(
        outcome=outcome,
        return_code=return_code,
        usage=BudgetUsage(seconds=(monotonic_ns() - started) / 1_000_000_000),
        stdout=stdout,
        stderr=stderr,
        detail=detail,
    )
    return (
        _apply_usage_receipt(receipt, context.environment)
        if outcome in {"succeeded", "failed"}
        else receipt
    )


class _LocalProcess(subprocess.Popen[bytes]):
    """Keep the leader waitable (and its PID reserved) until group signalling ends.

    communicate normally calls wait and reaps too early. WNOWAIT observes exit
    instead; only cleanup releases ownership to Popen.wait. No other thread or
    SIGCHLD handler may reap this executor's children.
    """

    def __init__(self, *args, **kwargs):
        self.group_cleanup_pending = True
        super().__init__(*args, **kwargs)

    def wait(self, timeout=None):
        return self._wait(timeout)

    def _wait(self, timeout):
        # communicate's KeyboardInterrupt path calls _wait directly.
        if not self.group_cleanup_pending:
            return super()._wait(timeout)
        deadline = None if timeout is None else monotonic_ns() + int(timeout * 1e9)
        while True:
            status = os.waitid(os.P_PID, self.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            if status is not None:
                self.returncode = (
                    status.si_status
                    if status.si_code == os.CLD_EXITED
                    else -status.si_status
                )
                return self.returncode
            if deadline is not None and monotonic_ns() >= deadline:
                raise subprocess.TimeoutExpired(self.args, timeout)
            sleep(0.005)


def _signal_local_group(pgid: int, sig: int) -> bool:
    # start_new_session establishes pgid == child's pid before Popen returns.
    # Never derive it from getpgid after the leader may have exited.
    if pgid <= 1 or pgid == os.getpgrp():
        raise OSError("refusing to signal unsafe process group")
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        return False
    except PermissionError as exc:
        # Darwin reports EPERM (not ESRCH) for a group containing only zombies.
        # Keep the unreaped leader as the identity anchor while confirming this
        # with the trusted OS process table. Any uncertainty stays fail-closed.
        if sys.platform != "darwin" or exc.errno != errno.EPERM:
            raise
        status = os.waitid(os.P_PID, pgid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        if status is None:
            raise
        try:
            snapshot = subprocess.run(
                ["/bin/ps", "-g", str(pgid), "-o", "stat="],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=0.2,
                env={"PATH": os.defpath, "LC_ALL": "C"},
            )
        except subprocess.SubprocessError as probe_error:
            raise OSError(
                f"process-group state probe failed: {probe_error}"
            ) from probe_error
        states = snapshot.stdout.split()
        if (
            snapshot.returncode != 0
            or not states
            or any(not state.startswith(b"Z") for state in states)
        ):
            raise
        return False
    return True


def _cleanup_local_process(
    process: subprocess.Popen[bytes], stdout: bytes, stderr: bytes
) -> tuple[bytes, bytes, list[str]]:
    """Bounded TERM/KILL cleanup of our session, then drain and reap the leader.

    This is not a sandbox: descendants that deliberately create another session
    are outside the group. Never interpret the leader exiting or pipe EOF as
    proof that the group has gone away.
    """
    errors: list[str] = []
    deadline = monotonic_ns() + 1_000_000_000
    interrupted = None
    group_exists = True
    try:
        group_exists = _signal_local_group(process.pid, signal.SIGTERM)
        if group_exists:
            sleep(0.15)
    except OSError as exc:
        errors.append(f"TERM: {exc}")
    except BaseException as exc:
        interrupted = exc
    try:
        if group_exists:
            _signal_local_group(process.pid, signal.SIGKILL)
    except OSError as exc:
        errors.append(f"KILL: {exc}")
        # Group cleanup remains unconfirmed, but still try to reap our child.
        try:
            os.kill(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError as exc:
            errors.append(f"leader KILL: {exc}")
    except BaseException as exc:
        interrupted = interrupted or exc
        # A signal delivery interrupted before the syscall must not bypass the
        # final group kill. Retry once while the leader still reserves its PID.
        try:
            _signal_local_group(process.pid, signal.SIGKILL)
        except OSError as retry_error:
            errors.append(f"KILL retry: {retry_error}")
            try:
                os.kill(process.pid, signal.SIGKILL)
            except OSError as leader_error:
                errors.append(f"leader KILL: {leader_error}")
        except BaseException as retry_error:
            interrupted.add_note(f"KILL retry interrupted: {retry_error}")
    finally:
        # No group signal may occur after this point. The observed exit code
        # did not mean waitpid had reaped the leader; let Popen do that now.
        process.group_cleanup_pending = False
        process.returncode = None

    def remaining_cleanup() -> float:
        return max(0.0, (deadline - monotonic_ns()) / 1_000_000_000)

    try:
        captured_stdout, captured_stderr = process.communicate(
            timeout=remaining_cleanup()
        )
        if captured_stdout is not None:
            stdout = captured_stdout
        if captured_stderr is not None:
            stderr = captured_stderr
    except subprocess.TimeoutExpired as exc:
        # communicate retries return cumulative snapshots, not new chunks.
        if exc.stdout is not None:
            stdout = _as_bytes(exc.stdout)
        if exc.stderr is not None:
            stderr = _as_bytes(exc.stderr)
        errors.append("output drain timed out")
    except (OSError, ValueError) as exc:
        errors.append(f"output drain: {exc}")
    except BaseException as exc:
        interrupted = interrupted or exc
    finally:
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                try:
                    stream.close()
                except OSError as exc:
                    errors.append(f"pipe close: {exc}")
        try:
            process.wait(timeout=remaining_cleanup())
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"leader reap: {exc}")
    if interrupted is not None:
        raise interrupted
    return stdout, stderr, errors


class AttemptLedger:
    """Append-only attempt records with immutable logs and artifact snapshots."""

    def __init__(self, project: Path, directory: str):
        self.project = project.resolve(strict=True)
        _validate_relative_path(directory)
        self.relative_directory = directory

    def next_attempt(self) -> int:
        try:
            names = _secure_list_directory(self.project, self.relative_directory)
        except FileNotFoundError:
            return 1
        greatest = 0
        for name in names:
            match = _ATTEMPT_FILE.match(name)
            if match:
                greatest = max(greatest, int(match.group(1)))
        return greatest + 1

    def append(
        self,
        *,
        workflow: str,
        context: AttemptContext,
        receipt: ExecutionReceipt,
        cumulative_usage: BudgetUsage,
        revision: str,
        inputs: Sequence[Mapping[str, object]],
        configuration: Mapping[str, object] | None = None,
        workflow_outcome: str | None = None,
        artifacts: Sequence[tuple[str, str, bytes]] = (),
    ) -> dict[str, object]:
        validate_full_commit(revision)
        stem = f"attempt-{context.attempt:04d}"
        stdout_name = f"{self.relative_directory}/{stem}.stdout"
        stderr_name = f"{self.relative_directory}/{stem}.stderr"
        record_name = f"{self.relative_directory}/{stem}.json"
        artifact_names = [
            f"{self.relative_directory}/{stem}.artifact-{index:02d}"
            for index in range(1, len(artifacts) + 1)
        ]
        paths = [stdout_name, stderr_name, *artifact_names, record_name]
        if len(set(paths)) != len(paths):
            raise FileExistsError("attempt ledger paths must be distinct")

        _secure_write_exclusive(self.project, stdout_name, receipt.stdout)
        _secure_write_exclusive(self.project, stderr_name, receipt.stderr)
        artifact_records: list[dict[str, object]] = []
        for snapshot_name, (role, source_path, data) in zip(
            artifact_names, artifacts, strict=True
        ):
            _validate_relative_path(source_path)
            _secure_write_exclusive(self.project, snapshot_name, data)
            artifact_records.append(
                {
                    "role": role,
                    "source_path": source_path,
                    "snapshot": _file_reference_bytes(snapshot_name, data),
                }
            )
        record = {
            "contract": {"name": "research-os/attempt-record", "version": "1.0.0"},
            "workflow": workflow,
            "attempt": context.attempt,
            "round": context.round,
            "revision": revision,
            "inputs": [dict(item) for item in inputs],
            "configuration": dict(configuration or {}),
            "command": list(context.command),
            "cwd": context.cwd,
            "environment_keys": sorted(context.environment),
            "execution_outcome": receipt.outcome,
            "workflow_outcome": workflow_outcome or receipt.outcome,
            "return_code": receipt.return_code,
            "detail": receipt.detail,
            "usage": receipt.usage.as_dict(),
            "cumulative_usage": cumulative_usage.as_dict(),
            "stdout": _file_reference_bytes(stdout_name, receipt.stdout),
            "stderr": _file_reference_bytes(stderr_name, receipt.stderr),
            "artifacts": artifact_records,
        }
        _secure_write_exclusive(self.project, record_name, _json_bytes(record))
        return record

    def records(self) -> list[dict[str, object]]:
        try:
            names = _secure_list_directory(self.project, self.relative_directory)
        except FileNotFoundError:
            return []
        records: list[dict[str, object]] = []
        for name in sorted(names):
            if not name.startswith("attempt-") or not name.endswith(".json"):
                continue
            relative = f"{self.relative_directory}/{name}"
            value = json.loads(_secure_read_bytes(self.project, relative))
            if not isinstance(value, dict):
                raise ValueError(f"attempt record must be an object: {relative}")
            records.append(value)
        return records


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_full_commit(value: str) -> str:
    if not isinstance(value, str) or _FULL_COMMIT.fullmatch(value) is None:
        raise ValueError("pin must use a full 40-character lowercase Git commit")
    return value


def load_pinned_bytes(
    project: Path, relative_path: str, expected_sha256: str, commit: str
) -> bytes:
    root = project.resolve(strict=True)
    validate_full_commit(commit)
    _validate_sha256(expected_sha256)
    working = _secure_read_bytes(root, relative_path)
    actual = hashlib.sha256(working).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"pinned input digest mismatch for {relative_path}")
    committed = _git_blob(root, commit, relative_path)
    if committed != working:
        raise ValueError(
            f"working bytes do not match pinned Git revision for {relative_path}"
        )
    return working


def load_pinned_json(
    project: Path, relative_path: str, expected_sha256: str, commit: str
) -> dict[str, object]:
    data = load_pinned_bytes(project, relative_path, expected_sha256, commit)
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON input must be an object: {relative_path}")
    return value


def ensure_outputs_available(project: Path, paths: Sequence[str]) -> None:
    root = project.resolve(strict=True)
    for path in paths:
        _validate_relative_path(path)
    if len(set(paths)) != len(paths):
        raise FileExistsError("workflow outputs must use distinct paths")
    for path in paths:
        try:
            _secure_lstat(root, path)
        except FileNotFoundError:
            continue
        raise FileExistsError(f"workflow output already exists: {path}")


def write_outputs_exclusive(project: Path, outputs: Mapping[str, bytes]) -> None:
    root = project.resolve(strict=True)
    names = list(outputs)
    for name in names:
        _validate_relative_path(name)
    if len(set(names)) != len(names):
        raise FileExistsError("workflow outputs must use distinct paths")
    created: list[str] = []
    try:
        for name in names:
            _secure_write_exclusive(root, name, outputs[name])
            created.append(name)
    except Exception:
        for name in reversed(created):
            try:
                _secure_unlink(root, name)
            except FileNotFoundError:
                pass
        raise


def read_project_bytes(project: Path, relative_path: str) -> bytes:
    return _secure_read_bytes(project.resolve(strict=True), relative_path)


def remove_project_file(project: Path, relative_path: str) -> None:
    _secure_unlink(project.resolve(strict=True), relative_path)


def json_bytes(value: object) -> bytes:
    return _json_bytes(value)


def _git_blob(project: Path, commit: str, relative_path: str) -> bytes:
    _validate_relative_path(relative_path)
    try:
        completed = subprocess.run(
            ["git", "-C", str(project), "show", f"{commit}:{relative_path}"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("unable to resolve pinned Git revision") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(
            f"unable to resolve pinned Git bytes for {relative_path}: {detail}"
        )
    return completed.stdout


def _validate_sha256(value: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(c not in "0123456789abcdef" for c in value)
    ):
        raise ValueError(
            "input SHA-256 pin must be 64 lowercase hexadecimal characters"
        )


def _file_reference_bytes(path: str, data: bytes) -> dict[str, str]:
    return {"path": path, "sha256": hashlib.sha256(data).hexdigest()}


def _resolve_relative(
    project: Path,
    value: str,
    *,
    allow_dot: bool = False,
    strict: bool = False,
) -> Path:
    _validate_relative_path(value, allow_dot=allow_dot)
    path = (project / value).resolve(strict=strict)
    try:
        path.relative_to(project)
    except ValueError as exc:
        raise ValueError("path escapes project") from exc
    return path


def _validate_relative_path(value: str, *, allow_dot: bool = False) -> None:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("path must be a safe project-relative path")
    if allow_dot and value == ".":
        return
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError("path must be a safe project-relative path")
    if any(part.casefold() == ".git" for part in path.parts):
        raise ValueError("path cannot enter .git")


def _open_root(project: Path) -> int:
    return os.open(project, _DIRECTORY_FLAGS)


def _open_parent(project: Path, relative_path: str, *, create: bool) -> tuple[int, str]:
    _validate_relative_path(relative_path)
    parts = PurePosixPath(relative_path).parts
    descriptor = _open_root(project)
    try:
        for part in parts[:-1]:
            if create:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=descriptor)
                except FileExistsError:
                    pass
            child = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor, parts[-1]
    except Exception:
        os.close(descriptor)
        raise


def _open_directory(project: Path, relative_directory: str) -> int:
    _validate_relative_path(relative_directory)
    descriptor = _open_root(project)
    try:
        for part in PurePosixPath(relative_directory).parts:
            child = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _secure_list_directory(project: Path, relative_directory: str) -> list[str]:
    descriptor = _open_directory(project, relative_directory)
    try:
        return os.listdir(descriptor)
    finally:
        os.close(descriptor)


def _secure_lstat(project: Path, relative_path: str) -> os.stat_result:
    descriptor, name = _open_parent(project, relative_path, create=False)
    try:
        return os.stat(name, dir_fd=descriptor, follow_symlinks=False)
    finally:
        os.close(descriptor)


def _secure_read_bytes(project: Path, relative_path: str) -> bytes:
    descriptor, name = _open_parent(project, relative_path, create=False)
    file_descriptor: int | None = None
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        file_descriptor = os.open(name, flags, dir_fd=descriptor)
        status = os.fstat(file_descriptor)
        if not _is_regular(status):
            raise ValueError(f"project path is not a regular file: {relative_path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(descriptor)


def _secure_write_exclusive(project: Path, relative_path: str, data: bytes) -> None:
    descriptor, name = _open_parent(project, relative_path, create=True)
    file_descriptor: int | None = None
    created = False
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        file_descriptor = os.open(name, flags, 0o600, dir_fd=descriptor)
        created = True
        view = memoryview(data)
        while view:
            written = os.write(file_descriptor, view)
            view = view[written:]
        os.fsync(file_descriptor)
    except Exception:
        if file_descriptor is not None:
            os.close(file_descriptor)
            file_descriptor = None
        if created:
            try:
                os.unlink(name, dir_fd=descriptor)
            except FileNotFoundError:
                pass
        raise
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        os.close(descriptor)


def _secure_unlink(project: Path, relative_path: str) -> None:
    descriptor, name = _open_parent(project, relative_path, create=False)
    try:
        os.unlink(name, dir_fd=descriptor)
    finally:
        os.close(descriptor)


def _is_regular(status: os.stat_result) -> bool:
    import stat

    return stat.S_ISREG(status.st_mode)


def _apply_usage_receipt(
    receipt: ExecutionReceipt, environment: Mapping[str, str]
) -> ExecutionReceipt:
    names = {
        "cost_usd": "RESEARCH_OS_USAGE_COST_USD",
        "tokens": "RESEARCH_OS_USAGE_TOKENS",
        "gpu_hours": "RESEARCH_OS_USAGE_GPU_HOURS",
    }
    supplied = [name for name in names.values() if name in environment]
    if not supplied:
        return receipt
    if len(supplied) != len(names):
        raise ValueError(
            "usage receipt must provide cost, tokens, and GPU-hours together"
        )
    try:
        reported = BudgetUsage(
            seconds=receipt.usage.seconds,
            cost_usd=float(environment[names["cost_usd"]]),
            tokens=int(environment[names["tokens"]]),
            gpu_hours=float(environment[names["gpu_hours"]]),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("usage receipt values are invalid") from exc
    return ExecutionReceipt(
        outcome=receipt.outcome,
        return_code=receipt.return_code,
        usage=reported,
        stdout=receipt.stdout,
        stderr=receipt.stderr,
        detail=receipt.detail,
    )


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _as_bytes(value: bytes | str | None) -> bytes:
    if value is None:
        return b""
    return (
        value if isinstance(value, bytes) else value.encode("utf-8", errors="replace")
    )
