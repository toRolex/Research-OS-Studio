from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Mapping


class ConfigurationError(ValueError):
    pass


def relative_path(value: str, *, directory: bool = False) -> str:
    if directory and value == ".":
        return value
    if not isinstance(value, str) or not value or any(c in value for c in "\\\x00\n\r"):
        raise ConfigurationError("expected safe relative path")
    parts = value.split("/")
    if any(p in {"", ".", ".."} or p.casefold() == ".git" for p in parts):
        raise ConfigurationError("path traversal or reserved path")
    if PurePosixPath(value).is_absolute():
        raise ConfigurationError("absolute path not allowed")
    return value


def full_digest(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ConfigurationError("SHA-256 must be 64 lowercase hexadecimal characters")
    return value


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def digest(value: object) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


@dataclass(frozen=True)
class RemoteConfig:
    backend: str
    host: str
    root: str
    revision: str
    inputs: Mapping[str, str]
    ssh_executable: str = "ssh"
    python_executable: str = "python3"
    user: str | None = None
    port: int = 22
    timeout_seconds: float = 10.0
    max_transfer_bytes: int = 8 * 1024 * 1024
    slurm: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.backend not in {"ssh", "slurm"}:
            raise ConfigurationError("backend must be ssh or slurm")
        if (
            not isinstance(self.host, str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", self.host) is None
        ):
            raise ConfigurationError(
                "host must be a plain DNS name or IPv4 address, not SSH options"
            )
        if self.user is not None and (
            not isinstance(self.user, str)
            or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", self.user) is None
        ):
            raise ConfigurationError("invalid SSH user")
        if (
            not isinstance(self.root, str)
            or not self.root.startswith("/")
            or self.root == "/"
            or any(c in self.root for c in "\x00\r\n\\")
            or any(p in {"", ".", "..", ".git"} for p in self.root.split("/")[1:])
        ):
            raise ConfigurationError(
                "root must be a canonical absolute remote checkout path"
            )
        if (
            not isinstance(self.revision, str)
            or re.fullmatch(r"[0-9a-f]{40}", self.revision) is None
        ):
            raise ConfigurationError("revision must be a full lowercase Git commit")
        if not isinstance(self.inputs, Mapping) or not self.inputs:
            raise ConfigurationError("at least one pinned remote input is required")
        for path, sha in self.inputs.items():
            relative_path(path)
            full_digest(sha)
        for name in (self.ssh_executable, self.python_executable):
            if (
                not isinstance(name, str)
                or re.fullmatch(
                    r"(?:/[A-Za-z0-9_. /-]+|[A-Za-z0-9_][A-Za-z0-9_.-]*)", name
                )
                is None
                or ".." in name.split("/")
            ):
                raise ConfigurationError(
                    "executable must be a name or absolute path, never shell syntax"
                )
        if type(self.port) is not int or not 1 <= self.port <= 65535:
            raise ConfigurationError("invalid port")
        if (
            type(self.timeout_seconds) not in {float, int}
            or not math.isfinite(self.timeout_seconds)
            or not 0 < self.timeout_seconds <= 3600
        ):
            raise ConfigurationError("invalid timeout")
        if (
            type(self.max_transfer_bytes) is not int
            or not 1 <= self.max_transfer_bytes <= 64 * 1024 * 1024
        ):
            raise ConfigurationError("invalid transfer limit")
        if not isinstance(self.slurm, Mapping) or set(self.slurm) - {
            "partition",
            "account",
            "qos",
            "cpus_per_task",
            "mem",
            "gpus",
        }:
            raise ConfigurationError("unsupported SLURM resource option")
        if self.backend == "ssh" and self.slurm:
            raise ConfigurationError("SLURM resources require slurm backend")
        for value in self.slurm.values():
            if (
                not isinstance(value, str)
                or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_:.-]*", value) is None
            ):
                raise ConfigurationError("unsafe SLURM option value")
        # Copy caller-owned mappings: a frozen configuration must not drift in place.
        object.__setattr__(self, "inputs", dict(self.inputs))
        object.__setattr__(self, "slurm", dict(self.slurm))

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> RemoteConfig:
        if not isinstance(value, Mapping):
            raise ConfigurationError("configuration must be an object")
        fields = set(cls.__dataclass_fields__)
        if set(value) - fields:
            raise ConfigurationError("unknown configuration fields")
        try:
            return cls(**value)
        except TypeError as exc:
            raise ConfigurationError(str(exc)) from exc

    @classmethod
    def load(cls, path: Path) -> RemoteConfig:
        return cls.from_mapping(json.loads(path.read_bytes()))

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
