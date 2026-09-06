from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .common import Issue, issue, reject_unknown, require_nonempty_string

PROJECT_ROLES = frozenset({"user", "researcher", "reviewer", "maintainer", "agent"})


def validate_principals(value: object, path: str = "/spec/principals") -> list[Issue]:
    if not isinstance(value, list):
        return [issue("principal.array", path, "must be a non-empty array")]
    issues: list[Issue] = []
    if not value:
        issues.append(issue("principal.empty", path, "Project must bind at least one principal"))
    identities: set[str] = set()
    has_user = False
    for index, principal in enumerate(value):
        principal_path = f"{path}/{index}"
        if not isinstance(principal, dict):
            issues.append(issue("principal.object", principal_path, "must be an object"))
            continue
        issues.extend(reject_unknown(principal, {"identity", "roles", "display_name"}, principal_path))
        identity = principal.get("identity")
        issues.extend(require_nonempty_string(identity, f"{principal_path}/identity", "principal.identity"))
        if isinstance(identity, str):
            if identity in identities:
                issues.append(issue("principal.duplicate", f"{principal_path}/identity", "principal identity must be unique"))
            identities.add(identity)
        roles = principal.get("roles")
        if not isinstance(roles, list) or not roles:
            issues.append(issue("principal.roles", f"{principal_path}/roles", "must be a non-empty role array"))
        else:
            seen_roles: set[str] = set()
            for role_index, role in enumerate(roles):
                role_path = f"{principal_path}/roles/{role_index}"
                if role not in PROJECT_ROLES:
                    issues.append(issue("principal.role", role_path, "unsupported Project role"))
                elif role in seen_roles:
                    issues.append(issue("principal.role_duplicate", role_path, "duplicate Project role"))
                else:
                    seen_roles.add(role)
            has_user = has_user or "user" in seen_roles
        if "display_name" in principal:
            issues.extend(require_nonempty_string(principal["display_name"], f"{principal_path}/display_name", "principal.display_name"))
    if not has_user:
        issues.append(issue("principal.user_required", path, "Project must bind at least one user principal"))
    return issues


def principal_roles(project: Mapping[str, Any], identity: object) -> frozenset[str]:
    if not isinstance(identity, str):
        return frozenset()
    spec = project.get("spec", {})
    if not isinstance(spec, Mapping):
        return frozenset()
    principals = spec.get("principals", [])
    if not isinstance(principals, Sequence) or isinstance(principals, (str, bytes)):
        return frozenset()
    for principal in principals:
        if isinstance(principal, Mapping) and principal.get("identity") == identity:
            roles = principal.get("roles", [])
            if isinstance(roles, Sequence) and not isinstance(roles, (str, bytes)):
                return frozenset(role for role in roles if isinstance(role, str))
    return frozenset()
