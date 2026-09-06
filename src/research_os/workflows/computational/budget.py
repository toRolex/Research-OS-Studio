from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from math import isfinite
from time import monotonic_ns
from typing import Mapping

BUDGET_DIMENSIONS = (
    "seconds",
    "cost_usd",
    "tokens",
    "gpu_hours",
    "attempts",
    "rounds",
)


class BudgetExceeded(RuntimeError):
    def __init__(self, dimension: str, limit: int | float, projected: int | float):
        self.dimension = dimension
        self.limit = limit
        self.projected = projected
        super().__init__(
            f"budget exceeded for {dimension}: projected {projected!r} > limit {limit!r}"
        )


@dataclass(frozen=True)
class BudgetLimits:
    seconds: float
    cost_usd: float
    tokens: int
    gpu_hours: float
    attempts: int
    rounds: int

    def __post_init__(self) -> None:
        values = asdict(self)
        for name in ("seconds", "cost_usd", "gpu_hours"):
            value = values[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric")
            if not isfinite(float(value)) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        for name in ("tokens", "attempts", "rounds"):
            value = values[name]
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be non-negative")

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "BudgetLimits":
        if set(value) != set(BUDGET_DIMENSIONS):
            missing = sorted(set(BUDGET_DIMENSIONS) - set(value))
            extra = sorted(set(value) - set(BUDGET_DIMENSIONS))
            raise ValueError(
                f"budget must define exactly six counters; missing={missing}, extra={extra}"
            )
        return cls(
            seconds=_number(value["seconds"], "seconds"),
            cost_usd=_number(value["cost_usd"], "cost_usd"),
            tokens=_integer(value["tokens"], "tokens"),
            gpu_hours=_number(value["gpu_hours"], "gpu_hours"),
            attempts=_integer(value["attempts"], "attempts"),
            rounds=_integer(value["rounds"], "rounds"),
        )

    def as_dict(self) -> dict[str, int | float]:
        return asdict(self)


@dataclass(frozen=True)
class BudgetUsage:
    seconds: float = 0.0
    cost_usd: float = 0.0
    tokens: int = 0
    gpu_hours: float = 0.0
    attempts: int = 0
    rounds: int = 0

    def __post_init__(self) -> None:
        BudgetLimits(
            seconds=self.seconds,
            cost_usd=self.cost_usd,
            tokens=self.tokens,
            gpu_hours=self.gpu_hours,
            attempts=self.attempts,
            rounds=self.rounds,
        )

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "BudgetUsage":
        if set(value) != set(BUDGET_DIMENSIONS):
            raise ValueError("usage must define exactly six counters")
        return cls(
            seconds=_number(value["seconds"], "seconds"),
            cost_usd=_number(value["cost_usd"], "cost_usd"),
            tokens=_integer(value["tokens"], "tokens"),
            gpu_hours=_number(value["gpu_hours"], "gpu_hours"),
            attempts=_integer(value["attempts"], "attempts"),
            rounds=_integer(value["rounds"], "rounds"),
        )

    def plus(self, other: "BudgetUsage") -> "BudgetUsage":
        return BudgetUsage(
            seconds=self.seconds + other.seconds,
            cost_usd=self.cost_usd + other.cost_usd,
            tokens=self.tokens + other.tokens,
            gpu_hours=self.gpu_hours + other.gpu_hours,
            attempts=self.attempts + other.attempts,
            rounds=self.rounds + other.rounds,
        )

    def as_dict(self) -> dict[str, int | float]:
        value = asdict(self)
        value["seconds"] = round(self.seconds, 9)
        value["cost_usd"] = round(self.cost_usd, 9)
        value["gpu_hours"] = round(self.gpu_hours, 9)
        return value


class BudgetCounter:
    def __init__(self, limits: BudgetLimits, usage: BudgetUsage | None = None):
        self.limits = limits
        self._usage = usage or BudgetUsage()
        self._started_ns = monotonic_ns()
        self._assert_within(self._usage)

    @property
    def usage(self) -> BudgetUsage:
        return self._usage

    def elapsed_seconds(self) -> float:
        return max(0.0, (monotonic_ns() - self._started_ns) / 1_000_000_000)

    def projected(self, delta: BudgetUsage) -> BudgetUsage:
        return self._usage.plus(delta)

    def require(self, delta: BudgetUsage = BudgetUsage()) -> BudgetUsage:
        projected = self.projected(delta)
        self._assert_within(projected, include_elapsed=True)
        return projected

    def consume(self, delta: BudgetUsage) -> BudgetUsage:
        projected = self.require(delta)
        self._usage = projected
        return self._usage

    def observe(self, delta: BudgetUsage) -> BudgetUsage:
        """Record actual usage even when an executor exceeded its allowance."""
        self._usage = self.projected(delta)
        return self._usage

    def sync_elapsed(self) -> BudgetUsage:
        self._assert_within(self._usage, include_elapsed=True)
        return self._usage

    def first_exhausted_dimension(self) -> str | None:
        values = self._usage.as_dict()
        values["seconds"] = max(float(values["seconds"]), self.elapsed_seconds())
        limits = self.limits.as_dict()
        for name in BUDGET_DIMENSIONS:
            if values[name] >= limits[name]:
                return name
        return None

    def remaining(self) -> BudgetUsage:
        values = self._usage.as_dict()
        values["seconds"] = max(float(values["seconds"]), self.elapsed_seconds())
        limits = self.limits.as_dict()
        return BudgetUsage(
            seconds=max(0.0, float(limits["seconds"]) - float(values["seconds"])),
            cost_usd=max(0.0, float(limits["cost_usd"]) - float(values["cost_usd"])),
            tokens=max(0, int(limits["tokens"]) - int(values["tokens"])),
            gpu_hours=max(0.0, float(limits["gpu_hours"]) - float(values["gpu_hours"])),
            attempts=max(0, int(limits["attempts"]) - int(values["attempts"])),
            rounds=max(0, int(limits["rounds"]) - int(values["rounds"])),
        )

    def _assert_within(
        self, projected: BudgetUsage, *, include_elapsed: bool = False
    ) -> None:
        values = projected.as_dict()
        if include_elapsed:
            values["seconds"] = max(float(values["seconds"]), self.elapsed_seconds())
        limits = self.limits.as_dict()
        for name in BUDGET_DIMENSIONS:
            if values[name] > limits[name]:
                raise BudgetExceeded(name, limits[name], values[name])


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise TypeError(f"{name} must be numeric")
    try:
        number = float(Decimal(str(value)))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(number) or number < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return number


def _integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value
