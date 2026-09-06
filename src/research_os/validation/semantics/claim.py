from __future__ import annotations

from .common import Issue, reject_unknown, require_nonempty_string, validate_artifact_envelope, validate_fixed_ref
from .scope import validate_scope


def validate_claim(value: object) -> list[Issue]:
    issues = validate_artifact_envelope(value, "claim")
    if not isinstance(value, dict) or not isinstance(value.get("spec"), dict):
        return issues
    spec = value["spec"]
    issues.extend(reject_unknown(spec, {"project", "workstream", "statement", "scope", "conditions", "limitations"}, "/spec"))
    issues.extend(validate_fixed_ref(spec.get("project"), "/spec/project"))
    issues.extend(validate_fixed_ref(spec.get("workstream"), "/spec/workstream"))
    issues.extend(require_nonempty_string(spec.get("statement"), "/spec/statement", "claim.statement"))
    issues.extend(validate_scope(spec.get("scope"), "/spec/scope"))
    for field in ("conditions", "limitations"):
        issues.extend(_optional_strings(spec, field))
    return issues


def _optional_strings(spec: dict[str, object], field: str) -> list[Issue]:
    if field not in spec:
        return []
    from .common import validate_string_array

    return validate_string_array(spec[field], f"/spec/{field}", unique=True)
