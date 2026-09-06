from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from .builders import BUILDERS
from .models import (
    ARTIFACT_CONTRACT,
    REPORT_CONTRACT,
    TYPE_VERSION,
    InputPin,
    InputRequirement,
    OuterWorkflowError,
    PinnedInput,
    WorkflowDefinition,
    WorkflowResult,
    WORKFLOWS,
)


def _object(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise OuterWorkflowError("input.schema", f"{field} must be an object")
    return value


def _validate_artifact_envelope(
    root: Mapping[str, Any], *, path: str, requirement: InputRequirement
) -> None:
    allowed_fields = {
        "contract",
        "target",
        "type",
        "spec",
        "title",
        "provenance",
        "relations",
        "assurance",
    }
    unknown = set(root) - allowed_fields
    if unknown:
        raise OuterWorkflowError(
            "input.schema", f"input {path} contains unknown fields: {sorted(unknown)}"
        )
    contract = _object(root.get("contract"), "contract")
    if set(contract) != {"name", "version"}:
        raise OuterWorkflowError(
            "input.schema", "contract must contain only name and version"
        )
    if (
        contract.get("name") != ARTIFACT_CONTRACT["name"]
        or contract.get("version") != ARTIFACT_CONTRACT["version"]
    ):
        raise OuterWorkflowError(
            "input.contract", "input must use research-os/artifact 1.1.0"
        )
    artifact_type = _object(root.get("type"), "type")
    if set(artifact_type) != {"name", "version"}:
        raise OuterWorkflowError("input.schema", "type must contain only name and version")
    if (
        artifact_type.get("name") not in requirement.type_names
        or artifact_type.get("version") != TYPE_VERSION
    ):
        raise OuterWorkflowError(
            "input.type",
            f"input {requirement.name} type must be one of: {', '.join(requirement.type_names)}",
        )
    target = _object(root.get("target"), "target")
    if set(target) != {"kind", "path"} or target.get("kind") != "git":
        raise OuterWorkflowError(
            "input.target", "outer workflow input must use a local live git target"
        )
    try:
        target_path = _safe_relative_path(target.get("path"), "artifact target")
    except (OuterWorkflowError, TypeError) as exc:
        raise OuterWorkflowError(
            "input.target", "artifact target must be a safe project-relative path"
        ) from exc
    if target_path != path:
        raise OuterWorkflowError(
            "input.target", "artifact target path must match the pinned input path"
        )
    _object(root.get("spec"), "spec")
    if "title" in root and not isinstance(root["title"], str):
        raise OuterWorkflowError("input.schema", "title must be a string")
    for field in ("provenance", "relations", "assurance"):
        if field in root and not isinstance(root[field], list):
            raise OuterWorkflowError("input.schema", f"{field} must be an array")


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _safe_relative_path(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise OuterWorkflowError(
            "path.invalid", f"{field} must be a safe project-relative file path"
        )
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or value in {".", ".."}
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise OuterWorkflowError(
            "path.invalid", f"{field} must be a safe project-relative file path"
        )
    return path.as_posix()


def _resolve_project_file(
    project: Path, relative: str, field: str, *, allow_missing: bool
) -> Path:
    clean = _safe_relative_path(relative, field)
    candidate = project.joinpath(*PurePosixPath(clean).parts)
    current = project
    for part in PurePosixPath(clean).parts:
        current = current / part
        if current.is_symlink():
            raise OuterWorkflowError(
                "path.symlink", f"{field} must not traverse a symlink"
            )
        if not current.exists():
            break
    if not allow_missing and (not candidate.is_file() or candidate.is_symlink()):
        raise OuterWorkflowError(
            "input.missing", f"{field} does not name a regular file"
        )
    try:
        candidate.resolve(strict=False).relative_to(project)
    except ValueError as exc:
        raise OuterWorkflowError("path.escape", f"{field} escapes the project") from exc
    return candidate


def _requirements_for(
    definition: WorkflowDefinition, count: int
) -> tuple[InputRequirement, ...]:
    if len(definition.inputs) == 1:
        requirement = definition.inputs[0]
        if not requirement.minimum <= count <= requirement.maximum:
            raise OuterWorkflowError(
                "input.count",
                f"{definition.name} requires {requirement.minimum}..{requirement.maximum} pinned inputs",
            )
        return (requirement,) * count
    if count != len(definition.inputs):
        raise OuterWorkflowError(
            "input.count",
            f"{definition.name} requires exactly {len(definition.inputs)} pinned inputs",
        )
    return definition.inputs


def _read_pinned_bytes(project: Path, relative: str, field: str) -> bytes:
    path = _resolve_project_file(project, relative, field, allow_missing=False)
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        raise OuterWorkflowError(
            "path.changed", f"{field} changed before it could be opened"
        ) from exc
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode):
            raise OuterWorkflowError(
                "input.missing", f"{field} does not name a regular file"
            )
        data = stream.read()
        try:
            current = os.stat(path, follow_symlinks=False)
        except OSError as exc:
            raise OuterWorkflowError(
                "input.changed", f"{field} changed while it was being read"
            ) from exc
        if not os.path.samestat(opened, current):
            raise OuterWorkflowError(
                "input.changed", f"{field} changed while it was being read"
            )
    return data


def _load_pinned_input(
    project: Path,
    pin: InputPin,
    requirement: InputRequirement,
    seen_paths: set[str],
) -> PinnedInput:
    clean = _safe_relative_path(pin.path, f"input {requirement.name}")
    if clean in seen_paths:
        raise OuterWorkflowError(
            "input.duplicate", "each pinned input path must be distinct"
        )
    seen_paths.add(clean)
    if len(pin.sha256) != 64 or any(
        character not in "0123456789abcdef" for character in pin.sha256
    ):
        raise OuterWorkflowError(
            "input.pin.invalid",
            "input SHA-256 must be 64 lowercase hexadecimal characters",
        )
    data = _read_pinned_bytes(project, clean, f"input {requirement.name}")
    actual = hashlib.sha256(data).hexdigest()
    if actual != pin.sha256:
        raise OuterWorkflowError(
            "input.pin.mismatch", f"input {clean} does not match the supplied SHA-256"
        )
    try:
        artifact = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OuterWorkflowError(
            "input.json", f"input {clean} must be UTF-8 JSON"
        ) from exc
    root = _object(artifact, "artifact")
    _validate_artifact_envelope(root, path=clean, requirement=requirement)
    if hashlib.sha256(
        _read_pinned_bytes(project, clean, f"input {requirement.name}")
    ).hexdigest() != pin.sha256:
        raise OuterWorkflowError(
            "input.changed", f"input {clean} changed while it was being read"
        )
    return PinnedInput(
        requirement=requirement.name, path=clean, sha256=pin.sha256, artifact=root
    )


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _candidate_artifact(
    definition: WorkflowDefinition,
    pinned: tuple[PinnedInput, ...],
    output_path: str,
    candidate: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], Mapping[str, int]]:
    draft = BUILDERS[definition.name](pinned, candidate)
    unknown_usage = set(draft.usage) - set(definition.budget)
    if unknown_usage:
        raise OuterWorkflowError(
            "budget.usage",
            f"builder reported unknown budget counters: {sorted(unknown_usage)}",
        )
    for counter, used in draft.usage.items():
        if (
            isinstance(used, bool)
            or not isinstance(used, int)
            or used < 0
            or used > definition.budget[counter]
        ):
            raise OuterWorkflowError(
                "budget.exceeded", f"builder exceeded {counter} budget"
            )
    artifact = {
        "contract": dict(ARTIFACT_CONTRACT),
        "target": {"kind": "git", "path": output_path},
        "type": {"name": definition.output_type, "version": TYPE_VERSION},
        "spec": _copy(draft.spec),
        "provenance": [
            {
                "target": _copy(item.artifact["target"]),
                "sha256": item.sha256,
                "purpose": f"pinned {item.requirement} workflow input",
            }
            for item in pinned
        ],
    }
    return artifact, draft.usage


