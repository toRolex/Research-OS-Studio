from __future__ import annotations

from .common import Issue, reject_unknown, require_nonempty_string, validate_artifact_envelope, validate_string_array
from .identity import validate_principals


def validate_project(value: object) -> list[Issue]:
    issues = validate_artifact_envelope(value, "project")
    if not isinstance(value, dict) or not isinstance(value.get("spec"), dict):
        return issues
    spec = value["spec"]
    issues.extend(reject_unknown(spec, {"name", "question", "boundaries", "principals"}, "/spec"))
    issues.extend(require_nonempty_string(spec.get("name"), "/spec/name", "project.name"))
    issues.extend(require_nonempty_string(spec.get("question"), "/spec/question", "project.question"))
    issues.extend(validate_string_array(spec.get("boundaries"), "/spec/boundaries", nonempty=True, unique=True))
    issues.extend(validate_principals(spec.get("principals")))
    return issues
