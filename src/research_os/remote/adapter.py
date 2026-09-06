from __future__ import annotations

import base64
import fcntl
import hashlib
import json
import math
import os
import re
import shlex
import shutil
import subprocess
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic, sleep, time
from typing import Callable, Mapping

from research_os.workflows.computational.budget import BudgetUsage
from research_os.workflows.computational.execution import (
    AttemptContext,
    ExecutionReceipt,
)

from .config import (
    ConfigurationError,
    RemoteConfig,
    digest,
    full_digest,
    json_bytes,
    relative_path,
)

TERMINAL = {"succeeded", "failed", "cancelled", "timed_out"}
ACTIVE = {"submitted", "queued", "running", "cancel_requested"}
KNOWN = TERMINAL | ACTIVE | {"available", "blocked", "unknown", "retrieved"}


@dataclass(frozen=True)
class RemoteReceipt:
    operation: str
    state: str
    exit_code: int
    detail: str
    attempt: int | None = None
    token: str | None = None
    job: Mapping[str, object] | None = None
    evidence: Mapping[str, object] = field(default_factory=dict)
    real_environment: str = "NOT_EVALUATED"

    @property
    def hard_stop(self) -> bool:
        return self.state in {"unknown", "blocked", "failed", "timed_out", "cancelled"}

    def as_dict(self) -> dict[str, object]:
        return dict(
            asdict(self),
            contract={"name": "research-os/remote-receipt", "version": "1.0.0"},
            hard_stop=self.hard_stop,
        )


class TransportUnavailable(RuntimeError):
    pass


class SSHTransport:
    """One authenticated OpenSSH invocation; remote command has no user argv.

    SSH reparses its command through the login shell. Quote every fixed Python
    argument; send research argv/environment solely through JSON stdin.
    """

    def __init__(self, config: RemoteConfig):
        self.config = config

    def __call__(
        self, request: Mapping[str, object], timeout: float
    ) -> Mapping[str, object]:
        config = self.config
        executable = shutil.which(config.ssh_executable)
        if executable is None:
            raise TransportUnavailable("SSH executable unavailable")
        source = Path(__file__).with_name("worker.py").read_text()
        target = (config.user + "@" if config.user else "") + config.host
        remote_command = shlex.join([config.python_executable, "-c", source])
        argv = [
            executable,
            "-F",
            "/dev/null",
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=yes",
            "-o",
            "ClearAllForwardings=yes",
            "-o",
            "ControlMaster=no",
            "-o",
            "ControlPath=none",
            "-o",
            "ConnectionAttempts=1",
            "-o",
            "ConnectTimeout=" + str(max(1, math.ceil(timeout))),
            "-p",
            str(config.port),
            "--",
            target,
            remote_command,
        ]
        payload = dict(request)
        if request["operation"] == "submit":
            payload["worker_source"] = source
        try:
            completed = subprocess.run(
                argv,
                input=json_bytes(payload),
                capture_output=True,
                check=False,
                timeout=timeout,
            )
        except OSError as exc:
            raise TransportUnavailable(str(exc)) from exc
        if completed.returncode:
            raise TransportUnavailable(
                f"SSH/remote executable exited {completed.returncode}: "
                + completed.stderr[:2048].decode(errors="replace")
            )
        if len(completed.stdout) > config.max_transfer_bytes * 2 + 16384:
            raise ValueError("remote response exceeds transfer limit")
        return json.loads(completed.stdout)


class LedgerError(ValueError):
    pass


