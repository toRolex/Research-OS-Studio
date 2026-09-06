from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from research_os.validation.foundation.targets import is_canonical_https_uri, is_safe_git_path

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TYPE_VERSION = "1.0.0"
ARTIFACT_CONTRACTS = frozenset({"1.0.0", "1.1.0"})
SEMANTIC_TYPES = frozenset(
    {"project", "workstream", "claim", "evidence", "assessment", "migration-rule", "migration-receipt"}
)


@dataclass(frozen=True, order=True)
class Issue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def issue(code: str, path: str, message: str) -> Issue:
    return Issue(code, path, message)


def is_exact_semver(value: object) -> bool:
    return isinstance(value, str) and SEMVER_RE.fullmatch(value) is not None


def semver_key(value: str) -> tuple[int, int, int, int, tuple[tuple[int, object], ...]]:
    """Return a key implementing SemVer 2.0.0 precedence (build metadata ignored)."""
    if not is_exact_semver(value):
        raise ValueError(f"not exact SemVer: {value!r}")
    without_build = value.split("+", 1)[0]
    core, separator, prerelease = without_build.partition("-")
    major, minor, patch = (int(part) for part in core.split("."))
    if not separator:
        return major, minor, patch, 1, ()
    identifiers: list[tuple[int, object]] = []
    for identifier in prerelease.split("."):
        if identifier.isdigit():
            identifiers.append((0, int(identifier)))
        else:
            identifiers.append((1, identifier))
    return major, minor, patch, 0, tuple(identifiers)


def reject_unknown(value: Mapping[str, Any], allowed: set[str] | frozenset[str], path: str) -> list[Issue]:
    return [
        issue("field.unknown", f"{path}/{key}", f"unknown field: {key}")
        for key in value
        if key not in allowed
    ]


def require_nonempty_string(value: object, path: str, code: str = "string.required") -> list[Issue]:
    if not isinstance(value, str) or not value.strip():
        return [issue(code, path, "must be a non-empty string")]
    return []


def validate_string_array(
    value: object,
    path: str,
    *,
    nonempty: bool = False,
    unique: bool = False,
) -> list[Issue]:
    if not isinstance(value, list):
        return [issue("array.required", path, "must be an array")]
    issues: list[Issue] = []
    if nonempty and not value:
        issues.append(issue("array.empty", path, "must not be empty"))
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}/{index}"
        if not isinstance(item, str) or not item.strip():
            issues.append(issue("array.item", item_path, "must be a non-empty string"))
        elif unique and item in seen:
            issues.append(issue("array.duplicate", item_path, "must not contain duplicates"))
        elif isinstance(item, str):
            seen.add(item)
    return issues


def _safe_git_path(value: object) -> bool:
    return is_safe_git_path(value)


def _canonical_https_uri(value: object) -> bool:
    return is_canonical_https_uri(value)


def validate_target(value: object, path: str = "/target", *, fixed: bool = False) -> list[Issue]:
    if not isinstance(value, dict):
        return [issue("target.object", path, "must be a target object")]
    kind = value.get("kind")
    issues: list[Issue] = []
    if kind == "git":
        issues.extend(reject_unknown(value, {"kind", "path", "commit", "repository"}, path))
        if not _safe_git_path(value.get("path")):
            issues.append(issue("target.path", f"{path}/path", "must be a safe repository-relative file path"))
        commit = value.get("commit")
        repository = value.get("repository")
        if commit is not None and (not isinstance(commit, str) or COMMIT_RE.fullmatch(commit) is None):
            issues.append(issue("target.commit", f"{path}/commit", "must be a full 40-character lowercase commit"))
        if fixed and commit is None:
            issues.append(issue("target.not_fixed", f"{path}/commit", "fixed Git target requires commit"))
        if repository is not None:
            if not _canonical_https_uri(repository):
                issues.append(issue("target.repository", f"{path}/repository", "must be a credential-free canonical HTTPS URI"))
            if commit is None:
                issues.append(issue("target.cross_repository_live", f"{path}/commit", "cross-repository target must be fixed"))
        return issues
    if kind == "uri":
        issues.extend(reject_unknown(value, {"kind", "uri", "sha256"}, path))
        if not _canonical_https_uri(value.get("uri")):
            issues.append(issue("target.uri", f"{path}/uri", "must be a credential-free canonical HTTPS URI"))
        digest = value.get("sha256")
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            issues.append(issue("target.sha256", f"{path}/sha256", "must be 64 lowercase hexadecimal characters"))
        return issues
    return [issue("target.kind", f"{path}/kind", "must be git or uri")]


