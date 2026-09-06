from __future__ import annotations

import ipaddress
import re
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

from .issues import Issue

COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PERCENT_ESCAPE = re.compile(r"%([0-9A-Fa-f]{2})")
_PATH_CHARACTERS = re.compile(
    r"^(?:[A-Za-z0-9._~!$&'()*+,;=:@/-]|%[0-9A-F]{2})+$"
)


def is_canonical_https_uri(value: object) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if any(ord(character) < 0x20 or character == "\\" for character in value):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.hostname is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        return False
    hostname = parsed.hostname
    try:
        hostname.encode("ascii")
    except UnicodeEncodeError:
        return False
    if "%" in hostname or "_" in hostname:
        return False
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        labels = hostname.split(".")
        if any(
            not label
            or len(label) > 63
            or label.startswith("-")
            or label.endswith("-")
            or re.fullmatch(r"[a-z0-9-]+", label) is None
            for label in labels
        ):
            return False
    host_text = parsed.netloc.rsplit("@", 1)[-1]
    if host_text.startswith("["):
        host_text = host_text.split("]", 1)[0] + "]"
    else:
        host_text = host_text.split(":", 1)[0]
    if host_text != host_text.lower() or parsed.hostname.endswith("."):
        return False
    if port == 443:
        return False
    if parsed.path and not parsed.path.startswith("/"):
        return False
    if parsed.path and _PATH_CHARACTERS.fullmatch(parsed.path) is None:
        return False
    try:
        decoded_path = unquote(parsed.path, errors="strict")
    except UnicodeDecodeError:
        return False
    if any(ord(character) > 0x7F or character == "\\" for character in decoded_path):
        return False
    if "%2F" in parsed.path.upper() or "%5C" in parsed.path.upper():
        return False
    if any(part in {".", ".."} for part in decoded_path.split("/")):
        return False
    for match in _PERCENT_ESCAPE.finditer(parsed.path):
        if match.group(1) != match.group(1).upper():
            return False
        decoded = chr(int(match.group(1), 16))
        if decoded in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~":
            return False
    return True


def is_safe_git_path(value: object) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if "\\" in value or "\x00" in value or value.endswith("/"):
        return False
    if any(ord(character) < 0x20 for character in value):
        return False
    path = PurePosixPath(value)
    parts = value.split("/")
    return (
        not path.is_absolute()
        and all(part not in {"", ".", ".."} for part in parts)
        and all(part.casefold() != ".git" for part in parts)
    )


def validate_target(target: object, *, instance_path: str = "/target") -> list[Issue]:
    if not isinstance(target, dict):
        return [Issue("target.object", "target must be an object", instance_path)]
    kind = target.get("kind")
    issues: list[Issue] = []
    if kind == "git":
        _unknown_fields(target, {"kind", "path", "commit", "repository"}, issues, instance_path)
        if not is_safe_git_path(target.get("path")):
            issues.append(Issue("target.path", "git path must be a safe repository-relative file path", f"{instance_path}/path"))
        commit = target.get("commit")
        if commit is not None and (not isinstance(commit, str) or COMMIT_RE.fullmatch(commit) is None):
            issues.append(Issue("target.commit", "commit must be a full 40-character lowercase hexadecimal object ID", f"{instance_path}/commit"))
        repository = target.get("repository")
        if repository is not None:
            if commit is None:
                issues.append(Issue("target.repository_requires_commit", "cross-repository targets must include a fixed commit", instance_path))
            if not is_canonical_https_uri(repository):
                issues.append(Issue("target.repository", "repository must be a canonical credential-free HTTPS URI", f"{instance_path}/repository"))
        return issues
    if kind == "uri":
        _unknown_fields(target, {"kind", "uri", "sha256"}, issues, instance_path)
        if not is_canonical_https_uri(target.get("uri")):
            issues.append(Issue("target.uri", "URI target must be a canonical credential-free HTTPS URI without query or fragment", f"{instance_path}/uri"))
        digest = target.get("sha256")
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            issues.append(Issue("target.sha256", "sha256 must be 64 lowercase hexadecimal characters", f"{instance_path}/sha256"))
        return issues
    return [Issue("target.kind", "target.kind must be git or uri", f"{instance_path}/kind")]


def _unknown_fields(value: dict[object, object], allowed: set[str], issues: list[Issue], path: str) -> None:
    for key in value:
        if not isinstance(key, str) or key not in allowed:
            issues.append(Issue("target.field", f"unknown target field: {key}", f"{path}/{key}"))
