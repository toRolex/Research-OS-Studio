from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering

SEMVER_PATTERN = (
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
SEMVER_RE = re.compile(SEMVER_PATTERN)


@total_ordering
@dataclass(frozen=True, slots=True)
class SemVer:
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("major", "minor", "patch"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"SemVer {name} must be a non-negative integer")
        if not isinstance(self.prerelease, tuple) or not isinstance(self.build, tuple):
            raise TypeError("SemVer identifiers must be tuples")
        for identifier in self.prerelease:
            if not _valid_identifier(identifier) or (
                identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0")
            ):
                raise ValueError(f"invalid SemVer prerelease identifier: {identifier!r}")
        for identifier in self.build:
            if not _valid_identifier(identifier):
                raise ValueError(f"invalid SemVer build identifier: {identifier!r}")

    @classmethod
    def parse(cls, value: object) -> "SemVer":
        if not isinstance(value, str):
            raise TypeError("SemVer must be a string")
        match = SEMVER_RE.fullmatch(value)
        if match is None:
            raise ValueError(f"not an exact SemVer: {value!r}")
        core_and_pre, _, build = value.partition("+")
        core, separator, prerelease = core_and_pre.partition("-")
        major, minor, patch = (int(part) for part in core.split("."))
        return cls(
            major,
            minor,
            patch,
            tuple(prerelease.split(".")) if separator else (),
            tuple(build.split(".")) if build else (),
        )

    def __str__(self) -> str:
        value = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            value += "-" + ".".join(self.prerelease)
        if self.build:
            value += "+" + ".".join(self.build)
        return value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return self.precedence_key() == other.precedence_key()

    def __hash__(self) -> int:
        return hash(self.precedence_key())

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        core_self = (self.major, self.minor, self.patch)
        core_other = (other.major, other.minor, other.patch)
        if core_self != core_other:
            return core_self < core_other
        return _prerelease_less(self.prerelease, other.prerelease)

    def precedence_key(self) -> tuple[int, int, int, tuple[str, ...]]:
        """Build metadata is intentionally excluded by SemVer precedence."""
        return self.major, self.minor, self.patch, self.prerelease


def _valid_identifier(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and re.fullmatch(r"[0-9A-Za-z-]+", value) is not None
    )


def _prerelease_less(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    if not left:
        return False
    if not right:
        return True
    for left_part, right_part in zip(left, right, strict=False):
        if left_part == right_part:
            continue
        left_numeric = left_part.isdigit()
        right_numeric = right_part.isdigit()
        if left_numeric and right_numeric:
            return int(left_part) < int(right_part)
        if left_numeric != right_numeric:
            return left_numeric
        return left_part < right_part
    return len(left) < len(right)


def is_exact_semver(value: object) -> bool:
    try:
        SemVer.parse(value)
    except (TypeError, ValueError):
        return False
    return True
