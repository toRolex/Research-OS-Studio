from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

from .issues import Issue
from .semver import is_exact_semver
from .targets import is_canonical_https_uri, is_safe_git_path

FormatChecker = Callable[[object], bool]
_SUPPORTED_KEYWORDS = frozenset({
    "$schema", "$id", "$defs", "$ref", "title", "description", "type", "required",
    "additionalProperties", "properties", "const", "enum", "pattern", "minLength",
    "minItems", "oneOf", "allOf", "if", "then", "dependentRequired", "items", "format",
})
_DEFAULT_FORMATS: dict[str, FormatChecker] = {
    "research-os-git-path": is_safe_git_path,
    "research-os-canonical-https-uri": is_canonical_https_uri,
    "research-os-semver": is_exact_semver,
}


class LocalSchemaValidator:
    """Offline, fail-closed evaluator for the Foundation schema vocabulary.

    References are restricted to JSON files below ``schema_root``. HTTP(S) retrieval,
    unknown validation keywords, unknown formats, and missing references are errors.
    """

    def __init__(self, schema_root: Path, *, formats: dict[str, FormatChecker] | None = None) -> None:
        self.schema_root = schema_root.resolve()
        if not self.schema_root.is_dir():
            raise NotADirectoryError(self.schema_root)
        self.formats = dict(_DEFAULT_FORMATS)
        if formats:
            self.formats.update(formats)
        self._cache: dict[Path, object] = {}

    def validate_file(self, schema_path: Path, instance: object) -> list[Issue]:
        path = self._inside_root(schema_path.resolve())
        schema = self._load(path)
        return self._evaluate(schema, instance, path, "", frozenset())

    def _load(self, path: Path) -> object:
        if path not in self._cache:
            with path.open(encoding="utf-8") as stream:
                self._cache[path] = json.load(stream)
        return self._cache[path]

    def _inside_root(self, path: Path) -> Path:
        try:
            path.relative_to(self.schema_root)
        except ValueError as exc:
            raise ValueError(f"schema reference escapes local root: {path}") from exc
        return path

    def _evaluate(
        self,
        schema: object,
        instance: object,
        schema_path: Path,
        instance_path: str,
        references: frozenset[tuple[Path, str]],
    ) -> list[Issue]:
        if not isinstance(schema, dict):
            return [Issue("schema.object", "schema must be an object", instance_path)]
        unknown = set(schema) - _SUPPORTED_KEYWORDS
        if unknown:
            return [Issue("schema.keyword.unsupported", f"unsupported schema keyword(s): {sorted(unknown)}", instance_path)]
        definition_error = _schema_definition_error(schema)
        if definition_error is not None:
            return [Issue("schema.definition.blocked", definition_error, instance_path)]
        if "$ref" in schema:
            reference_key = (schema_path, str(schema["$ref"]))
            if reference_key in references:
                return [Issue("schema.reference.blocked", "cyclic schema reference", instance_path)]
            try:
                target_schema, target_path = self._resolve_ref(schema["$ref"], schema_path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                return [Issue("schema.reference.blocked", str(exc), instance_path)]
            return self._evaluate(
                target_schema,
                instance,
                target_path,
                instance_path,
                references | {reference_key},
            )
        issues: list[Issue] = []
        expected_type = schema.get("type")
        if expected_type is not None and not _matches_type(expected_type, instance):
            return [Issue("schema.type", f"expected {expected_type}", instance_path)]
        if "const" in schema and instance != schema["const"]:
            issues.append(Issue("schema.const", f"expected constant {schema['const']!r}", instance_path))
        if "enum" in schema and instance not in schema["enum"]:
            issues.append(Issue("schema.enum", "value is not in enum", instance_path))
        if isinstance(instance, str):
            minimum = schema.get("minLength")
            if isinstance(minimum, int) and len(instance) < minimum:
                issues.append(Issue("schema.min_length", f"minimum length is {minimum}", instance_path))
            pattern = schema.get("pattern")
            if isinstance(pattern, str) and re.search(pattern, instance) is None:
                issues.append(Issue("schema.pattern", "string does not match pattern", instance_path))
            format_name = schema.get("format")
            if format_name is not None:
                checker = self.formats.get(format_name)
                if checker is None:
                    issues.append(Issue("schema.format.blocked", f"unknown format: {format_name}", instance_path))
                elif not checker(instance):
                    issues.append(Issue("schema.format", f"invalid {format_name}", instance_path))
        if isinstance(instance, dict):
            required = schema.get("required", [])
            for name in required:
                if name not in instance:
                    issues.append(Issue("schema.required", f"missing required property: {name}", _join(instance_path, str(name))))
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                for name, child_schema in properties.items():
                    if name in instance:
                        issues.extend(self._evaluate(child_schema, instance[name], schema_path, _join(instance_path, name), references))
                if schema.get("additionalProperties") is False:
                    for name in instance:
                        if name not in properties:
                            issues.append(Issue("schema.additional_property", f"unknown property: {name}", _join(instance_path, str(name))))
            dependencies = schema.get("dependentRequired", {})
            for trigger, names in dependencies.items():
                if trigger in instance:
                    for name in names:
                        if name not in instance:
                            issues.append(Issue("schema.dependent_required", f"{trigger} requires {name}", _join(instance_path, name)))
        if isinstance(instance, list):
            minimum_items = schema.get("minItems")
            if isinstance(minimum_items, int) and len(instance) < minimum_items:
                issues.append(Issue("schema.min_items", f"minimum item count is {minimum_items}", instance_path))
            if "items" in schema:
                for index, item in enumerate(instance):
                    issues.extend(self._evaluate(schema["items"], item, schema_path, _join(instance_path, str(index)), references))
        if "allOf" in schema:
            for branch in schema["allOf"]:
                issues.extend(self._evaluate(branch, instance, schema_path, instance_path, references))
        if "if" in schema:
            condition_issues = self._evaluate(schema["if"], instance, schema_path, instance_path, references)
            if not condition_issues and "then" in schema:
                issues.extend(self._evaluate(schema["then"], instance, schema_path, instance_path, references))
        if "oneOf" in schema:
            branches = [self._evaluate(branch, instance, schema_path, instance_path, references) for branch in schema["oneOf"]]
            matches = sum(not branch_issues for branch_issues in branches)
            if matches != 1:
                issues.append(Issue("schema.one_of", f"expected exactly one matching branch, found {matches}", instance_path))
        return issues

    def _resolve_ref(self, reference: object, current_path: Path) -> tuple[object, Path]:
        if not isinstance(reference, str) or not reference:
            raise ValueError("schema reference must be a non-empty string")
        if reference.startswith(("http://", "https://")):
            raise ValueError("remote schema retrieval is prohibited")
        file_part, separator, fragment = reference.partition("#")
        target_path = current_path if not file_part else self._inside_root((current_path.parent / file_part).resolve())
        target = self._load(target_path)
        if separator:
            target = _resolve_pointer(target, fragment)
        return target, target_path


def _schema_definition_error(schema: dict[object, object]) -> str | None:
    if "type" in schema and schema["type"] not in {
        "object", "array", "string", "integer", "number", "boolean", "null"
    }:
        return "type must be a supported JSON type name"
    if "required" in schema and (
        not isinstance(schema["required"], list)
        or any(not isinstance(name, str) for name in schema["required"])
    ):
        return "required must be an array of property names"
    for keyword in ("properties", "$defs"):
        if keyword in schema and not isinstance(schema[keyword], dict):
            return f"{keyword} must be an object"
    if "dependentRequired" in schema:
        dependencies = schema["dependentRequired"]
        if not isinstance(dependencies, dict) or any(
            not isinstance(trigger, str)
            or not isinstance(names, list)
            or any(not isinstance(name, str) for name in names)
            for trigger, names in dependencies.items()
        ):
            return "dependentRequired must map property names to arrays of property names"
    for keyword in ("oneOf", "allOf"):
        if keyword in schema and (
            not isinstance(schema[keyword], list)
            or not schema[keyword]
            or any(not isinstance(branch, dict) for branch in schema[keyword])
        ):
            return f"{keyword} must be a non-empty array of schemas"
    for keyword in ("if", "then", "items"):
        if keyword in schema and not isinstance(schema[keyword], dict):
            return f"{keyword} must be a schema object"
    if "then" in schema and "if" not in schema:
        return "then requires if"
    for keyword in ("minLength", "minItems"):
        if keyword in schema and (
            not isinstance(schema[keyword], int)
            or isinstance(schema[keyword], bool)
            or schema[keyword] < 0
        ):
            return f"{keyword} must be a non-negative integer"
    if "pattern" in schema:
        if not isinstance(schema["pattern"], str):
            return "pattern must be a string"
        try:
            re.compile(schema["pattern"])
        except re.error:
            return "pattern must be a valid regular expression"
    if "format" in schema and not isinstance(schema["format"], str):
        return "format must be a string"
    if "enum" in schema and (
        not isinstance(schema["enum"], list) or not schema["enum"]
    ):
        return "enum must be a non-empty array"
    return None


def _matches_type(expected: object, value: object) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _resolve_pointer(document: object, fragment: str) -> object:
    if not fragment:
        return document
    if not fragment.startswith("/"):
        raise ValueError(f"unsupported schema fragment: #{fragment}")
    current = document
    for encoded in fragment[1:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise ValueError(f"unresolved schema pointer: #{fragment}")
        current = current[token]
    return current


def _join(prefix: str, token: str) -> str:
    escaped = token.replace("~", "~0").replace("/", "~1")
    return f"{prefix}/{escaped}"
