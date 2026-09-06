from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .model import (
    AdapterDefinition,
    ProjectionBlocked,
    ProjectionFile,
    ProjectionManifest,
    ProjectionPlan,
    SkillDescriptor,
    SkillKind,
    canonical_json,
    digest_bytes,
)


def load_adapter_definition(path: Path) -> tuple[AdapterDefinition, str]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"adapter definition must be a regular file: {path}")
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"adapter definition is not valid UTF-8 JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("adapter definition must be an object")
    return AdapterDefinition.from_dict(value), digest_bytes(raw)


def _frontmatter_fields(content: bytes) -> tuple[dict[str, str], str]:
    text = content.decode("utf-8")
    if not text.startswith("---\n"):
        raise ValueError("skill is missing YAML frontmatter")
    try:
        header, body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError("skill frontmatter is not terminated") from exc
    fields: dict[str, str] = {}
    for line in header.splitlines():
        if not line or line.startswith((" ", "\t")) or ":" not in line:
            raise ValueError("skill frontmatter must contain flat key/value fields")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if not key or key in fields:
            raise ValueError("skill frontmatter contains an invalid or duplicate key")
        fields[key] = value
    return fields, body


def _render_frontmatter(fields: dict[str, str], body: str) -> bytes:
    lines = ["---", *(f"{key}: {value}" for key, value in fields.items()), "---", body]
    return "\n".join(lines).encode("utf-8")


def _validate_skill(skill: SkillDescriptor) -> None:
    fields, _ = _frontmatter_fields(skill.content)
    if fields.get("name") != skill.name:
        raise ValueError(f"skill frontmatter name does not match descriptor: {skill.name}")


def _claude_files(skills: tuple[SkillDescriptor, ...]) -> tuple[ProjectionFile, ...]:
    files: list[ProjectionFile] = []
    for skill in skills:
        fields, body = _frontmatter_fields(skill.content)
        fields["user-invocable"] = "true" if skill.kind is SkillKind.WORKFLOW else "false"
        if skill.kind is SkillKind.WORKFLOW:
            fields["disable-model-invocation"] = "true"
        files.append(
            ProjectionFile(
                path=f".claude/skills/{skill.name}/SKILL.md",
                content=_render_frontmatter(fields, body),
            )
        )
    return tuple(files)


def _codex_policy(skill: SkillDescriptor) -> bytes:
    return b"policy:\n  allow_implicit_invocation: false\n"


def _codex_files(skills: tuple[SkillDescriptor, ...]) -> tuple[ProjectionFile, ...]:
    files: list[ProjectionFile] = []
    for skill in skills:
        files.extend(
            (
                ProjectionFile(
                    path=f".agents/skills/{skill.name}/SKILL.md",
                    content=skill.content,
                ),
                ProjectionFile(
                    path=f".agents/skills/{skill.name}/agents/openai.yaml",
                    content=_codex_policy(skill),
                ),
            )
        )
    return tuple(files)


def _canonical_descriptor(skill: SkillDescriptor) -> dict[str, str]:
    return {
        "name": skill.name,
        "version": skill.version,
        "kind": skill.kind.value,
        "sha256": skill.sha256,
    }


