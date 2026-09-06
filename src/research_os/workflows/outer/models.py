from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

ARTIFACT_CONTRACT = MappingProxyType(
    {"name": "research-os/artifact", "version": "1.1.0"}
)
REPORT_CONTRACT = MappingProxyType(
    {"name": "research-os/workflow-report", "version": "1.0.0"}
)
TYPE_VERSION = "1.0.0"


class OuterWorkflowError(ValueError):
    """A deterministic outer-workflow contract failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class InputRequirement:
    name: str
    type_names: tuple[str, ...]
    minimum: int = 1
    maximum: int = 1


@dataclass(frozen=True)
class WorkflowDefinition:
    name: str
    inputs: tuple[InputRequirement, ...]
    output_type: str
    budget: Mapping[str, int]
    invariants: tuple[str, ...]
    options: tuple[str, ...]


@dataclass(frozen=True)
class InputPin:
    path: str
    sha256: str


@dataclass(frozen=True)
class PinnedInput:
    requirement: str
    path: str
    sha256: str
    artifact: Mapping[str, Any]


@dataclass(frozen=True)
class CandidateDraft:
    spec: Mapping[str, Any]
    usage: Mapping[str, int]


@dataclass(frozen=True)
class WorkflowResult:
    artifact: Mapping[str, Any]
    report: Mapping[str, Any]


def _definition(
    name: str,
    inputs: tuple[InputRequirement, ...],
    output_type: str,
    budget: Mapping[str, int],
    invariants: tuple[str, ...],
    options: tuple[str, ...],
) -> WorkflowDefinition:
    return WorkflowDefinition(
        name=name,
        inputs=inputs,
        output_type=output_type,
        budget=MappingProxyType(dict(budget)),
        invariants=invariants,
        options=options,
    )


REFLECTABLE_TYPES = (
    "research-charter",
    "literature-review",
    "research-gap",
    "research-idea",
    "novelty-review",
    "reflection-input",
)

WORKFLOWS: Mapping[str, WorkflowDefinition] = MappingProxyType(
    {
        definition.name: definition
        for definition in (
            _definition(
                "research-charter",
                (InputRequirement("question", ("research-question",)),),
                "research-charter",
                {"source_count": 1, "candidate_count": 1},
                (
                    "preserve the supplied research question",
                    "preserve explicit non-empty research boundaries",
                    "do not infer human acceptance",
                ),
                (
                    "review candidate charter",
                    "invoke a user-selected workflow with pinned inputs",
                ),
            ),
            _definition(
                "research-literature",
                (InputRequirement("charter", ("research-charter",)),),
                "literature-review",
                {
                    "source_count": 1,
                    "candidate_count": 1,
                    "query_count": 0,
                    "citation_count": 50,
                },
                (
                    "preserve the charter question and boundaries",
                    "use only citations already pinned in the input",
                    "record no unpinned search result",
                ),
                (
                    "review candidate literature report",
                    "invoke research-gap with this pinned candidate",
                ),
            ),
            _definition(
                "research-gap",
                (InputRequirement("literature", ("literature-review",)),),
                "research-gap",
                {"source_count": 1, "candidate_count": 1, "gap_count": 3},
                (
                    "derive gaps only from the pinned literature artifact",
                    "label unsupported gaps instead of inventing evidence",
                    "do not select a gap for the user",
                ),
                (
                    "review gap candidates",
                    "invoke research-idea with a pinned accepted gap",
                ),
            ),
            _definition(
                "research-idea",
                (InputRequirement("gap", ("research-gap",)),),
                "research-idea",
                {"source_count": 1, "candidate_count": 1, "idea_count": 3},
                (
                    "preserve the selected gap wording",
                    "keep assumptions and tests explicit",
                    "do not claim novelty",
                ),
                (
                    "review idea candidates",
                    "invoke research-novelty with pinned idea and literature inputs",
                ),
            ),
            _definition(
                "research-novelty",
                (
                    InputRequirement("idea", ("research-idea",)),
                    InputRequirement("literature", ("literature-review",)),
                ),
                "novelty-review",
                {"source_count": 2, "candidate_count": 1, "comparison_count": 8},
                (
                    "compare only against pinned prior-work records",
                    "separate observed differences from novelty judgment",
                    "do not accept or reject the idea for the user",
                ),
                (
                    "review novelty candidate",
                    "revise an input in a later explicit invocation",
                ),
            ),
            _definition(
                "research-reflect",
                (
                    InputRequirement(
                        "subjects", REFLECTABLE_TYPES, minimum=1, maximum=12
                    ),
                ),
                "research-reflection",
                {
                    "source_count": 12,
                    "candidate_count": 1,
                    "observation_count": 12,
                    "option_count": 5,
                },
                (
                    "preserve failures and uncertainty",
                    "do not alter research semantics or budgets",
                    "do not choose or invoke a next workflow",
                ),
                ("review reflection candidate", "choose any later workflow explicitly"),
            ),
        )
    }
)
