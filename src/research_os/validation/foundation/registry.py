from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from threading import RLock

from .issues import Issue
from .semver import SemVer

TYPE_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
TypeValidator = Callable[[object], Iterable[Issue]]


@dataclass(frozen=True, slots=True)
class TypeDescriptor:
    name: str
    version: SemVer
    validator: TypeValidator

    def identity(self) -> tuple[str, str]:
        return self.name, str(self.version)


class TypeRegistry:
    """Thread-safe registry of exact Artifact type/version validators."""

    def __init__(self, descriptors: Iterable[TypeDescriptor] = ()) -> None:
        self._entries: dict[tuple[str, str], TypeDescriptor] = {}
        self._lock = RLock()
        for descriptor in descriptors:
            self.register_descriptor(descriptor)

    def register(
        self, name: str, version: str, validator: TypeValidator
    ) -> TypeDescriptor:
        if not isinstance(name, str) or TYPE_NAME_RE.fullmatch(name) is None:
            raise ValueError("type name must be lowercase kebab-case")
        if not callable(validator):
            raise TypeError("type validator must be callable")
        descriptor = TypeDescriptor(name, SemVer.parse(version), validator)
        self.register_descriptor(descriptor)
        return descriptor

    def register_descriptor(self, descriptor: TypeDescriptor) -> None:
        if not isinstance(descriptor, TypeDescriptor):
            raise TypeError("descriptor must be a TypeDescriptor")
        if TYPE_NAME_RE.fullmatch(descriptor.name) is None:
            raise ValueError("type name must be lowercase kebab-case")
        if not isinstance(descriptor.version, SemVer):
            raise TypeError("descriptor version must be a SemVer")
        if not callable(descriptor.validator):
            raise TypeError("type validator must be callable")
        identity = descriptor.identity()
        with self._lock:
            if identity in self._entries:
                raise ValueError(f"type already registered: {identity[0]}@{identity[1]}")
            self._entries[identity] = descriptor

    def resolve(self, name: object, version: object) -> TypeDescriptor | None:
        if not isinstance(name, str) or not isinstance(version, str):
            return None
        with self._lock:
            return self._entries.get((name, version))

    def validate(self, name: object, version: object, spec: object) -> list[Issue]:
        descriptor = self.resolve(name, version)
        if descriptor is None:
            identity = f"{name}@{version}"
            return [Issue("type.unsupported", f"unregistered Artifact type/version: {identity}", "/type")]
        try:
            issues = list(descriptor.validator(spec))
        except Exception as exc:
            return [
                Issue(
                    "type.validator_error",
                    f"type validator raised {type(exc).__name__}",
                    "/spec",
                )
            ]
        if any(not isinstance(issue, Issue) for issue in issues):
            return [Issue("type.validator_contract", "type validator must return only Issue values", "/spec")]
        return issues

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            types = [
                {"name": descriptor.name, "version": str(descriptor.version)}
                for descriptor in sorted(
                    self._entries.values(),
                    key=lambda item: (item.name, item.version, str(item.version)),
                )
            ]
        return {
            "contract": {"name": "research-os/type-registry", "version": "1.0.0"},
            "types": types,
        }

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)
