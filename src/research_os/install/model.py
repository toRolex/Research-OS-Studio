from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Any, Mapping

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _exact_keys(value: Mapping[str, Any], expected: set[str], subject: str) -> None:
    unknown = set(value) - expected
    if unknown:
        raise ValueError(f"{subject} has unknown fields: {', '.join(sorted(unknown))}")


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _semver(value: object, field: str) -> str:
    text = _text(value, field)
    if not SEMVER.fullmatch(text):
        raise ValueError(f"{field} must be exact SemVer")
    return text


def _sha256(value: object, field: str) -> str:
    text = _text(value, field)
    if not SHA256.fullmatch(text):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return text


def _safe_projection_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or not value or value.endswith("/"):
        raise ValueError("projection path must be a relative file path")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("projection path contains an unsafe component")
    return path.as_posix()


class SkillKind(StrEnum):
    WORKFLOW = "workflow"
    DISCIPLINE = "discipline"


class CapabilityState(StrEnum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNVERIFIED = "unverified"


@dataclass(frozen=True, slots=True)
class SkillDescriptor:
    name: str
    version: str
    kind: SkillKind
    sha256: str
    content: bytes

    def __post_init__(self) -> None:
        kind = self.kind if isinstance(self.kind, SkillKind) else SkillKind(self.kind)
        object.__setattr__(self, "kind", kind)
        if not SKILL_NAME.fullmatch(self.name):
            raise ValueError("skill name is invalid")
        _semver(self.version, "skill.version")
        _sha256(self.sha256, "skill.sha256")
        if digest_bytes(self.content) != self.sha256:
            raise ValueError(f"skill digest does not match content: {self.name}")
        try:
            self.content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"skill content is not UTF-8: {self.name}") from exc


