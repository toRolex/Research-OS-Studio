"""Self-contained, stdlib-only remote worker sent over authenticated OpenSSH.

Linux SSH process identity uses boot ID and /proc start ticks. SLURM supports
single non-federated jobs, not arrays/requeue. No installation/configuration is
performed on the remote host; an existing pinned Git checkout is required.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


TERMINAL = {"succeeded", "failed", "cancelled", "timed_out"}


def encoded(value):
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def save(path, value, exclusive=False):
    data = encoded(value)
    target = path if exclusive else path.with_name(path.name + ".new")
    with target.open("xb" if exclusive else "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if not exclusive:
        os.replace(target, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def run(argv, *, data=None, timeout=10):
    return subprocess.run(
        argv, input=data, capture_output=True, timeout=timeout, check=False
    )


def safe(root, name):
    if (
        not isinstance(name, str)
        or not name
        or any(c in name for c in "\\\x00\n\r")
        or any(p in {"", ".", "..", ".git"} for p in name.split("/"))
    ):
        raise ValueError("unsafe relative path")
    path = root / name
    current = root
    for part in Path(name).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink forbidden")
    path.resolve().relative_to(root.resolve())
    return path


def read_confined(root, name, limit):
    safe(root, name)
    parts = name.split("/")
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        fd = os.open(
            parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=directory
        )
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            import stat

            if not stat.S_ISREG(before.st_mode):
                raise ValueError("retrieval source must be regular file")
            data = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
        if len(data) > limit or (before.st_size, before.st_mtime_ns) != (
            after.st_size,
            after.st_mtime_ns,
        ):
            raise ValueError("source changed or transfer limit exceeded")
        return data
    finally:
        os.close(directory)


def identity(pid):
    # A disappeared/reused PID never proves completion.
    stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    if stat[0] == "Z":
        raise ValueError("supervisor is a zombie")
    return {
        "pid": pid,
        "start_ticks": stat[19],
        "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
    }


def snapshot(config, directory):
    root = Path(config["root"])
    revision = config["revision"]
    if root.is_symlink() or root.resolve() != root:
        raise ValueError("remote root must not traverse symlinks")
    result = run(["git", "-C", str(root), "rev-parse", "HEAD"])
    if result.returncode or result.stdout.decode().strip() != revision:
        raise ValueError("remote revision mismatch")
    listing = run(["git", "-C", str(root), "ls-tree", "-r", "-z", revision])
    if listing.returncode:
        raise ValueError("cannot list pinned checkout")
    total = 0
    hashes = {}
    directory.mkdir()
    for entry in listing.stdout.split(b"\x00"):
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        name = name.decode()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("snapshot does not support symlinks or submodules")
        path = safe(directory, name)
        blob = run(["git", "-C", str(root), "cat-file", "blob", oid])
        if blob.returncode:
            raise ValueError("pinned blob unavailable")
        total += len(blob.stdout)
        if total > 64 * 1024 * 1024:
            raise ValueError("remote snapshot exceeds 64 MiB")
        hashes[name] = hashlib.sha256(blob.stdout).hexdigest()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(blob.stdout)
        path.chmod(0o700 if mode == "100755" else 0o600)
    for name, expected in config["inputs"].items():
        if hashes.get(name) != expected:
            raise ValueError("pinned input digest mismatch: " + name)
    return hashes


def supervise(directory):
    request = json.loads((directory / "request.json").read_bytes())
    context = request["context"]
    result = {
        "state": "unknown",
        "return_code": None,
        "detail": "supervisor interrupted",
    }
    started = time.monotonic()
    deadline = request["deadline_epoch_seconds"]
    child = None
    try:
        if time.time() >= deadline:
            result = {
                "state": "timed_out",
                "return_code": 124,
                "detail": "absolute deadline expired before job start",
                "token": request["token"],
                "seconds": 0.0,
            }
            save(directory / "result.json", result)
            return
        cwd = directory / "work"
        if context["cwd"] != ".":
            cwd = safe(cwd, context["cwd"])
        environment = os.environ.copy()
        environment.update(context["environment"])
        with (
            (directory / "stdout").open("xb") as stdout,
            (directory / "stderr").open("xb") as stderr,
        ):
            child = subprocess.Popen(
                context["command"],
                cwd=cwd,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            save(directory / "child.json", {"pid": child.pid}, True)
            state = None
            while child.poll() is None:
                if (directory / "cancel.request").exists():
                    state = "cancelled"
                elif (
                    time.monotonic() - started >= request["seconds"]
                    or time.time() >= deadline
                ):
                    state = "timed_out"
                if state:
                    os.killpg(child.pid, signal.SIGKILL)
                    break
                time.sleep(0.05)
            code = child.wait()
            # Kill remaining descendants before publishing a terminal receipt.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            result = {
                "state": state or ("succeeded" if code == 0 else "failed"),
                "return_code": code,
                "detail": "remote process group exited",
            }
    except Exception as exc:
        # Tool launch failure is not successful execution.
        result = {
            "state": "failed" if child is None else "unknown",
            "return_code": 127 if child is None else None,
            "detail": str(exc),
        }
    finally:
        if child is not None:
            try:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait(timeout=5)
            except Exception as exc:
                result = {
                    "state": "unknown",
                    "return_code": None,
                    "detail": "process group cleanup unconfirmed: " + str(exc),
                }
    result.update({"token": request["token"], "seconds": time.monotonic() - started})
    save(directory / "result.json", result)


def slurm_status(directory, request, job):
    job_id = job["job_id"]
    queue = run(["squeue", "--noheader", "--jobs=" + job_id, "--format=%i|%j|%T"])
    accounting = run(
        [
            "sacct",
            "--noheader",
            "--allocations",
            "--parsable2",
            "--jobs=" + job_id,
            "--format=JobIDRaw,JobName%80,State%40,ExitCode",
        ]
    )
    if queue.returncode or accounting.returncode:
        raise ValueError("scheduler query unavailable; state unknown")
    qrows = [
        line.split("|") for line in queue.stdout.decode().splitlines() if line.strip()
    ]
    arows = [
        line.split("|")
        for line in accounting.stdout.decode().splitlines()
        if line.strip()
    ]
    if len(qrows) > 1 or len(arows) > 1 or not (qrows or arows):
        raise ValueError("ambiguous or missing scheduler job")
    for row in qrows + arows:
        if (
            len(row) not in {3, 4}
            or row[0].strip() != job_id
            or row[1].strip() != job["job_name"]
        ):
            raise ValueError("scheduler identity mismatch")
    state = (arows[0][2] if arows else qrows[0][2]).strip()
    if qrows and arows and qrows[0][2].strip() != state:
        raise ValueError("contradictory scheduler states")
    mapping = {
        "PENDING": "queued",
        "CONFIGURING": "queued",
        "RUNNING": "running",
        "COMPLETING": "running",
        "COMPLETED": "succeeded",
        "FAILED": "failed",
        "TIMEOUT": "timed_out",
        "CANCELLED": "cancelled",
        "OUT_OF_MEMORY": "failed",
        "NODE_FAIL": "failed",
        "BOOT_FAIL": "failed",
        "DEADLINE": "timed_out",
    }
    if state.startswith("CANCELLED by "):
        state = "CANCELLED"
    if state not in mapping:
        raise ValueError("unsupported scheduler state: " + state)
    result = {"state": mapping[state], "return_code": None, "scheduler_state": state}
    if result["state"] in TERMINAL:
        if not arows or not re.fullmatch(r"[0-9]+:[0-9]+", arows[0][3].strip()):
            raise ValueError("terminal accounting receipt missing")
        code, sig = map(int, arows[0][3].strip().split(":"))
        if result["state"] == "succeeded" and (code or sig):
            raise ValueError("COMPLETED contradicts nonzero exit")
        result["return_code"] = code if not sig else -sig
        if result["state"] == "succeeded":
            local = json.loads((directory / "result.json").read_bytes())
            if local["token"] != request["token"] or local["state"] not in TERMINAL:
                raise ValueError("worker completion receipt missing or ambiguous")
            result.update(local)
    return result


def handle(request):
    config = request["config"]
    operation = request["operation"]
    if operation == "probe":
        tools = ["git"] + (
            ["sbatch", "squeue", "sacct", "scancel"]
            if config["backend"] == "slurm"
            else []
        )
        missing = [tool for tool in tools if shutil.which(tool) is None]
        if (
            config["backend"] == "ssh"
            and not Path("/proc/sys/kernel/random/boot_id").is_file()
        ):
            missing.append("Linux /proc process identity")
        return {
            "state": "blocked" if missing else "available",
            "remote_epoch_seconds": time.time(),
            "detail": "missing: " + ", ".join(missing)
            if missing
            else "tools present; real lifecycle NOT_EVALUATED",
        }
    token = request["token"]
    if not re.fullmatch(r"[0-9a-f]{64}", token):
        raise ValueError("invalid attempt token")
    root = Path(config["root"])
    if root.resolve() != root:
        raise ValueError("root traverses symlink")
    directory = safe(root, ".research-os/remote-jobs/" + token)
    if operation == "submit":
        # mkdir is the remote idempotency barrier. Existing intent is NEVER re-run.
        directory.mkdir(parents=True, exist_ok=False)
        directory.chmod(0o700)
        save(directory / "request.json", request, True)
        snapshot(config, directory / "work")
        worker = directory / "worker.py"
        with worker.open("x") as stream:
            stream.write(request["worker_source"])
        if config["backend"] == "ssh":
            with (directory / "supervisor.log").open("xb") as log:
                process = subprocess.Popen(
                    [sys.executable, str(worker), "supervise", str(directory)],
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
            job = {"backend": "ssh", "process": identity(process.pid), "token": token}
        else:
            job_name = "ros-" + token
            import shlex

            script = (
                "#!/bin/sh\nexec "
                + shlex.join([sys.executable, str(worker), "supervise", str(directory)])
                + "\n"
            )
            argv = [
                "sbatch",
                "--parsable",
                "--no-requeue",
                "--job-name=" + job_name,
                "--output=" + str(directory / "scheduler.stdout"),
                "--error=" + str(directory / "scheduler.stderr"),
                "--chdir=" + str(directory / "work"),
                "--time=" + str(max(1, int((request["seconds"] + 59) // 60))),
            ]
            for key, value in config["slurm"].items():
                if key == "time":
                    raise ValueError("SLURM time comes from the remaining hard budget")
                argv.append("--" + key.replace("_", "-") + "=" + value)
            submitted = run(argv, data=script.encode())
            output = submitted.stdout.decode().strip()
            if submitted.returncode or not re.fullmatch(r"[1-9][0-9]*", output):
                raise ValueError("sbatch acceptance ambiguous; never resubmit")
            job = {
                "backend": "slurm",
                "job_id": output,
                "job_name": job_name,
                "token": token,
            }
        save(directory / "job.json", job, True)
        return {"state": "submitted", "job": job, "return_code": None}
    saved = json.loads((directory / "request.json").read_bytes())
    job = json.loads((directory / "job.json").read_bytes())
    if job != request["job"] or saved["config"] != config:
        raise ValueError("remote job identity or configuration drift")
    if operation == "status":
        if config["backend"] == "slurm":
            result = slurm_status(directory, request, job)
        elif (directory / "result.json").exists():
            result = json.loads((directory / "result.json").read_bytes())
            if result["token"] != token:
                raise ValueError("completion identity mismatch")
        elif identity(job["process"]["pid"]) == job["process"]:
            result = {"state": "running", "return_code": None}
        else:
            raise ValueError("supervisor identity drift")
        return dict(result, job=job)
    if operation == "cancel":
        if config["backend"] == "slurm":
            # Cancellation needs a unique live identity, not healthy accounting.
            # Never infer completion from an empty queue or a successful scancel.
            queue = run(
                ["squeue", "--noheader", "--jobs=" + job["job_id"], "--format=%i|%j|%T"]
            )
            rows = [
                line.split("|")
                for line in queue.stdout.decode().splitlines()
                if line.strip()
            ]
            if (
                queue.returncode
                or len(rows) != 1
                or len(rows[0]) != 3
                or rows[0][0].strip() != job["job_id"]
                or rows[0][1].strip() != job["job_name"]
            ):
                raise ValueError("cancellation cannot confirm unique live job identity")
            result = run(["scancel", "--", job["job_id"]])
            if result.returncode:
                raise ValueError("scancel failed; terminal state not proven")
        else:
            if identity(job["process"]["pid"]) != job["process"]:
                raise ValueError("supervisor identity drift")
            try:
                save(directory / "cancel.request", {"token": token}, True)
            except FileExistsError:
                pass
        return {"state": "cancel_requested", "job": job, "return_code": None}
    if operation in {"log", "artifact"}:
        name = request["path"]
        if operation == "log" and name not in {"stdout", "stderr"}:
            raise ValueError("unsupported log")
        data = read_confined(
            directory / "work" if operation == "artifact" else directory,
            name,
            config["max_transfer_bytes"],
        )
        return {
            "state": "retrieved",
            "job": job,
            "path": name,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data),
            "data": base64.b64encode(data).decode(),
            "return_code": None,
        }
    raise ValueError("unsupported operation")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "supervise":
        supervise(Path(sys.argv[2]))
        return
    request = json.load(sys.stdin)
    try:
        result = handle(request)
    except (FileNotFoundError, PermissionError) as exc:
        result = {
            "state": "blocked" if request["operation"] == "probe" else "unknown",
            "detail": str(exc),
        }
    except Exception as exc:
        result = {"state": "unknown", "detail": str(exc)}
    result.update(
        {
            "protocol": "research-os/remote-wire/1",
            "operation": request["operation"],
            "token": request.get("token"),
        }
    )
    sys.stdout.buffer.write(encoded(result))


if __name__ == "__main__":
    main()
