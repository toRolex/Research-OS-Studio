from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .budget import BudgetCounter, BudgetExceeded, BudgetLimits, BudgetUsage
from .execution import (
    AttemptContext,
    AttemptLedger,
    ExecutionReceipt,
    Executor,
    execute_local_command,
    json_bytes,
    load_pinned_bytes,
    load_pinned_json,
    read_project_bytes,
    validate_full_commit,
    write_outputs_exclusive,
)

ARTIFACT_CONTRACT = {"name": "research-os/artifact", "version": "1.1.0"}
WORKFLOW_VERSION = "1.0.0"
MODES = {"ordinary", "bounded_autonomy"}
_ALLOWED_ARTIFACT_FIELDS = {
    "contract",
    "target",
    "type",
    "spec",
    "title",
    "provenance",
    "relations",
    "assurance",
}


@dataclass(frozen=True)
class WorkflowOutcome:
    workflow: str
    status: str
    stop_reason: str
    outputs: tuple[str, ...]
    next_steps: tuple[str, ...]
    budget_usage: BudgetUsage = BudgetUsage()

    def as_dict(self) -> dict[str, object]:
        return {
            "workflow": self.workflow,
            "status": self.status,
            "stop_reason": self.stop_reason,
            "outputs": list(self.outputs),
            "next_steps": list(self.next_steps),
            "budget_usage": self.budget_usage.as_dict(),
        }


def design_experiment(
    project: Path,
    *,
    source: str,
    source_sha256: str,
    source_commit: str,
    output: str,
    report: str,
    hypothesis: str,
    dataset: Mapping[str, object],
    controls: Sequence[str],
    metrics: Sequence[Mapping[str, object]],
    run_matrix: Sequence[Mapping[str, object]],
    success_criteria: Sequence[str],
    failure_criteria: Sequence[str],
    stop_criteria: Sequence[str],
    budget: Mapping[str, object],
    project_ref: Mapping[str, object] | None = None,
    workstream_ref: Mapping[str, object] | None = None,
) -> WorkflowOutcome:
    workflow = "design-experiment"
    source_value = load_pinned_json(project, source, source_sha256, source_commit)
    _require_artifact(source_value, None, source, source_commit)
    _verify_references(project, source_value)
    boundary = _boundary(
        project, {"project": project_ref, "workstream": workstream_ref}
    )
    limits = BudgetLimits.from_mapping(budget)
    _non_empty_text(hypothesis, "hypothesis")
    _text_list(controls, "controls", non_empty=True)
    _object_list(metrics, "metrics", non_empty=True)
    _object_list(run_matrix, "run_matrix", non_empty=True)
    _text_list(success_criteria, "success_criteria", non_empty=True)
    _text_list(failure_criteria, "failure_criteria", non_empty=True)
    _text_list(stop_criteria, "stop_criteria", non_empty=True)
    if not isinstance(dataset, Mapping) or not dataset:
        raise ValueError("dataset must be a non-empty object")

    source_pin = _pin(
        source,
        source_sha256,
        source_commit,
        source_value,
        "user-selected design input",
    )
    artifact = _artifact(
        output,
        "experiment-design",
        {
            **boundary,
            "hypothesis": hypothesis.strip(),
            "dataset": dict(dataset),
            "controls": list(controls),
            "metrics": [dict(item) for item in metrics],
            "run_matrix": [dict(item) for item in run_matrix],
            "success_criteria": list(success_criteria),
            "failure_criteria": list(failure_criteria),
            "stop_criteria": list(stop_criteria),
            "budget": limits.as_dict(),
            "status": "candidate",
        },
        provenance=[source_pin],
    )
    outcome = WorkflowOutcome(
        workflow=workflow,
        status="stopped",
        stop_reason="candidate_created",
        outputs=(output, report),
        next_steps=("review experiment design", "invoke prepare-experiment explicitly"),
    )
    _write_artifact_and_report(
        project,
        output,
        artifact,
        report,
        _report(
            workflow,
            [(source, source_sha256, source_commit)],
            [output],
            outcome,
        ),
    )
    return outcome


