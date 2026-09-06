from __future__ import annotations

import tomllib
import json
import os
import tempfile
import uuid
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from .proof import (
    MathematicalWorkflowError,
    validate_independent_review,
    validate_math_proof,
    validate_statement,
)
from .records import (
    ValidationIssue,
    canonical_digest,
    file_sha256,
    read_json,
    resolve_under,
    write_json_exclusive,
)

LEAN_CONTRACT = "research-os/lean-formalization-run"
VERSION = "1.0.0"
LEAN_RESULTS = {"verified", "not-verified", "statement-mismatch"}
LEAN_STOP_REASONS = {
    "workflow-complete",
    "proof-gap",
    "tooling-blocked",
    "budget-exhausted",
    "execution-failed",
    "user-stopped",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
TOOLCHAIN_PATTERN = re.compile(r"^[A-Za-z0-9_.:/@+-]+$")
DECLARATION_PATTERN = re.compile(
    r"^\s*(?:theorem|lemma|example)\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*:\s*(.*?)\s*:=\s*by\s*$"
)
FORBIDDEN_TOKEN_PATTERNS = {
    "sorry": re.compile(r"\bsorry\b"),
    "admit": re.compile(r"\badmit\b"),
    "placeholder": re.compile(r"\b(?:TODO|FIXME|PLACEHOLDER)\b", re.IGNORECASE),
    "unsafe": re.compile(r"\bunsafe\b"),
    "metaprogram": re.compile(
        r"\b(?:elab|macro|syntax|run_meta|initialize|builtin_initialize|implemented_by|extern)\b|#(?:eval|check_failure)\b"
    ),
}
DECLARED_AXIOM_PATTERN = re.compile(
    r"^\s*(?:axiom|constant)\s+([A-Za-z_][A-Za-z0-9_'.]*)\b", re.MULTILINE
)
IMPORT_PATTERN = re.compile(
    r"^\s*(?:(?:public|private)\s+)?import\s+([^\n]+)$", re.MULTILINE
)
PRINT_AXIOMS_PATTERN = re.compile(
    r"^\s*#print\s+axioms\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$", re.MULTILINE
)
AXIOMS_OUTPUT_PATTERN = re.compile(
    r"depends on axioms:\s*\[([^\]]*)\]", re.IGNORECASE | re.DOTALL
)


@dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    cwd: str
    returncode: int
    stdout: str
    stderr: str

    def as_dict(self) -> dict[str, object]:
        return {
            "argv": list(self.argv),
            "cwd": self.cwd,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass(frozen=True)
class LeanRunResult:
    exit_code: int
    report: dict[str, object]


class Runner(Protocol):
    def __call__(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str] | None = None,
        timeout: int = 120,
    ) -> CommandResult: ...


def _run_command(
    argv: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
    timeout: int = 120,
) -> CommandResult:
    completed = subprocess.run(
        list(argv),
        cwd=cwd,
        env=dict(env) if env is not None else None,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    return CommandResult(
        tuple(argv), str(cwd), completed.returncode, completed.stdout, completed.stderr
    )


def _without_comments(text: str) -> str:
    result: list[str] = []
    index = 0
    block_depth = 0
    in_string = False
    escaped = False
    while index < len(text):
        if block_depth:
            if text.startswith("/-", index):
                block_depth += 1
                index += 2
            elif text.startswith("-/", index):
                block_depth -= 1
                index += 2
            else:
                if text[index] == "\n":
                    result.append("\n")
                index += 1
            continue
        if in_string:
            character = text[index]
            result.append(character)
            index += 1
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if text.startswith("--", index):
            newline = text.find("\n", index)
            if newline == -1:
                break
            result.append("\n")
            index = newline + 1
            continue
        if text.startswith("/-", index):
            block_depth = 1
            index += 2
            continue
        character = text[index]
        result.append(character)
        index += 1
        if character == '"':
            in_string = True
    return "".join(result)


def _normalize_lean_statement(statement: str) -> str:
    return "".join(statement.split())


def extract_declaration_statement(source: str, declaration: str) -> str | None:
    clean = _without_comments(source)
    lines = clean.splitlines()
    collecting = False
    fragments: list[str] = []
    for line in lines:
        match = DECLARATION_PATTERN.match(line)
        if match and match.group(1) == declaration:
            return _normalize_lean_statement(match.group(2))
        prefix = re.match(
            rf"^\s*(?:theorem|lemma|example)\s+{re.escape(declaration)}\s*:\s*(.*)$",
            line,
        )
        if prefix:
            collecting = True
            fragments.append(prefix.group(1))
            if ":= by" in prefix.group(1):
                break
            continue
        if collecting:
            fragments.append(line)
            if ":= by" in line:
                break
    if not collecting:
        return None
    combined = " ".join(fragments)
    statement, separator, _ = combined.partition(":= by")
    return _normalize_lean_statement(statement) if separator else None


def compare_trusted_statement(
    project: Path, metadata: Mapping[str, Any]
) -> tuple[dict[str, object], list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    comparator = metadata.get("comparator")
    if not isinstance(comparator, Mapping):
        return {"status": "statement-mismatch"}, [
            ValidationIssue(
                "lean.comparator.config",
                "comparator metadata is required",
                "/comparator",
            )
        ]
    declaration = comparator.get("declaration")
    trusted_file = comparator.get("trusted_file")
    solution_file = comparator.get("solution_file")
    if not all(
        isinstance(item, str) and item
        for item in (declaration, trusted_file, solution_file)
    ):
        return {"status": "statement-mismatch"}, [
            ValidationIssue(
                "lean.comparator.config",
                "comparator file and declaration fields are required",
                "/comparator",
            )
        ]
    try:
        trusted_path = resolve_under(project, trusted_file, must_exist=True)
        solution_path = resolve_under(project, solution_file, must_exist=True)
        trusted_source = trusted_path.read_text(encoding="utf-8")
        solution_source = solution_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return {"status": "statement-mismatch"}, [
            ValidationIssue("lean.comparator.read", str(exc), "/comparator")
        ]
    trusted_statement = extract_declaration_statement(trusted_source, declaration)
    solution_statement = extract_declaration_statement(solution_source, declaration)
    if trusted_statement is None:
        issues.append(
            ValidationIssue(
                "lean.comparator.trusted_missing",
                "trusted declaration was not found",
                f"/{trusted_file}",
            )
        )
    if solution_statement is None:
        issues.append(
            ValidationIssue(
                "lean.comparator.solution_missing",
                "solution declaration was not found",
                f"/{solution_file}",
            )
        )
    expected = comparator.get("normalized_statement_sha256")
    if trusted_statement is not None:
        actual = canonical_digest(trusted_statement)
        if expected != actual:
            issues.append(
                ValidationIssue(
                    "lean.comparator.trusted_digest",
                    "trusted statement differs from locked comparator digest",
                    "/comparator/normalized_statement_sha256",
                )
            )
    else:
        actual = None
    if (
        trusted_statement is not None
        and solution_statement is not None
        and trusted_statement != solution_statement
    ):
        issues.append(
            ValidationIssue(
                "lean.statement-mismatch",
                "solution declaration does not exactly match trusted statement",
                f"/{solution_file}",
            )
        )
    return {
        "status": "match" if not issues else "statement-mismatch",
        "declaration": declaration,
        "trusted_normalized_statement": trusted_statement,
        "solution_normalized_statement": solution_statement,
        "normalized_statement_sha256": actual,
    }, issues


def _imports(clean: str) -> list[str]:
    return [module for line in IMPORT_PATTERN.findall(clean) for module in line.split()]


def _lean_sources(project: Path) -> list[str]:
    # Conservative closure: every project Lean file may be a Lake build target.
    # Package sources are included; only generated caches and retained runs are not.
    return sorted(
        path.relative_to(project).as_posix()
        for path in project.rglob("*.lean")
        if not any(
            part in {".git", ".lean-runs"} for part in path.relative_to(project).parts
        )
        and ".lake/build/" not in path.relative_to(project).as_posix()
    )


def _dependency_issues(
    project: Path, metadata: Mapping[str, Any]
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        manifest_path = project / "lake-manifest.json"
        manifest = (
            read_json(resolve_under(project, "lake-manifest.json", must_exist=True))
            if manifest_path.exists()
            else {"packages": []}
        )
        packages = manifest.get("packages", [])
        actual = sorted(
            (item["name"], item["rev"])
            for item in packages
            if item.get("type") == "git"
        )
        expected = sorted(
            (item["name"], item["revision"])
            for item in metadata.get("dependencies", [])
            if isinstance(item, Mapping)
        )
        if (
            len(actual) != len(packages)
            or actual != expected
            or any(
                not re.fullmatch(r"[0-9a-f]{40}", revision) for _, revision in expected
            )
        ):
            raise ValueError(
                "dependency manifest must exactly match full locked git revisions; path dependencies are unsupported"
            )
        config = project / "lakefile.toml"
        if config.exists():
            parsed = tomllib.loads(
                resolve_under(project, "lakefile.toml", must_exist=True).read_text()
            )
            requirements = parsed.get("require", [])
            if any("path" in item for item in requirements) or {
                item["name"] for item in requirements
            } - {name for name, _ in expected}:
                raise ValueError(
                    "Lake requirements are not covered by locked dependencies"
                )
        if (project / "lakefile.lean").exists():
            raise ValueError(
                "executable lakefile.lean is outside the auditable TOML build profile"
            )
        for name, revision in expected:
            checkout = resolve_under(project, f".lake/packages/{name}")
            if not (checkout / ".git").exists():
                raise ValueError(
                    f"dependency {name} checkout revision cannot be independently verified"
                )
            head = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"],
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            if head.returncode or head.stdout.strip() != revision:
                raise ValueError(
                    f"dependency {name} actual checkout revision differs from lock"
                )
            if not any(
                path.startswith(f".lake/packages/{name}/")
                for path in _lean_sources(project)
            ):
                raise ValueError(
                    f"dependency {name} sources are unavailable for closure audit"
                )
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        issues.append(
            ValidationIssue("lean.dependencies.manifest", str(exc), "/dependencies")
        )
    return issues


def validate_formalization_metadata(
    project: Path, metadata: object
) -> list[ValidationIssue]:
    if not isinstance(metadata, Mapping):
        return [
            ValidationIssue(
                "lean.metadata.object", "formalization metadata must be an object", "/"
            )
        ]
    issues: list[ValidationIssue] = []
    required = {
        "contract",
        "statement",
        "proof",
        "review",
        "authorization",
        "toolchain",
        "dependencies",
        "sources",
        "allowed_imports",
        "permitted_axioms",
        "comparator",
        "replay",
        "claim_boundary",
    }
    missing = sorted(required - set(metadata))
    issues.extend(
        ValidationIssue(
            "lean.metadata.required", f"missing field: {field}", f"/{field}"
        )
        for field in missing
    )
    unknown = sorted(set(metadata) - required)
    issues.extend(
        ValidationIssue("lean.metadata.field", f"unknown field: {field}", f"/{field}")
        for field in unknown
    )
    if metadata.get("contract") != {
        "name": "research-os/lean-formalization",
        "version": VERSION,
    }:
        issues.append(
            ValidationIssue(
                "lean.metadata.contract",
                "unsupported formalization contract",
                "/contract",
            )
        )
    for field in ("statement", "authorization"):
        value = metadata.get(field)
        if (
            not isinstance(value, Mapping)
            or type(value.get("revision")) is not int
            or value["revision"] < 1
        ):
            issues.append(
                ValidationIssue(
                    "lean.revision.type",
                    "revision must be a positive integer, never bool",
                    f"/{field}/revision",
                )
            )
    toolchain = metadata.get("toolchain")
    if not isinstance(toolchain, Mapping):
        issues.append(
            ValidationIssue(
                "lean.toolchain", "toolchain metadata is required", "/toolchain"
            )
        )
    else:
        lean_version = toolchain.get("lean")
        lake_version = toolchain.get("lake")
        toolchain_file = toolchain.get("file")
        if not isinstance(lean_version, str) or not TOOLCHAIN_PATTERN.fullmatch(
            lean_version
        ):
            issues.append(
                ValidationIssue(
                    "lean.toolchain.lean",
                    "Lean toolchain identifier must be exact",
                    "/toolchain/lean",
                )
            )
        if not isinstance(lake_version, str) or not lake_version.strip():
            issues.append(
                ValidationIssue(
                    "lean.toolchain.lake",
                    "Lake version must be fixed",
                    "/toolchain/lake",
                )
            )
        try:
            path = resolve_under(project, toolchain_file, must_exist=True)
            if path.read_text(encoding="utf-8").strip() != lean_version:
                issues.append(
                    ValidationIssue(
                        "lean.toolchain.lock",
                        "lean-toolchain content differs from metadata",
                        "/toolchain/file",
                    )
                )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            issues.append(
                ValidationIssue("lean.toolchain.file", str(exc), "/toolchain/file")
            )
    dependencies = metadata.get("dependencies")
    if isinstance(dependencies, list) and dependencies:
        issues.append(
            ValidationIssue(
                "lean.dependencies.unsupported",
                "P0 isolated-rebuild supports no external dependencies",
                "/dependencies",
            )
        )
    if not isinstance(dependencies, list):
        issues.append(
            ValidationIssue(
                "lean.dependencies", "dependencies must be an array", "/dependencies"
            )
        )
    else:
        for index, dependency in enumerate(dependencies):
            if (
                not isinstance(dependency, Mapping)
                or not isinstance(dependency.get("name"), str)
                or not dependency["name"]
                or not isinstance(dependency.get("revision"), str)
                or not dependency["revision"]
                or dependency["revision"] in {"main", "master", "latest", "HEAD"}
            ):
                issues.append(
                    ValidationIssue(
                        "lean.dependency.lock",
                        "each dependency requires a non-floating exact revision",
                        f"/dependencies/{index}",
                    )
                )
    issues.extend(_dependency_issues(project, metadata))
    sources = metadata.get("sources")
    if not isinstance(sources, list) or not sources:
        issues.append(
            ValidationIssue(
                "lean.sources", "sources must be a non-empty array", "/sources"
            )
        )
    else:
        seen_paths: set[str] = set()
        for index, source in enumerate(sources):
            if not isinstance(source, Mapping):
                issues.append(
                    ValidationIssue(
                        "lean.source",
                        "source entry must be an object",
                        f"/sources/{index}",
                    )
                )
                continue
            source_path = source.get("path")
            if isinstance(source_path, str) and (
                Path(source_path).suffix
                in {".olean", ".ilean", ".o", ".a", ".so", ".dylib", ".c"}
                or any(
                    part in {"build", ".cache", "cache"}
                    for part in Path(source_path).parts
                )
            ):
                issues.append(
                    ValidationIssue(
                        "lean.source.compiled",
                        "build/cache/compiled artifacts cannot be source inputs",
                        f"/sources/{index}",
                    )
                )
            if source_path in seen_paths:
                issues.append(
                    ValidationIssue(
                        "lean.source.duplicate",
                        "source paths must be unique",
                        f"/sources/{index}/path",
                    )
                )
            elif isinstance(source_path, str):
                seen_paths.add(source_path)
            try:
                path = resolve_under(project, source_path, must_exist=True)
            except (OSError, ValueError) as exc:
                issues.append(
                    ValidationIssue(
                        "lean.source.path", str(exc), f"/sources/{index}/path"
                    )
                )
                continue
            source_digest = source.get("sha256")
            if (
                not isinstance(source_digest, str)
                or not SHA256_PATTERN.fullmatch(source_digest)
                or source_digest != file_sha256(path)
            ):
                issues.append(
                    ValidationIssue(
                        "lean.source.digest",
                        "source digest differs from lock",
                        f"/sources/{index}/sha256",
                    )
                )
    comparator = metadata.get("comparator")
    if not isinstance(comparator, Mapping):
        issues.append(
            ValidationIssue(
                "lean.comparator.config",
                "comparator metadata is required",
                "/comparator",
            )
        )
    else:
        allowed_comparator_fields = {
            "trusted_file",
            "solution_file",
            "declaration",
            "normalized_statement_sha256",
        }
        if set(comparator) != allowed_comparator_fields:
            issues.append(
                ValidationIssue(
                    "lean.comparator.config",
                    "comparator fields must be exact",
                    "/comparator",
                )
            )
        comparator_digest = comparator.get("normalized_statement_sha256")
        if not isinstance(comparator_digest, str) or not SHA256_PATTERN.fullmatch(
            comparator_digest
        ):
            issues.append(
                ValidationIssue(
                    "lean.comparator.digest",
                    "comparator statement digest must be lowercase SHA-256",
                    "/comparator/normalized_statement_sha256",
                )
            )
        if isinstance(sources, list):
            locked_paths = {
                source.get("path") for source in sources if isinstance(source, Mapping)
            }
            for field in ("trusted_file", "solution_file"):
                if comparator.get(field) not in locked_paths:
                    issues.append(
                        ValidationIssue(
                            "lean.comparator.source",
                            f"{field} must be present in the locked source set",
                            f"/comparator/{field}",
                        )
                    )
    discovered = set(_lean_sources(project))
    discovered.update(
        name
        for name in (
            "lakefile.toml",
            "lakefile.lean",
            "lake-manifest.json",
            "lean-toolchain",
        )
        if (project / name).exists()
    )
    discovered.update(
        path.relative_to(project).as_posix()
        for path in project.rglob("*")
        if path.is_file()
        and path.name in {"lakefile.toml", "lake-manifest.json", "lean-toolchain"}
        and ".lean-runs" not in path.parts
    )
    locked = (
        {
            entry.get("path")
            for entry in sources
            if isinstance(entry, Mapping) and isinstance(entry.get("path"), str)
        }
        if isinstance(sources, list)
        else set()
    )
    for relative in sorted(discovered - locked):
        issues.append(
            ValidationIssue(
                "lean.sources.coverage",
                "build/import source is absent from metadata.sources",
                f"/{relative}",
            )
        )
    comparator = metadata.get("comparator", {})
    if isinstance(comparator, Mapping):
        for field in ("trusted_file", "solution_file"):
            if comparator.get(field) not in locked:
                issues.append(
                    ValidationIssue(
                        "lean.comparator.source_lock",
                        "comparator source must be locked",
                        f"/comparator/{field}",
                    )
                )
    for field in ("allowed_imports", "permitted_axioms"):
        value = metadata.get(field)
        if not isinstance(value, list) or any(
            not isinstance(item, str) or not item for item in value
        ):
            issues.append(
                ValidationIssue(
                    f"lean.{field}",
                    f"{field} must be an array of non-empty strings",
                    f"/{field}",
                )
            )
    authorization = metadata.get("authorization")
    statement = metadata.get("statement")
    if not isinstance(authorization, Mapping) or not isinstance(statement, Mapping):
        issues.append(
            ValidationIssue(
                "lean.authorization",
                "authorization and statement bindings are required",
                "/authorization",
            )
        )
    else:
        revision = statement.get("revision")
        digest = statement.get("semantic_digest")
        expected_phrase = f"AUTHORIZE LEAN r{revision} {digest}"
        if (
            authorization.get("phrase") != expected_phrase
            or authorization.get("revision") != revision
            or authorization.get("statement_digest") != digest
            or not isinstance(authorization.get("principal"), str)
            or not authorization["principal"].strip()
        ):
            issues.append(
                ValidationIssue(
                    "lean.authorization",
                    "Lean authorization is absent or stale",
                    "/authorization",
                )
            )
    replay = metadata.get("replay")
    if (
        not isinstance(replay, Mapping)
        or set(replay) != {"command", "independent_principal"}
        or replay.get("command") != ["lake", "build"]
        or not isinstance(replay.get("independent_principal"), str)
        or not replay["independent_principal"].strip()
    ):
        issues.append(
            ValidationIssue(
                "lean.replay.config",
                "replay must fix `lake build` and an independent principal",
                "/replay",
            )
        )
    boundary = metadata.get("claim_boundary")
    required_boundary = "Kernel pass covers only the fixed Lean statement in the recorded trusted base; it does not establish natural-language alignment, paper correctness, research significance, or human acceptance."
    if boundary != required_boundary:
        issues.append(
            ValidationIssue(
                "lean.claim_boundary",
                "formal verification claim boundary must be exact",
                "/claim_boundary",
            )
        )
    return issues


def audit_lean_project(
    project: Path, metadata: Mapping[str, Any]
) -> tuple[dict[str, object], list[ValidationIssue]]:
    issues = validate_formalization_metadata(project, metadata)
    source_audits: list[dict[str, object]] = []
    allowed_imports = (
        set(metadata.get("allowed_imports", []))
        if isinstance(metadata.get("allowed_imports"), list)
        else set()
    )
    permitted_axioms = (
        set(metadata.get("permitted_axioms", []))
        if isinstance(metadata.get("permitted_axioms"), list)
        else set()
    )
    sources = [
        {"path": relative}
        for relative in sorted(
            set(_lean_sources(project))
            | {
                entry["path"]
                for entry in metadata.get("sources", [])
                if isinstance(entry, Mapping)
                and isinstance(entry.get("path"), str)
                and entry["path"].endswith(".lean")
            }
        )
    ]
    if isinstance(sources, list):
        for source_entry in sources:
            if not isinstance(source_entry, Mapping):
                continue
            relative = source_entry.get("path")
            try:
                path = resolve_under(project, relative, must_exist=True)
                clean = _without_comments(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, ValueError):
                continue
            findings: dict[str, object] = {
                "path": relative,
                "sha256": file_sha256(path),
                "forbidden_tokens": [],
                "imports": _imports(clean),
                "declared_axioms": DECLARED_AXIOM_PATTERN.findall(clean),
                "print_axioms": PRINT_AXIOMS_PATTERN.findall(clean),
            }
            forbidden: list[str] = []
            for name, pattern in FORBIDDEN_TOKEN_PATTERNS.items():
                if pattern.search(clean):
                    forbidden.append(name)
                    issues.append(
                        ValidationIssue(
                            f"lean.{name}",
                            f"forbidden {name} token in Lean source",
                            f"/{relative}",
                        )
                    )
            findings["forbidden_tokens"] = forbidden
            for imported in findings["imports"]:
                if imported not in allowed_imports:
                    issues.append(
                        ValidationIssue(
                            "lean.import",
                            f"unapproved import: {imported}",
                            f"/{relative}",
                        )
                    )
            for axiom in findings["declared_axioms"]:
                if axiom not in permitted_axioms:
                    issues.append(
                        ValidationIssue(
                            "lean.axiom.declared",
                            f"unapproved declared axiom: {axiom}",
                            f"/{relative}",
                        )
                    )
            source_audits.append(findings)
    comparator, comparator_issues = compare_trusted_statement(project, metadata)
    issues.extend(comparator_issues)
    return {
        "metadata": "pass"
        if not any(
            issue.code.startswith("lean.metadata")
            or issue.code.startswith("lean.toolchain")
            or issue.code.startswith("lean.depend")
            or issue.code.startswith("lean.source")
            or issue.code.startswith("lean.authorization")
            or issue.code.startswith("lean.replay")
            or issue.code.startswith("lean.claim")
            for issue in issues
        )
        else "fail",
        "sources": source_audits,
        "comparator": comparator,
        "verdict": "pass" if not issues else "fail",
    }, issues


def _parse_kernel_axioms(output: str, declaration: str) -> set[str] | None:
    pattern = re.compile(
        r"^'"
        + re.escape(declaration)
        + r"' (?:does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])\s*$",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(output))
    if len(matches) != 1:
        return None
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_'.]*", matches[0].group(1) or ""))


def _kernel_probe(
    project: Path,
    metadata: Mapping[str, Any],
    tooling: Mapping[str, Any],
    runner: Runner,
    environment: Mapping[str, str] | None,
) -> tuple[dict[str, object], list[ValidationIssue]]:
    comparator = metadata["comparator"]
    declaration = comparator["declaration"]
    issues: list[ValidationIssue] = []
    report: dict[str, object] = {
        "declaration": declaration,
        "method": "kernel-elaborated-Expr-exact-comparison",
    }
    types: list[str] = []
    locked_inputs = _input_manifest(project, metadata)
    # P0 supports only closed Nat/Eq formulas over a fixed toolchain trusted base.
    # Equal names in different custom environments are not semantic equality.
    trusted_constants = {
        "Nat",
        "Nat.add",
        "Nat.zero",
        "Nat.succ",
        "Eq",
        "OfNat.ofNat",
        "instOfNatNat",
        "HAdd.hAdd",
        "instHAdd",
        "instAddNat",
    }
    with tempfile.TemporaryDirectory(prefix="research-os-lean-probe-") as directory:
        for label, field in (
            ("trusted", "trusted_file"),
            ("solution", "solution_file"),
        ):
            module = comparator[field].removesuffix(".lean").replace("/", ".")
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", module) or not re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_'.]*", declaration
            ):
                return report, [
                    ValidationIssue(
                        "lean.comparator.name",
                        "unsupported module or declaration name",
                        "/comparator",
                    )
                ]
            source = (
                f"import Lean\nimport {module}\n"
                "open Lean in\nrun_meta do\n"
                f"  let info ← getConstInfo `{declaration}\n"
                '  logInfo ("ROS_TYPE_JSON:" ++ (Json.str (reprStr info.type)).compress)\n'
                "  let names := info.type.getUsedConstants\n"
                '  logInfo ("ROS_CONSTANTS_JSON:" ++ (toJson (names.toList.map Name.toString)).compress)\n'
                f"#print axioms {declaration}\n"
            )
            path = Path(directory) / f"{label}-Probe.lean"
            with path.open("x") as stream:
                stream.write(source)
            if _input_manifest(project, metadata) != locked_inputs:
                issues.append(
                    ValidationIssue(
                        "lean.stage.drift",
                        "input changed before kernel probe",
                        "/comparator",
                    )
                )
                break
            command = runner(
                [tooling["lake_executable"], "env", "lean", str(path)],
                cwd=project,
                env=environment,
            )
            if _input_manifest(project, metadata) != locked_inputs:
                issues.append(
                    ValidationIssue(
                        "lean.stage.drift",
                        "input changed during kernel probe",
                        "/comparator",
                    )
                )
                break
            report[label] = {
                "command": command.as_dict(),
                "probe_source": source,
                "probe_sha256": file_sha256(path),
            }
            values = re.findall(r'^ROS_TYPE_JSON:(".*")$', command.stdout, re.MULTILINE)
            if command.returncode or len(values) != 1:
                issues.append(
                    ValidationIssue(
                        "lean.comparator.kernel",
                        "kernel type probe failed or output is ambiguous",
                        f"/comparator/{field}",
                    )
                )
            else:
                try:
                    types.append(json.loads(values[0]))
                except ValueError:
                    issues.append(
                        ValidationIssue(
                            "lean.comparator.kernel",
                            "invalid kernel type serialization",
                            "/comparator",
                        )
                    )
            constants_lines = re.findall(
                r"^ROS_CONSTANTS_JSON:(\[.*\])$", command.stdout, re.MULTILINE
            )
            try:
                constants = (
                    json.loads(constants_lines[0])
                    if len(constants_lines) == 1
                    else None
                )
                if (
                    not isinstance(constants, list)
                    or not constants
                    or any(
                        not isinstance(name, str) or name not in trusted_constants
                        for name in constants
                    )
                ):
                    issues.append(
                        ValidationIssue(
                            "lean.comparator.trusted_base",
                            "custom type definitions are outside the closed builtin kernel comparator profile",
                            "/comparator",
                        )
                    )
                report[label]["type_constants"] = constants
            except ValueError:
                issues.append(
                    ValidationIssue(
                        "lean.comparator.trusted_base",
                        "invalid type closure output",
                        "/comparator",
                    )
                )
            axioms = _parse_kernel_axioms(command.stdout, declaration)
            if axioms is None:
                issues.append(
                    ValidationIssue(
                        "lean.axiom.output",
                        "expected exactly one axiom report for fixed target",
                        "/comparator",
                    )
                )
            elif not axioms.issubset(set(metadata["permitted_axioms"])):
                issues.append(
                    ValidationIssue(
                        "lean.axiom.kernel",
                        f"unapproved target axioms: {sorted(axioms)}",
                        "/permitted_axioms",
                    )
                )
            report[label]["reported_axioms"] = (
                sorted(axioms) if axioms is not None else None
            )
    if len(types) == 2 and types[0] != types[1]:
        issues.append(
            ValidationIssue(
                "lean.statement-mismatch",
                "kernel elaborated declaration types differ",
                "/comparator",
            )
        )
    report["type_digest"] = (
        canonical_digest(types[0]) if len(types) == 2 and types[0] == types[1] else None
    )
    return report, issues


def _input_manifest(project: Path, metadata: Mapping[str, Any]) -> list[dict[str, str]]:
    paths = {entry["path"] for entry in metadata["sources"]}
    paths.update(_lean_sources(project))
    paths.update(
        name
        for name in (
            "lakefile.toml",
            "lakefile.lean",
            "lake-manifest.json",
            "lean-toolchain",
        )
        if (project / name).exists()
    )
    return [
        {
            "path": relative,
            "sha256": file_sha256(resolve_under(project, relative, must_exist=True)),
        }
        for relative in sorted(paths)
    ]


def _copy_inputs(
    project: Path, target: Path, manifest: Sequence[Mapping[str, str]]
) -> None:
    target.mkdir(parents=True, exist_ok=False)
    for entry in manifest:
        source = resolve_under(project, entry["path"], must_exist=True)
        destination = resolve_under(target, entry["path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(source.read_bytes())
        if file_sha256(destination) != entry["sha256"]:
            raise ValueError("input changed while copying snapshot")


def kernel_replay(
    project: Path,
    metadata: Mapping[str, Any],
    *,
    runner: Runner = _run_command,
    principal: str | None = None,
    environment: Mapping[str, str] | None = None,
    excluded_principals: Sequence[str] = (),
) -> tuple[dict[str, object], list[ValidationIssue]]:
    audit, issues = audit_lean_project(project, metadata)
    replay = metadata.get("replay", {})
    replay_principal = principal or replay.get("independent_principal")
    forbidden = {
        metadata.get("authorization", {}).get("principal"),
        *excluded_principals,
    }
    if (
        not isinstance(replay_principal, str)
        or not replay_principal.strip()
        or replay_principal in forbidden
        or replay_principal != replay.get("independent_principal")
    ):
        issues.append(
            ValidationIssue(
                "lean.replay.independence",
                "replay principal must be fixed and different from authors and authorizer",
                "/replay",
            )
        )
    if issues:
        return {"verdict": "fail", "audit": audit}, issues
    receipt: dict[str, object] = {
        "principal": replay_principal,
        "principal_binding": "caller-declared; not OS identity authentication",
        "principal_attestation": "caller-declared",
        "capability": "isolated-rebuild",
        "toolchain_scope": "direct-executables-only",
        "toctou_model": "non-adversarial",
        "support_profile": "dependency-free closed builtin propositions in a trusted execution environment",
        "origin": str(project.resolve()),
    }
    try:
        original = _input_manifest(project, metadata)
        with tempfile.TemporaryDirectory(
            prefix="research-os-lean-replay-"
        ) as directory:
            tree = Path(directory) / "tree"
            _copy_inputs(project, tree, original)
            replay_env = dict(environment if environment is not None else os.environ)
            for variable in (
                "LEAN_PATH",
                "LEAN_SRC_PATH",
                "LAKE_HOME",
                "LAKE_PACKAGES_DIR",
            ):
                replay_env.pop(variable, None)
            tooling, tooling_issues = _tooling_status(
                tree, metadata, runner=runner, environment=replay_env
            )
            issues.extend(tooling_issues)
            before = _input_manifest(tree, metadata)
            receipt.update(
                {
                    "worktree": str(tree.resolve()),
                    "isolation": "fresh-file-copy-no-build-cache",
                    "inputs": before,
                    "input_digest": canonical_digest(before),
                    "project_digest": canonical_digest(before),
                    "tooling": tooling,
                    "dependencies": metadata["dependencies"],
                    "metadata_digest": canonical_digest(metadata),
                }
            )
            if not issues:
                build = runner(
                    [tooling["lake_executable"], "build"], cwd=tree, env=replay_env
                )
                receipt["command"] = build.as_dict()
                if build.returncode != 0:
                    issues.append(
                        ValidationIssue(
                            "lean.kernel_replay",
                            "isolated lake build failed",
                            "/replay",
                        )
                    )
                if Path(build.cwd).resolve() != tree.resolve():
                    issues.append(
                        ValidationIssue(
                            "lean.replay.cwd",
                            "runner receipt is not bound to isolated tree",
                            "/replay",
                        )
                    )
                _, after_issues = audit_lean_project(tree, metadata)
                issues.extend(after_issues)
                if not issues:
                    kernel, kernel_issues = _kernel_probe(
                        tree, metadata, tooling, runner, replay_env
                    )
                    receipt["kernel"] = kernel
                    issues.extend(kernel_issues)
            after = _input_manifest(tree, metadata)
            receipt["output_digest"] = canonical_digest(after)
            if before != after or original != _input_manifest(project, metadata):
                issues.append(
                    ValidationIssue(
                        "lean.replay.drift",
                        "actual input tree changed during replay",
                        "/replay",
                    )
                )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        issues.append(ValidationIssue("lean.replay.execution", str(exc), "/replay"))
    receipt["verdict"] = "pass" if not issues else "fail"
    receipt["receipt_digest"] = canonical_digest(receipt)
    return receipt, issues


def _tooling_status(
    project: Path,
    metadata: Mapping[str, Any],
    *,
    runner: Runner,
    environment: Mapping[str, str] | None,
) -> tuple[dict[str, object], list[ValidationIssue]]:
    lake = shutil.which("lake", path=environment.get("PATH") if environment else None)
    lean = shutil.which("lean", path=environment.get("PATH") if environment else None)
    if lake is None or lean is None:
        missing = [
            name for name, path in (("lake", lake), ("lean", lean)) if path is None
        ]
        return {"available": False, "missing": missing}, [
            ValidationIssue(
                "lean.tooling.unavailable",
                f"missing executable(s): {', '.join(missing)}",
                "/tooling",
            )
        ]
    lean_version = runner([lean, "--version"], cwd=project, env=environment)
    lake_version = runner([lake, "--version"], cwd=project, env=environment)
    issues: list[ValidationIssue] = []
    expected_lean = metadata.get("toolchain", {}).get("lean", "")
    expected_lake = metadata.get("toolchain", {}).get("lake", "")
    version = expected_lean.rsplit(":v", 1)[-1]
    lean_match = re.match(
        r"Lean \(version ([^,\s)]+)(?:[,\s)]|$)", lean_version.stdout.strip()
    )
    if (
        lean_version.returncode != 0
        or not lean_match
        or lean_match.group(1) not in {version, expected_lean}
    ):
        issues.append(
            ValidationIssue(
                "lean.toolchain.runtime",
                "runtime Lean version differs from lock",
                "/toolchain/lean",
            )
        )
    lake_pattern = re.escape(expected_lake)
    if re.fullmatch(r"Lake version \d+(?:\.\d+)+", expected_lake):
        lake_pattern += r"(?:-[0-9a-f]{7,40})?"
    if lake_version.returncode != 0 or not re.fullmatch(
        lake_pattern + rf"(?: \(Lean version {re.escape(version)}\))?",
        lake_version.stdout.strip(),
    ):
        issues.append(
            ValidationIssue(
                "lean.lake.runtime",
                "runtime Lake version differs from lock",
                "/toolchain/lake",
            )
        )
    return {
        "available": True,
        "lean_executable": lean,
        "lake_executable": lake,
        "lean_executable_sha256": file_sha256(Path(lean)),
        "lake_executable_sha256": file_sha256(Path(lake)),
        "lean_version": lean_version.as_dict(),
        "lake_version": lake_version.as_dict(),
    }, issues


def run_lean_formalize(
    *,
    project: Path,
    statement: Mapping[str, Any],
    proof: Mapping[str, Any],
    review: Mapping[str, Any],
    metadata_path: str = "formalization.json",
    max_attempts: int = 1,
    candidate_source_revisions: Sequence[Mapping[str, Any]] = (),
    user_stop: bool = False,
    runner: Runner = _run_command,
    environment: Mapping[str, str] | None = None,
) -> LeanRunResult:
    project = project.resolve()
    history = resolve_under(project, f".lean-runs/{uuid.uuid4().hex}")
    history.mkdir(parents=True, exist_ok=False)
    write_json_exclusive(
        history / "request.json",
        {
            "statement": statement,
            "proof": proof,
            "review": review,
            "candidates": list(candidate_source_revisions),
            "max_attempts": max_attempts,
        },
    )
    sequence = 0
    builds_started = 0
    baseline: list[dict[str, str]] | None = None
    metadata_digest: str | None = None

    executable_locks: dict[str, str] = {}

    def journal_runner(argv, *, cwd, env=None, timeout=120):
        nonlocal sequence, builds_started
        if argv[-1] == "build" and Path(cwd).resolve() == project:
            builds_started += 1
        sequence += 1
        path = history / f"command-{sequence:04d}.json"
        if baseline is not None:
            if (
                _input_manifest(project, metadata) != baseline
                or file_sha256(project / metadata_path) != metadata_digest
            ):
                raise ValueError(
                    "lean.stage.drift: pinned project changed before command"
                )
        executable = Path(argv[0])
        digest = file_sha256(executable)
        if executable_locks.setdefault(str(executable), digest) != digest:
            raise ValueError("tool executable changed between stages")
        try:
            result = runner(argv, cwd=cwd, env=env, timeout=timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            result = CommandResult(
                tuple(argv),
                str(cwd),
                127 if isinstance(exc, OSError) else 124,
                "",
                f"{type(exc).__name__}: {exc}",
            )
        write_json_exclusive(path, result.as_dict())
        if type(result.returncode) is not int:
            raise ValueError("command exit code must be int, never bool")
        if file_sha256(executable) != digest:
            raise ValueError("tool executable changed during stage")
        if baseline is not None:
            if (
                _input_manifest(project, metadata) != baseline
                or file_sha256(project / metadata_path) != metadata_digest
            ):
                raise ValueError(
                    "lean.stage.drift: pinned project changed during command"
                )
        if Path(result.cwd).resolve() != Path(cwd).resolve() or tuple(
            result.argv
        ) != tuple(argv):
            raise ValueError("command receipt differs from actual invocation")
        return result

    try:
        if (
            type(max_attempts) is not int
            or max_attempts < 1
            or len(candidate_source_revisions) > max_attempts
        ):
            raise MathematicalWorkflowError(
                [
                    ValidationIssue(
                        "lean.budget",
                        "positive integer budget must cover supplied candidates before snapshot",
                        "/budget",
                    )
                ]
            )
        metadata = read_json(resolve_under(project, metadata_path, must_exist=True))
        write_json_exclusive(history / "metadata.json", metadata)
        if isinstance(metadata, Mapping):
            retained = []
            for entry in (
                metadata.get("sources", [])
                if isinstance(metadata.get("sources"), list)
                else []
            ):
                try:
                    source = resolve_under(project, entry.get("path"), must_exist=True)
                    retained.append(
                        {"path": entry["path"], "sha256": file_sha256(source)}
                    )
                except (OSError, ValueError, AttributeError):
                    continue
            for relative in _lean_sources(project):
                source = resolve_under(project, relative, must_exist=True)
                retained.append({"path": relative, "sha256": file_sha256(source)})
            # Retain actual bytes even for invalid/stale candidates and metadata.
            unique = {entry["path"]: entry for entry in retained}
            _copy_inputs(project, history / "submitted-source", list(unique.values()))
        if isinstance(metadata, Mapping) and not validate_formalization_metadata(
            project, metadata
        ):
            manifest = _input_manifest(project, metadata)
            baseline = manifest
            metadata_digest = file_sha256(project / metadata_path)
            for index, candidate in enumerate(
                candidate_source_revisions
                or [{"id": "locked-source", "sources": manifest}],
                1,
            ):
                candidate_path = history / f"candidate-{index:04d}"
                candidate_path.mkdir()
                write_json_exclusive(
                    candidate_path / "candidate.json",
                    {
                        "candidate": candidate,
                        "actual_sources": manifest,
                        "source_digest": canonical_digest(manifest),
                        "metadata": metadata,
                    },
                )
                _copy_inputs(project, candidate_path / "source", manifest)
        result = _run_lean_formalize(
            project=project,
            statement=statement,
            proof=proof,
            review=review,
            metadata_path=metadata_path,
            max_attempts=max_attempts,
            candidate_source_revisions=candidate_source_revisions,
            user_stop=user_stop,
            runner=journal_runner,
            environment=environment,
        )
    except MathematicalWorkflowError as exc:
        issues = list(exc.issues)
        write_json_exclusive(
            history / "failure.json",
            {"issues": [issue.as_dict() for issue in issues]},
        )
        if any(issue.code == "lean.review.verdict" for issue in issues):
            report = _lean_report(
                "not-verified",
                "proof-gap",
                {},
                issues,
                max_attempts,
                0,
            )
            result = _make_result(1, report)
        else:
            raise
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report = _lean_report(
            "not-verified",
            "execution-failed",
            {},
            [ValidationIssue("lean.execution", str(exc), "/")],
            max_attempts,
            builds_started,
        )
        result = _make_result(1, report)
    report = dict(result.report)
    report["history_path"] = str(history)
    report["commands_recorded"] = sequence
    result = _make_result(result.exit_code, report)
    write_json_exclusive(history / "report.json", result.report)
    return result


def _run_lean_formalize(
    *,
    project: Path,
    statement: Mapping[str, Any],
    proof: Mapping[str, Any],
    review: Mapping[str, Any],
    metadata_path: str = "formalization.json",
    max_attempts: int = 1,
    candidate_source_revisions: Sequence[Mapping[str, Any]] = (),
    user_stop: bool = False,
    runner: Runner = _run_command,
    environment: Mapping[str, str] | None = None,
) -> LeanRunResult:
    prerequisite_issues = validate_statement(statement, require_confirmed=True)
    prerequisite_issues.extend(validate_math_proof(proof, statement=statement))
    prerequisite_issues.extend(
        validate_independent_review(
            review, project_root=project, statement=statement, proof=proof
        )
    )
    if proof.get("result") != "candidate":
        prerequisite_issues.append(
            ValidationIssue(
                "lean.proof.required",
                "an ordinary candidate proof is required",
                "/proof",
            )
        )
    if review.get("verdict") not in {"pass", "inconclusive", "fail"}:
        prerequisite_issues.append(
            ValidationIssue(
                "lean.review.required",
                "an executed independent review is required",
                "/review",
            )
        )
    elif review.get("verdict") != "pass":
        prerequisite_issues.append(
            ValidationIssue(
                "lean.review.verdict",
                "independent review must pass before Lean formalization",
                "/review/verdict",
            )
        )
    if prerequisite_issues:
        raise MathematicalWorkflowError(prerequisite_issues)
    if (
        isinstance(max_attempts, bool)
        or not isinstance(max_attempts, int)
        or max_attempts < 1
    ):
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "lean.budget",
                    "max_attempts must be a positive integer",
                    "/budget/max_attempts",
                )
            ]
        )
    if len(candidate_source_revisions) > max_attempts:
        raise MathematicalWorkflowError(
            [
                ValidationIssue(
                    "lean.budget.exceeded",
                    "candidate revisions exceed hard attempt budget",
                    "/candidate_source_revisions",
                )
            ]
        )
    if user_stop:
        return _make_result(
            1,
            {
                "contract": {"name": LEAN_CONTRACT, "version": VERSION},
                "result": "not-verified",
                "stop_reason": "user-stopped",
                "verdict": "fail",
                "issues": [],
                "next_steps": [],
            },
        )
    try:
        metadata_file = resolve_under(project, metadata_path, must_exist=True)
        metadata = read_json(metadata_file)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise MathematicalWorkflowError(
            [ValidationIssue("lean.metadata.read", str(exc), "/metadata")]
        ) from exc
    metadata_issues = validate_formalization_metadata(project, metadata)
    expected_statement = {
        "revision": statement.get("revision"),
        "semantic_digest": statement.get("semantic_digest"),
    }
    if metadata.get("statement") != expected_statement:
        metadata_issues.append(
            ValidationIssue(
                "lean.statement-mismatch",
                "metadata statement binding differs from confirmed statement",
                "/statement",
            )
        )
    if metadata.get("proof") != {"run_digest": proof.get("run_digest")}:
        metadata_issues.append(
            ValidationIssue(
                "lean.proof.binding",
                "metadata proof binding differs from ordinary proof",
                "/proof",
            )
        )
    if metadata.get("review") != {"review_digest": review.get("review_digest")}:
        metadata_issues.append(
            ValidationIssue(
                "lean.review.binding",
                "metadata review binding differs from independent review",
                "/review",
            )
        )
    if any(issue.code == "lean.statement-mismatch" for issue in metadata_issues):
        return _make_result(
            1,
            _lean_report(
                "statement-mismatch",
                "workflow-complete",
                metadata,
                metadata_issues,
                max_attempts,
                0,
            ),
        )
    if metadata_issues:
        return _make_result(
            1,
            _lean_report(
                "not-verified",
                "execution-failed",
                metadata,
                metadata_issues,
                max_attempts,
                0,
            ),
        )
    baseline_sources = {entry["path"]: entry["sha256"] for entry in metadata["sources"]}
    attempts: list[dict[str, object]] = []
    revisions = list(candidate_source_revisions) or [
        {"id": "locked-source", "sources": baseline_sources}
    ]
    if len(revisions) > max_attempts:
        return _make_result(
            1,
            _lean_report(
                "not-verified",
                "budget-exhausted",
                metadata,
                [
                    ValidationIssue(
                        "lean.budget.exhausted", "no attempt budget remains", "/budget"
                    )
                ],
                max_attempts,
                0,
            ),
        )
    for index, revision in enumerate(revisions, start=1):
        supplied_sources = (
            revision.get("sources") if isinstance(revision, Mapping) else None
        )
        if supplied_sources != baseline_sources:
            issues = [
                ValidationIssue(
                    "lean.source.revision",
                    "candidate revision is not the locked source set",
                    f"/candidate_source_revisions/{index - 1}",
                )
            ]
            return _make_result(
                1,
                _lean_report(
                    "not-verified",
                    "execution-failed",
                    metadata,
                    issues,
                    max_attempts,
                    index - 1,
                ),
            )
        audit, audit_issues = audit_lean_project(project, metadata)
        if any(
            issue.code.startswith("lean.comparator")
            or issue.code == "lean.statement-mismatch"
            for issue in audit_issues
        ):
            report = _lean_report(
                "statement-mismatch",
                "workflow-complete",
                metadata,
                audit_issues,
                max_attempts,
                index,
            )
            report["audit"] = audit
            return _make_result(1, report)
        if audit_issues:
            report = _lean_report(
                "not-verified",
                "execution-failed",
                metadata,
                audit_issues,
                max_attempts,
                index - 1,
            )
            report["audit"] = audit
            return _make_result(1, report)
        tooling, tooling_issues = _tooling_status(
            project, metadata, runner=runner, environment=environment
        )
        if not tooling.get("available"):
            report = _lean_report(
                "not-verified",
                "tooling-blocked",
                metadata,
                tooling_issues,
                max_attempts,
                index - 1,
            )
            report["tooling"] = tooling
            report["audit"] = audit
            report["verdict"] = "blocked"
            return _make_result(3, report)
        if tooling_issues:
            report = _lean_report(
                "not-verified",
                "tooling-blocked",
                metadata,
                tooling_issues,
                max_attempts,
                index - 1,
            )
            report["tooling"] = tooling
            report["audit"] = audit
            report["verdict"] = "blocked"
            return _make_result(3, report)
        build = runner(
            [tooling["lake_executable"], "build"], cwd=project, env=environment
        )
        attempt = {
            "number": index,
            "candidate": revision.get("id", f"attempt-{index}"),
            "build": build.as_dict(),
        }
        attempts.append(attempt)
        if build.returncode != 0:
            if index == len(revisions):
                exhausted = index >= max_attempts
                report = _lean_report(
                    "not-verified",
                    "budget-exhausted" if exhausted else "execution-failed",
                    metadata,
                    [
                        ValidationIssue(
                            "lean.build",
                            "lake build failed"
                            + (" and attempt budget is exhausted" if exhausted else ""),
                            "/build",
                        )
                    ],
                    max_attempts,
                    index,
                )
                report["attempts"] = attempts
                report["tooling"] = tooling
                report["audit"] = audit
                return _make_result(1, report)
            continue
        kernel, kernel_issues = _kernel_probe(
            project, metadata, tooling, runner, environment
        )
        replay_receipt, replay_issues = (
            kernel_replay(
                project,
                metadata,
                runner=runner,
                environment=environment,
                excluded_principals=[
                    proof["actor_principal"],
                    review["reviewer_principal"],
                ],
            )
            if not kernel_issues
            else ({"verdict": "not-run"}, [])
        )
        all_issues = kernel_issues + replay_issues
        if not all_issues and replay_receipt.get("kernel", {}).get(
            "type_digest"
        ) != kernel.get("type_digest"):
            all_issues.append(
                ValidationIssue(
                    "lean.replay.kernel_drift",
                    "isolated kernel type differs from original probe",
                    "/replay",
                )
            )
        mismatch = any(issue.code == "lean.statement-mismatch" for issue in all_issues)
        report = _lean_report(
            "statement-mismatch"
            if mismatch
            else ("verified" if not all_issues else "not-verified"),
            "workflow-complete" if not all_issues or mismatch else "execution-failed",
            metadata,
            all_issues,
            max_attempts,
            index,
        )
        report.update(
            {
                "attempts": attempts,
                "tooling": tooling,
                "audit": audit,
                "kernel_axioms": kernel,
                "kernel_comparator": kernel,
                "kernel_replay": replay_receipt,
            }
        )
        if not all_issues:
            report["verdict"] = "pass"
            report["next_steps"] = [
                "record formal_verification assessment",
                "perform human paper-to-statement alignment separately",
            ]
            return _make_result(0, report)
        return _make_result(1, report)
    report = _lean_report(
        "not-verified",
        "execution-failed",
        metadata,
        [
            ValidationIssue(
                "lean.build", "all supplied candidate builds failed", "/attempts"
            )
        ],
        max_attempts,
        len(attempts),
    )
    report["attempts"] = attempts
    return _make_result(1, report)


def _make_result(exit_code: int, report: dict[str, object]) -> LeanRunResult:
    if type(exit_code) is not int or exit_code not in {0, 1, 2, 3}:
        raise ValueError("invalid Lean exit code")
    value = dict(report)
    value.pop("report_digest", None)
    value["report_digest"] = canonical_digest(value)
    return LeanRunResult(exit_code, value)


def _lean_report(
    result: str,
    stop_reason: str,
    metadata: Mapping[str, Any],
    issues: Sequence[ValidationIssue],
    maximum: int,
    used: int,
) -> dict[str, object]:
    if result not in LEAN_RESULTS or stop_reason not in LEAN_STOP_REASONS:
        raise ValueError("invalid Lean result or stop reason")
    report: dict[str, object] = {
        "contract": {"name": LEAN_CONTRACT, "version": VERSION},
        "statement": metadata.get("statement"),
        "result": result,
        "stop_reason": stop_reason,
        "verdict": "fail",
        "budget": {"max_attempts": maximum, "attempts_used": used},
        "issues": [issue.as_dict() for issue in issues],
        "claim_boundary": metadata.get("claim_boundary"),
        "next_steps": [],
    }
    return report
