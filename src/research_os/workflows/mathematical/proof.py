from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .records import (
    RecordError,
    ValidationIssue,
    canonical_digest,
    ordered_unique_strings,
    reject_unknown,
    require_mapping,
    require_nonempty_string,
    require_string_list,
    resolve_under,
)

STATEMENT_CONTRACT = "research-os/mathematical-statement"
PROOF_CONTRACT = "research-os/math-proof-run"
REVIEW_CONTRACT = "research-os/independent-proof-review"
VERSION = "1.0.0"
SEMANTIC_FIELDS = ("quantifiers", "hypotheses", "domain", "conclusion")
STOP_REASONS = {
    "workflow-complete",
    "counterexample-found",
    "statement-unconfirmed",
    "proof-gap",
    "budget-exhausted",
    "execution-failed",
    "user-stopped",
}
ATTEMPT_OUTCOMES = {"candidate-proof", "proof-gap", "counterexample", "failed"}
REVIEW_VERDICTS = {"pass", "fail", "inconclusive"}


class MathematicalWorkflowError(RecordError):
    """Input or invariant failure that must stop before producing a false result."""


@dataclass(frozen=True)
class StatementIdentity:
    revision: int
    digest: str


def _statement_semantics(value: Mapping[str, Any]) -> dict[str, object]:
    return {field: value.get(field) for field in SEMANTIC_FIELDS}


def _statement_digest(value: Mapping[str, Any]) -> str:
    return canonical_digest(_statement_semantics(value))


def create_statement_candidate(
    *,
    revision: int,
    quantifiers: Sequence[str],
    hypotheses: Sequence[str],
    domain: str,
    conclusion: str,
    rationale: str,
    supersedes: str | None = None,
) -> dict[str, object]:
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "statement.revision",
                    "revision must be a positive integer",
                    "/revision",
                )
            ]
        )
    semantics: dict[str, object] = {
        "quantifiers": ordered_unique_strings(quantifiers),
        "hypotheses": ordered_unique_strings(hypotheses),
        "domain": domain.strip(),
        "conclusion": conclusion.strip(),
    }
    statement: dict[str, object] = {
        "contract": {"name": STATEMENT_CONTRACT, "version": VERSION},
        "revision": revision,
        **semantics,
        "rationale": rationale.strip(),
        "semantic_digest": canonical_digest(semantics),
        "confirmation": None,
    }
    if supersedes is not None:
        statement["supersedes"] = supersedes
    issues = validate_statement(statement)
    if issues:
        raise MathematicalWorkflowError(issues)
    return statement


def confirm_statement(
    statement: Mapping[str, Any], *, principal: str, confirmation: str
) -> dict[str, object]:
    issues = validate_statement(statement, require_confirmed=False)
    if issues:
        raise MathematicalWorkflowError(issues)
    revision = statement["revision"]
    digest = statement["semantic_digest"]
    expected = f"CONFIRM STATEMENT r{revision} {digest}"
    if confirmation != expected:
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "statement.confirmation",
                    f"confirmation must be exactly {expected}",
                    "/confirmation",
                )
            ]
        )
    if not isinstance(principal, str) or not principal.strip():
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "statement.principal", "principal must be non-empty", "/principal"
                )
            ]
        )
    result = dict(statement)
    result["confirmation"] = {
        "principal": principal.strip(),
        "revision": revision,
        "semantic_digest": digest,
        "phrase": confirmation,
    }
    return result


def revise_statement(
    previous: Mapping[str, Any],
    *,
    quantifiers: Sequence[str] | None = None,
    hypotheses: Sequence[str] | None = None,
    domain: str | None = None,
    conclusion: str | None = None,
    rationale: str,
) -> dict[str, object]:
    issues = validate_statement(previous, require_confirmed=False)
    if issues:
        raise MathematicalWorkflowError(issues)
    semantics = _statement_semantics(previous)
    proposed = {
        "quantifiers": list(quantifiers)
        if quantifiers is not None
        else semantics["quantifiers"],
        "hypotheses": list(hypotheses)
        if hypotheses is not None
        else semantics["hypotheses"],
        "domain": domain if domain is not None else semantics["domain"],
        "conclusion": conclusion if conclusion is not None else semantics["conclusion"],
    }
    normalized = {
        "quantifiers": ordered_unique_strings(proposed["quantifiers"]),
        "hypotheses": ordered_unique_strings(proposed["hypotheses"]),
        "domain": str(proposed["domain"]).strip(),
        "conclusion": str(proposed["conclusion"]).strip(),
    }
    new_digest = canonical_digest(normalized)
    if new_digest == previous["semantic_digest"]:
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "statement.revision.no_semantic_change",
                    "a new statement revision requires a semantic change",
                    "/",
                )
            ]
        )
    return create_statement_candidate(
        revision=int(previous["revision"]) + 1,
        quantifiers=normalized["quantifiers"],
        hypotheses=normalized["hypotheses"],
        domain=normalized["domain"],
        conclusion=normalized["conclusion"],
        rationale=rationale,
        supersedes=str(previous["semantic_digest"]),
    )


