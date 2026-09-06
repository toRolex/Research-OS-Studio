from __future__ import annotations

from collections.abc import Iterable

from .issues import Issue
from .registry import TYPE_NAME_RE, TypeRegistry
from .semver import is_exact_semver
from .targets import validate_target

SUPPORTED_ENVELOPE_VERSIONS = frozenset({"1.0.0", "1.1.0"})
_ALLOWED_FIELDS = frozenset(
    {
        "contract",
        "target",
        "type",
        "spec",
        "title",
        "provenance",
        "relations",
        "assurance",
    }
)


def validate_artifact(value: object, registry: TypeRegistry) -> list[Issue]:
    if not isinstance(registry, TypeRegistry):
        raise TypeError("registry must be a TypeRegistry")
    if not isinstance(value, dict):
        return [Issue("artifact.object", "Artifact must be a JSON object", "")]
    issues: list[Issue] = []
    _unknown_fields(value, _ALLOWED_FIELDS, issues, "artifact.field", "")
    contract = value.get("contract")
    if not isinstance(contract, dict):
        issues.append(Issue("contract.object", "contract must be an object", "/contract"))
    else:
        _unknown_fields(
            contract, {"name", "version"}, issues, "contract.field", "/contract"
        )
        if contract.get("name") != "research-os/artifact":
            issues.append(
                Issue(
                    "contract.name",
                    "contract.name must be research-os/artifact",
                    "/contract/name",
                )
            )
        version = contract.get("version")
        if not is_exact_semver(version):
            issues.append(
                Issue(
                    "contract.version",
                    "contract.version must be exact SemVer",
                    "/contract/version",
                )
            )
        elif version not in SUPPORTED_ENVELOPE_VERSIONS:
            issues.append(
                Issue(
                    "contract.version.unsupported",
                    "unsupported Artifact envelope version",
                    "/contract/version",
                )
            )
    issues.extend(validate_target(value.get("target")))
    artifact_type = value.get("type")
    type_name: object = None
    type_version: object = None
    if not isinstance(artifact_type, dict):
        issues.append(Issue("type.object", "type must be an object", "/type"))
    else:
        _unknown_fields(
            artifact_type, {"name", "version"}, issues, "type.field", "/type"
        )
        type_name = artifact_type.get("name")
        type_version = artifact_type.get("version")
        if not isinstance(type_name, str) or TYPE_NAME_RE.fullmatch(type_name) is None:
            issues.append(
                Issue("type.name", "type.name must be lowercase kebab-case", "/type/name")
            )
        if not is_exact_semver(type_version):
            issues.append(
                Issue(
                    "type.version",
                    "type.version must be exact SemVer",
                    "/type/version",
                )
            )
    spec = value.get("spec")
    if not isinstance(spec, dict):
        issues.append(Issue("spec.object", "spec must be an object", "/spec"))
    elif (
        isinstance(type_name, str)
        and TYPE_NAME_RE.fullmatch(type_name) is not None
        and is_exact_semver(type_version)
    ):
        issues.extend(registry.validate(type_name, type_version, spec))
    if "title" in value and not isinstance(value["title"], str):
        issues.append(Issue("artifact.title", "title must be a string", "/title"))
    for field in ("provenance", "relations", "assurance"):
        if field not in value:
            continue
        observations = value[field]
        if not isinstance(observations, list):
            issues.append(
                Issue(f"artifact.{field}", f"{field} must be an array", f"/{field}")
            )
            continue
        for index, observation in enumerate(observations):
            if not isinstance(observation, dict):
                issues.append(
                    Issue(
                        f"artifact.{field}.item",
                        f"{field} items must be objects",
                        f"/{field}/{index}",
                    )
                )
    return issues


def validate_artifacts(
    values: Iterable[object], registry: TypeRegistry
) -> list[list[Issue]]:
    return [validate_artifact(value, registry) for value in values]


def _unknown_fields(
    value: dict[object, object],
    allowed: set[str] | frozenset[str],
    issues: list[Issue],
    code: str,
    path: str,
) -> None:
    for key in value:
        if not isinstance(key, str) or key not in allowed:
            issues.append(Issue(code, f"unknown field: {key}", f"{path}/{key}"))
