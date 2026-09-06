from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .common import (
    Issue,
    is_exact_semver,
    reject_unknown,
    require_nonempty_string,
    semver_key,
    validate_artifact_envelope,
    validate_component_ref,
    validate_fixed_ref,
    validate_timestamp,
)


def validate_version_range(value: object, path: str = "/spec/source") -> list[Issue]:
    if not isinstance(value, dict):
        return [Issue("version_range.object", path, "must be a structured SemVer range")]
    issues = reject_unknown(value, {"min", "min_inclusive", "max", "max_inclusive"}, path)
    minimum = value.get("min")
    maximum = value.get("max")
    if not is_exact_semver(minimum):
        issues.append(Issue("version_range.min", f"{path}/min", "must be exact SemVer"))
    if not is_exact_semver(maximum):
        issues.append(Issue("version_range.max", f"{path}/max", "must be exact SemVer"))
    for field in ("min_inclusive", "max_inclusive"):
        if not isinstance(value.get(field), bool):
            issues.append(Issue("version_range.bound", f"{path}/{field}", "must be boolean"))
    if is_exact_semver(minimum) and is_exact_semver(maximum):
        lower = semver_key(minimum)
        upper = semver_key(maximum)
        if lower > upper or (lower == upper and (value.get("min_inclusive") is not True or value.get("max_inclusive") is not True)):
            issues.append(Issue("version_range.empty", path, "range must contain at least one version"))
    return issues


def version_in_range(version: str, version_range: Mapping[str, Any]) -> bool:
    if not is_exact_semver(version) or validate_version_range(version_range):
        return False
    candidate = semver_key(version)
    minimum = semver_key(version_range["min"])
    maximum = semver_key(version_range["max"])
    lower_ok = candidate > minimum or (candidate == minimum and version_range["min_inclusive"])
    upper_ok = candidate < maximum or (candidate == maximum and version_range["max_inclusive"])
    return bool(lower_ok and upper_ok)


def validate_migration_rule(value: object) -> list[Issue]:
    issues = validate_artifact_envelope(value, "migration-rule")
    if not isinstance(value, dict) or not isinstance(value.get("spec"), dict):
        return issues
    spec = value["spec"]
    issues.extend(reject_unknown(spec, {"artifact_type", "source", "target_version", "migrator", "input_validator", "output_validator"}, "/spec"))
    issues.extend(require_nonempty_string(spec.get("artifact_type"), "/spec/artifact_type", "migration.artifact_type"))
    issues.extend(validate_version_range(spec.get("source"), "/spec/source"))
    if not is_exact_semver(spec.get("target_version")):
        issues.append(Issue("migration.target_version", "/spec/target_version", "must be exact SemVer"))
    for field in ("migrator", "input_validator", "output_validator"):
        issues.extend(validate_component_ref(spec.get(field), f"/spec/{field}"))
    source = spec.get("source")
    target = spec.get("target_version")
    if isinstance(source, Mapping) and is_exact_semver(target) and version_in_range(target, source):
        issues.append(Issue("migration.target_in_source", "/spec/target_version", "target version must be outside source range"))
    return issues


def select_migration_rule(
    rules: Sequence[Mapping[str, Any]],
    *,
    artifact_type: str,
    source_version: str,
    target_version: str,
) -> tuple[Mapping[str, Any] | None, list[Issue]]:
    matches: list[Mapping[str, Any]] = []
    invalid: list[Issue] = []
    for index, rule in enumerate(rules):
        rule_issues = validate_migration_rule(rule)
        if rule_issues:
            invalid.extend(Issue(item.code, f"/{index}{item.path}", item.message) for item in rule_issues)
            continue
        spec = rule["spec"]
        if spec["artifact_type"] == artifact_type and spec["target_version"] == target_version and version_in_range(source_version, spec["source"]):
            matches.append(rule)
    if invalid:
        return None, invalid
    if not matches:
        return None, [Issue("migration.no_rule", "", "no migration rule matches source and target")]
    if len(matches) > 1:
        return None, [Issue("migration.multiple_rules", "", "multiple migration rules match source and target")]
    return matches[0], []