def validate_fixed_ref(
    value: object,
    path: str = "/ref",
    *,
    repository: Path | None = None,
    structural_only: bool = True,
) -> list[Issue]:
    if not isinstance(value, dict):
        return [issue("fixed_ref.object", path, "must be an object containing target and sha256")]
    issues = reject_unknown(value, {"target", "sha256"}, path)
    target = value.get("target")
    target_issues = validate_target(target, f"{path}/target", fixed=True)
    issues.extend(target_issues)
    digest = value.get("sha256")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        issues.append(issue("fixed_ref.sha256", f"{path}/sha256", "must be 64 lowercase hexadecimal characters"))
    if isinstance(target, dict) and target.get("kind") == "uri" and digest != target.get("sha256"):
        issues.append(issue("fixed_ref.digest_mismatch", f"{path}/sha256", "must equal URI target sha256"))
    if not target_issues and repository is not None and isinstance(digest, str) and SHA256_RE.fullmatch(digest):
        issues.extend(_verify_local_git_ref(target, digest, path, repository))
    elif (
        not structural_only
        and not target_issues
        and isinstance(target, Mapping)
        and target.get("kind") == "git"
    ):
        issues.append(
            issue(
                "fixed_ref.verification_context_required",
                path,
                "fixed Git references require a repository for commit-byte verification",
            )
        )
    return issues


def _verify_local_git_ref(
    target: Mapping[str, Any],
    digest: str,
    path: str,
    repository: Path,
) -> list[Issue]:
    if target.get("kind") != "git":
        return [issue("fixed_ref.external_unverified", path, "URI references require externally supplied retrieval evidence")]
    commit = target.get("commit")
    relative = target.get("path")
    if not isinstance(commit, str) or not isinstance(relative, str):
        return []
    root = repository.resolve()
    try:
        tree = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-z", commit, "--", relative],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        return [issue("fixed_ref.git_unavailable", path, f"cannot resolve fixed Git object: {exc}")]
    entries = [entry for entry in tree.split(b"\0") if entry]
    if len(entries) != 1:
        return [issue("fixed_ref.missing", f"{path}/target/path", "fixed Git path does not name exactly one object")]
    metadata, separator, encoded_path = entries[0].partition(b"\t")
    fields = metadata.split()
    if not separator or len(fields) != 3 or encoded_path != relative.encode("utf-8"):
        return [issue("fixed_ref.git_response", path, "Git returned an unexpected tree entry")]
    mode, object_type, object_id = fields
    if mode == b"120000":
        return [issue("fixed_ref.symlink", f"{path}/target/path", "fixed references must not name a symbolic link")]
    if object_type != b"blob":
        return [issue("fixed_ref.not_file", f"{path}/target/path", "fixed references must name a regular file blob")]
    try:
        payload = subprocess.run(
            ["git", "-C", str(root), "cat-file", "blob", object_id.decode("ascii")],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, UnicodeDecodeError, subprocess.CalledProcessError) as exc:
        return [issue("fixed_ref.git_unavailable", path, f"cannot read fixed Git blob: {exc}")]
    if hashlib.sha256(payload).hexdigest() != digest:
        return [issue("fixed_ref.digest_mismatch", f"{path}/sha256", "does not match bytes stored at the fixed Git commit")]
    return []


def fixed_ref_key(value: Mapping[str, Any]) -> tuple[object, ...]:
    target = value.get("target", {})
    if not isinstance(target, Mapping):
        return (None,)
    if target.get("kind") == "git":
        return ("git", target.get("repository"), target.get("commit"), target.get("path"), value.get("sha256"))
    return ("uri", target.get("uri"), target.get("sha256"), value.get("sha256"))


def validate_fixed_ref_array(value: object, path: str, *, nonempty: bool = False) -> list[Issue]:
    if not isinstance(value, list):
        return [issue("array.required", path, "must be an array")]
    issues: list[Issue] = []
    if nonempty and not value:
        issues.append(issue("array.empty", path, "must not be empty"))
    seen: set[tuple[object, ...]] = set()
    for index, item in enumerate(value):
        item_path = f"{path}/{index}"
        item_issues = validate_fixed_ref(item, item_path, structural_only=True)
        issues.extend(item_issues)
        if not item_issues and isinstance(item, Mapping):
            key = fixed_ref_key(item)
            if key in seen:
                issues.append(issue("array.duplicate", item_path, "duplicate fixed reference"))
            seen.add(key)
    return issues