def build_projection(
    adapter: AdapterDefinition,
    adapter_sha256: str,
    skills: Iterable[SkillDescriptor],
    *,
    excluded_skills: Iterable[SkillDescriptor] = (),
    projection_scope: str = "complete",
    blocked_capabilities: tuple[str, ...] = (),
) -> ProjectionPlan | ProjectionBlocked:
    ordered = tuple(sorted(skills, key=lambda item: item.name))
    excluded = tuple(sorted(excluded_skills, key=lambda item: item.name))
    if projection_scope not in {"complete", "workflow-only"}:
        raise ValueError("projection_scope must be complete or workflow-only")
    if projection_scope == "complete" and (excluded or blocked_capabilities):
        raise ValueError("complete projection cannot exclude canonical skills")
    if projection_scope == "workflow-only":
        if any(skill.kind is not SkillKind.DISCIPLINE for skill in excluded):
            raise ValueError("workflow-only projection may exclude disciplines only")
        if any(skill.kind is not SkillKind.WORKFLOW for skill in ordered):
            raise ValueError("workflow-only projection may include workflows only")
        if not excluded or blocked_capabilities != ("discipline_private_visibility",):
            raise ValueError("workflow-only projection must record blocked discipline visibility")
    all_names = [skill.name for skill in (*ordered, *excluded)]
    if len(set(all_names)) != len(all_names):
        raise ValueError("canonical skill names must be unique across included and excluded skills")
    baseline: tuple[str, ...]
    kinds = {skill.kind for skill in ordered}
    if adapter.adapter == "claude-code":
        required = []
        if SkillKind.WORKFLOW in kinds:
            required.append("workflow_model_invocation_control")
        if SkillKind.DISCIPLINE in kinds:
            required.append("discipline_private_visibility")
        baseline = tuple(required)
    elif adapter.adapter == "codex":
        required = []
        if SkillKind.WORKFLOW in kinds:
            required.append("workflow_implicit_invocation_control")
        if SkillKind.DISCIPLINE in kinds:
            required.append("discipline_private_visibility")
        baseline = tuple(required)
    else:
        raise ValueError(f"unsupported adapter: {adapter.adapter}")
    missing = adapter.capability_profile.missing(
        tuple(sorted(set(adapter.required_capabilities) | set(baseline)))
    )
    if missing:
        return ProjectionBlocked(adapter=adapter.adapter, missing_capabilities=missing)
    if len({skill.name for skill in ordered}) != len(ordered):
        raise ValueError("canonical skill names must be unique")
    for skill in (*ordered, *excluded):
        _validate_skill(skill)
    if adapter.adapter == "claude-code":
        files = _claude_files(ordered)
    elif adapter.adapter == "codex":
        files = _codex_files(ordered)
    else:
        raise ValueError(f"unsupported adapter: {adapter.adapter}")
    file_digests = {item.path: item.sha256 for item in files}
    canonical = tuple(_canonical_descriptor(skill) for skill in ordered)
    excluded_canonical = tuple(_canonical_descriptor(skill) for skill in excluded)
    workflows = tuple(skill.name for skill in ordered if skill.kind is SkillKind.WORKFLOW)
    disciplines = tuple(skill.name for skill in ordered if skill.kind is SkillKind.DISCIPLINE)
    unsigned = {
        "contract": {"name": "research-os/projection-manifest", "version": "1.0.0"},
        "adapter": {
            "name": adapter.adapter,
            "version": adapter.version,
            "sha256": adapter_sha256,
        },
        "projection_version": adapter.projection_version,
        "capability_profile": adapter.capability_profile.to_dict(),
        "workflow_invocation": adapter.workflow_invocation,
        "automatic_next_workflow": adapter.automatic_next_workflow,
        "projection_scope": projection_scope,
        "canonical_skills": list(canonical),
        "excluded_canonical_skills": list(excluded_canonical),
        "blocked_capabilities": list(blocked_capabilities),
        "workflow_entries": list(workflows),
        "discipline_entries": list(disciplines),
        "files": file_digests,
    }
    projection_digest = digest_bytes(canonical_json(unsigned))
    manifest = ProjectionManifest(
        adapter=adapter.adapter,
        adapter_version=adapter.version,
        projection_version=adapter.projection_version,
        adapter_sha256=adapter_sha256,
        capability_profile=adapter.capability_profile,
        workflow_invocation=adapter.workflow_invocation,
        automatic_next_workflow=adapter.automatic_next_workflow,
        projection_scope=projection_scope,
        canonical_skills=canonical,
        excluded_canonical_skills=excluded_canonical,
        blocked_capabilities=blocked_capabilities,
        workflow_entries=workflows,
        discipline_entries=disciplines,
        files=file_digests,
        projection_digest=projection_digest,
    )
    manifest_file = ProjectionFile(
        path=f".research-os/projections/{adapter.adapter}/manifest.json",
        content=canonical_json(manifest.to_dict()),
    )
    return ProjectionPlan(manifest=manifest, files=(*files, manifest_file))
