from __future__ import annotations

from collections.abc import Sequence

from .common import Issue, issue

WHOLE_SUBJECT = "whole_subject"


def parse_json_pointer(pointer: object) -> tuple[str, ...]:
    if not isinstance(pointer, str):
        raise ValueError("JSON Pointer must be a string")
    if pointer == "":
        return ()
    if not pointer.startswith("/"):
        raise ValueError("JSON Pointer must be empty or start with /")
    tokens: list[str] = []
    for raw in pointer[1:].split("/"):
        decoded: list[str] = []
        index = 0
        while index < len(raw):
            char = raw[index]
            if char != "~":
                decoded.append(char)
                index += 1
                continue
            if index + 1 >= len(raw) or raw[index + 1] not in {"0", "1"}:
                raise ValueError("JSON Pointer contains invalid ~ escape")
            decoded.append("~" if raw[index + 1] == "0" else "/")
            index += 2
        tokens.append("".join(decoded))
    return tuple(tokens)


def validate_scope(value: object, path: str = "/scope") -> list[Issue]:
    if value == WHOLE_SUBJECT:
        return []
    if not isinstance(value, list):
        return [issue("scope.type", path, "must be whole_subject or a non-empty JSON Pointer array")]
    issues: list[Issue] = []
    if not value:
        issues.append(issue("scope.empty", path, "JSON Pointer scope must not be empty"))
    seen: set[str] = set()
    parsed: list[tuple[int, tuple[str, ...]]] = []
    for index, pointer in enumerate(value):
        pointer_path = f"{path}/{index}"
        if not isinstance(pointer, str):
            issues.append(issue("scope.pointer", pointer_path, "must be a JSON Pointer string"))
            continue
        if pointer in seen:
            issues.append(issue("scope.duplicate", pointer_path, "duplicate JSON Pointer"))
        seen.add(pointer)
        try:
            tokens = parse_json_pointer(pointer)
        except ValueError as exc:
            issues.append(issue("scope.pointer", pointer_path, str(exc)))
        else:
            parsed.append((index, tokens))
    for left_index, left in parsed:
        for right_index, right in parsed:
            if left_index >= right_index:
                continue
            if _tokens_overlap(left, right):
                issues.append(
                    issue(
                        "scope.redundant",
                        f"{path}/{right_index}",
                        f"overlaps pointer at index {left_index}; scope must be minimal",
                    )
                )
    return issues


def scopes_overlap(left: object, right: object) -> bool:
    if validate_scope(left) or validate_scope(right):
        raise ValueError("both scopes must be valid")
    if left == WHOLE_SUBJECT or right == WHOLE_SUBJECT:
        return True
    assert isinstance(left, Sequence) and not isinstance(left, str)
    assert isinstance(right, Sequence) and not isinstance(right, str)
    return any(
        _tokens_overlap(parse_json_pointer(a), parse_json_pointer(b))
        for a in left
        for b in right
    )


def _tokens_overlap(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    common = min(len(left), len(right))
    return left[:common] == right[:common]