def prepare_experiment(
    project: Path,
    *,
    design: str,
    design_sha256: str,
    design_commit: str,
    output: str,
    report: str,
    ledger_directory: str,
    commands: Sequence[Sequence[str]],
    mode: str = "ordinary",
    executor: Executor = execute_local_command,
    environment: Mapping[str, str] | None = None,
    stop_requested: bool | Callable[[], bool] = False,
) -> WorkflowOutcome:
    workflow = "prepare-experiment"
    design_value = load_pinned_json(project, design, design_sha256, design_commit)
    _require_artifact(design_value, "experiment-design", design, design_commit)
    _verify_references(project, design_value)
    boundary = _boundary(project, _spec(design_value))
    mode = _mode(mode)
    command_list = _commands(commands)
    if not command_list:
        raise ValueError(
            "prepare-experiment requires at least one build/test/check command"
        )
    limits = BudgetLimits.from_mapping(_require_budget(_spec(design_value)))
    counter = BudgetCounter(limits)
    ledger = AttemptLedger(project, ledger_directory)
    revision = _current_commit(project)
    inputs = [_fixed_reference(design, design_sha256, design_commit)]
    records: list[dict[str, object]] = []
    final = "not_prepared"
    stop_reason = "execution_failed"

    for command in command_list:
        if _user_stopped(stop_requested):
            stop_reason = "user_stopped"
            break
        if records and mode == "ordinary":
            break
        try:
            counter.require(BudgetUsage(attempts=1, rounds=1))
        except BudgetExceeded:
            stop_reason = "budget_exhausted"
            break
        attempt = ledger.next_attempt()
        context = AttemptContext(
            attempt=attempt,
            round=len(records) + 1,
            command=command,
            environment=dict(environment or {}),
        )
        receipt = executor(project, context, counter.remaining())
        receipt, usage, over_budget = _consume_receipt(counter, receipt)
        attempt_outcome = "budget_exhausted" if over_budget else _receipt_stop(receipt)
        records.append(
            ledger.append(
                workflow=workflow,
                context=context,
                receipt=receipt,
                cumulative_usage=usage,
                revision=revision,
                inputs=inputs,
                configuration={"mode": mode},
                workflow_outcome=attempt_outcome,
            )
        )
        if over_budget:
            stop_reason = "budget_exhausted"
            break
        if receipt.outcome == "succeeded":
            final = "prepared"
            stop_reason = "preparation_complete"
            break
        stop_reason = _receipt_stop(receipt)
        if mode == "ordinary" or receipt.outcome == "blocked":
            break

    artifact = _artifact(
        output,
        "experiment-preparation",
        {
            **boundary,
            "design": _fixed_reference(design, design_sha256, design_commit),
            "mode": mode,
            "status": final,
            "stop_reason": stop_reason,
            "attempt_ledger": ledger_directory,
            "attempts": records,
            "budget": {"limits": limits.as_dict(), "usage": counter.usage.as_dict()},
        },
        provenance=[
            _pin(
                design,
                design_sha256,
                design_commit,
                design_value,
                "pinned experiment design",
            )
        ],
    )
    outcome = WorkflowOutcome(
        workflow=workflow,
        status="stopped",
        stop_reason=stop_reason,
        outputs=(output, report),
        next_steps=("inspect preserved preparation attempts",)
        if final != "prepared"
        else ("invoke run-experiment explicitly",),
        budget_usage=counter.usage,
    )
    _write_artifact_and_report(
        project,
        output,
        artifact,
        report,
        _report(
            workflow,
            [(design, design_sha256, design_commit)],
            [output],
            outcome,
        ),
    )
    return outcome