def validate_migration_receipt(
    value: object,
    *,
    rule: Mapping[str, Any] | None = None,
    rule_digest: str | None = None,
    input_artifact: Mapping[str, Any] | None = None,
    input_digest: str | None = None,
    output_artifact: Mapping[str, Any] | None = None,
    output_digest: str | None = None,
) -> list[Issue]:
    issues = validate_artifact_envelope(value, "migration-receipt")
    if not isinstance(value, dict) or not isinstance(value.get("spec"), dict):
        return issues
    spec = value["spec"]
    issues.extend(
        reject_unknown(
            spec,
            {
                "input",
                "output",
                "input_contract",
                "output_contract",
                "rule",
                "migrator",
                "input_validator",
                "output_validator",
                "created_at",
            },
            "/spec",
        )
    )
    for field in ("input", "output", "rule"):
        issues.extend(validate_fixed_ref(spec.get(field), f"/spec/{field}"))
    for field in ("input_contract", "output_contract"):
        issues.extend(_validate_contract_ref(spec.get(field), f"/spec/{field}"))
    for field in ("migrator", "input_validator", "output_validator"):
        issues.extend(_validate_execution(spec.get(field), f"/spec/{field}"))
    issues.extend(validate_timestamp(spec.get("created_at"), "/spec/created_at"))

    context = {
        "rule": (rule, rule_digest),
        "input": (input_artifact, input_digest),
        "output": (output_artifact, output_digest),
    }
    for field, (artifact, digest) in context.items():
        if artifact is None or digest is None:
            issues.append(
                Issue(
                    "migration.context_required",
                    f"/spec/{field}",
                    f"successful receipt validation requires supplied {field} Artifact and digest",
                )
            )
        else:
            issues.extend(_validate_bound_artifact(spec.get(field), artifact, digest, f"/spec/{field}"))

    if rule is not None and rule_digest is not None:
        rule_issues = validate_migration_rule(rule)
        issues.extend(Issue(item.code, f"/context/rule{item.path}", item.message) for item in rule_issues)
        rule_spec = rule.get("spec")
        if isinstance(rule_spec, Mapping):
            for field in ("migrator", "input_validator", "output_validator"):
                execution = spec.get(field)
                component = execution.get("component") if isinstance(execution, Mapping) else None
                if component != rule_spec.get(field):
                    issues.append(
                        Issue(
                            "migration.component_mismatch",
                            f"/spec/{field}/component",
                            f"must equal the component fixed by the selected migration rule",
                        )
                    )
            input_contract = spec.get("input_contract")
            output_contract = spec.get("output_contract")
            if isinstance(input_contract, Mapping):
                if input_contract.get("type_name") != rule_spec.get("artifact_type"):
                    issues.append(Issue("migration.input_type_mismatch", "/spec/input_contract/type_name", "must match migration rule artifact_type"))
                source_version = input_contract.get("type_version")
                source_range = rule_spec.get("source")
                if not isinstance(source_version, str) or not isinstance(source_range, Mapping) or not version_in_range(source_version, source_range):
                    issues.append(Issue("migration.source_version_mismatch", "/spec/input_contract/type_version", "must fall within the migration rule source range"))
            if isinstance(output_contract, Mapping):
                if output_contract.get("type_name") != rule_spec.get("artifact_type"):
                    issues.append(Issue("migration.output_type_mismatch", "/spec/output_contract/type_name", "must match migration rule artifact_type"))
                if output_contract.get("type_version") != rule_spec.get("target_version"):
                    issues.append(Issue("migration.target_version_mismatch", "/spec/output_contract/type_version", "must equal the migration rule target_version"))

    _compare_contract_to_artifact(spec.get("input_contract"), input_artifact, "/spec/input_contract", issues)
    _compare_contract_to_artifact(spec.get("output_contract"), output_artifact, "/spec/output_contract", issues)

    input_ref = spec.get("input")
    output_ref = spec.get("output")
    if isinstance(input_ref, Mapping) and isinstance(output_ref, Mapping):
        if input_ref == output_ref:
            issues.append(Issue("migration.overwrite", "/spec/output", "migration output must be a new fixed Artifact revision"))
        input_target = input_ref.get("target")
        output_target = output_ref.get("target")
        if isinstance(input_target, Mapping) and isinstance(output_target, Mapping):
            if input_target.get("kind") == output_target.get("kind") == "git" and input_target.get("commit") == output_target.get("commit"):
                issues.append(Issue("migration.new_commit", "/spec/output/target/commit", "migration output must use a new Git commit"))
    input_contract = spec.get("input_contract")
    output_contract = spec.get("output_contract")
    if isinstance(input_contract, Mapping) and isinstance(output_contract, Mapping) and input_contract == output_contract:
        issues.append(Issue("migration.version_unchanged", "/spec/output_contract", "migration must change contract or type version"))
    return issues


def _validate_bound_artifact(
    recorded_ref: object,
    artifact: Mapping[str, Any],
    digest: str,
    path: str,
) -> list[Issue]:
    target = artifact.get("target")
    if not isinstance(target, Mapping) or not isinstance(recorded_ref, Mapping):
        return [Issue("migration.binding_mismatch", path, "receipt reference must bind the supplied Artifact")]
    expected = {"target": target, "sha256": digest}
    if recorded_ref != expected:
        return [Issue("migration.binding_mismatch", path, "receipt reference must bind the supplied Artifact revision and digest")]
    return []


def _compare_contract_to_artifact(
    contract_ref: object,
    artifact: Mapping[str, Any] | None,
    path: str,
    issues: list[Issue],
) -> None:
    if artifact is None or not isinstance(contract_ref, Mapping):
        return
    contract = artifact.get("contract")
    type_ref = artifact.get("type")
    if not isinstance(contract, Mapping) or not isinstance(type_ref, Mapping):
        issues.append(Issue("migration.artifact_envelope", path, "supplied Artifact must expose contract and type refs"))
        return
    actual = {
        "artifact_contract": contract.get("version"),
        "type_name": type_ref.get("name"),
        "type_version": type_ref.get("version"),
    }
    if contract_ref != actual:
        issues.append(Issue("migration.contract_mismatch", path, "receipt contract ref must match the supplied Artifact envelope"))


def _validate_contract_ref(value: object, path: str) -> list[Issue]:
    if not isinstance(value, dict):
        return [Issue("migration.contract", path, "must be an object")]
    issues = reject_unknown(value, {"artifact_contract", "type_name", "type_version"}, path)
    if not is_exact_semver(value.get("artifact_contract")):
        issues.append(Issue("migration.artifact_contract", f"{path}/artifact_contract", "must be exact SemVer"))
    issues.extend(require_nonempty_string(value.get("type_name"), f"{path}/type_name", "migration.type_name"))
    if not is_exact_semver(value.get("type_version")):
        issues.append(Issue("migration.type_version", f"{path}/type_version", "must be exact SemVer"))
    return issues


def _validate_execution(value: object, path: str) -> list[Issue]:
    if not isinstance(value, dict):
        return [Issue("migration.execution", path, "must bind component and verdict")]
    issues = reject_unknown(value, {"component", "verdict"}, path)
    issues.extend(validate_component_ref(value.get("component"), f"{path}/component"))
    if value.get("verdict") != "pass":
        issues.append(Issue("migration.execution_verdict", f"{path}/verdict", "must be pass in a successful migration receipt"))
    return issues
