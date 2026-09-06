from __future__ import annotations

from .common import Issue, reject_unknown, require_nonempty_string, validate_artifact_envelope, validate_fixed_ref

WORKSTREAM_STATES = frozenset({"active", "paused"})


def validate_workstream(value: object) -> list[Issue]:
    issues = validate_artifact_envelope(value, "workstream")
    if not isinstance(value, dict) or not isinstance(value.get("spec"), dict):
        return issues
    spec = value["spec"]
    issues.extend(reject_unknown(spec, {"project", "name", "intent", "state"}, "/spec"))
    issues.extend(validate_fixed_ref(spec.get("project"), "/spec/project"))
    issues.extend(require_nonempty_string(spec.get("name"), "/spec/name", "workstream.name"))
    issues.extend(require_nonempty_string(spec.get("intent"), "/spec/intent", "workstream.intent"))
    if spec.get("state") not in WORKSTREAM_STATES:
        issues.append(Issue("workstream.state", "/spec/state", "must be active or paused"))
    return issues