def run_experiment(
    project: Path,
    *,
    design: str,
    design_sha256: str,
    design_commit: str,
    preparation: str,
    preparation_sha256: str,
    preparation_commit: str,
    output: str,
    report: str,
    ledger_directory: str,
    commands: Sequence[Sequence[str]],
    expected_result: str,
    mode: str = "ordinary",
    executor: Executor = execute_local_command,
    environment: Mapping[str, str] | None = None,
    stop_requested: bool | Callable[[], bool] = False,
) -> WorkflowOutcome:
    workflow = "run-experiment"
    design_value = load_pinned_json(project, design, design_sha256, design_commit)
    preparation_value = load_pinned_json(
        project, preparation, preparation_sha256, preparation_commit
    )
    _require_artifact(design_value, "experiment-design", design, design_commit)
    _verify_references(project, design_value)
    _require_artifact(
        preparation_value,
        "experiment-preparation",
        preparation,
        preparation_commit,
    )
    _verify_references(project, preparation_value)
    preparation_spec = _spec(preparation_value)
    boundary = _boundary(project, _spec(design_value))
    if _boundary(project, preparation_spec) != boundary:
        raise ValueError("preparation and design Project/Workstream mismatch")
    if preparation_spec.get("status") != "prepared":
        raise ValueError("run-experiment requires a prepared experiment")
    design_ref = preparation_spec.get("design")
    if design_ref != _fixed_reference(design, design_sha256, design_commit):
        raise ValueError("preparation does not reference the selected pinned design")
    mode = _mode(mode)
    command_list = _commands(commands)
    if not command_list:
        raise ValueError("run-experiment requires at least one command")
    _safe_relative(expected_result)
    try:
        read_project_bytes(project, expected_result)
    except FileNotFoundError:
        pass
    else:
        raise FileExistsError("expected result must not pre-exist the run")

    limits = BudgetLimits.from_mapping(_require_budget(_spec(design_value)))
    prior_usage = BudgetUsage.from_mapping(_require_usage(preparation_spec))
    counter = BudgetCounter(limits, prior_usage)
    ledger = AttemptLedger(project, ledger_directory)
    revision = _current_commit(project)
    inputs = [
        _fixed_reference(design, design_sha256, design_commit),
        _fixed_reference(preparation, preparation_sha256, preparation_commit),
    ]
    records: list[dict[str, object]] = []
    successful_result: dict[str, object] | None = None
    stop_reason = "execution_failed"

    for command in command_list:
        if _user_stopped(stop_requested):
            stop_reason = "user_stopped"
            break
        if records and mode == "ordinary":
            break
        if records:
            try:
                read_project_bytes(project, expected_result)
            except FileNotFoundError:
                pass
            else:
                stop_reason = "partial_result_requires_user_action"
                break
        try:
            counter.require(BudgetUsage(attempts=1, rounds=1))
        except BudgetExceeded:
            stop_reason = "budget_exhausted"
            break
        attempt = ledger.next_attempt()
        context = AttemptContext(
            attempt=attempt,
            round=len(records) + 1,
            command=command,
            environment=dict(environment or {}),
        )
        receipt = executor(project, context, counter.remaining())
        receipt, usage, over_budget = _consume_receipt(counter, receipt)
        snapshots: list[tuple[str, str, bytes]] = []
        result_data: bytes | None = None
        if receipt.outcome == "succeeded" and not over_budget:
            try:
                result_data = read_project_bytes(project, expected_result)
            except FileNotFoundError:
                stop_reason = "result_missing"
            else:
                result_digest = hashlib.sha256(result_data).hexdigest()
                successful_result = {
                    "target": {"kind": "git", "path": expected_result},
                    "sha256": result_digest,
                    "size_bytes": len(result_data),
                }
                snapshots.append(("result", expected_result, result_data))
                stop_reason = "run_complete"
        elif over_budget:
            stop_reason = "budget_exhausted"
        else:
            stop_reason = _receipt_stop(receipt)
            try:
                partial = read_project_bytes(project, expected_result)
            except FileNotFoundError:
                pass
            else:
                snapshots.append(("partial_result", expected_result, partial))

        records.append(
            ledger.append(
                workflow=workflow,
                context=context,
                receipt=receipt,
                cumulative_usage=usage,
                revision=revision,
                inputs=inputs,
                configuration={"mode": mode, "expected_result": expected_result},
                workflow_outcome=stop_reason,
                artifacts=snapshots,
            )
        )
        if successful_result or over_budget:
            break
        if mode == "ordinary" or receipt.outcome == "blocked":
            break
        if counter.first_exhausted_dimension() is not None:
            stop_reason = "budget_exhausted"
            break

    artifact = _artifact(
        output,
        "experiment-run",
        {
            **boundary,
            "design": _fixed_reference(design, design_sha256, design_commit),
            "preparation": _fixed_reference(
                preparation, preparation_sha256, preparation_commit
            ),
            "mode": mode,
            "status": "succeeded" if successful_result else "failed",
            "stop_reason": stop_reason,
            "attempt_ledger": ledger_directory,
            "attempts": records,
            "result": successful_result,
            "budget": {"limits": limits.as_dict(), "usage": counter.usage.as_dict()},
            "claim_assessment": "not_performed",
        },
        provenance=[
            _pin(
                design,
                design_sha256,
                design_commit,
                design_value,
                "pinned experiment design",
            ),
            _pin(
                preparation,
                preparation_sha256,
                preparation_commit,
                preparation_value,
                "pinned preparation result",
            ),
        ],
    )
    outcome = WorkflowOutcome(
        workflow=workflow,
        status="stopped",
        stop_reason=stop_reason,
        outputs=(output, report),
        next_steps=("invoke analyze-experiment explicitly",)
        if successful_result
        else ("inspect preserved attempts", "revise inputs or explicitly add budget"),
        budget_usage=counter.usage,
    )
    _write_artifact_and_report(
        project,
        output,
        artifact,
        report,
        _report(
            workflow,
            [
                (design, design_sha256, design_commit),
                (preparation, preparation_sha256, preparation_commit),
            ],
            [output],
            outcome,
        ),
    )
    return outcome