def validate_statement(
    value: object, *, require_confirmed: bool = False
) -> list[ValidationIssue]:
    statement, issues = require_mapping(value, "statement.object", "/")
    if statement is None:
        return issues
    allowed = {
        "contract",
        "revision",
        "quantifiers",
        "hypotheses",
        "domain",
        "conclusion",
        "rationale",
        "semantic_digest",
        "confirmation",
        "supersedes",
    }
    issues.extend(
        reject_unknown(statement, allowed, code="statement.field", location="")
    )
    if statement.get("contract") != {"name": STATEMENT_CONTRACT, "version": VERSION}:
        issues.append(
            ValidationIssue(
                "statement.contract", "unsupported statement contract", "/contract"
            )
        )
    revision = statement.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        issues.append(
            ValidationIssue(
                "statement.revision", "revision must be a positive integer", "/revision"
            )
        )
    issues.extend(
        require_string_list(
            statement.get("quantifiers"),
            code="statement.quantifiers",
            location="/quantifiers",
        )
    )
    issues.extend(
        require_string_list(
            statement.get("hypotheses"),
            code="statement.hypotheses",
            location="/hypotheses",
        )
    )
    issues.extend(
        require_nonempty_string(
            statement.get("domain"), code="statement.domain", location="/domain"
        )
    )
    issues.extend(
        require_nonempty_string(
            statement.get("conclusion"),
            code="statement.conclusion",
            location="/conclusion",
        )
    )
    issues.extend(
        require_nonempty_string(
            statement.get("rationale"),
            code="statement.rationale",
            location="/rationale",
        )
    )
    if all(field in statement for field in SEMANTIC_FIELDS):
        try:
            expected_digest = _statement_digest(statement)
        except (TypeError, ValueError):
            expected_digest = ""
        if statement.get("semantic_digest") != expected_digest:
            issues.append(
                ValidationIssue(
                    "statement.digest",
                    "semantic digest does not match statement fields",
                    "/semantic_digest",
                )
            )
    if "supersedes" in statement and (
        not isinstance(statement["supersedes"], str)
        or len(statement["supersedes"]) != 64
    ):
        issues.append(
            ValidationIssue(
                "statement.supersedes",
                "supersedes must be a SHA-256 digest",
                "/supersedes",
            )
        )
    confirmation = statement.get("confirmation")
    if confirmation is None:
        if require_confirmed:
            issues.append(
                ValidationIssue(
                    "statement.unconfirmed",
                    "statement requires explicit confirmation",
                    "/confirmation",
                )
            )
    elif isinstance(confirmation, Mapping):
        expected_confirmation = {
            "principal": confirmation.get("principal"),
            "revision": revision,
            "semantic_digest": statement.get("semantic_digest"),
            "phrase": f"CONFIRM STATEMENT r{revision} {statement.get('semantic_digest')}",
        }
        if (
            dict(confirmation) != expected_confirmation
            or not isinstance(confirmation.get("principal"), str)
            or not confirmation["principal"].strip()
        ):
            issues.append(
                ValidationIssue(
                    "statement.confirmation.stale",
                    "confirmation is not bound to this revision and digest",
                    "/confirmation",
                )
            )
    else:
        issues.append(
            ValidationIssue(
                "statement.confirmation",
                "confirmation must be null or an object",
                "/confirmation",
            )
        )
    return issues


