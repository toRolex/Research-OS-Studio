from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .common import (
    Issue,
    fixed_ref_key,
    reject_unknown,
    require_nonempty_string,
    validate_artifact_envelope,
    validate_fixed_ref,
    validate_fixed_ref_array,
    validate_timestamp,
)
from .identity import principal_roles
from .scope import scopes_overlap, validate_scope

ASSURANCE_DIMENSIONS = frozenset(
    {
        "structural_conformance",
        "empirical_reproducibility",
        "mathematical_argument_review",
        "formal_verification",
        "independent_review",
        "human_acceptance",
    }
)
VERDICTS = frozenset({"pass", "fail", "inconclusive", "not_applicable"})
VALIDITIES = frozenset({"active", "superseded", "revoked", "expired"})
CONFLICTING_VERDICTS = VERDICTS


def validate_assessment(
    value: object,
    *,
    project: Mapping[str, Any] | None = None,
    project_digest: str | None = None,
    evidence_by_digest: Mapping[str, Mapping[str, Any]] | None = None,
    structural_only: bool = False,
) -> list[Issue]:
    issues = validate_artifact_envelope(value, "assessment")
    if not isinstance(value, dict) or not isinstance(value.get("spec"), dict):
        return issues
    spec = value["spec"]
    if not structural_only and project is None:
        issues.append(
            Issue(
                "assessment.project_context_required",
                "/spec/project",
                "Assessment claims require the bound Project Artifact and digest",
            )
        )
    elif project is not None and project_digest is None:
        issues.append(
            Issue(
                "assessment.project_digest_required",
                "/spec/project",
                "Project-backed identity checks require the supplied Project digest",
            )
        )
    issues.extend(
        reject_unknown(
            spec,
            {
                "project",
                "subject",
                "dimension",
                "scope",
                "verdict",
                "method",
                "evidence",
                "assessor",
                "assessed_at",
                "validity",
                "validity_reason",
                "isolation_receipt",
            },
            "/spec",
        )
    )
    issues.extend(validate_fixed_ref(spec.get("project"), "/spec/project"))
    issues.extend(validate_fixed_ref(spec.get("subject"), "/spec/subject"))
    dimension = spec.get("dimension")
    if dimension not in ASSURANCE_DIMENSIONS:
        issues.append(Issue("assessment.dimension", "/spec/dimension", "unsupported Assurance dimension"))
    issues.extend(validate_scope(spec.get("scope"), "/spec/scope"))
    if spec.get("verdict") not in VERDICTS:
        issues.append(Issue("assessment.verdict", "/spec/verdict", "unsupported Assessment verdict"))
    issues.extend(require_nonempty_string(spec.get("method"), "/spec/method", "assessment.method"))
    issues.extend(validate_fixed_ref_array(spec.get("evidence"), "/spec/evidence", nonempty=True))
    if not structural_only:
        if evidence_by_digest is None:
            issues.append(
                Issue(
                    "assessment.evidence_context_required",
                    "/spec/evidence",
                    "Assessment claims require supplied Evidence Artifacts",
                )
            )
        elif isinstance(spec.get("evidence"), list):
            for index, evidence_ref in enumerate(spec["evidence"]):
                if not isinstance(evidence_ref, Mapping):
                    continue
                digest = evidence_ref.get("sha256")
                evidence = evidence_by_digest.get(digest) if isinstance(digest, str) else None
                if evidence is None or not isinstance(evidence.get("target"), Mapping):
                    issues.append(
                        Issue(
                            "assessment.evidence_missing",
                            f"/spec/evidence/{index}",
                            "referenced Evidence Artifact was not supplied",
                        )
                    )
                elif fixed_ref_key(evidence_ref) != fixed_ref_key(
                    {"target": evidence["target"], "sha256": digest}
                ):
                    issues.append(
                        Issue(
                            "assessment.evidence_mismatch",
                            f"/spec/evidence/{index}",
                            "Evidence reference must bind the supplied Artifact target and digest",
                        )
                    )
    issues.extend(require_nonempty_string(spec.get("assessor"), "/spec/assessor", "assessment.assessor"))
    issues.extend(validate_timestamp(spec.get("assessed_at"), "/spec/assessed_at"))
    validity = spec.get("validity")
    if validity not in VALIDITIES:
        issues.append(Issue("assessment.validity", "/spec/validity", "unsupported Assessment validity"))
    if validity == "active" and "validity_reason" in spec:
        issues.append(Issue("assessment.validity_reason", "/spec/validity_reason", "active Assessment must not have validity_reason"))
    if validity in VALIDITIES - {"active"}:
        issues.extend(require_nonempty_string(spec.get("validity_reason"), "/spec/validity_reason", "assessment.validity_reason"))

    assessor = spec.get("assessor")
    if project is not None and project_digest is not None:
        project_target = project.get("target")
        bound_project = spec.get("project")
        if (
            not isinstance(project_target, Mapping)
            or not isinstance(bound_project, Mapping)
            or fixed_ref_key(bound_project)
            != fixed_ref_key({"target": project_target, "sha256": project_digest})
        ):
            issues.append(
                Issue(
                    "assessment.project_mismatch",
                    "/spec/project",
                    "Assessment must bind the supplied Project revision and digest",
                )
            )
        roles = principal_roles(project, assessor)
        if not roles:
            issues.append(Issue("assessment.assessor_unbound", "/spec/assessor", "assessor must be a bound Project principal"))
        if dimension == "human_acceptance" and "user" not in roles:
            issues.append(Issue("assessment.human_role", "/spec/assessor", "human_acceptance requires Project role user"))
        if dimension == "independent_review" and "reviewer" not in roles:
            issues.append(Issue("assessment.reviewer_role", "/spec/assessor", "independent_review requires Project role reviewer"))

    if dimension == "human_acceptance":
        if spec.get("verdict") != "pass":
            issues.append(Issue("assessment.human_verdict", "/spec/verdict", "human_acceptance must record pass"))
        if "isolation_receipt" in spec:
            issues.append(Issue("assessment.isolation_unexpected", "/spec/isolation_receipt", "human_acceptance must not carry an isolation receipt"))
    elif dimension == "independent_review":
        issues.extend(_validate_isolation_receipt(spec.get("isolation_receipt"), spec, project))
    elif "isolation_receipt" in spec:
        issues.append(Issue("assessment.isolation_unexpected", "/spec/isolation_receipt", "isolation receipt is only valid for independent_review"))
    return issues


