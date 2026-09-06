"""Deterministic mathematical-proof and optional Lean workflow primitives.

This package is intentionally independent from the shared CLI facade.  The facade may
project these primitives later, while leaf tests can exercise the complete workflow
semantics directly.
"""

from .lean import (
    CommandResult,
    LeanRunResult,
    audit_lean_project,
    compare_trusted_statement,
    kernel_replay,
    run_lean_formalize,
    validate_formalization_metadata,
)
from .proof import (
    MathematicalWorkflowError,
    confirm_statement,
    create_independent_review,
    create_statement_candidate,
    revise_statement,
    run_math_proof,
    validate_independent_review,
    validate_math_proof,
    validate_statement,
)
from .records import (
    ValidationIssue,
    canonical_digest,
    canonical_json_bytes,
    file_sha256,
)

__all__ = [
    "CommandResult",
    "LeanRunResult",
    "MathematicalWorkflowError",
    "ValidationIssue",
    "audit_lean_project",
    "canonical_digest",
    "canonical_json_bytes",
    "compare_trusted_statement",
    "confirm_statement",
    "create_independent_review",
    "create_statement_candidate",
    "file_sha256",
    "kernel_replay",
    "revise_statement",
    "run_lean_formalize",
    "run_math_proof",
    "validate_formalization_metadata",
    "validate_independent_review",
    "validate_math_proof",
    "validate_statement",
]
