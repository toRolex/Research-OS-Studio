from __future__ import annotations

import json
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

from .models import CandidateDraft, OuterWorkflowError, PinnedInput, WORKFLOWS

Builder = Callable[[tuple[PinnedInput, ...], Mapping[str, Any] | None], CandidateDraft]


def _object(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise OuterWorkflowError("input.schema", f"{field} must be an object")
    return value


def _text(value: Any, field: str, *, non_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise OuterWorkflowError("input.schema", f"{field} must be a string")
    result = value.strip()
    if non_empty and not result:
        raise OuterWorkflowError("input.schema", f"{field} must not be empty")
    return result


def _text_list(value: Any, field: str, *, non_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise OuterWorkflowError("input.schema", f"{field} must be a string array")
    result = [item.strip() for item in value if item.strip()]
    if non_empty and not result:
        raise OuterWorkflowError(
            "charter.boundaries.empty", f"{field} must contain an explicit boundary"
        )
    return result


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _candidate_object(
    candidate: Mapping[str, Any] | None,
    *,
    allowed: frozenset[str],
) -> Mapping[str, Any] | None:
    if candidate is None:
        return None
    source = _object(candidate, "candidate")
    unknown = set(source) - allowed
    if unknown:
        raise OuterWorkflowError(
            "candidate.schema",
            f"candidate contains unknown fields: {sorted(unknown)}",
        )
    return source


def _strict_text_values(value: Any, field: str) -> list[str]:
    return _text_list(value, field)


def _spec(pinned: PinnedInput) -> Mapping[str, Any]:
    return _object(pinned.artifact.get("spec"), "spec")


def _array(spec: Mapping[str, Any], field: str) -> list[Any]:
    value = spec.get(field, [])
    if not isinstance(value, list):
        raise OuterWorkflowError("input.schema", f"spec.{field} must be an array")
    return _copy(value)


def _item_text(item: Any, fields: Sequence[str]) -> str:
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        for field in fields:
            value = item.get(field)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def build_research_charter(
    inputs: tuple[PinnedInput, ...], candidate: Mapping[str, Any] | None = None
) -> CandidateDraft:
    spec = _spec(inputs[0])
    source = _candidate_object(
        candidate,
        allowed=frozenset(
            {"question", "boundaries", "success_criteria", "budget", "invariants"}
        ),
    )
    source = source if source is not None else spec
    source_question = _text(spec.get("question"), "spec.question", non_empty=True)
    question = _text(source.get("question"), "candidate.question", non_empty=True)
    if question != source_question:
        raise OuterWorkflowError(
            "invariant.question",
            "candidate question must exactly preserve the pinned research question",
        )
    source_boundaries = _text_list(
        spec.get("boundaries"), "spec.boundaries", non_empty=True
    )
    boundaries = _text_list(
        source.get("boundaries"), "candidate.boundaries", non_empty=True
    )
    if boundaries != source_boundaries:
        raise OuterWorkflowError(
            "invariant.boundaries",
            "candidate boundaries must exactly preserve the pinned research boundaries",
        )
    source_success_criteria = _text_list(
        spec.get("success_criteria", []), "spec.success_criteria"
    )
    success_criteria = _text_list(
        source.get("success_criteria", source_success_criteria),
        "candidate.success_criteria",
    )
    if success_criteria != source_success_criteria:
        raise OuterWorkflowError(
            "invariant.success_criteria",
            "candidate success criteria must preserve the pinned research criteria",
        )
    source_budget = _copy(_object(spec.get("budget", {}), "spec.budget"))
    budget = _copy(_object(source.get("budget", source_budget), "candidate.budget"))
    if budget != source_budget:
        raise OuterWorkflowError(
            "invariant.budget", "candidate budget must preserve the pinned research budget"
        )
    source_invariants = _text_list(spec.get("invariants", []), "spec.invariants")
    invariants = _text_list(
        source.get("invariants", source_invariants), "candidate.invariants"
    )
    if invariants != source_invariants:
        raise OuterWorkflowError(
            "invariant.invariants",
            "candidate invariants must preserve the pinned research invariants",
        )
    candidate_spec = {
        "question": question,
        "boundaries": boundaries,
        "success_criteria": success_criteria,
        "budget": budget,
        "invariants": invariants,
        "status": "candidate",
    }
    return CandidateDraft(candidate_spec, {"source_count": 1, "candidate_count": 1})


def build_research_literature(
    inputs: tuple[PinnedInput, ...], candidate: Mapping[str, Any] | None = None
) -> CandidateDraft:
    spec = _spec(inputs[0])
    source = _candidate_object(
        candidate,
        allowed=frozenset(
            {"question", "boundaries", "citations", "synthesis", "limitations"}
        ),
    )
    source = source if source is not None else spec
    charter_question = _text(spec.get("question"), "spec.question", non_empty=True)
    question = _text(
        source.get("question", charter_question), "candidate.question", non_empty=True
    )
    if question != charter_question:
        raise OuterWorkflowError(
            "invariant.question",
            "literature candidate must preserve the charter question",
        )
    charter_boundaries = _text_list(
        spec.get("boundaries"), "spec.boundaries", non_empty=True
    )
    boundaries = _text_list(
        source.get("boundaries", charter_boundaries),
        "candidate.boundaries",
        non_empty=True,
    )
    if boundaries != charter_boundaries:
        raise OuterWorkflowError(
            "invariant.boundaries",
            "literature candidate must preserve the charter boundaries",
        )
    citations = _array(source, "citations")
    if candidate is not None and any(
        item not in _array(spec, "citations") for item in citations
    ):
        raise OuterWorkflowError(
            "invariant.unpinned_source",
            "literature candidate may contain only citations pinned in the charter input",
        )
    limit = WORKFLOWS["research-literature"].budget["citation_count"]
    kept = citations[:limit]
    if "limitations" in source:
        limitations = _array(source, "limitations")
    else:
        limitations = _array(source, "literature_limitations")
    if len(citations) > limit:
        limitations.append(
            f"{len(citations) - limit} pinned citations omitted by the fixed citation budget."
        )
    candidate_spec = {
        "question": question,
        "boundaries": boundaries,
        "queries": [],
        "citations": kept,
        "synthesis": _text(
            source.get("synthesis", source.get("literature_synthesis", "")),
            "candidate.synthesis",
        ),
        "limitations": limitations,
        "status": "candidate",
    }
    return CandidateDraft(
        candidate_spec,
        {
            "source_count": 1,
            "candidate_count": 1,
            "query_count": 0,
            "citation_count": len(kept),
        },
    )


def _pinned_citation_keys(citations: list[Any]) -> set[str]:
    return {
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for item in citations
    }


def _validated_gap_rows(
    declared: list[Any], citations: list[Any], *, limit: int
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    pinned = _pinned_citation_keys(citations)
    for item in declared[:limit]:
        row = _object(item, "gap candidate")
        unknown = set(row) - {"statement", "evidence"}
        if unknown:
            raise OuterWorkflowError(
                "candidate.schema", f"gap candidate contains unknown fields: {sorted(unknown)}"
            )
        statement = _text(row.get("statement"), "gap candidate statement", non_empty=True)
        evidence = row.get("evidence", [])
        if not isinstance(evidence, list):
            raise OuterWorkflowError(
                "input.schema", "gap candidate evidence must be an array"
            )
        if any(
            json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            not in pinned
            for value in evidence
        ):
            raise OuterWorkflowError(
                "invariant.unpinned_source",
                "gap evidence may reference only pinned citation records",
            )
        gaps.append(
            {
                "statement": statement,
                "evidence": _copy(evidence),
                "support": "declared" if evidence else "unsupported",
            }
        )
    return gaps


def build_research_gap(
    inputs: tuple[PinnedInput, ...], candidate: Mapping[str, Any] | None = None
) -> CandidateDraft:
    spec = _spec(inputs[0])
    source = _candidate_object(
        candidate, allowed=frozenset({"question", "gaps"})
    )
    source = source if source is not None else spec
    citations = _array(spec, "citations")
    declared = _array(source, "gaps") if "gaps" in source else _array(source, "gap_candidates")
    limit = WORKFLOWS["research-gap"].budget["gap_count"]
    gaps = _validated_gap_rows(declared, citations, limit=limit)
    if not gaps:
        gaps.append(
            {
                "statement": "No evidence-backed research gap is declared in the pinned literature artifact.",
                "evidence": [],
                "support": "unsupported",
            }
        )
    question = _text(
        source.get("question", spec.get("question")),
        "candidate.question",
        non_empty=True,
    )
    if question != _text(spec.get("question"), "spec.question", non_empty=True):
        raise OuterWorkflowError(
            "invariant.question", "gap candidate must preserve the literature question"
        )
    candidate_spec = {
        "question": question,
        "gaps": gaps,
        "citation_count": len(citations),
        "selection": None,
        "status": "candidate",
    }
    return CandidateDraft(
        candidate_spec,
        {"source_count": 1, "candidate_count": 1, "gap_count": len(gaps)},
    )


def build_research_idea(
    inputs: tuple[PinnedInput, ...], candidate: Mapping[str, Any] | None = None
) -> CandidateDraft:
    spec = _spec(inputs[0])
    source = _candidate_object(
        candidate, allowed=frozenset({"gap", "ideas"})
    )
    source = source if source is not None else spec
    gaps = _array(spec, "gaps")
    selected_gap = spec.get("selected_gap")
    if selected_gap is None:
        if len(gaps) != 1:
            raise OuterWorkflowError(
                "idea.gap.selection_required",
                "the pinned gap artifact must explicitly select one gap when multiple or zero candidates exist",
            )
        selected_gap = gaps[0]
    gap = _item_text(selected_gap, ("statement", "gap", "description"))
    if not gap:
        raise OuterWorkflowError(
            "idea.gap.required",
            "the pinned gap artifact must contain a selected or sole candidate gap",
        )
    declared = _array(source, "ideas") if "ideas" in source else _array(source, "idea_candidates")
    limit = WORKFLOWS["research-idea"].budget["idea_count"]
    if len(declared) > limit:
        raise OuterWorkflowError("budget.exceeded", "candidate exceeded idea_count budget")
    ideas: list[dict[str, Any]] = []
    for item in declared:
        row = _object(item, "idea candidate")
        unknown = set(row) - {"proposal", "assumptions", "tests"}
        if unknown:
            raise OuterWorkflowError(
                "candidate.schema", f"idea candidate contains unknown fields: {sorted(unknown)}"
            )
        proposal = _text(row.get("proposal"), "idea proposal", non_empty=True)
        assumptions = _strict_text_values(row.get("assumptions", []), "idea assumptions")
        tests = _strict_text_values(row.get("tests", []), "idea tests")
        ideas.append(
            {"proposal": proposal, "assumptions": assumptions, "tests": tests}
        )
    if not ideas:
        ideas.append(
            {
                "proposal": f"Investigate the pinned gap without changing its meaning: {gap}",
                "assumptions": [],
                "tests": [],
            }
        )
    if candidate is not None:
        candidate_gap = _text(source.get("gap"), "candidate.gap", non_empty=True)
        if candidate_gap != gap:
            raise OuterWorkflowError(
                "invariant.gap", "idea candidate must preserve the selected gap wording"
            )
    candidate_spec = {
        "gap": gap,
        "ideas": ideas,
        "selection": None,
        "novelty_claim": None,
        "status": "candidate",
    }
    return CandidateDraft(
        candidate_spec,
        {"source_count": 1, "candidate_count": 1, "idea_count": len(ideas)},
    )


def build_research_novelty(
    inputs: tuple[PinnedInput, ...], candidate: Mapping[str, Any] | None = None
) -> CandidateDraft:
    idea_spec = _spec(inputs[0])
    literature_spec = _spec(inputs[1])
    source = _candidate_object(
        candidate, allowed=frozenset({"idea", "comparisons", "limitations"})
    )
    ideas = _array(idea_spec, "ideas")
    selected_idea = idea_spec.get("selected_idea")
    if selected_idea is None:
        if len(ideas) != 1:
            raise OuterWorkflowError(
                "novelty.idea.selection_required",
                "the pinned idea artifact must explicitly select one idea when multiple or zero candidates exist",
            )
        selected_idea = ideas[0]
    idea = _item_text(selected_idea, ("proposal", "idea", "description"))
    if not idea:
        raise OuterWorkflowError(
            "novelty.idea.required", "the pinned idea artifact must contain an idea"
        )
    if source is not None:
        candidate_idea = _text(source.get("idea"), "candidate.idea", non_empty=True)
        if candidate_idea != idea:
            raise OuterWorkflowError(
                "invariant.idea", "novelty candidate must preserve the pinned idea"
            )
    prior_work = _array(literature_spec, "prior_work") or _array(
        literature_spec, "citations"
    )
    limit = WORKFLOWS["research-novelty"].budget["comparison_count"]
    comparisons = []
    for item in prior_work[:limit]:
        work = _item_text(item, ("title", "work", "citation", "uri"))
        if not work:
            continue
        observed = (
            item.get("observed_difference", "not stated")
            if isinstance(item, dict)
            else "not stated"
        )
        comparisons.append(
            {
                "prior_work": work,
                "observed_difference": str(observed).strip() or "not stated",
            }
        )
    if source is None:
        candidate_comparisons = comparisons
        limitations = (
            []
            if comparisons
            else ["No pinned prior-work records were available for comparison."]
        )
    else:
        raw_comparisons = _array(source, "comparisons")
        if len(raw_comparisons) > limit:
            raise OuterWorkflowError(
                "budget.exceeded", "candidate exceeded comparison_count budget"
            )
        pinned_names = {item["prior_work"] for item in comparisons}
        candidate_comparisons = []
        for row in raw_comparisons:
            row_object = _object(row, "candidate comparison")
            unknown = set(row_object) - {"prior_work", "observed_difference"}
            if unknown:
                raise OuterWorkflowError(
                    "candidate.schema",
                    f"candidate comparison contains unknown fields: {sorted(unknown)}",
                )
            prior_work_name = _text(
                row_object.get("prior_work"),
                "candidate comparison prior_work",
                non_empty=True,
            )
            if prior_work_name not in pinned_names:
                raise OuterWorkflowError(
                    "invariant.unpinned_source",
                    "novelty comparisons may reference only pinned prior work",
                )
            candidate_comparisons.append(
                {
                    "prior_work": prior_work_name,
                    "observed_difference": _text(
                        row_object.get("observed_difference"),
                        "candidate comparison observed_difference",
                        non_empty=True,
                    ),
                }
            )
        limitations = _strict_text_values(
            source.get("limitations", []), "candidate.limitations"
        )
    candidate_spec = {
        "idea": idea,
        "comparisons": candidate_comparisons,
        "coverage": "pinned-prior-work-only",
        "novelty_verdict": "inconclusive",
        "limitations": limitations,
        "status": "candidate",
    }
    return CandidateDraft(
        candidate_spec,
        {
            "source_count": 2,
            "candidate_count": 1,
            "comparison_count": len(candidate_comparisons),
        },
    )


def build_research_reflect(
    inputs: tuple[PinnedInput, ...], candidate: Mapping[str, Any] | None = None
) -> CandidateDraft:
    source = _candidate_object(
        candidate, allowed=frozenset({"observations"})
    )
    limit = WORKFLOWS["research-reflect"].budget["observation_count"]
    pinned_observations: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    uncertainties: list[dict[str, Any]] = []
    for pinned in inputs:
        spec = _spec(pinned)
        for field, kind, destination in (
            ("observations", "observation", pinned_observations),
            ("failures", "failure", failures),
            ("uncertainties", "uncertainty", uncertainties),
        ):
            for value in _array(spec, field):
                destination.append(
                    {"source": pinned.path, "kind": kind, "value": _copy(value)}
                )
    if source is None:
        observations = pinned_observations
    else:
        observations = [
            {"source": "candidate", "kind": "observation", "value": value}
            for value in _strict_text_values(
                source.get("observations", []), "candidate.observations"
            )
        ]
    combined_count = len(observations) + len(failures) + len(uncertainties)
    if combined_count > limit:
        raise OuterWorkflowError(
            "budget.exceeded", "candidate exceeded observation_count budget"
        )
    reflection = {
        "subjects": [
            {
                "path": pinned.path,
                "sha256": pinned.sha256,
                "type": _object(pinned.artifact["type"], "type")["name"],
            }
            for pinned in inputs
        ],
        "observations": observations,
        "failures": failures,
        "uncertainties": uncertainties,
        "decisions": [],
        "status": "candidate",
    }
    option_count = len(WORKFLOWS["research-reflect"].options)
    return CandidateDraft(
        reflection,
        {
            "source_count": len(inputs),
            "candidate_count": 1,
            "observation_count": combined_count,
            "option_count": option_count,
        },
    )


BUILDERS: Mapping[str, Builder] = MappingProxyType(
    {
        "research-charter": build_research_charter,
        "research-literature": build_research_literature,
        "research-gap": build_research_gap,
        "research-idea": build_research_idea,
        "research-novelty": build_research_novelty,
        "research-reflect": build_research_reflect,
    }
)
