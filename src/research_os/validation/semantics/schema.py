from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from .assurance import validate_assessment
from .claim import validate_claim
from .common import Issue, issue, validate_timestamp
from .evidence import validate_evidence
from .migration import validate_migration_receipt, validate_migration_rule
from .project import validate_project
from .workstream import validate_workstream

Validator = Callable[..., list[Issue]]
_SCHEMA_ROOT = Path(__file__).resolve().parents[4] / "core" / "contracts"
_SCHEMA_KEYWORDS = frozenset(
    {
        "$schema",
        "$id",
        "$defs",
        "$ref",
        "type",
        "required",
        "additionalProperties",
        "properties",
        "const",
        "enum",
        "pattern",
        "minLength",
        "minItems",
        "uniqueItems",
        "oneOf",
        "allOf",
        "if",
        "then",
        "else",
        "items",
        "format",
        "title",
        "description",
    }
)


class SemanticsSchemaValidator:
    """Offline executable boundary for semantics JSON Schemas plus invariants."""

    _validators: dict[tuple[str, str], Validator] = {
        ("project", "1.0.0"): validate_project,
        ("workstream", "1.0.0"): validate_workstream,
        ("claim", "1.0.0"): validate_claim,
        ("evidence", "1.0.0"): validate_evidence,
        ("assessment", "1.0.0"): validate_assessment,
        ("migration-rule", "1.0.0"): validate_migration_rule,
        ("migration-receipt", "1.0.0"): validate_migration_receipt,
    }

    def __init__(self, schema_root: Path = _SCHEMA_ROOT) -> None:
        self.schema_root = schema_root.resolve()
        self._cache: dict[Path, object] = {}

    def validate(
        self,
        type_name: str,
        value: object,
        *,
        version: str = "1.0.0",
        **context: object,
    ) -> list[Issue]:
        validator = self._validators.get((type_name, version))
        if validator is None:
            return [
                issue(
                    "semantics.contract.unsupported",
                    "/type",
                    f"unsupported semantics contract: {type_name}@{version}",
                )
            ]
        schema_path = (
            self.schema_root / "semantics" / f"{type_name}-{version}.schema.json"
        )
        try:
            schema_issues = self._evaluate(
                self._load(schema_path), value, schema_path, "", frozenset()
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return [issue("semantics.schema.blocked", "", str(exc))]
        if schema_issues:
            return schema_issues
        if type_name == "assessment":
            if context:
                return validator(value, **context)
            return validator(value, structural_only=True)
        if type_name == "migration-receipt":
            return validator(value, **context)
        if context:
            return [
                issue(
                    "semantics.context.unexpected",
                    "",
                    f"{type_name} does not accept validation context",
                )
            ]
        return validator(value)

    def _load(self, path: Path) -> object:
        path = path.resolve()
        try:
            path.relative_to(self.schema_root)
        except ValueError as exc:
            raise ValueError(f"schema reference escapes contract root: {path}") from exc
        if path not in self._cache:
            self._cache[path] = json.loads(path.read_text(encoding="utf-8"))
        return self._cache[path]

    def _evaluate(
        self,
        schema: object,
        instance: object,
        schema_path: Path,
        instance_path: str,
        references: frozenset[tuple[Path, str]],
    ) -> list[Issue]:
        if isinstance(schema, bool):
            return [] if schema else [issue("schema.false", instance_path, "value is prohibited")]
        if not isinstance(schema, dict):
            return [issue("schema.object", instance_path, "schema must be an object or boolean")]
        self._validate_schema_document(schema, schema_path)
        if "$ref" in schema:
            reference = schema["$ref"]
            key = (schema_path, str(reference))
            if key in references:
                return [issue("schema.reference.blocked", instance_path, "cyclic schema reference")]
            target, target_path = self._resolve_ref(reference, schema_path)
            return self._evaluate(
                target, instance, target_path, instance_path, references | {key}
            )

        issues: list[Issue] = []
        expected_type = schema.get("type")
        if expected_type is not None and not _matches_type(expected_type, instance):
            return [issue("schema.type", instance_path, f"expected {expected_type}")]
        if "const" in schema and instance != schema["const"]:
            issues.append(issue("schema.const", instance_path, "value differs from required constant"))
        if "enum" in schema and instance not in schema["enum"]:
            issues.append(issue("schema.enum", instance_path, "value is not in enum"))
        if isinstance(instance, str):
            minimum = schema.get("minLength")
            if isinstance(minimum, int) and len(instance) < minimum:
                issues.append(issue("schema.min_length", instance_path, f"minimum length is {minimum}"))
            pattern = schema.get("pattern")
            if isinstance(pattern, str) and re.fullmatch(pattern, instance) is None:
                issues.append(issue("schema.pattern", instance_path, "string does not match pattern"))
            format_name = schema.get("format")
            if format_name == "date-time" and validate_timestamp(instance, instance_path):
                issues.append(issue("schema.format", instance_path, "invalid UTC date-time"))
            elif format_name == "uri":
                from .common import _canonical_https_uri

                if not _canonical_https_uri(instance):
                    issues.append(issue("schema.format", instance_path, "invalid canonical HTTPS URI"))
            elif format_name not in {None, "date-time", "uri"}:
                issues.append(issue("schema.format.blocked", instance_path, f"unsupported format: {format_name}"))
        if isinstance(instance, dict):
            for name in schema.get("required", []):
                if name not in instance:
                    issues.append(issue("schema.required", _join(instance_path, name), f"missing property: {name}"))
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                for name, child in properties.items():
                    if name in instance:
                        issues.extend(
                            self._evaluate(
                                child,
                                instance[name],
                                schema_path,
                                _join(instance_path, name),
                                references,
                            )
                        )
                if schema.get("additionalProperties") is False:
                    for name in instance:
                        if name not in properties:
                            issues.append(issue("schema.additional_property", _join(instance_path, str(name)), f"unknown property: {name}"))
        if isinstance(instance, list):
            minimum = schema.get("minItems")
            if isinstance(minimum, int) and len(instance) < minimum:
                issues.append(issue("schema.min_items", instance_path, f"minimum items is {minimum}"))
            if schema.get("uniqueItems") is True:
                encoded = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in instance]
                if len(encoded) != len(set(encoded)):
                    issues.append(issue("schema.unique_items", instance_path, "array items must be unique"))
            if "items" in schema:
                for index, item in enumerate(instance):
                    issues.extend(
                        self._evaluate(
                            schema["items"],
                            item,
                            schema_path,
                            _join(instance_path, str(index)),
                            references,
                        )
                    )
        if "oneOf" in schema:
            branches = [
                self._evaluate(branch, instance, schema_path, instance_path, references)
                for branch in schema["oneOf"]
            ]
            matches = sum(not branch for branch in branches)
            if matches != 1:
                issues.append(issue("schema.one_of", instance_path, f"expected one matching branch, found {matches}"))
        for child in schema.get("allOf", []):
            issues.extend(
                self._evaluate(child, instance, schema_path, instance_path, references)
            )
        if "if" in schema:
            condition = self._evaluate(
                schema["if"], instance, schema_path, instance_path, references
            )
            branch = schema.get("then") if not condition else schema.get("else")
            if branch is not None:
                issues.extend(
                    self._evaluate(branch, instance, schema_path, instance_path, references)
                )
        return issues

    def _validate_schema_document(self, schema: Mapping[str, Any], schema_path: Path) -> None:
        unknown = set(schema) - _SCHEMA_KEYWORDS
        if unknown:
            raise ValueError(
                f"unsupported schema keyword(s) in {schema_path.name}: {sorted(unknown)}"
            )
        properties = schema.get("properties")
        if properties is not None and not isinstance(properties, Mapping):
            raise ValueError(f"properties must be an object in {schema_path.name}")
        definitions = schema.get("$defs")
        if definitions is not None and not isinstance(definitions, Mapping):
            raise ValueError(f"$defs must be an object in {schema_path.name}")

    def _resolve_ref(self, reference: object, current_path: Path) -> tuple[object, Path]:
        if not isinstance(reference, str) or not reference:
            raise ValueError("schema reference must be a non-empty string")
        if reference.startswith(("http://", "https://")):
            raise ValueError("remote schema retrieval is prohibited")
        file_part, separator, fragment = reference.partition("#")
        target_path = current_path if not file_part else current_path.parent / file_part
        target = self._load(target_path)
        if separator:
            target = _resolve_pointer(target, fragment)
        return target, target_path.resolve()


def _matches_type(expected: object, value: object) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def _resolve_pointer(document: object, fragment: str) -> object:
    if not fragment:
        return document
    if not fragment.startswith("/"):
        raise ValueError(f"unsupported schema fragment: #{fragment}")
    current = document
    for encoded in fragment[1:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, Mapping) or token not in current:
            raise ValueError(f"unresolved schema pointer: #{fragment}")
        current = current[token]
    return current


def _join(prefix: str, token: str) -> str:
    escaped = str(token).replace("~", "~0").replace("/", "~1")
    return f"{prefix}/{escaped}"