def _validate_lemma_map(value: object) -> list[ValidationIssue]:
    if not isinstance(value, list) or not value:
        return [
            ValidationIssue(
                "proof.lemma_map", "lemma_map must be a non-empty array", "/lemma_map"
            )
        ]
    issues: list[ValidationIssue] = []
    identifiers: set[str] = set()
    dependencies: dict[str, list[str]] = {}
    for index, raw in enumerate(value):
        location = f"/lemma_map/{index}"
        if not isinstance(raw, Mapping):
            issues.append(
                ValidationIssue("proof.lemma", "lemma must be an object", location)
            )
            continue
        issues.extend(
            reject_unknown(
                raw,
                {"id", "statement", "depends_on", "status"},
                code="proof.lemma.field",
                location=location,
            )
        )
        identifier = raw.get("id")
        if (
            not isinstance(identifier, str)
            or not identifier.strip()
            or identifier in identifiers
        ):
            issues.append(
                ValidationIssue(
                    "proof.lemma.id",
                    "lemma id must be non-empty and unique",
                    f"{location}/id",
                )
            )
            continue
        identifiers.add(identifier)
        issues.extend(
            require_nonempty_string(
                raw.get("statement"),
                code="proof.lemma.statement",
                location=f"{location}/statement",
            )
        )
        issues.extend(
            require_string_list(
                raw.get("depends_on"),
                code="proof.lemma.depends_on",
                location=f"{location}/depends_on",
            )
        )
        if raw.get("status") not in {"open", "proved", "gap"}:
            issues.append(
                ValidationIssue(
                    "proof.lemma.status",
                    "lemma status must be open, proved, or gap",
                    f"{location}/status",
                )
            )
        dependencies[identifier] = (
            list(raw.get("depends_on", []))
            if isinstance(raw.get("depends_on"), list)
            else []
        )
    for identifier, required in dependencies.items():
        for dependency in required:
            if dependency not in identifiers:
                issues.append(
                    ValidationIssue(
                        "proof.lemma.dependency",
                        f"unknown dependency {dependency}",
                        f"/lemma_map/{identifier}",
                    )
                )
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> bool:
        if identifier in visiting:
            return False
        if identifier in visited:
            return True
        visiting.add(identifier)
        if any(
            not visit(dependency) for dependency in dependencies.get(identifier, [])
        ):
            return False
        visiting.remove(identifier)
        visited.add(identifier)
        return True

    for identifier in identifiers:
        visiting.clear()
        if not visit(identifier):
            issues.append(
                ValidationIssue(
                    "proof.lemma.cycle",
                    "lemma dependencies must be acyclic",
                    "/lemma_map",
                )
            )
            break
    return issues


def _retained_proof_gaps(attempts: object, lemmas: object) -> list[dict[str, str]]:
    """No implicit closure: a later candidate cannot erase an earlier obligation."""
    gaps: list[dict[str, str]] = []
    for attempt in attempts if isinstance(attempts, list) else []:
        if not isinstance(attempt, Mapping):
            continue
        supplied = attempt.get("gaps")
        details = (
            [gap.strip() for gap in supplied if isinstance(gap, str) and gap.strip()]
            if isinstance(supplied, list)
            else []
        )
        if not details and attempt.get("outcome") in {"proof-gap", "failed"}:
            details = [f"Unclosed {attempt['outcome']} attempt"]
        gaps.extend(
            {"attempt": str(attempt.get("id", "")), "gap": gap} for gap in details
        )
    for lemma in lemmas if isinstance(lemmas, list) else []:
        if isinstance(lemma, Mapping) and lemma.get("status") in {"open", "gap"}:
            gaps.append(
                {"attempt": "lemma-map", "gap": str(lemma.get("statement", ""))}
            )
    return gaps