def _exclusive(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(fd)
    finally:
        os.close(fd)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _confined(root: Path, value: str) -> Path:
    relative_path(value)
    current = root
    for part in Path(value).parts:
        current = current / part
        if current.is_symlink():
            raise LedgerError("symlink in local path")
    current.resolve().relative_to(root)
    return current


class RemoteAdapter:
    """Persistent single-ledger capability boundary. Never automatically resubmit.

    A ledger belongs to one explicit run. Durable intent precedes the side effect;
    missing/corrupt receipt and unknown state block ALL later attempts. Status can
    still inspect the original identity, but unknown is sticky, never auto-cleared.
    """

    def __init__(
        self,
        project: Path,
        config: RemoteConfig | None,
        *,
        ledger_directory: str = ".research-os/remote-attempts",
        transport: Callable | None = None,
    ):
        self.project = project.resolve(strict=True)
        self.config = RemoteConfig.from_mapping(config.as_dict()) if config else None
        self.directory = _confined(self.project, ledger_directory)
        self.transport = transport or (
            SSHTransport(self.config) if self.config else None
        )
        self.config_digest = digest(self.config.as_dict()) if self.config else None

    @contextmanager
    def _locked(self):
        _confined(self.project, self.directory.relative_to(self.project).as_posix())
        self.directory.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(
            self.directory / ".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
        )
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            os.close(descriptor)

    def _events(self) -> list[dict]:
        events = []
        previous = None
        for path in sorted(self.directory.iterdir()):
            if path.name == ".lock":
                continue
            if path.is_symlink() or not re.fullmatch(
                r"event-[0-9]{8}\.json", path.name
            ):
                raise LedgerError("unexpected or symlink ledger entry")
            if path.name != f"event-{len(events) + 1:08d}.json":
                raise LedgerError("ledger sequence gap")
            try:
                event = json.loads(path.read_bytes())
                claimed = event.pop("sha256")
                if claimed != digest(event) or event["previous"] != previous:
                    raise LedgerError("ledger hash chain mismatch")
                if event["configuration_sha256"] != self.config_digest:
                    raise LedgerError("pinned configuration changed")
                previous = claimed
                event["sha256"] = claimed
                events.append(event)
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                raise LedgerError("incomplete/corrupt attempt ledger") from exc
        return events

    def _append(self, events: list[dict], kind: str, token: str, value: dict) -> dict:
        event = {
            "contract": {
                "name": "research-os/remote-attempt-event",
                "version": "1.0.0",
            },
            "sequence": len(events) + 1,
            "previous": events[-1]["sha256"] if events else None,
            "configuration_sha256": self.config_digest,
            "kind": kind,
            "token": token,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "value": value,
        }
        event["sha256"] = digest(event)
        _exclusive(
            self.directory / f"event-{len(events) + 1:08d}.json", json_bytes(event)
        )
        events.append(event)
        return event

    def records(self) -> list[dict]:
        with self._locked():
            return self._events()

    def _receipt(
        self,
        operation,
        state,
        detail="",
        *,
        intent=None,
        job=None,
        evidence=None,
        exit_code=None,
    ):
        code = (
            exit_code
            if exit_code is not None
            else (
                3
                if state == "blocked"
                else 1
                if state in {"unknown", "failed", "cancelled", "timed_out"}
                else 0
            )
        )
        return RemoteReceipt(
            operation,
            state,
            code,
            detail,
            intent.get("attempt") if intent else None,
            intent.get("token") if intent else None,
            job,
            evidence or {},
        )

    def _call(self, operation: str, *, timeout=None, **extra) -> dict:
        if self.config is None or self.transport is None:
            raise TransportUnavailable("remote configuration absent")
        if digest(self.config.as_dict()) != self.config_digest:
            raise LedgerError("configuration mutated")
        request = {"operation": operation, "config": self.config.as_dict(), **extra}
        response = self.transport(
            request,
            min(timeout or self.config.timeout_seconds, self.config.timeout_seconds),
        )
        if (
            not isinstance(response, Mapping)
            or response.get("protocol") != "research-os/remote-wire/1"
            or response.get("operation") != operation
            or response.get("token") != extra.get("token")
            or response.get("state") not in KNOWN
        ):
            raise ValueError("invalid or ambiguous remote receipt")
        return dict(response)

    def probe(self) -> RemoteReceipt:
        try:
            result = self._call("probe")
            if result["state"] not in {"available", "blocked"}:
                raise ValueError("invalid capability response")
            return self._receipt(
                "probe", result["state"], result.get("detail", ""), evidence=result
            )
        except (TransportUnavailable, subprocess.TimeoutExpired) as exc:
            return self._receipt("probe", "blocked", str(exc))
        except (ValueError, OSError) as exc:
            return self._receipt("probe", "unknown", str(exc))

    def _intents(self, events):
        return [event["value"] for event in events if event["kind"] == "intent"]

    def _state(self, events, intent):
        receipts = [
            event["value"]
            for event in events
            if event["token"] == intent["token"] and event["kind"] == "receipt"
        ]
        job = next((receipt["job"] for receipt in receipts if receipt.get("job")), None)
        if not receipts or any(receipt["state"] == "unknown" for receipt in receipts):
            return "unknown", job
        lifecycle = [
            r for r in receipts if r["operation"] in {"submit", "status", "cancel"}
        ]
        return lifecycle[-1]["state"] if lifecycle else "unknown", job

    def _valid_job(self, job, token):
        if (
            not isinstance(job, dict)
            or job.get("token") != token
            or job.get("backend") != self.config.backend
        ):
            raise ValueError("remote job identity mismatch")
        if self.config.backend == "slurm":
            if (
                set(job) != {"backend", "token", "job_id", "job_name"}
                or re.fullmatch(r"[1-9][0-9]*", str(job.get("job_id"))) is None
                or job.get("job_name") != "ros-" + token
            ):
                raise ValueError("invalid SLURM single-job identity")
        else:
            process = job.get("process")
            if (
                set(job) != {"backend", "token", "process"}
                or not isinstance(process, dict)
                or set(process) != {"pid", "start_ticks", "boot_id"}
                or type(process["pid"]) is not int
                or process["pid"] <= 1
                or not isinstance(process["start_ticks"], str)
                or not process["start_ticks"].isdigit()
                or not isinstance(process["boot_id"], str)
                or re.fullmatch(r"[0-9a-f-]{36}", process["boot_id"]) is None
            ):
                raise ValueError("invalid SSH process identity")
        return job

    def submit(self, context: AttemptContext, remaining: BudgetUsage) -> RemoteReceipt:
        deadline = time() + remaining.seconds
        if self.config is None:
            return self._receipt("submit", "blocked", "remote configuration absent")
        try:
            if (
                type(context.attempt) is not int
                or type(context.round) is not int
                or context.attempt < 1
                or context.round < 1
            ):
                raise ConfigurationError("invalid attempt/round")
            relative_path(context.cwd, directory=True)
            if not context.command or any(
                not isinstance(p, str) or not p or "\x00" in p for p in context.command
            ):
                raise ConfigurationError("command must be nonempty argv without NUL")
            if any(
                re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) is None
                or not isinstance(value, str)
                or "\x00" in value
                for key, value in context.environment.items()
            ):
                raise ConfigurationError("invalid environment")
            if remaining.seconds <= 0 or remaining.attempts < 1 or remaining.rounds < 1:
                return self._receipt(
                    "submit",
                    "blocked",
                    "remaining attempt/round/time budget unavailable",
                )
            # No unmetered paid/GPU execution: this profile enforces only CPU walltime.
            if (
                remaining.cost_usd
                or remaining.tokens
                or remaining.gpu_hours
                or self.config.slurm.get("gpus")
            ):
                return self._receipt(
                    "submit",
                    "blocked",
                    "monetary/token/GPU metering unavailable in remote CPU profile",
                )
            with self._locked():
                events = self._events()
                intents = self._intents(events)
                for intent in intents:
                    state, job = self._state(events, intent)
                    if intent["attempt"] == context.attempt or state not in TERMINAL:
                        return self._receipt(
                            "submit",
                            "unknown",
                            "attempt already reserved or unresolved job; never resubmit",
                            intent=intent,
                            job=job,
                        )
                if intents and context.attempt <= max(i["attempt"] for i in intents):
                    raise ConfigurationError("attempt must increase monotonically")
                probe_started = time()
                capability = self.probe()
                probe_finished = time()
                if capability.state != "available":
                    return self._receipt(
                        "submit",
                        capability.state,
                        capability.detail,
                        evidence=capability.as_dict(),
                    )
                remote_clock = capability.evidence.get("remote_epoch_seconds")
                if (
                    type(remote_clock) not in {int, float}
                    or not math.isfinite(remote_clock)
                    or not probe_started - 1 <= remote_clock <= probe_finished + 1
                ):
                    return self._receipt(
                        "submit",
                        "blocked",
                        "remote clock unavailable or skew exceeds one second; deadline not enforceable",
                    )
                if probe_finished >= deadline:
                    return self._receipt(
                        "submit", "blocked", "deadline expired during capability check"
                    )
                intent = {
                    "attempt": context.attempt,
                    "round": context.round,
                    "context": {
                        "attempt": context.attempt,
                        "round": context.round,
                        "command": list(context.command),
                        "cwd": context.cwd,
                        "environment": dict(context.environment),
                    },
                    "configuration": self.config.as_dict(),
                    "remaining": remaining.as_dict(),
                    "ledger": self.directory.relative_to(self.project).as_posix(),
                    "project": str(self.project),
                }
                intent["local_deadline_epoch_seconds"] = deadline
                deadline = remote_clock + max(0, deadline - probe_finished)
                intent["deadline_epoch_seconds"] = deadline
                token = digest(intent)
                intent["token"] = token
                self._append(events, "intent", token, intent)
                try:
                    result = self._call(
                        "submit",
                        token=token,
                        context=intent["context"],
                        seconds=remaining.seconds,
                        deadline_epoch_seconds=deadline,
                    )
                    job = self._valid_job(result.get("job"), token)
                    if result["state"] != "submitted":
                        raise ValueError("submit acknowledgement ambiguous")
                    receipt = self._receipt(
                        "submit",
                        "submitted",
                        "job accepted; execution not complete",
                        intent=intent,
                        job=job,
                        evidence=result,
                    )
                except (
                    ValueError,
                    OSError,
                    TransportUnavailable,
                    subprocess.TimeoutExpired,
                ) as exc:
                    receipt = self._receipt(
                        "submit",
                        "unknown",
                        "submission may have been accepted: " + str(exc),
                        intent=intent,
                    )
                self._append(events, "receipt", token, receipt.as_dict())
                return receipt
        except ConfigurationError as exc:
            return self._receipt("submit", "blocked", str(exc), exit_code=2)
        except (ValueError, OSError) as exc:
            return self._receipt(
                "submit", "unknown", "local ledger hard stop: " + str(exc)
            )

    def _operate(
        self,
        operation,
        attempt,
        *,
        path=None,
        expected_sha256=None,
        destination=None,
        timeout=None,
    ):
        if self.config is None:
            return self._receipt(operation, "blocked", "remote configuration absent")
        try:
            if destination is not None:
                self.validate_destination(destination)
            with self._locked():
                events = self._events()
                matches = [i for i in self._intents(events) if i["attempt"] == attempt]
                if len(matches) != 1:
                    raise ConfigurationError(
                        "attempt does not identify exactly one recorded submission"
                    )
                intent = matches[0]
                state, job = self._state(events, intent)
                if job is None:
                    return self._receipt(
                        operation,
                        "unknown",
                        "no durable job identity; manual reconciliation required, never resubmit",
                        intent=intent,
                    )
                self._valid_job(job, intent["token"])
                if state == "unknown" and operation not in {"status", "cancel"}:
                    return self._receipt(
                        operation,
                        "unknown",
                        "unknown-state latch requires manual reconciliation",
                        intent=intent,
                        job=job,
                    )
                if operation == "cancel" and state in TERMINAL:
                    return self._receipt(
                        operation,
                        state,
                        "already terminal; no cancel issued",
                        intent=intent,
                        job=job,
                    )
                if operation == "artifact" and state != "succeeded":
                    return self._receipt(
                        operation,
                        "blocked",
                        "artifacts require proven successful job",
                        intent=intent,
                        job=job,
                    )
                try:
                    extra = {"token": intent["token"], "job": job}
                    if path is not None:
                        extra["path"] = path
                    result = self._call(operation, timeout=timeout, **extra)
                    if result.get("job") != job:
                        raise ValueError("remote response changed pinned job identity")
                    new_state = result["state"]
                    if operation == "status":
                        if new_state not in TERMINAL | {"queued", "running"}:
                            raise ValueError("unknown remote state")
                        if state in TERMINAL and state != new_state:
                            raise ValueError("terminal state contradicted")
                        if (
                            new_state in TERMINAL
                            and type(result.get("return_code")) is not int
                        ):
                            raise ValueError("missing terminal return code")
                        if new_state == "succeeded" and result["return_code"] != 0:
                            raise ValueError("success contradicts return code")
                        if new_state == "failed" and result["return_code"] == 0:
                            raise ValueError("failure contradicts return code")
                        if state == "unknown":
                            raise ValueError(
                                "unknown-state latch retained despite later observation"
                            )
                    elif operation == "cancel":
                        if (
                            new_state != "cancel_requested"
                            and new_state not in TERMINAL
                        ):
                            raise ValueError("cancel result ambiguous")
                        # Cancellation acknowledgment is NOT completion.
                        if new_state in TERMINAL:
                            raise ValueError(
                                "cancel raced with completion; query status explicitly"
                            )
                    else:
                        if new_state != "retrieved" or result.get("path") != path:
                            raise ValueError("retrieval receipt mismatch")
                        data = base64.b64decode(result["data"], validate=True)
                        actual = hashlib.sha256(data).hexdigest()
                        if (
                            len(data) > self.config.max_transfer_bytes
                            or type(result.get("size_bytes")) is not int
                            or result["size_bytes"] != len(data)
                            or result.get("sha256") != actual
                            or (expected_sha256 and actual != expected_sha256)
                        ):
                            raise ValueError(
                                "retrieved artifact digest or size mismatch"
                            )
                        _publish(self.project, destination, data)
                        result = {
                            key: value for key, value in result.items() if key != "data"
                        }
                        result.update(
                            {
                                "destination": destination,
                                "expected_sha256": expected_sha256,
                                "digest_verified": True,
                            }
                        )
                    if state == "unknown" and operation == "cancel":
                        new_state = "unknown"
                        result["detail"] = (
                            "cancel requested for pinned identity; unknown-state latch retained"
                        )
                    receipt = self._receipt(
                        operation,
                        new_state,
                        result.get("detail", "remote observation recorded"),
                        intent=intent,
                        job=job,
                        evidence=result,
                    )
                except (
                    ValueError,
                    KeyError,
                    TypeError,
                    OSError,
                    TransportUnavailable,
                    subprocess.TimeoutExpired,
                ) as exc:
                    receipt = self._receipt(
                        operation, "unknown", str(exc), intent=intent, job=job
                    )
                self._append(events, "receipt", intent["token"], receipt.as_dict())
                return receipt
        except ConfigurationError as exc:
            return self._receipt(operation, "blocked", str(exc), exit_code=2)
        except (ValueError, OSError) as exc:
            return self._receipt(
                operation, "unknown", "local ledger hard stop: " + str(exc)
            )

    def validate_destination(self, destination: str) -> None:
        relative_path(destination)
        path = self.project / destination
        if (
            path == self.directory
            or self.directory in path.parents
            or path in self.directory.parents
        ):
            raise ConfigurationError(
                "retrieval destination overlaps the attempt ledger"
            )

    def status(self, attempt: int, *, timeout: float | None = None) -> RemoteReceipt:
        return self._operate("status", attempt, timeout=timeout)

    def cancel(self, attempt: int) -> RemoteReceipt:
        return self._operate("cancel", attempt)

    def log(self, attempt: int, stream: str, destination: str) -> RemoteReceipt:
        if stream not in {"stdout", "stderr"}:
            return self._receipt(
                "log", "blocked", "stream must be stdout or stderr", exit_code=2
            )
        relative_path(destination)
        return self._operate("log", attempt, path=stream, destination=destination)

    def retrieve_artifact(
        self, attempt: int, path: str, expected_sha256: str, destination: str
    ) -> RemoteReceipt:
        relative_path(path)
        relative_path(destination)
        full_digest(expected_sha256)
        return self._operate(
            "artifact",
            attempt,
            path=path,
            expected_sha256=expected_sha256,
            destination=destination,
        )


