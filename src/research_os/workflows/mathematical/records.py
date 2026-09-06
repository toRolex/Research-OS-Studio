from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True, order=True)
class ValidationIssue:
    code: str
    message: str
    location: str = ""

    def as_dict(self) -> dict[str, str]:
        value = {"code": self.code, "message": self.message}
        if self.location:
            value["location"] = self.location
        return value


class RecordError(ValueError):
    def __init__(self, issues: Sequence[ValidationIssue]):
        self.issues = tuple(issues)
        super().__init__(
            "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        )


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def write_json_exclusive(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        payload = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        os.write(descriptor, payload.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def safe_relative_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(
        part not in {"", ".", ".."} and part.casefold() != ".git"
        for part in value.split("/")
    )


def resolve_under(root: Path, relative: object, *, must_exist: bool = False) -> Path:
    if not safe_relative_path(relative):
        raise ValueError("path must be a safe project-relative path")
    root = root.resolve()
    candidate = root / str(relative)
    current = root
    for part in PurePosixPath(str(relative)).parts:
        current /= part
        if current.is_symlink():
            raise ValueError("path contains a symbolic link")
    result = candidate.resolve(strict=False)
    try:
        result.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes project root") from exc
    if must_exist and not result.is_file():
        raise FileNotFoundError(result)
    return result


def require_mapping(
    value: object, code: str, location: str
) -> tuple[Mapping[str, Any] | None, list[ValidationIssue]]:
    if isinstance(value, Mapping):
        return value, []
    return None, [ValidationIssue(code, "must be an object", location)]


def reject_unknown(
    value: Mapping[str, Any], allowed: Iterable[str], *, code: str, location: str
) -> list[ValidationIssue]:
    allowed_set = set(allowed)
    return [
        ValidationIssue(code, f"unknown field: {field}", f"{location}/{field}")
        for field in sorted(value)
        if field not in allowed_set
    ]


def require_nonempty_string(
    value: object, *, code: str, location: str
) -> list[ValidationIssue]:
    if isinstance(value, str) and value.strip():
        return []
    return [ValidationIssue(code, "must be a non-empty string", location)]


def require_string_list(
    value: object,
    *,
    code: str,
    location: str,
    allow_empty: bool = True,
) -> list[ValidationIssue]:
    if not isinstance(value, list):
        return [ValidationIssue(code, "must be an array", location)]
    if not allow_empty and not value:
        return [ValidationIssue(code, "must be a non-empty array", location)]
    issues: list[ValidationIssue] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            issues.append(
                ValidationIssue(
                    code,
                    "array entries must be non-empty strings",
                    f"{location}/{index}",
                )
            )
    return issues


def require_exact_digest(
    value: object, expected: str, *, code: str, location: str
) -> list[ValidationIssue]:
    if value == expected:
        return []
    return [ValidationIssue(code, "digest does not match the fixed subject", location)]


def ordered_unique_strings(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return result