def run_math_proof(
    *,
    statement: Mapping[str, Any],
    actor_principal: str,
    examples: Sequence[Mapping[str, Any]],
    counterexamples: Sequence[Mapping[str, Any]],
    lemma_map: Sequence[Mapping[str, Any]],
    attempts: Sequence[Mapping[str, Any]],
    max_attempts: int,
    user_stop: bool = False,
    execution_error: str | None = None,
) -> dict[str, object]:
    statement_issues = validate_statement(statement, require_confirmed=True)
    if statement_issues:
        raise MathematicalWorkflowError(statement_issues)
    if not isinstance(actor_principal, str) or not actor_principal.strip():
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "proof.actor", "actor principal is required", "/actor_principal"
                )
            ]
        )
    if (
        isinstance(max_attempts, bool)
        or not isinstance(max_attempts, int)
        or max_attempts < 1
    ):
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "proof.budget",
                    "max_attempts must be a positive integer",
                    "/budget/max_attempts",
                )
            ]
        )
    if len(attempts) > max_attempts:
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "proof.budget.exceeded",
                    "supplied attempts exceed the hard attempt budget",
                    "/attempts",
                )
            ]
        )
    normalized_examples = [dict(item) for item in examples]
    normalized_counterexamples = [dict(item) for item in counterexamples]
    normalized_lemmas = [dict(item) for item in lemma_map]
    normalized_attempts = [dict(item) for item in attempts]
    result: dict[str, object] = {
        "contract": {"name": PROOF_CONTRACT, "version": VERSION},
        "statement": {
            "revision": statement["revision"],
            "semantic_digest": statement["semantic_digest"],
        },
        "actor_principal": actor_principal.strip(),
        "examples": normalized_examples,
        "counterexamples": normalized_counterexamples,
        "lemma_map": normalized_lemmas,
        "budget": {
            "max_attempts": max_attempts,
            "attempts_used": len(normalized_attempts),
        },
        "attempts": normalized_attempts,
        "proof_gaps": [],
        "result": "candidate",
        "stop_reason": "workflow-complete",
        "next_steps": [
            "request independent proof review",
            "record human acceptance separately",
        ],
    }
    gaps = _retained_proof_gaps(normalized_attempts, normalized_lemmas)
    result["proof_gaps"] = gaps
    if user_stop:
        result.update(result="proof-gap", stop_reason="user-stopped", next_steps=[])
    elif execution_error:
        result.update(
            result="proof-gap",
            stop_reason="execution-failed",
            execution_error=execution_error,
            next_steps=[],
        )
    elif normalized_counterexamples or any(
        attempt.get("outcome") == "counterexample" for attempt in normalized_attempts
    ):
        result.update(
            result="proof-gap",
            stop_reason="counterexample-found",
            next_steps=["propose a new statement revision for user confirmation"],
        )
    elif any(
        attempt.get("outcome") == "candidate-proof" for attempt in normalized_attempts
    ):
        if gaps:
            result.update(result="proof-gap", stop_reason="proof-gap", next_steps=[])
        else:
            result.update(result="candidate", stop_reason="workflow-complete")
    elif len(normalized_attempts) == max_attempts:
        result.update(
            result="proof-gap",
            stop_reason="budget-exhausted",
            next_steps=[
                "user may authorize a new bounded invocation",
                "revise statement",
            ],
        )
    else:
        result.update(
            result="proof-gap",
            stop_reason="proof-gap",
            next_steps=["add a bounded proof attempt", "revise statement"],
        )
    result["run_digest"] = canonical_digest(
        {key: value for key, value in result.items() if key != "run_digest"}
    )
    issues = validate_math_proof(result, statement=statement)
    if issues:
        raise MathematicalWorkflowError(issues)
    return result


