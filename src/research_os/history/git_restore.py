from __future__ import annotations

import ctypes
import errno
import hashlib
import io
import json
import os
import re
import secrets
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Mapping

from research_os.install.bundle import InstallManifest, _check_directory_identity, _directory_fd, _path_has_symlink, _same_inode
from research_os.install.model import digest_bytes

FULL_COMMIT = re.compile(r"^[0-9a-f]{40}$")
LEGACY_RUNTIME_MANIFEST = ".research-os/runtime/manifest.json"
INSTALL_MANIFEST = ".research-os/install-manifest.json"


def _run_git(repository: Path, *arguments: str, text: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=False,
        capture_output=True,
        text=text,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )


def _existing_parent(path: Path) -> Path:
    current = path
    while not current.exists() and not current.is_symlink():
        parent = current.parent
        if parent == current:
            raise ValueError("history output has no existing parent")
        current = parent
    if current.is_symlink() or not current.is_dir():
        raise ValueError("history output parent must be a regular directory path")
    return current


def _safe_member_name(name: str) -> str:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or name.endswith("/"):
        raise ValueError(f"unsafe archive member path: {name}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe archive member path: {name}")
    return path.as_posix()


def _resolved_commit(repository: Path, commit: str) -> str:
    if not FULL_COMMIT.fullmatch(commit):
        raise ValueError("commit must be a full lowercase 40-character object ID")
    result = _run_git(repository, "rev-parse", "--verify", f"{commit}^{{commit}}", text=True)
    if result.returncode:
        raise ValueError("commit is not a reachable commit object")
    resolved = result.stdout.strip()
    if resolved != commit:
        raise ValueError("commit did not resolve exactly")
    return resolved


def _reject_gitlinks(repository: Path, commit: str) -> None:
    result = _run_git(repository, "ls-tree", "-rz", "-r", commit)
    if result.returncode:
        raise ValueError(
            result.stderr.decode("utf-8", errors="replace").strip()
            or "git ls-tree failed"
        )
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        try:
            metadata, raw_name = record.split(b"\t", 1)
            mode, kind, _object_id = metadata.split(b" ", 2)
        except ValueError as exc:
            raise ValueError("git tree contains an unparsable entry") from exc
        if mode == b"160000" or kind == b"commit":
            name = raw_name.decode("utf-8", errors="backslashreplace")
            raise ValueError(
                f"history contains unsupported gitlink mode 160000: {name}"
            )


def _archive(repository: Path, commit: str) -> dict[str, bytes]:
    result = _run_git(repository, "archive", "--format=tar", commit)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip() or "git archive failed")
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            name = _safe_member_name(member.name)
            if not member.isfile():
                raise ValueError(f"history contains an unsupported non-regular file: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(f"cannot read history member: {name}")
            files[name] = stream.read()
    return dict(sorted(files.items()))


def _legacy_manifest_inventory(files: Mapping[str, bytes]) -> tuple[str, ...] | None:
    raw = files.get(LEGACY_RUNTIME_MANIFEST)
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("legacy runtime manifest is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict) or value.get("contract") != {
        "name": "research-os/runtime-manifest",
        "version": "1.0.0",
    }:
        raise ValueError("legacy runtime manifest contract is unsupported")
    inventory = value.get("files")
    if not isinstance(inventory, list) or not inventory or not all(isinstance(item, str) for item in inventory):
        raise ValueError("legacy runtime manifest files must be a non-empty string array")
    normalized: list[str] = []
    for item in inventory:
        name = _safe_member_name(item)
        if name == "manifest.json":
            raise ValueError("legacy runtime manifest must not list itself")
        full = f".research-os/runtime/{name}"
        if full not in files:
            raise ValueError(f"legacy runtime is incomplete: {full}")
        normalized.append(name)
    required = {"scripts/research-os.py"}
    if not required.issubset(normalized):
        raise ValueError("legacy runtime lacks its historical entrypoint")
    return tuple(sorted(set(normalized)))


def _current_manifest_inventory(files: Mapping[str, bytes]) -> tuple[str, ...] | None:
    raw = files.get(INSTALL_MANIFEST)
    if raw is None:
        return None
    manifest = InstallManifest.from_bytes(raw)
    for name, expected in manifest.files.items():
        actual = files.get(name)
        if actual is None:
            raise ValueError(f"install history is incomplete: {name}")
        if digest_bytes(actual) != expected:
            raise ValueError(f"install history has drifted bytes: {name}")
    return tuple(manifest.files)


@dataclass(frozen=True, slots=True)
class HistoryManifest:
    commit: str
    profile: str
    files: Mapping[str, str]
    tree_digest: str

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": {"name": "research-os/history-manifest", "version": "1.0.0"},
            "commit": self.commit,
            "profile": self.profile,
            "files": dict(self.files),
            "tree_digest": self.tree_digest,
            "read_only": True,
        }


@dataclass(frozen=True, slots=True)
class HistoryBlocked:
    issues: tuple[dict[str, str], ...]
    exit_code: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": {"name": "research-os/history-result", "version": "1.0.0"},
            "verdict": "fail",
            "status": "stopped",
            "stop_reason": "history_restore_failed",
            "issues": [dict(issue) for issue in self.issues],
            "outputs": [],
            "next_steps": [],
        }