def analyze_experiment(
    project: Path,
    *,
    run: str,
    run_sha256: str,
    run_commit: str,
    output: str,
    report: str,
    analyzer: Callable[[bytes, Mapping[str, object]], Mapping[str, object]],
    analysis_directory: str = "analysis",
) -> WorkflowOutcome:
    """Analyze bytes fixed by the selected run commit, without an execution seam."""
    workflow = "analyze-experiment"
    run_value = load_pinned_json(project, run, run_sha256, run_commit)
    _require_artifact(run_value, "experiment-run", run, run_commit)
    _verify_references(project, run_value)
    run_spec = _spec(run_value)
    boundary = _boundary(project, run_spec)
    result = run_spec.get("result")
    if run_spec.get("status") != "succeeded" or not isinstance(result, Mapping):
        raise ValueError("analysis requires a successful run with a pinned result")
    target = result.get("target")
    result_sha256 = result.get("sha256")
    if not isinstance(target, Mapping) or target.get("kind") != "git":
        raise ValueError("run result target is incomplete")
    result_path = target.get("path")
    if not isinstance(result_path, str) or not isinstance(result_sha256, str):
        raise ValueError("run result reference is incomplete")
    _safe_relative(result_path)
    _safe_relative(analysis_directory)
    data = load_pinned_bytes(project, result_path, result_sha256, run_commit)

    project_root = project.resolve(strict=True)
    sandbox = project_root / analysis_directory
    if sandbox.exists() or sandbox.is_symlink():
        raise FileExistsError("analysis directory must not pre-exist")
    sandbox.mkdir(parents=True)
    before = _tree_digests(project_root, exclude=(sandbox,))
    analysis = analyzer(data, run_spec)
    after = _tree_digests(project_root, exclude=(sandbox,))
    if before != after:
        raise RuntimeError(
            "analysis attempted to mutate pinned inputs or experiment state"
        )
    if not isinstance(analysis, Mapping):
        raise TypeError("analyzer must return an object")
    required = {"method", "findings", "uncertainties", "criterion_results"}
    if set(analysis) != required:
        raise ValueError(f"analysis must define exactly {sorted(required)}")
    _non_empty_text(analysis["method"], "analysis.method")
    _object_list(analysis["findings"], "analysis.findings")
    _text_list(analysis["uncertainties"], "analysis.uncertainties")
    _object_list(analysis["criterion_results"], "analysis.criterion_results")

    artifact = _artifact(
        output,
        "experiment-analysis",
        {
            **boundary,
            "run": _fixed_reference(run, run_sha256, run_commit),
            "result": _fixed_reference(result_path, result_sha256, run_commit),
            "method": analysis["method"],
            "findings": analysis["findings"],
            "uncertainties": analysis["uncertainties"],
            "criterion_results": analysis["criterion_results"],
            "additional_runs_performed": False,
            "status": "candidate",
        },
        provenance=[
            _pin(
                run,
                run_sha256,
                run_commit,
                run_value,
                "pinned experiment run",
            )
        ],
    )
    outcome = WorkflowOutcome(
        workflow=workflow,
        status="stopped",
        stop_reason="analysis_complete",
        outputs=(output, report),
        next_steps=("review analysis", "invoke assess-result-to-claim explicitly"),
    )
    _write_artifact_and_report(
        project,
        output,
        artifact,
        report,
        _report(
            workflow,
            [(run, run_sha256, run_commit)],
            [output],
            outcome,
        ),
    )
    return outcome