@dataclass(frozen=True, slots=True)
class CapabilityProfile:
    version: str
    capabilities: Mapping[str, CapabilityState]

    def __post_init__(self) -> None:
        _semver(self.version, "capability_profile.version")
        normalized: dict[str, CapabilityState] = {}
        for name, state in self.capabilities.items():
            if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
                raise ValueError(f"invalid capability name: {name!r}")
            normalized[name] = state if isinstance(state, CapabilityState) else CapabilityState(state)
        object.__setattr__(self, "capabilities", MappingProxyType(dict(sorted(normalized.items()))))

    def missing(self, required: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(
            name
            for name in sorted(set(required))
            if self.capabilities.get(name, CapabilityState.UNSUPPORTED) is not CapabilityState.SUPPORTED
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "capabilities": {name: state.value for name, state in self.capabilities.items()},
        }


@dataclass(frozen=True, slots=True)
class AdapterDefinition:
    adapter: str
    version: str
    projection_version: str
    workflow_invocation: str
    automatic_next_workflow: bool
    workflow_policy: Mapping[str, object]
    discipline_policy: Mapping[str, object]
    required_capabilities: tuple[str, ...]
    capability_profile: CapabilityProfile

    def __post_init__(self) -> None:
        if self.adapter not in {"claude-code", "codex"}:
            raise ValueError(f"unsupported adapter: {self.adapter}")
        _semver(self.version, "adapter.version")
        _semver(self.projection_version, "adapter.projection_version")
        if self.workflow_invocation != "explicit_user_only":
            raise ValueError("workflow_invocation must be explicit_user_only")
        if not isinstance(self.automatic_next_workflow, bool) or self.automatic_next_workflow:
            raise ValueError("automatic_next_workflow must be false")
        if not isinstance(self.workflow_policy, Mapping) or not isinstance(self.discipline_policy, Mapping):
            raise ValueError("adapter policies must be objects")
        workflow_policy = dict(self.workflow_policy)
        discipline_policy = dict(self.discipline_policy)
        if self.adapter == "claude-code":
            if workflow_policy != {
                "user_invocable": True,
                "disable_model_invocation": True,
            }:
                raise ValueError("claude-code workflow_policy does not enforce explicit user invocation")
            if discipline_policy != {
                "user_invocable": False,
                "workflow_internal_only": True,
            }:
                raise ValueError("claude-code discipline_policy does not enforce workflow-only visibility")
        elif self.adapter == "codex":
            if workflow_policy != {"allow_implicit_invocation": False}:
                raise ValueError("codex workflow_policy does not disable implicit invocation")
            if discipline_policy != {"allow_implicit_invocation": False}:
                raise ValueError("codex discipline_policy does not disable implicit invocation")
        required = tuple(sorted(set(self.required_capabilities)))
        for name in required:
            if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
                raise ValueError(f"invalid required capability: {name!r}")
        object.__setattr__(self, "required_capabilities", required)
        object.__setattr__(self, "workflow_policy", MappingProxyType(workflow_policy))
        object.__setattr__(self, "discipline_policy", MappingProxyType(discipline_policy))

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> AdapterDefinition:
        expected = {
            "adapter",
            "version",
            "projection_version",
            "role",
            "core_semantics",
            "workflow_invocation",
            "automatic_next_workflow",
            "workflow_policy",
            "discipline_policy",
            "required_capabilities",
            "capability_profile",
        }
        _exact_keys(value, expected, "adapter")
        if value.get("role") != "generated platform projection":
            raise ValueError("adapter.role is invalid")
        if value.get("core_semantics") != "shared":
            raise ValueError("adapter.core_semantics must be shared")
        raw_profile = value.get("capability_profile")
        if not isinstance(raw_profile, Mapping):
            raise ValueError("capability_profile must be an object")
        _exact_keys(raw_profile, {"version", "capabilities"}, "capability_profile")
        capabilities = raw_profile.get("capabilities")
        if not isinstance(capabilities, Mapping):
            raise ValueError("capability_profile.capabilities must be an object")
        required = value.get("required_capabilities")
        if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
            raise ValueError("required_capabilities must be a string array")
        return cls(
            adapter=_text(value.get("adapter"), "adapter.adapter"),
            version=_semver(value.get("version"), "adapter.version"),
            projection_version=_semver(value.get("projection_version"), "adapter.projection_version"),
            workflow_invocation=_text(value.get("workflow_invocation"), "adapter.workflow_invocation"),
            automatic_next_workflow=value.get("automatic_next_workflow"),
            workflow_policy=value.get("workflow_policy"),
            discipline_policy=value.get("discipline_policy"),
            required_capabilities=tuple(required),
            capability_profile=CapabilityProfile(
                version=_semver(raw_profile.get("version"), "capability_profile.version"),
                capabilities=capabilities,
            ),
        )


@dataclass(frozen=True, slots=True)
class ProjectionFile:
    path: str
    content: bytes

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", _safe_projection_path(self.path))

    @property
    def sha256(self) -> str:
        return digest_bytes(self.content)


@dataclass(frozen=True, slots=True)
class ProjectionManifest:
    adapter: str
    adapter_version: str
    projection_version: str
    adapter_sha256: str
    capability_profile: CapabilityProfile
    workflow_invocation: str
    automatic_next_workflow: bool
    projection_scope: str
    canonical_skills: tuple[Mapping[str, str], ...]
    excluded_canonical_skills: tuple[Mapping[str, str], ...]
    blocked_capabilities: tuple[str, ...]
    workflow_entries: tuple[str, ...]
    discipline_entries: tuple[str, ...]
    files: Mapping[str, str]
    projection_digest: str

    def to_dict(self, *, include_digest: bool = True) -> dict[str, object]:
        result: dict[str, object] = {
            "contract": {"name": "research-os/projection-manifest", "version": "1.0.0"},
            "adapter": {
                "name": self.adapter,
                "version": self.adapter_version,
                "sha256": self.adapter_sha256,
            },
            "projection_version": self.projection_version,
            "capability_profile": self.capability_profile.to_dict(),
            "workflow_invocation": self.workflow_invocation,
            "automatic_next_workflow": self.automatic_next_workflow,
            "projection_scope": self.projection_scope,
            "canonical_skills": [dict(skill) for skill in self.canonical_skills],
            "excluded_canonical_skills": [dict(skill) for skill in self.excluded_canonical_skills],
            "blocked_capabilities": list(self.blocked_capabilities),
            "workflow_entries": list(self.workflow_entries),
            "discipline_entries": list(self.discipline_entries),
            "files": dict(self.files),
        }
        if include_digest:
            result["projection_digest"] = self.projection_digest
        return result


@dataclass(frozen=True, slots=True)
class ProjectionPlan:
    manifest: ProjectionManifest
    files: tuple[ProjectionFile, ...]


@dataclass(frozen=True, slots=True)
class ProjectionBlocked:
    adapter: str
    missing_capabilities: tuple[str, ...]

    exit_code: int = 3
    verdict: str = "blocked"
    status: str = "stopped"
    stop_reason: str = "platform_capability_unavailable"

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": {"name": "research-os/adapter-result", "version": "1.0.0"},
            "adapter": self.adapter,
            "verdict": self.verdict,
            "status": self.status,
            "stop_reason": self.stop_reason,
            "missing_capabilities": list(self.missing_capabilities),
            "issues": [
                {
                    "code": "adapter.capability",
                    "message": f"required capability is not supported: {name}",
                }
                for name in self.missing_capabilities
            ],
            "outputs": [],
            "next_steps": [],
        }