def _validate_isolation_receipt(
    value: object,
    assessment_spec: Mapping[str, Any],
    project: Mapping[str, Any] | None,
) -> list[Issue]:
    path = "/spec/isolation_receipt"
    if not isinstance(value, dict):
        return [Issue("isolation.required", path, "independent_review requires an isolation receipt")]
    issues = reject_unknown(value, {"reviewer", "authors", "inputs", "fresh_context", "conversation_history_access", "issued_at"}, path)
    reviewer = value.get("reviewer")
    issues.extend(require_nonempty_string(reviewer, f"{path}/reviewer", "isolation.reviewer"))
    if reviewer != assessment_spec.get("assessor"):
        issues.append(Issue("isolation.reviewer_mismatch", f"{path}/reviewer", "must equal Assessment assessor"))
    authors = value.get("authors")
    if not isinstance(authors, list) or not authors:
        issues.append(Issue("isolation.authors", f"{path}/authors", "must be a non-empty principal array"))
    else:
        seen: set[str] = set()
        for index, author in enumerate(authors):
            author_path = f"{path}/authors/{index}"
            if not isinstance(author, str) or not author.strip():
                issues.append(Issue("isolation.author", author_path, "must be a non-empty principal identity"))
            elif author in seen:
                issues.append(Issue("isolation.author_duplicate", author_path, "duplicate author principal"))
            else:
                seen.add(author)
            if author == reviewer:
                issues.append(Issue("isolation.same_principal", author_path, "reviewer must differ from every author"))
            if project is not None and not principal_roles(project, author):
                issues.append(Issue("isolation.author_unbound", author_path, "author must be a bound Project principal"))
    inputs = value.get("inputs")
    issues.extend(validate_fixed_ref_array(inputs, f"{path}/inputs", nonempty=True))
    if isinstance(inputs, list) and isinstance(assessment_spec.get("subject"), Mapping):
        subject_key = fixed_ref_key(assessment_spec["subject"])
        input_keys = {fixed_ref_key(item) for item in inputs if isinstance(item, Mapping)}
        if subject_key not in input_keys:
            issues.append(Issue("isolation.subject_missing", f"{path}/inputs", "fixed inputs must include the Assessment subject"))
    if value.get("fresh_context") is not True:
        issues.append(Issue("isolation.fresh_context", f"{path}/fresh_context", "must be true"))
    if value.get("conversation_history_access") is not False:
        issues.append(Issue("isolation.history", f"{path}/conversation_history_access", "must be false"))
    issues.extend(validate_timestamp(value.get("issued_at"), f"{path}/issued_at"))
    return issues


def find_assurance_conflicts(assessments: Sequence[Mapping[str, Any]]) -> list[Issue]:
    issues: list[Issue] = []
    eligible: list[tuple[int, Mapping[str, Any], Mapping[str, Any]]] = []
    for index, assessment in enumerate(assessments):
        assessment_issues = validate_assessment(assessment, structural_only=True)
        if assessment_issues:
            issues.extend(
                Issue(item.code, f"/{index}{item.path}", item.message)
                for item in assessment_issues
            )
            continue
        spec = assessment["spec"]
        if spec.get("validity") == "active" and spec.get("verdict") in CONFLICTING_VERDICTS:
            eligible.append((index, assessment, spec))
    for left_pos, (left_index, _left, left_spec) in enumerate(eligible):
        for right_index, _right, right_spec in eligible[left_pos + 1 :]:
            if fixed_ref_key(left_spec["subject"]) != fixed_ref_key(right_spec["subject"]):
                continue
            if left_spec["dimension"] != right_spec["dimension"]:
                continue
            if left_spec["verdict"] == right_spec["verdict"]:
                continue
            if scopes_overlap(left_spec["scope"], right_spec["scope"]):
                issues.append(
                    Issue(
                        "assurance.conflict",
                        f"/{right_index}",
                        f"conflicts with Assessment at index {left_index}: same fixed subject and dimension, overlapping scope, different active verdict",
                    )
                )
    return issues


def validate_revision_isolation(subject: Mapping[str, Any], assessments: Sequence[Mapping[str, Any]]) -> list[Issue]:
    subject_issues = validate_fixed_ref(subject, "/subject")
    if subject_issues:
        return subject_issues
    issues: list[Issue] = []
    expected = fixed_ref_key(subject)
    for index, assessment in enumerate(assessments):
        assessment_issues = validate_assessment(assessment, structural_only=True)
        if assessment_issues:
            issues.extend(
                Issue(item.code, f"/{index}{item.path}", item.message)
                for item in assessment_issues
            )
            continue
        spec = assessment["spec"]
        actual = fixed_ref_key(spec["subject"])
        if actual != expected:
            issues.append(Issue("assurance.revision_mismatch", f"/{index}/spec/subject", "Assessment does not bind this exact subject revision and digest"))
    return issues