def assess_result_to_claim(
    project: Path,
    *,
    analysis: str,
    analysis_sha256: str,
    analysis_commit: str,
    claim: str,
    claim_sha256: str,
    claim_commit: str,
    evidence_output: str,
    assessment_output: str,
    report: str,
    method: str,
    conditions: Sequence[str],
    scope: Sequence[str],
    verdict: str,
    limitations: Sequence[str],
) -> WorkflowOutcome:
    workflow = "assess-result-to-claim"
    analysis_value = load_pinned_json(
        project, analysis, analysis_sha256, analysis_commit
    )
    claim_value = load_pinned_json(project, claim, claim_sha256, claim_commit)
    _require_artifact(analysis_value, "experiment-analysis", analysis, analysis_commit)
    if "role" in _spec(analysis_value):
        raise ValueError(
            "assess-result-to-claim requires experiment findings, not a prior assessment"
        )
    _require_artifact(claim_value, "claim", claim, claim_commit)
    _verify_references(project, analysis_value)
    _verify_references(project, claim_value)
    boundary = _boundary(project, _spec(analysis_value))
    if _boundary(project, _spec(claim_value)) != boundary:
        raise ValueError("analysis and Claim Project/Workstream mismatch")
    _validate_analysis_handoff(project, analysis_value, boundary)
    _non_empty_text(method, "method")
    _text_list(conditions, "conditions")
    _scope(scope)
    if verdict not in {"supports", "does_not_support", "inconclusive"}:
        raise ValueError("verdict must be supports, does_not_support, or inconclusive")
    _text_list(limitations, "limitations")

    provenance = [
        _pin(
            analysis,
            analysis_sha256,
            analysis_commit,
            analysis_value,
            "pinned experiment analysis",
        ),
        _pin(
            claim,
            claim_sha256,
            claim_commit,
            claim_value,
            "pinned claim under assessment",
        ),
    ]
    scoped = scope if isinstance(scope, str) else list(scope)
    assessment = _artifact(
        assessment_output,
        "experiment-analysis",
        {
            **boundary,
            "role": "result-to-claim-assessment",
            "analysis": _fixed_reference(analysis, analysis_sha256, analysis_commit),
            "claim": _fixed_reference(claim, claim_sha256, claim_commit),
            "verdict": verdict,
            "method": method.strip(),
            "conditions": list(conditions),
            "scope": scoped,
            "limitations": list(limitations),
            "claim_truth_determined": False,
            "human_acceptance": "not_performed",
            "status": "candidate",
        },
        provenance=provenance,
    )
    artifacts = {assessment_output: assessment}
    if verdict == "supports":
        artifacts = {
            evidence_output: _artifact(
                evidence_output,
                "evidence",
                {
                    **boundary,
                    "description": "Fixed experiment analysis used within the declared support boundary; not proof or global truth. "
                    + "Limitations: "
                    + ("; ".join(limitations) or "none declared"),
                },
                provenance=provenance,
                relations=[
                    {
                        "relation": "supports",
                        "claim": _fixed_reference(claim, claim_sha256, claim_commit),
                        "scope": scoped,
                        "method": method.strip(),
                        "conditions": list(conditions),
                    }
                ],
            ),
            **artifacts,
        }
    if len({evidence_output, assessment_output, report}) != 3:
        raise ValueError("Evidence, analysis and report output paths must be distinct")
    for artifact in artifacts.values():
        _validate_contract(artifact)
        _verify_references(project, artifact)
    outcome = WorkflowOutcome(
        workflow=workflow,
        status="stopped",
        stop_reason="assessment_complete",
        outputs=(*artifacts, report),
        next_steps=(
            "review evidence boundary",
            "record independent or human assessment separately",
        ),
    )
    write_outputs_exclusive(
        project,
        {
            **{path: json_bytes(artifact) for path, artifact in artifacts.items()},
            report: json_bytes(
                _report(
                    workflow,
                    [
                        (analysis, analysis_sha256, analysis_commit),
                        (claim, claim_sha256, claim_commit),
                    ],
                    list(artifacts),
                    outcome,
                )
            ),
        },
    )
    return outcome