def validate_math_proof(
    value: object, *, statement: Mapping[str, Any] | None = None
) -> list[ValidationIssue]:
    record, issues = require_mapping(value, "proof.object", "/")
    if record is None:
        return issues
    allowed = {
        "contract",
        "statement",
        "actor_principal",
        "examples",
        "counterexamples",
        "lemma_map",
        "budget",
        "attempts",
        "proof_gaps",
        "result",
        "stop_reason",
        "next_steps",
        "execution_error",
        "run_digest",
    }
    issues.extend(reject_unknown(record, allowed, code="proof.field", location=""))
    if record.get("contract") != {"name": PROOF_CONTRACT, "version": VERSION}:
        issues.append(
            ValidationIssue(
                "proof.contract", "unsupported proof record contract", "/contract"
            )
        )
    issues.extend(
        require_nonempty_string(
            record.get("actor_principal"),
            code="proof.actor",
            location="/actor_principal",
        )
    )
    fixed_statement = record.get("statement")
    if (
        not isinstance(fixed_statement, Mapping)
        or type(fixed_statement.get("revision")) is not int
        or fixed_statement["revision"] < 1
        or set(fixed_statement) != {"revision", "semantic_digest"}
        or not isinstance(fixed_statement.get("semantic_digest"), str)
        or len(fixed_statement["semantic_digest"]) != 64
        or any(
            char not in "0123456789abcdef"
            for char in fixed_statement["semantic_digest"]
        )
    ):
        issues.append(
            ValidationIssue(
                "proof.statement",
                "proof must fix statement revision and digest",
                "/statement",
            )
        )
    elif statement is not None and fixed_statement != {
        "revision": statement.get("revision"),
        "semantic_digest": statement.get("semantic_digest"),
    }:
        issues.append(
            ValidationIssue(
                "proof.statement.mismatch",
                "proof is not bound to supplied statement",
                "/statement",
            )
        )
    for field in (
        "examples",
        "counterexamples",
        "attempts",
        "proof_gaps",
        "next_steps",
    ):
        if not isinstance(record.get(field), list):
            issues.append(
                ValidationIssue(
                    f"proof.{field}", f"{field} must be an array", f"/{field}"
                )
            )
    issues.extend(_validate_lemma_map(record.get("lemma_map")))
    budget = record.get("budget")
    if not isinstance(budget, Mapping):
        issues.append(
            ValidationIssue("proof.budget", "budget must be an object", "/budget")
        )
    else:
        maximum = budget.get("max_attempts")
        used = budget.get("attempts_used")
        if (
            any(
                isinstance(item, bool) or not isinstance(item, int) or item < 0
                for item in (maximum, used)
            )
            or maximum < 1
            or used > maximum
        ):
            issues.append(
                ValidationIssue("proof.budget", "attempt budget is invalid", "/budget")
            )
        elif isinstance(record.get("attempts"), list) and used != len(
            record["attempts"]
        ):
            issues.append(
                ValidationIssue(
                    "proof.budget.accounting",
                    "attempts_used must equal retained attempts",
                    "/budget/attempts_used",
                )
            )
    if isinstance(record.get("examples"), list):
        for index, example in enumerate(record["examples"]):
            if not isinstance(example, Mapping):
                issues.append(
                    ValidationIssue(
                        "proof.example",
                        "example must be an object",
                        f"/examples/{index}",
                    )
                )
    if isinstance(record.get("counterexamples"), list):
        for index, counterexample in enumerate(record["counterexamples"]):
            if not isinstance(counterexample, Mapping):
                issues.append(
                    ValidationIssue(
                        "proof.counterexample",
                        "counterexample must be an object",
                        f"/counterexamples/{index}",
                    )
                )
    if isinstance(record.get("attempts"), list):
        seen: set[str] = set()
        for index, attempt in enumerate(record["attempts"]):
            location = f"/attempts/{index}"
            if not isinstance(attempt, Mapping):
                issues.append(
                    ValidationIssue(
                        "proof.attempt", "attempt must be an object", location
                    )
                )
                continue
            identifier = attempt.get("id")
            if (
                not isinstance(identifier, str)
                or not identifier.strip()
                or identifier in seen
            ):
                issues.append(
                    ValidationIssue(
                        "proof.attempt.id",
                        "attempt id must be non-empty and unique",
                        f"{location}/id",
                    )
                )
            else:
                seen.add(identifier)
            if attempt.get("outcome") not in ATTEMPT_OUTCOMES:
                issues.append(
                    ValidationIssue(
                        "proof.attempt.outcome",
                        "unsupported attempt outcome",
                        f"{location}/outcome",
                    )
                )
            issues.extend(
                require_nonempty_string(
                    attempt.get("approach"),
                    code="proof.attempt.approach",
                    location=f"{location}/approach",
                )
            )
            issues.extend(
                require_nonempty_string(
                    attempt.get("argument"),
                    code="proof.attempt.argument",
                    location=f"{location}/argument",
                )
            )
            issues.extend(
                require_string_list(
                    attempt.get("gaps"),
                    code="proof.attempt.gaps",
                    location=f"{location}/gaps",
                )
            )
    retained_gaps = _retained_proof_gaps(
        record.get("attempts"), record.get("lemma_map")
    )
    if record.get("proof_gaps") != retained_gaps:
        issues.append(
            ValidationIssue(
                "proof.gaps.history",
                "proof_gaps must retain every unresolved obligation",
                "/proof_gaps",
            )
        )
    has_candidate = isinstance(record.get("attempts"), list) and any(
        isinstance(attempt, Mapping) and attempt.get("outcome") == "candidate-proof"
        for attempt in record["attempts"]
    )
    if record.get("result") in {"candidate", "reviewed"} and (
        retained_gaps
        or record.get("proof_gaps")
        or not has_candidate
        or record.get("counterexamples")
        or (
            isinstance(record.get("attempts"), list)
            and any(
                isinstance(attempt, Mapping)
                and attempt.get("outcome") == "counterexample"
                for attempt in record["attempts"]
            )
        )
        or record.get("execution_error")
        or record.get("stop_reason") != "workflow-complete"
    ):
        issues.append(
            ValidationIssue(
                "proof.result.inconsistent",
                "candidate requires a complete argument without unresolved gaps or stops",
                "/result",
            )
        )
    if (
        record.get("result") == "proof-gap"
        and record.get("stop_reason") == "workflow-complete"
    ):
        issues.append(
            ValidationIssue(
                "proof.result.inconsistent",
                "a proof gap cannot complete the workflow",
                "/stop_reason",
            )
        )
    if record.get("result") not in {"candidate", "proof-gap", "reviewed"}:
        issues.append(
            ValidationIssue(
                "proof.result", "unsupported mathematical result", "/result"
            )
        )
    if record.get("stop_reason") not in STOP_REASONS:
        issues.append(
            ValidationIssue(
                "proof.stop_reason", "unsupported stop reason", "/stop_reason"
            )
        )
    expected_digest = canonical_digest(
        {key: item for key, item in record.items() if key != "run_digest"}
    )
    if record.get("run_digest") != expected_digest:
        issues.append(
            ValidationIssue(
                "proof.digest",
                "run digest does not match retained history",
                "/run_digest",
            )
        )
    return issues