def _publish(root: Path, destination: str, data: bytes):
    """Publish verified bytes without replacement, using no-follow directory FDs."""
    relative_path(destination)
    parts = destination.split("/")
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    temporary = None
    try:
        for part in parts[:-1]:
            try:
                os.mkdir(part, 0o700, dir_fd=directory)
            except FileExistsError:
                pass
            next_fd = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = next_fd
        temporary = ".remote-retrieval-" + os.urandom(16).hex()
        fd = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory,
        )
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(
            temporary,
            parts[-1],
            src_dir_fd=directory,
            dst_dir_fd=directory,
            follow_symlinks=False,
        )
        os.fsync(directory)
    finally:
        if temporary is not None:
            os.unlink(temporary, dir_fd=directory)
        os.close(directory)


class RemoteExecutor:
    """Projection onto computational Executor; lifecycle ledger remains canonical.

    Only CPU/no-cost/no-token profile is evaluated. Unknown, unfinished or
    cancelled jobs map to blocked, preventing autonomous workflow resubmission.
    Artifacts are returned only with caller-pinned expected digests.
    """

    def __init__(
        self,
        adapter: RemoteAdapter,
        *,
        artifacts: Mapping[str, tuple[str, str]] | None = None,
        poll_interval: float = 0.1,
    ):
        if not math.isfinite(poll_interval) or poll_interval <= 0:
            raise ConfigurationError("poll interval must be positive")
        self.adapter = adapter
        self.artifacts = dict(artifacts or {})
        self.poll_interval = poll_interval
        self.last_receipt: RemoteReceipt | None = None
        for remote, (local, sha) in self.artifacts.items():
            relative_path(remote)
            adapter.validate_destination(local)
            full_digest(sha)

    def __call__(
        self, project: Path, context: AttemptContext, remaining: BudgetUsage
    ) -> ExecutionReceipt:
        started = monotonic()
        if project.resolve() != self.adapter.project:
            raise ConfigurationError(
                "executor project differs from pinned remote ledger"
            )
        receipt = self.adapter.submit(context, remaining)
        while receipt.state in ACTIVE:
            left = remaining.seconds - (monotonic() - started)
            if left <= 0:
                break
            receipt = self.adapter.status(context.attempt, timeout=left)
            if receipt.state in ACTIVE:
                sleep(
                    min(
                        self.poll_interval,
                        max(0, remaining.seconds - (monotonic() - started)),
                    )
                )
        if receipt.state in ACTIVE:
            receipt = self.adapter.cancel(context.attempt)
        if receipt.state == "succeeded":
            for remote, (local, sha) in self.artifacts.items():
                retrieval = self.adapter.retrieve_artifact(
                    context.attempt, remote, sha, local
                )
                if retrieval.state != "retrieved":
                    receipt = retrieval
                    break
        self.last_receipt = receipt
        stdout, stderr = b"", b""
        if receipt.state in TERMINAL:
            for stream in ("stdout", "stderr"):
                destination = (
                    self.adapter.directory.relative_to(self.adapter.project).as_posix()
                    + f"-logs/attempt-{context.attempt:04d}.{stream}"
                )
                result = self.adapter.log(context.attempt, stream, destination)
                if result.state != "retrieved":
                    receipt = result
                    break
                data = (self.adapter.project / destination).read_bytes()
                if stream == "stdout":
                    stdout = data
                else:
                    stderr = data
        self.last_receipt = receipt
        outcome = (
            receipt.state if receipt.state in {"succeeded", "failed"} else "blocked"
        )
        code = (
            receipt.evidence.get("return_code")
            if outcome in {"succeeded", "failed"}
            else None
        )
        elapsed = monotonic() - started
        return ExecutionReceipt(
            outcome=outcome,
            return_code=code,
            usage=BudgetUsage(seconds=elapsed),
            stdout=stdout,
            stderr=stderr,
            detail=json_bytes(receipt.as_dict()).decode(),
        )
