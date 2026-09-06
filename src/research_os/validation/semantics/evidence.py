from __future__ import annotations

from .common import Issue, reject_unknown, require_nonempty_string, validate_artifact_envelope, validate_fixed_ref
from .scope import validate_scope


def validate_evidence(value: object) -> list[Issue]:
    issues = validate_artifact_envelope(value, "evidence", allow_relations=True)
    if not isinstance(value, dict) or not isinstance(value.get("spec"), dict):
        return issues
    spec = value["spec"]
    issues.extend(reject_unknown(spec, {"project", "workstream", "description"}, "/spec"))
    issues.extend(validate_fixed_ref(spec.get("project"), "/spec/project"))
    issues.extend(validate_fixed_ref(spec.get("workstream"), "/spec/workstream"))
    issues.extend(require_nonempty_string(spec.get("description"), "/spec/description", "evidence.description"))
    relations = value.get("relations")
    if not isinstance(relations, list):
        issues.append(Issue("supports.required", "/relations", "Evidence must declare a non-empty supports array"))
        return issues
    if not relations:
        issues.append(Issue("supports.empty", "/relations", "Evidence must support at least one Claim"))
    seen: set[tuple[object, ...]] = set()
    for index, relation in enumerate(relations):
        relation_path = f"/relations/{index}"
        if not isinstance(relation, dict):
            issues.append(Issue("supports.object", relation_path, "must be an object"))
            continue
        issues.extend(reject_unknown(relation, {"relation", "claim", "scope", "method", "conditions"}, relation_path))
        if relation.get("relation") != "supports":
            issues.append(Issue("supports.relation", f"{relation_path}/relation", "only supports is canonical"))
        claim = relation.get("claim")
        claim_issues = validate_fixed_ref(claim, f"{relation_path}/claim")
        issues.extend(claim_issues)
        if not claim_issues and isinstance(claim, dict):
            from .common import fixed_ref_key

            key = fixed_ref_key(claim)
            if key in seen:
                issues.append(Issue("supports.duplicate", f"{relation_path}/claim", "duplicate Claim support relation"))
            seen.add(key)
        issues.extend(validate_scope(relation.get("scope"), f"{relation_path}/scope"))
        issues.extend(require_nonempty_string(relation.get("method"), f"{relation_path}/method", "supports.method"))
        conditions = relation.get("conditions")
        if not isinstance(conditions, list):
            issues.append(Issue("supports.conditions", f"{relation_path}/conditions", "must be an array; use [] when unconditional"))
        else:
            from .common import validate_string_array

            issues.extend(validate_string_array(conditions, f"{relation_path}/conditions", unique=True))
    return issues