@dataclass(frozen=True, slots=True)
class HistoryResult:
    manifest: HistoryManifest
    output: Path

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": {"name": "research-os/history-result", "version": "1.0.0"},
            "verdict": "pass",
            "status": "stopped",
            "stop_reason": "historical_environment_restored",
            "commit": self.manifest.commit,
            "profile": self.manifest.profile,
            "output": str(self.output),
            "read_only": True,
            "next_steps": [],
        }


def inspect_history(repository: Path, commit: str) -> tuple[HistoryManifest, Mapping[str, bytes]]:
    repository = repository.resolve(strict=True)
    resolved = _resolved_commit(repository, commit)
    _reject_gitlinks(repository, resolved)
    files = _archive(repository, resolved)
    current = _current_manifest_inventory(files)
    legacy = _legacy_manifest_inventory(files)
    if current is not None:
        profile = "project-local-install-v1"
    elif legacy is not None:
        profile = "legacy-self-contained-runtime-v1"
    else:
        raise ValueError("history contains neither a current install manifest nor a supported legacy runtime manifest")
    digests = {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}
    tree_digest = hashlib.sha256(
        b"".join(f"{name}\0{digests[name]}\n".encode("utf-8") for name in sorted(digests))
    ).hexdigest()
    manifest = HistoryManifest(
        commit=resolved,
        profile=profile,
        files=MappingProxyType(digests),
        tree_digest=tree_digest,
    )
    return manifest, MappingProxyType(files)


def _publish_directory(source: str, destination: str, *, parent_fd: int) -> None:
    """Atomically publish without replacing even an empty competing directory."""
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        function = getattr(libc, "renameatx_np", None)
        flags = 0x00000004  # RENAME_EXCL
    elif sys.platform.startswith("linux"):
        function = getattr(libc, "renameat2", None)
        flags = 1  # RENAME_NOREPLACE
    else:
        function = None
        flags = 0
    if function is None:
        raise OSError(errno.ENOTSUP, "atomic no-clobber directory publish unavailable")
    function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    function.restype = ctypes.c_int
    if function(parent_fd, os.fsencode(source), parent_fd, os.fsencode(destination), flags):
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), destination)


def _stage_history(descriptor: int, files: Mapping[str, bytes], manifest: HistoryManifest) -> None:
    payload = dict(files)
    payload[".research-os/history-restore.json"] = (
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    for name, content in payload.items():
        parent = os.dup(descriptor)
        try:
            components = PurePosixPath(name).parts
            for component in components[:-1]:
                try:
                    os.mkdir(component, dir_fd=parent)
                except FileExistsError:
                    pass
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                os.close(parent)
                parent = child
            file_fd = os.open(
                components[-1], os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o644, dir_fd=parent,
            )
            with os.fdopen(file_fd, "w+b") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
                stream.seek(0)
                if stream.read() != content:
                    raise ValueError(f"staged history verification failed: {name}")
        finally:
            os.close(parent)


def restore_history(repository: Path, commit: str, output: Path) -> HistoryResult | HistoryBlocked:
    try:
        repository = repository.resolve(strict=True)
        requested_output = output.expanduser().absolute()
        # macOS exposes system temporary paths via /var and /tmp aliases.
        # Canonicalize only these fixed OS aliases, never user-controlled parents.
        if sys.platform == "darwin":
            for alias in (Path("/var"), Path("/tmp")):
                if requested_output.is_relative_to(alias):
                    requested_output = alias.resolve(strict=True) / requested_output.relative_to(alias)
                    break
        existing_parent = _existing_parent(requested_output.parent)
        with _directory_fd(existing_parent):
            pass
        if _path_has_symlink(requested_output.parent, existing_parent):
            raise ValueError("history output path traverses a symlink")
        output = requested_output
        if output.exists() or output.is_symlink():
            raise ValueError("history output must not already exist")
        resolved_output = output.resolve(strict=False)
        if resolved_output == repository or resolved_output.is_relative_to(repository):
            raise ValueError("history output must be outside the source repository")
        manifest, files = inspect_history(repository, commit)
        if ".research-os/history-restore.json" in files:
            raise ValueError("history already contains the reserved restore receipt path")
    except (OSError, ValueError) as exc:
        return HistoryBlocked(({"code": "history.preflight", "message": str(exc)},))
    staging_name = f".{output.name}.restore-{secrets.token_hex(16)}"
    try:
        with _directory_fd(output.parent, create=True) as parent:
            os.mkdir(staging_name, mode=0o700, dir_fd=parent)
            staging_fd = os.open(
                staging_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent
            )
            try:
                token = os.fstat(staging_fd)
                _stage_history(staging_fd, files, manifest)
                _check_directory_identity(output.parent, parent)
                if not _same_inode(token, os.stat(staging_name, dir_fd=parent, follow_symlinks=False)):
                    raise ValueError("history staging identity changed before publish")
                _publish_directory(staging_name, output.name, parent_fd=parent)
                if not _same_inode(token, os.stat(output.name, dir_fd=parent, follow_symlinks=False)):
                    raise ValueError("history output identity changed during publish")
                _check_directory_identity(output.parent, parent)
            finally:
                os.close(staging_fd)
    except (OSError, ValueError) as exc:
        # Do not rmtree a public name: another writer may have replaced it.
        return HistoryBlocked((
            {"code": "history.write", "message": str(exc)},
            {"code": "history.cleanup_required", "message":
             f"No rollback deletion attempted; inspect {output.parent / staging_name} and {output}"},
        ))
    return HistoryResult(manifest=manifest, output=output)
