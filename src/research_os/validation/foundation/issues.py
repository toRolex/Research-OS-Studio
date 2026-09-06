from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Issue:
    """A deterministic validation observation."""

    code: str
    message: str
    instance_path: str = ""
    data: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.code or not isinstance(self.code, str):
            raise ValueError("issue code must be a non-empty string")
        if not self.message or not isinstance(self.message, str):
            raise ValueError("issue message must be a non-empty string")
        if not isinstance(self.instance_path, str):
            raise TypeError("issue instance_path must be a string")
        if not isinstance(self.data, Mapping):
            raise TypeError("issue data must be a mapping")
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))

    def as_dict(self) -> dict[str, object]:
        value: dict[str, object] = {"code": self.code, "message": self.message}
        if self.instance_path:
            value["instance_path"] = self.instance_path
        if self.data:
            value["data"] = dict(self.data)
        return value