def _report(
    definition: WorkflowDefinition,
    pinned: tuple[PinnedInput, ...],
    output_path: str,
    report_path: str,
    artifact_sha256: str,
    usage: Mapping[str, int],
) -> dict[str, Any]:
    return {
        "contract": dict(REPORT_CONTRACT),
        "workflow": {"name": definition.name, "version": TYPE_VERSION},
        "status": "stopped",
        "stop_reason": "candidate_complete",
        "inputs": [
            {"name": item.requirement, "path": item.path, "sha256": item.sha256}
            for item in pinned
        ],
        "outputs": [
            {"kind": "candidate", "path": output_path, "sha256": artifact_sha256},
            {"kind": "report", "path": report_path},
        ],
        "budget": {
            "limits": dict(definition.budget),
            "used": {counter: usage.get(counter, 0) for counter in definition.budget},
        },
        "invariants": list(definition.invariants),
        "next_steps": list(definition.options),
        "automatic_next_workflow": False,
        "human_acceptance": None,
    }


def _ensure_output_parent(project: Path, destination: Path, field: str) -> None:
    relative_parent = destination.parent.relative_to(project)
    current = project
    for part in relative_parent.parts:
        current = current / part
        if current.is_symlink():
            raise OuterWorkflowError(
                "path.symlink", f"{field} parent must not traverse a symlink"
            )
        if current.exists() and not current.is_dir():
            raise OuterWorkflowError(
                "output.parent", f"{field} parent must be a directory"
            )
        if not current.exists():
            current.mkdir()
    if not destination.parent.is_dir():
        raise OuterWorkflowError("output.parent", f"{field} parent must be a directory")