def validate_component_ref(value: object, path: str) -> list[Issue]:
    if not isinstance(value, dict):
        return [issue("component.object", path, "must be a fixed component object")]
    issues = reject_unknown(value, {"name", "version", "sha256"}, path)
    issues.extend(require_nonempty_string(value.get("name"), f"{path}/name", "component.name"))
    if not is_exact_semver(value.get("version")):
        issues.append(issue("component.version", f"{path}/version", "must be exact SemVer"))
    digest = value.get("sha256")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        issues.append(issue("component.sha256", f"{path}/sha256", "must be 64 lowercase hexadecimal characters"))
    return issues


def validate_timestamp(value: object, path: str) -> list[Issue]:
    if not isinstance(value, str):
        return [issue("timestamp.type", path, "must be an RFC 3339 UTC timestamp")]
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return [issue("timestamp.format", path, "must be an RFC 3339 UTC timestamp")]
    if not value.endswith("Z") or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        return [issue("timestamp.utc", path, "must use UTC with Z suffix")]
    return []


def validate_provenance(value: object, path: str = "/provenance") -> list[Issue]:
    if not isinstance(value, list):
        return [issue("provenance.array", path, "must be an array")]
    issues: list[Issue] = []
    for index, record in enumerate(value):
        record_path = f"{path}/{index}"
        if not isinstance(record, dict):
            issues.append(issue("provenance.object", record_path, "must be an object"))
            continue
        issues.extend(reject_unknown(record, {"activity", "inputs", "generator"}, record_path))
        issues.extend(require_nonempty_string(record.get("activity"), f"{record_path}/activity", "provenance.activity"))
        issues.extend(validate_fixed_ref_array(record.get("inputs"), f"{record_path}/inputs", nonempty=True))
        if "generator" in record:
            issues.extend(validate_component_ref(record.get("generator"), f"{record_path}/generator"))
    return issues


def validate_artifact_envelope(
    value: object,
    expected_type: str,
    *,
    allow_relations: bool = False,
) -> list[Issue]:
    if not isinstance(value, dict):
        return [issue("artifact.object", "", "Artifact must be an object")]
    allowed = {"contract", "target", "type", "spec", "title", "provenance", "assurance"}
    if allow_relations:
        allowed.add("relations")
    issues = reject_unknown(value, allowed, "")
    contract = value.get("contract")
    if not isinstance(contract, dict):
        issues.append(issue("contract.object", "/contract", "must be an object"))
    else:
        issues.extend(reject_unknown(contract, {"name", "version"}, "/contract"))
        if contract.get("name") != "research-os/artifact":
            issues.append(issue("contract.name", "/contract/name", "must be research-os/artifact"))
        version = contract.get("version")
        if not is_exact_semver(version):
            issues.append(issue("contract.version", "/contract/version", "must be exact SemVer"))
        elif version not in ARTIFACT_CONTRACTS:
            issues.append(issue("contract.unsupported", "/contract/version", "unsupported Artifact contract version"))
    issues.extend(validate_target(value.get("target"), "/target"))
    type_ref = value.get("type")
    if not isinstance(type_ref, dict):
        issues.append(issue("type.object", "/type", "must be an object"))
    else:
        issues.extend(reject_unknown(type_ref, {"name", "version"}, "/type"))
        if type_ref.get("name") != expected_type:
            issues.append(issue("type.name", "/type/name", f"must be {expected_type}"))
        if type_ref.get("version") != TYPE_VERSION:
            issues.append(issue("type.version", "/type/version", f"must be {TYPE_VERSION}"))
    if not isinstance(value.get("spec"), dict):
        issues.append(issue("spec.object", "/spec", "must be an object"))
    if "title" in value and (not isinstance(value["title"], str) or not value["title"].strip()):
        issues.append(issue("title.string", "/title", "must be a non-empty string"))
    if "provenance" in value:
        issues.extend(validate_provenance(value["provenance"]))
    if "assurance" in value:
        issues.extend(validate_fixed_ref_array(value["assurance"], "/assurance"))
    return issues


def prefixed(issues: Iterable[Issue], prefix: str) -> list[Issue]:
    return [Issue(item.code, f"{prefix}{item.path}", item.message) for item in issues]