def _artifact(
    path: str,
    type_name: str,
    spec: Mapping[str, object],
    *,
    provenance: Sequence[Mapping[str, object]] | None = None,
    relations: Sequence[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    _safe_relative(path)
    value: dict[str, object] = {
        "contract": dict(ARTIFACT_CONTRACT),
        "target": {"kind": "git", "path": path},
        "type": {"name": type_name, "version": "1.0.0"},
        "spec": dict(spec),
    }
    if provenance is not None:
        value["provenance"] = [dict(item) for item in provenance]
    if relations is not None:
        value["relations"] = [dict(item) for item in relations]
    return value


def _report(
    workflow: str,
    inputs: Sequence[tuple[str, str, str]],
    outputs: Sequence[str],
    outcome: WorkflowOutcome,
) -> dict[str, object]:
    return {
        "contract": {"name": "research-os/workflow-report", "version": "1.0.0"},
        "workflow": {"name": workflow, "version": WORKFLOW_VERSION},
        "inputs": [
            _fixed_reference(path, digest, commit) for path, digest, commit in inputs
        ],
        "outputs": [{"kind": "git", "path": path} for path in outputs],
        "status": outcome.status,
        "stop_reason": outcome.stop_reason,
        "budget_usage": outcome.budget_usage.as_dict(),
        "next_steps": list(outcome.next_steps),
        "automatic_next_workflow": False,
    }


def _write_artifact_and_report(
    project: Path,
    output: str,
    artifact: Mapping[str, object],
    report: str,
    report_value: Mapping[str, object],
) -> None:
    _validate_contract(artifact)
    _verify_references(project, artifact)
    if output == report:
        raise ValueError("Artifact and report paths must be distinct")
    write_outputs_exclusive(
        project,
        {output: json_bytes(artifact), report: json_bytes(report_value)},
    )


def _pin(
    path: str,
    digest: str,
    commit: str,
    value: Mapping[str, object],
    purpose: str,
) -> dict[str, object]:
    return {"activity": purpose, "inputs": [_fixed_reference(path, digest, commit)]}


def _fixed_reference(path: str, digest: str, commit: str) -> dict[str, object]:
    return {"target": _fixed_target(path, commit), "sha256": _sha256(digest)}


def _fixed_target(path: str, commit: str) -> dict[str, str]:
    _safe_relative(path)
    return {"kind": "git", "path": path, "commit": validate_full_commit(commit)}


def _fixed_claim_target(
    claim: Mapping[str, object], selected_path: str, selected_commit: str
) -> dict[str, object]:
    target = claim.get("target")
    if not isinstance(target, Mapping) or target != {
        "kind": "git",
        "path": selected_path,
    }:
        raise ValueError("Claim Artifact must use the selected live Git path")
    return _fixed_target(selected_path, selected_commit)


def _spec(value: Mapping[str, object]) -> Mapping[str, object]:
    spec = value.get("spec")
    if not isinstance(spec, Mapping):
        raise ValueError("Artifact spec must be an object")
    return spec


def _require_artifact(
    value: Mapping[str, object],
    expected: str | None,
    selected_path: str,
    selected_commit: str,
) -> None:
    _validate_contract(value)
    unknown = set(value) - _ALLOWED_ARTIFACT_FIELDS
    if unknown:
        raise ValueError(f"Artifact has unknown top-level fields: {sorted(unknown)}")
    if value.get("contract") != ARTIFACT_CONTRACT:
        raise ValueError("unsupported Artifact contract")
    if expected is not None and value.get("type") != {
        "name": expected,
        "version": "1.0.0",
    }:
        raise ValueError(f"expected {expected} Artifact version 1.0.0")
    target = value.get("target")
    if not isinstance(target, Mapping) or target.get("kind") != "git":
        raise ValueError("Artifact target must be a Git target")
    if target.get("path") != selected_path:
        raise ValueError("Artifact target path does not match selected input path")
    target_commit = target.get("commit")
    if target_commit is not None and target_commit != selected_commit:
        raise ValueError("Artifact target commit conflicts with selected input pin")
    _spec(value)


def _verify_references(project: Path, value: object) -> None:
    from research_os.validation.semantics import validate_fixed_ref

    if isinstance(value, Mapping):
        target = value.get("target")
        if (
            isinstance(target, Mapping)
            and "sha256" in value
            and ("commit" in target or target.get("kind") == "uri")
        ):
            if target.get("kind") != "git" or "repository" in target:
                raise ValueError(
                    "computational fixed references must be same-repository Git"
                )
            issues = validate_fixed_ref(
                {"target": dict(target), "sha256": value["sha256"]},
                repository=project,
                structural_only=False,
            )
            if issues:
                raise ValueError(
                    "invalid fixed reference: "
                    + "; ".join(item.code for item in issues)
                )
        for child in value.values():
            _verify_references(project, child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _verify_references(project, child)


def _validate_contract(value: Mapping[str, object]) -> None:
    from research_os.contracts import validate_artifact
    from research_os.validation.semantics import validate_provenance

    issues = validate_artifact(dict(value))
    if "provenance" in value:
        issues.extend(validate_provenance(value["provenance"]))
    if issues:
        raise ValueError("invalid Artifact: " + "; ".join(item.code for item in issues))
    if value.get("type") == {"name": "experiment-analysis", "version": "1.0.0"}:
        _validate_analysis_spec(_spec(value))


def _validate_analysis_spec(spec: Mapping[str, object]) -> None:
    from research_os.validation.semantics import validate_fixed_ref

    assessment = spec.get("role") == "result-to-claim-assessment"
    references = ("analysis", "claim") if assessment else ("run", "result")
    for name in references:
        if validate_fixed_ref(spec.get(name)):
            raise ValueError(f"analysis requires fixed {name}")
    _non_empty_text(spec.get("method"), "analysis.method")
    if spec.get("status") != "candidate":
        raise ValueError("analysis status must be candidate")
    if assessment:
        if spec.get("verdict") not in {"supports", "does_not_support", "inconclusive"}:
            raise ValueError("invalid result-to-claim verdict")
        _scope(spec.get("scope"))
        _text_list(spec.get("conditions"), "conditions")
        _text_list(spec.get("limitations"), "limitations")
        if (
            spec.get("claim_truth_determined") is not False
            or spec.get("human_acceptance") != "not_performed"
        ):
            raise ValueError(
                "result-to-claim analysis cannot establish truth or human acceptance"
            )
    else:
        if "role" in spec:
            raise ValueError("unknown experiment-analysis role")
        _object_list(spec.get("findings"), "analysis.findings")
        _text_list(spec.get("uncertainties"), "analysis.uncertainties")
        _object_list(spec.get("criterion_results"), "analysis.criterion_results")
        if spec.get("additional_runs_performed") is not False:
            raise ValueError("analysis must not perform additional runs")


def _validate_analysis_handoff(
    project: Path, analysis: Mapping[str, object], boundary: Mapping[str, object]
) -> None:
    spec = _spec(analysis)
    run_ref = spec["run"]
    run = _load_reference(project, run_ref, "experiment-run")
    run_spec = _spec(run)
    _verify_references(project, run)
    if _boundary(project, run_spec) != boundary:
        raise ValueError("analysis and run Project/Workstream mismatch")
    result = run_spec.get("result")
    if run_spec.get("status") != "succeeded" or not isinstance(result, Mapping):
        raise ValueError("assessment requires a successful pinned run")
    target = result.get("target")
    if not isinstance(target, Mapping) or target.get("kind") != "git":
        raise ValueError("run result must be a local Git file")
    expected = _fixed_reference(
        target.get("path"), result.get("sha256"), run_ref["target"]["commit"]
    )
    if spec["result"] != expected:
        raise ValueError("analysis result does not match the selected run result")
    design = _load_reference(project, run_spec.get("design"), "experiment-design")
    preparation = _load_reference(
        project, run_spec.get("preparation"), "experiment-preparation"
    )
    if (
        _boundary(project, _spec(design)) != boundary
        or _boundary(project, _spec(preparation)) != boundary
    ):
        raise ValueError("experiment chain Project/Workstream mismatch")
    if _spec(preparation).get("status") != "prepared" or _spec(preparation).get(
        "design"
    ) != run_spec.get("design"):
        raise ValueError("run does not bind a preparation of its selected design")


def _load_reference(
    project: Path, reference: object, expected: str | None = None
) -> Mapping[str, object]:
    from research_os.validation.semantics import validate_fixed_ref

    issues = validate_fixed_ref(reference, repository=project, structural_only=False)
    if issues:
        raise ValueError(
            "invalid fixed reference: " + "; ".join(item.code for item in issues)
        )
    target = reference["target"]
    if target.get("kind") != "git" or "repository" in target:
        raise ValueError(
            "computational inputs require same-repository fixed Git references"
        )
    value = load_pinned_json(
        project, target["path"], reference["sha256"], target["commit"]
    )
    _require_artifact(value, expected, target["path"], target["commit"])
    return value


def _boundary(project: Path, spec: Mapping[str, object]) -> dict[str, object]:
    project_ref, workstream_ref = spec.get("project"), spec.get("workstream")
    _load_reference(project, project_ref, "project")
    workstream = _load_reference(project, workstream_ref, "workstream")
    if _spec(workstream).get("project") != project_ref:
        raise ValueError("Workstream does not belong to the selected fixed Project")
    return {"project": project_ref, "workstream": workstream_ref}


def _require_budget(spec: Mapping[str, object]) -> Mapping[str, object]:
    budget = spec.get("budget")
    if not isinstance(budget, Mapping):
        raise ValueError("experiment design budget must be an object")
    return budget


def _require_usage(preparation_spec: Mapping[str, object]) -> Mapping[str, object]:
    budget = preparation_spec.get("budget")
    if not isinstance(budget, Mapping) or not isinstance(budget.get("usage"), Mapping):
        raise ValueError("preparation budget usage is incomplete")
    return budget["usage"]


def _user_stopped(request: bool | Callable[[], bool]) -> bool:
    value = request() if callable(request) else request
    if type(value) is not bool:
        raise ValueError("stop_requested must be a boolean or return a boolean")
    return value


def _mode(value: str) -> str:
    if value not in MODES:
        raise ValueError("mode must be ordinary or bounded_autonomy")
    return value


def _commands(value: Sequence[Sequence[str]]) -> list[tuple[str, ...]]:
    if isinstance(value, (str, bytes)):
        raise ValueError("commands must be an array of argv arrays")
    commands: list[tuple[str, ...]] = []
    for command in value:
        if isinstance(command, (str, bytes)):
            raise ValueError("commands use argv arrays, never shell strings")
        argv = tuple(command)
        if not argv or any(not isinstance(part, str) or not part for part in argv):
            raise ValueError("every command must be a non-empty argv array")
        commands.append(argv)
    return commands


def _consume_receipt(
    counter: BudgetCounter, receipt: ExecutionReceipt
) -> tuple[ExecutionReceipt, BudgetUsage, bool]:
    delta = receipt.usage.plus(BudgetUsage(attempts=1, rounds=1))
    try:
        return receipt, counter.consume(delta), False
    except BudgetExceeded:
        usage = counter.observe(delta)
        if receipt.outcome in {"succeeded", "failed"}:
            receipt = ExecutionReceipt(
                outcome="failed",
                return_code=receipt.return_code
                if receipt.return_code not in {None, 0}
                else 1,
                usage=receipt.usage,
                stdout=receipt.stdout,
                stderr=receipt.stderr,
                detail="executor receipt exceeded hard budget",
            )
        return receipt, usage, True


def _receipt_stop(receipt: ExecutionReceipt) -> str:
    if receipt.outcome == "timed_out":
        return "budget_exhausted"
    if receipt.outcome == "blocked":
        return "external_prerequisite_unavailable"
    if receipt.outcome == "succeeded":
        return "succeeded"
    return "execution_failed"


def _safe_relative(value: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or value.startswith("/")
        or "\\" in value
        or "\x00" in value
        or any(part in {"", ".", ".."} for part in value.split("/"))
        or any(part.casefold() == ".git" for part in value.split("/"))
    ):
        raise ValueError("path must be a safe repository-relative file path")


def _sha256(value: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError("digest must be SHA-256 lowercase hexadecimal")
    return value


def _non_empty_text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")


def _text_list(value: object, name: str, *, non_empty: bool = False) -> None:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{name} must be an array")
    if non_empty and not value:
        raise ValueError(f"{name} must be a non-empty array")
    for item in value:
        _non_empty_text(item, f"{name} item")


def _object_list(value: object, name: str, *, non_empty: bool = False) -> None:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{name} must be an array")
    if non_empty and not value:
        raise ValueError(f"{name} must be a non-empty array")
    if any(not isinstance(item, Mapping) or not item for item in value):
        raise ValueError(f"{name} entries must be non-empty objects")


def _scope(scope: Sequence[str] | str) -> None:
    from research_os.validation.semantics import validate_scope

    issues = validate_scope(scope if isinstance(scope, str) else list(scope))
    if issues:
        raise ValueError("invalid scope: " + "; ".join(item.code for item in issues))


def _current_commit(project: Path) -> str:
    import subprocess

    completed = subprocess.run(
        ["git", "-C", str(project.resolve(strict=True)), "rev-parse", "HEAD"],
        capture_output=True,
        check=False,
        text=True,
        timeout=10,
    )
    if completed.returncode != 0:
        raise ValueError("workflow project must have a committed Git revision")
    return validate_full_commit(completed.stdout.strip())


def _tree_digests(project: Path, *, exclude: Sequence[Path] = ()) -> dict[str, str]:
    import os

    root = project.resolve(strict=True)
    excluded = tuple(path.resolve() for path in exclude)
    values: dict[str, str] = {}
    for directory, names, files in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        names[:] = [
            name
            for name in names
            if name != ".git"
            and not any(
                (directory_path / name).resolve() == item
                or item in (directory_path / name).resolve().parents
                for item in excluded
            )
            and not (directory_path / name).is_symlink()
        ]
        for name in sorted(files):
            path = directory_path / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                values[relative] = f"symlink:{os.readlink(path)}"
            else:
                values[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return values