def _review_subject(
    statement: Mapping[str, Any], proof: Mapping[str, Any]
) -> dict[str, object]:
    return {
        "statement_revision": statement.get("revision"),
        "statement_digest": statement.get("semantic_digest"),
        "proof_digest": proof.get("run_digest"),
    }


def _review_input_manifest(
    project_root: Path,
    inputs: object,
    statement: Mapping[str, Any],
    proof: Mapping[str, Any],
) -> tuple[list[dict[str, object]], list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    manifest: list[dict[str, object]] = []
    if not isinstance(project_root, Path) or not project_root.is_dir():
        return [], [
            ValidationIssue(
                "review.inputs.root",
                "an existing project_root Path is required",
                "/inputs",
            )
        ]
    if not isinstance(inputs, list) or len(inputs) != 2:
        return [], [
            ValidationIssue(
                "review.inputs",
                "manifest must contain exactly statement and candidate proof",
                "/inputs",
            )
        ]
    seen_paths: set[str] = set()
    seen_files: set[tuple[int, int]] = set()
    roles: set[str] = set()
    for index, item in enumerate(inputs):
        location = f"/isolation_receipt/inputs/{index}"
        if not isinstance(item, Mapping):
            issues.append(
                ValidationIssue("review.inputs", "input must be an object", location)
            )
            continue
        path, digest = item.get("path"), item.get("sha256")
        if (
            not isinstance(path, str)
            or path != path.strip()
            or any(char in path for char in "?#:")
            or any(ord(char) < 32 for char in path)
        ):
            issues.append(
                ValidationIssue(
                    "review.inputs.path",
                    "input must be a safe project-relative file path",
                    location,
                )
            )
            continue
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            issues.append(
                ValidationIssue(
                    "review.inputs.digest", "input requires lowercase SHA-256", location
                )
            )
            continue
        try:
            resolved = resolve_under(project_root, path, must_exist=True)
            stat = resolved.stat()
            identity = (stat.st_dev, stat.st_ino)
            if path in seen_paths or identity in seen_files:
                issues.append(
                    ValidationIssue(
                        "review.inputs.duplicate", "duplicate input file", location
                    )
                )
                continue
            seen_paths.add(path)
            seen_files.add(identity)
            data = resolved.read_bytes()
        except (OSError, ValueError, RuntimeError) as exc:
            issues.append(
                ValidationIssue(
                    "review.inputs.file",
                    f"input is not a safe existing regular file: {exc}",
                    location,
                )
            )
            continue
        if hashlib.sha256(data).hexdigest() != digest:
            issues.append(
                ValidationIssue(
                    "review.inputs.bytes",
                    "SHA-256 differs from actual file bytes",
                    location,
                )
            )
            continue
        try:
            document = json.loads(data)
            # Canonical equality also distinguishes JSON booleans from integer revisions.
            document_digest = canonical_digest(document)
            if document_digest == canonical_digest(statement):
                role, contract, subject_digest = (
                    "statement",
                    STATEMENT_CONTRACT,
                    statement.get("semantic_digest"),
                )
            elif document_digest == canonical_digest(proof):
                role, contract, subject_digest = (
                    "candidate-proof",
                    PROOF_CONTRACT,
                    proof.get("run_digest"),
                )
            else:
                raise ValueError(
                    "file does not contain the exact supplied statement or proof"
                )
        except (ValueError, TypeError, UnicodeError) as exc:
            issues.append(ValidationIssue("review.inputs.subject", str(exc), location))
            continue
        if role in roles:
            issues.append(
                ValidationIssue(
                    "review.inputs.duplicate",
                    "subject appears more than once",
                    location,
                )
            )
        roles.add(role)
        manifest.append(
            {
                "path": path,
                "sha256": digest,
                "role": role,
                "target": {"kind": "git", "path": path},
                "type": {"name": contract, "version": VERSION},
                "revision": statement.get("revision"),
                "subject_digest": subject_digest,
            }
        )
    if roles != {"statement", "candidate-proof"}:
        issues.append(
            ValidationIssue(
                "review.inputs.subject",
                "manifest must fix both statement and candidate proof",
                "/isolation_receipt/inputs",
            )
        )
    return manifest, issues


def create_independent_review(
    *,
    project_root: Path,
    statement: Mapping[str, Any],
    proof: Mapping[str, Any],
    reviewer_principal: str,
    input_paths: Sequence[str],
    input_digests: Sequence[str],
    findings: Sequence[Mapping[str, Any]],
    verdict: str,
    conversation_history_included: bool = False,
    hidden_state_included: bool = False,
    fresh_context: bool = True,
    history_access: bool = False,
) -> dict[str, object]:
    issues = validate_statement(statement, require_confirmed=True)
    issues.extend(validate_math_proof(proof, statement=statement))
    if proof.get("result") != "candidate":
        issues.append(
            ValidationIssue(
                "review.proof",
                "review requires a candidate proof without gaps",
                "/proof",
            )
        )
    if issues:
        raise MathematicalWorkflowError(issues)
    actor = proof["actor_principal"]
    if (
        not isinstance(reviewer_principal, str)
        or not reviewer_principal.strip()
        or reviewer_principal.strip()
        in {actor.strip(), statement["confirmation"]["principal"].strip()}
    ):
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "review.independence",
                    "reviewer principal must differ from proof actor",
                    "/reviewer_principal",
                )
            ]
        )
    if verdict not in REVIEW_VERDICTS:
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "review.verdict", "unsupported review verdict", "/verdict"
                )
            ]
        )
    if (
        conversation_history_included is not False
        or hidden_state_included is not False
        or fresh_context is not True
        or history_access is not False
    ):
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "review.isolation",
                    "independent review cannot include conversation history or hidden state",
                    "/isolation",
                )
            ]
        )
    if len(input_paths) != len(input_digests) or not input_paths:
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "review.inputs",
                    "input paths and digests must be non-empty and aligned",
                    "/inputs",
                )
            ]
        )
    inputs, input_issues = _review_input_manifest(
        project_root,
        [
            {"path": path, "sha256": digest}
            for path, digest in zip(input_paths, input_digests, strict=True)
        ],
        statement,
        proof,
    )
    if input_issues:
        raise MathematicalWorkflowError(input_issues)
    isolation = {
        "mode": "fresh-context-fixed-inputs",
        "fresh_context": True,
        "history_access": False,
        "reviewer_principal": reviewer_principal.strip(),
        "proof_actor_principal": actor,
        "user_principal": statement["confirmation"]["principal"].strip(),
        "statement_revision": statement["revision"],
        "statement_digest": statement["semantic_digest"],
        "conversation_history_included": False,
        "hidden_state_included": False,
        "inputs": inputs,
        "input_manifest_digest": canonical_digest(inputs),
    }
    review: dict[str, object] = {
        "contract": {"name": REVIEW_CONTRACT, "version": VERSION},
        "subject": _review_subject(statement, proof),
        "proof_actor_principal": actor,
        "reviewer_principal": reviewer_principal.strip(),
        "dimension": "independent_review",
        "method": "fresh context review of fixed supplied inputs",
        "isolation_receipt": isolation,
        "findings": [dict(finding) for finding in findings],
        "verdict": verdict,
        "human_acceptance": False,
    }
    review["review_digest"] = canonical_digest(
        {key: item for key, item in review.items() if key != "review_digest"}
    )
    validation = validate_independent_review(
        review, project_root=project_root, statement=statement, proof=proof
    )
    if validation:
        raise MathematicalWorkflowError(validation)
    return review


