"""Shared contract boundary: foundation envelope plus request-local domain registry."""
from __future__ import annotations

import re
from pathlib import Path

from .validation.foundation import (
    Issue, TypeRegistry, ValidationReportBuilder, is_exact_semver,
    is_safe_git_path, validate_target,
)
from .validation.foundation import validate_artifact as validate_envelope
from .validation import semantics

COMMIT = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def normalize_issues(issues):
    return [item if isinstance(item, Issue) else Issue(
        item.code, item.message, getattr(item, "path", getattr(item, "instance_path", ""))
    ) for item in issues]


def _fields(spec, required, *, candidate=False):
    issues = []
    for name, kind in required.items():
        value = spec.get(name)
        if not isinstance(value, kind) or (kind is str and not value.strip()):
            issues.append(Issue("spec." + name, f"{name} must be {kind.__name__}", "/spec/" + name))
    if candidate and spec.get("status") != "candidate":
        issues.append(Issue("spec.status", "status must be candidate", "/spec/status"))
    return issues


# Explicit structural profiles for workflow-owned Artifact outputs. Domain execution
# remains in the leaf; these checks never imply scientific or human acceptance.
WORKFLOW_SPECS = {
    "research-question": {"question": str, "boundaries": list},
    "research-charter": {"question": str, "boundaries": list, "success_criteria": list, "budget": dict, "invariants": list},
    "literature-review": {"question": str, "boundaries": list, "queries": list, "citations": list, "synthesis": str, "limitations": list},
    "research-gap": {"question": str, "gaps": list, "citation_count": int},
    "research-idea": {"gap": str, "ideas": list},
    "novelty-review": {"idea": str, "comparisons": list, "coverage": str, "novelty_verdict": str, "limitations": list},
    "research-reflection": {"observations": list, "failures": list, "uncertainties": list},
    "reflection-input": {"observations": list},
    "experiment-design": {"hypothesis": str, "dataset": dict, "controls": list, "metrics": list, "run_matrix": list, "success_criteria": list, "failure_criteria": list, "stop_criteria": list, "budget": dict},
    "experiment-preparation": {"status": str, "budget": dict},
    "experiment-run": {"status": str, "budget": dict},
    "experiment-analysis": {"status": str},
}


def build_registry(value=None, *, project=None, project_digest=None, evidence_by_digest=None, records=None, executed=None):
    """Each closure binds this request's complete Artifact, never global context."""
    registry = TypeRegistry()
    def register(name, validator):
        def observed(spec):
            if executed is not None:
                executed.append({'name': name, 'version': '1.0.0'})
            return validator(spec)
        registry.register(name, '1.0.0', observed)
    domain = {
        "project": semantics.validate_project,
        "workstream": semantics.validate_workstream,
        "claim": semantics.validate_claim,
        "evidence": semantics.validate_evidence,
        "assessment": lambda artifact: semantics.validate_assessment(
            artifact, project=project, project_digest=project_digest,
            evidence_by_digest=evidence_by_digest,
        ),
        "migration-rule": semantics.validate_migration_rule,
        "migration-receipt": semantics.validate_migration_receipt,
    }
    for name, validator in domain.items():
        register(name, lambda spec, check=validator: normalize_issues(check(value)))
    for name, required in WORKFLOW_SPECS.items():
        register(name, lambda spec, fields=required: _fields(spec, fields))
    from .workflows.mathematical import validate_statement, validate_math_proof
    register("mathematical-statement", lambda spec: normalize_issues(validate_statement(spec)))
    register("math-proof-run", lambda spec: normalize_issues(validate_math_proof(spec)))
    from .workflows.mathematical.projections import TYPES, validate_projection
    for name in TYPES:
        register(name, lambda spec: validate_projection(
            value, project=project, project_digest=project_digest, records=records))
    from .publication.contracts import validate_typed_publication
    for name in ('manuscript', 'publication', 'external-reference'):
        register(name, lambda spec: validate_typed_publication(value, records=records))
    return registry


def validate_artifact(value, **context):
    return validate_envelope(value, build_registry(value, **context))


def artifact_report(value, subject_name, raw, **context):
    import hashlib
    executed = []
    registry = build_registry(value, executed=executed, **context)
    issues = validate_envelope(value, registry)
    report = ValidationReportBuilder("artifact", "1.1.0", {"kind": "git", "path": subject_name},
                                     subject_sha256=hashlib.sha256(raw).hexdigest())
    report.add_evidence("validator.executed", "foundation envelope validator executed",
                        data={"name": "artifact-envelope", "version": "1.0.0"})
    for identity in executed:
        report.add_evidence("validator.executed", "registered type validator executed", data=identity)
    return report.extend_issues(issues).build()


def validate_assessment(value, **context):
    return normalize_issues(semantics.validate_assessment(value, **context))


def validate_publication_id(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value))


def resolve_project_path(project: Path, value: str) -> Path:
    if not is_safe_git_path(value):
        raise ValueError("path must be a safe project-relative file path")
    root = project.resolve()
    path = root
    for part in value.split("/"):
        path /= part
        if path.is_symlink():
            raise ValueError("path must not traverse a symlink")
    if not path.resolve().is_relative_to(root):
        raise ValueError("path escapes project")
    return path