def _write_temp(parent: Path, data: bytes) -> Path:
    descriptor, name = tempfile.mkstemp(prefix=".research-os-outer-", dir=parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        Path(name).unlink(missing_ok=True)
        raise
    return Path(name)


def _publish_exclusive(temp: Path, destination: Path, project: Path) -> None:
    try:
        resolved_parent = destination.parent.resolve(strict=True)
    except OSError as exc:
        raise OuterWorkflowError(
            "path.changed", f"destination parent changed before publishing {destination.name}"
        ) from exc
    try:
        resolved_parent.relative_to(project)
    except ValueError as exc:
        raise OuterWorkflowError(
            "path.changed", f"destination parent escaped before publishing {destination.name}"
        ) from exc
    if resolved_parent != destination.parent or destination.parent.is_symlink():
        raise OuterWorkflowError(
            "path.changed", f"destination parent changed before publishing {destination.name}"
        )
    try:
        os.link(temp, destination, follow_symlinks=False)
    except FileExistsError as exc:
        raise OuterWorkflowError(
            "output.exists", f"refusing to overwrite {destination.name}"
        ) from exc
    finally:
        temp.unlink(missing_ok=True)


def run_outer_workflow(
    workflow: str,
    *,
    project: str | Path,
    inputs: Sequence[InputPin],
    output_path: str,
    report_path: str,
    candidate: Mapping[str, Any] | None = None,
) -> WorkflowResult:
    """Publish one deterministic candidate/report pair and never dispatch a next workflow."""

    definition = WORKFLOWS.get(workflow)
    if definition is None:
        raise OuterWorkflowError(
            "workflow.unknown", f"unknown outer workflow: {workflow}"
        )
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise OuterWorkflowError("project.invalid", "project must be a directory")
    requirements = _requirements_for(definition, len(inputs))
    output_clean = _safe_relative_path(output_path, "output")
    report_clean = _safe_relative_path(report_path, "report")
    input_paths = [_safe_relative_path(pin.path, "input") for pin in inputs]
    if len(set((*input_paths, output_clean, report_clean))) != len(input_paths) + 2:
        raise OuterWorkflowError(
            "output.overlap", "input, candidate, and report paths must be distinct"
        )
    output = _resolve_project_file(root, output_clean, "output", allow_missing=True)
    report_path_value = _resolve_project_file(
        root, report_clean, "report", allow_missing=True
    )
    if output.exists() or report_path_value.exists():
        raise OuterWorkflowError(
            "output.exists", "candidate and report destinations must not exist"
        )

    seen_paths: set[str] = set()
    pinned = tuple(
        _load_pinned_input(root, pin, requirement, seen_paths)
        for pin, requirement in zip(inputs, requirements, strict=True)
    )
    artifact, usage = _candidate_artifact(definition, pinned, output_clean, candidate)
    artifact_bytes = _json_bytes(artifact)
    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    report = _report(
        definition, pinned, output_clean, report_clean, artifact_sha256, usage
    )
    report_bytes = _json_bytes(report)

    for item in pinned:
        current = _read_pinned_bytes(
            root, item.path, f"input {item.requirement}"
        )
        if hashlib.sha256(current).hexdigest() != item.sha256:
            raise OuterWorkflowError(
                "input.changed", f"input {item.path} changed during workflow execution"
            )

    _ensure_output_parent(root, output, "output")
    _ensure_output_parent(root, report_path_value, "report")
    if output.exists() or report_path_value.exists():
        raise OuterWorkflowError(
            "output.exists", "candidate and report destinations must not exist"
        )
    output_temp = _write_temp(output.parent, artifact_bytes)
    report_temp = _write_temp(report_path_value.parent, report_bytes)
    output_published = False
    try:
        _publish_exclusive(output_temp, output, root)
        output_published = True
        _publish_exclusive(report_temp, report_path_value, root)
    except BaseException:
        output_temp.unlink(missing_ok=True)
        report_temp.unlink(missing_ok=True)
        if output_published:
            try:
                if output.read_bytes() == artifact_bytes:
                    output.unlink()
            except OSError:
                pass
        raise
    return WorkflowResult(artifact=artifact, report=report)