def validate_independent_review(
    value: object,
    *,
    project_root: Path,
    statement: Mapping[str, Any] | None = None,
    proof: Mapping[str, Any] | None = None,
) -> list[ValidationIssue]:
    review, issues = require_mapping(value, "review.object", "/")
    if review is None:
        return issues
    allowed = {
        "contract",
        "subject",
        "proof_actor_principal",
        "reviewer_principal",
        "dimension",
        "method",
        "isolation_receipt",
        "findings",
        "verdict",
        "human_acceptance",
        "review_digest",
    }
    issues.extend(reject_unknown(review, allowed, code="review.field", location=""))
    if review.get("contract") != {"name": REVIEW_CONTRACT, "version": VERSION}:
        issues.append(
            ValidationIssue(
                "review.contract", "unsupported review contract", "/contract"
            )
        )
    if review.get("dimension") != "independent_review":
        issues.append(
            ValidationIssue(
                "review.dimension",
                "review dimension must be independent_review",
                "/dimension",
            )
        )
    actor = review.get("proof_actor_principal")
    reviewer = review.get("reviewer_principal")
    if (
        not isinstance(actor, str)
        or not actor.strip()
        or not isinstance(reviewer, str)
        or not reviewer.strip()
        or actor.strip() == reviewer.strip()
    ):
        issues.append(
            ValidationIssue(
                "review.independence",
                "reviewer principal must differ from proof actor",
                "/reviewer_principal",
            )
        )
    if review.get("human_acceptance") is not False:
        issues.append(
            ValidationIssue(
                "review.acceptance",
                "proof review cannot confer human acceptance",
                "/human_acceptance",
            )
        )
    if review.get("verdict") not in REVIEW_VERDICTS:
        issues.append(
            ValidationIssue("review.verdict", "unsupported review verdict", "/verdict")
        )
    if not isinstance(review.get("findings"), list) or any(
        not isinstance(finding, Mapping) for finding in review.get("findings", [])
    ):
        issues.append(
            ValidationIssue(
                "review.findings",
                "review findings must be an array of objects",
                "/findings",
            )
        )
    receipt = review.get("isolation_receipt")
    if not isinstance(receipt, Mapping):
        issues.append(
            ValidationIssue(
                "review.isolation",
                "isolation receipt is required",
                "/isolation_receipt",
            )
        )
    else:
        issues.extend(
            reject_unknown(
                receipt,
                {
                    "mode",
                    "fresh_context",
                    "history_access",
                    "reviewer_principal",
                    "proof_actor_principal",
                    "user_principal",
                    "statement_revision",
                    "statement_digest",
                    "conversation_history_included",
                    "hidden_state_included",
                    "inputs",
                    "input_manifest_digest",
                },
                code="review.isolation.field",
                location="/isolation_receipt",
            )
        )
        if (
            receipt.get("mode") != "fresh-context-fixed-inputs"
            or receipt.get("fresh_context") is not True
            or receipt.get("history_access") is not False
            or receipt.get("conversation_history_included") is not False
            or receipt.get("hidden_state_included") is not False
            or receipt.get("reviewer_principal") != reviewer
            or receipt.get("proof_actor_principal") != actor
        ):
            issues.append(
                ValidationIssue(
                    "review.isolation",
                    "review requires a bound fresh context with history access denied",
                    "/isolation_receipt",
                )
            )
        inputs = receipt.get("inputs")
        if receipt.get("input_manifest_digest") != canonical_digest(inputs):
            issues.append(
                ValidationIssue(
                    "review.isolation.digest",
                    "isolation input manifest digest is invalid",
                    "/isolation_receipt/input_manifest_digest",
                )
            )
    if not isinstance(statement, Mapping) or not isinstance(proof, Mapping):
        issues.append(
            ValidationIssue(
                "review.subject.missing",
                "supplied statement and proof are required for runtime verification",
                "/subject",
            )
        )
    else:
        issues.extend(validate_statement(statement, require_confirmed=True))
        issues.extend(validate_math_proof(proof, statement=statement))
        if proof.get("result") != "candidate":
            issues.append(
                ValidationIssue(
                    "review.proof",
                    "review requires a candidate proof without gaps",
                    "/subject",
                )
            )
        confirmation = statement.get("confirmation")
        user = (
            confirmation.get("principal") if isinstance(confirmation, Mapping) else None
        )
        if (
            not isinstance(user, str)
            or not user.strip()
            or (isinstance(reviewer, str) and reviewer.strip() == user.strip())
        ):
            issues.append(
                ValidationIssue(
                    "review.independence",
                    "reviewer must differ from the confirming user",
                    "/reviewer_principal",
                )
            )
        if canonical_digest(review.get("subject")) != canonical_digest(
            _review_subject(statement, proof)
        ):
            issues.append(
                ValidationIssue(
                    "review.subject",
                    "review does not fix supplied statement revision and proof",
                    "/subject",
                )
            )
        if actor != proof.get("actor_principal"):
            issues.append(
                ValidationIssue(
                    "review.actor",
                    "review proof actor differs from proof record",
                    "/proof_actor_principal",
                )
            )
        if isinstance(receipt, Mapping):
            if (
                receipt.get("user_principal")
                != (user.strip() if isinstance(user, str) else None)
                or type(receipt.get("statement_revision")) is not int
                or receipt.get("statement_revision") != statement.get("revision")
                or receipt.get("statement_digest") != statement.get("semantic_digest")
            ):
                issues.append(
                    ValidationIssue(
                        "review.isolation",
                        "receipt principal and statement identity are stale",
                        "/isolation_receipt",
                    )
                )
            manifest, input_issues = _review_input_manifest(
                project_root, receipt.get("inputs"), statement, proof
            )
            issues.extend(input_issues)
            if not input_issues and canonical_digest(
                receipt.get("inputs")
            ) != canonical_digest(manifest):
                issues.append(
                    ValidationIssue(
                        "review.inputs.binding",
                        "manifest typed targets and revisions do not match actual supplied subjects",
                        "/isolation_receipt/inputs",
                    )
                )
    expected_digest = canonical_digest(
        {key: item for key, item in review.items() if key != "review_digest"}
    )
    if review.get("review_digest") != expected_digest:
        issues.append(
            ValidationIssue(
                "review.digest",
                "review digest does not match receipt and findings",
                "/review_digest",
            )
        )
    return issues
