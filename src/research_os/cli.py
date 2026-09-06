from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from .contracts import (
    Issue,
    artifact_report,
    resolve_project_path,
    validate_artifact,
)
from .core import (
    freeze_publication,
    ApplicationFailure,
    invoke_workflow,
    validate_repository,
    validate_ports,
    WORKFLOW_IDS,
    generate_projection,
    load_json,
    load_projection_snapshot,
    research_charter,
    setup_project,
    validate_projection,
    validate_projection_value,
    verify_research_charter_execution,
)

from .lifecycle import (
    LifecycleFailure,
    TargetUnavailable,
    export_project,
    migrate_artifact,
    update_project,
)

PASS = 0
VALIDATION_FAILURE = 1
USAGE_ERROR = 2
BLOCKED = 3
ADAPTER_CHOICES = ("claude-code", "codex")


@dataclass(frozen=True)
class CodexHostRequest:
    workflow: str
    projection_digest: str
    project: str
    input_name: str
    output_name: str
    report_name: str
    input_sha256: str = ""
    discipline_entrypoints: tuple[str, ...] = ()
    automatic_next_workflow: bool = False

    def digest(self) -> str:
        value = {
            "automatic_next_workflow": self.automatic_next_workflow,
            "discipline_entrypoints": list(self.discipline_entrypoints),
            "input": self.input_name,
            "input_sha256": self.input_sha256,
            "output": self.output_name,
            "project": self.project,
            "projection_digest": self.projection_digest,
            "report": self.report_name,
            "workflow": self.workflow,
        }
        payload = (
            json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class CodexHostReceipt:
    request_digest: str
    status: str
    stop_reason: str
    exit_status: int


class CodexHost(Protocol):
    def __call__(
        self,
        request: CodexHostRequest,
        invoke_core: Callable[[], dict[str, object]],
    ) -> CodexHostReceipt: ...


def emit(value: object) -> None:
    json.dump(value, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def validation_report(subject, verdict, issues):
    # Pre-validation input/projection errors are command reports, not evidence
    # that the Artifact validator ran on bytes it never read.
    return command_report("validate", verdict, issues)


def command_report(
    command: str,
    verdict: str,
    issues: list[Issue],
    *,
    publication: object | None = None,
) -> dict[str, object]:
    report: dict[str, object] = {
        "contract": {"name": "research-os/command-report", "version": "1.0.0"},
        "command": command,
        "verdict": verdict,
    }
    if publication is not None:
        report["publication"] = publication
    report["issues"] = [issue.as_dict() for issue in issues]
    return report


def load_validation_context(project, context_name):
    """Read only explicitly selected fixed refs, preserving their original bytes."""
    from .lifecycle import read_target
    from .validation.semantics.common import validate_fixed_ref, fixed_ref_key
    from .workflows.mathematical.projections import fixed_artifact
    selected = load_json(resolve_project_path(project, context_name))
    if (not isinstance(selected, dict) or not {'project', 'evidence'} <= set(selected)
            or set(selected) - {'project', 'evidence', 'records'}
            or not isinstance(selected['evidence'], list) or not isinstance(selected.get('records', []), list)):
        raise ValueError('validation context requires project ref, evidence refs and optional records refs')
    records = {}
    for ref in [selected['project'], *selected['evidence'], *selected.get('records', [])]:
        issues = validate_fixed_ref(ref)
        if issues:
            raise ApplicationFailure([Issue(item.code, item.message) for item in issues])
        key = fixed_ref_key(ref)
        if key in records:
            continue
        data = read_target(project, ref['target'])
        if hashlib.sha256(data).hexdigest() != ref['sha256']:
            raise ApplicationFailure([Issue('context.digest', 'validation context digest mismatch')])
        records[key] = data
    def typed(ref, kind):
        try:
            artifact = fixed_artifact(ref, records, kind)
        except (ValueError, TypeError, KeyError) as exc:
            raise ApplicationFailure([Issue('context.artifact', str(exc))]) from exc
        issues = validate_artifact(artifact)
        if issues:
            raise ApplicationFailure(issues)
        return {**artifact, 'target': ref['target']}
    return {'project': typed(selected['project'], 'project'),
            'project_digest': selected['project']['sha256'],
            'evidence_by_digest': {ref['sha256']: typed(ref, 'evidence') for ref in selected['evidence']},
            'records': records}


def validate_command(
    project: Path, subject_name: str, *, adapter: str | None = None, context_name: str | None = None
) -> int:
    if adapter is not None:
        projection = (
            project / ".research-os" / "projections" / adapter / "manifest.json"
        )
        projection_issues = validate_projection(adapter, projection, project=project)
        if projection_issues:
            emit(validation_report(subject_name, "blocked", projection_issues))
            return BLOCKED
    try:
        subject = resolve_project_path(project, subject_name)
    except ValueError as exc:
        emit(
            validation_report(
                subject_name, "usage_error", [Issue("subject.path", str(exc))]
            )
        )
        return USAGE_ERROR
    if not subject.is_file():
        emit(
            validation_report(
                subject_name,
                "usage_error",
                [Issue("subject.missing", "subject file does not exist")],
            )
        )
        return USAGE_ERROR
    try:
        raw = subject.read_bytes()
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        emit(
            validation_report(subject_name, "fail", [Issue("artifact.json", str(exc))])
        )
        return VALIDATION_FAILURE
    except OSError as exc:
        emit(
            validation_report(
                subject_name, "usage_error", [Issue("subject.read", str(exc))]
            )
        )
        return USAGE_ERROR

    try:
        context = load_validation_context(project, context_name) if context_name is not None else {}
    except ApplicationFailure as exc:
        emit(validation_report(subject_name, 'fail', exc.issues))
        return VALIDATION_FAILURE
    except TargetUnavailable as exc:
        emit(validation_report(subject_name, 'blocked', [Issue('target.unavailable', str(exc))]))
        return BLOCKED
    except LifecycleFailure as exc:
        emit(validation_report(subject_name, 'fail', [Issue('lifecycle.invalid', str(exc))]))
        return VALIDATION_FAILURE
    except (ValueError, OSError, TypeError, KeyError) as exc:
        emit(validation_report(subject_name, 'usage_error', [Issue('context.invalid', str(exc))]))
        return USAGE_ERROR
    result = artifact_report(value, subject_name, raw, **context)
    target = value.get("target") if isinstance(value, dict) else None
    if result["verdict"] == "pass" and isinstance(target, dict) and (
        target.get("repository") or target.get("kind") == "uri"
    ) and os.environ.get("RESEARCH_OS_OFFLINE") == "1":
        result["verdict"] = "blocked"
        result["issues"] = [Issue("target.unavailable", "external target unavailable while offline").as_dict()]
    emit(result)
    return {"pass": PASS, "fail": VALIDATION_FAILURE, "blocked": BLOCKED}[result["verdict"]]


def claude_charter_command(project: Path) -> int:
    """Fail closed until the host can enforce the fixed tracer's isolation."""
    execution: dict[str, object] = {"adapter": "claude-code", "host_invoked": False}
    if os.environ.get("RESEARCH_OS_OFFLINE") == "1":
        issues = [
            Issue(
                "adapter.offline",
                "model execution is prohibited by RESEARCH_OS_OFFLINE=1",
            )
        ]
    else:
        manifest = project / ".research-os/projections/claude-code/manifest.json"
        issues = validate_projection("claude-code", manifest, project=project)
        if not issues:
            execution["pins"] = load_json(manifest)["canonical_skills"]
            issues = [
                Issue(
                    "adapter.isolation_unavailable",
                    "this Adapter has no verified host isolation profile; real Claude Code execution is blocked",
                )
            ]
    value = command_report("research-charter", "blocked", issues)
    value.update(
        {
            "status": "stopped",
            "stop_reason": "external_prerequisite_unavailable",
            "outputs": [],
            "next_steps": [],
            "execution": execution,
        }
    )
    emit(value)
    return BLOCKED


def codex_charter_command(
    args: argparse.Namespace, codex_host: CodexHost | None = None
) -> int:
    command = f"adapter {args.adapter} research-charter"
    if args.adapter != "codex" or args.confirm != "RUN research-charter":
        emit(
            command_report(
                command,
                "usage_error",
                [
                    Issue(
                        "workflow.confirmation",
                        "Codex tracer requires explicit --confirm 'RUN research-charter'",
                    )
                ],
            )
        )
        return USAGE_ERROR

    project = args.project.resolve()
    manifest_path = project / ".research-os/projections/codex/manifest.json"
    try:
        projection = load_projection_snapshot(manifest_path)
    except (OSError, ValueError) as exc:
        return _emit_codex_blocked(command, [Issue("projection.read", str(exc))], None)
    manifest = projection.value
    issues = validate_projection_value(
        "codex", manifest, manifest_path, project=project
    )
    if issues:
        return _emit_codex_blocked(command, issues, None)
    digest = manifest["projection_digest"]
    if codex_host is None or os.environ.get("RESEARCH_OS_OFFLINE") == "1":
        if os.environ.get("RESEARCH_OS_OFFLINE") == "1":
            issues = [
                Issue(
                    "codex.offline",
                    "offline policy forbids model egress; Codex was not started",
                )
            ]
        else:
            issues = [
                Issue(
                    "codex.isolation_unverified",
                    "no verified Codex execution isolation profile is available; refusing to start the host",
                )
            ]
        return _emit_codex_blocked(command, issues, digest)

    output_names = (args.output, args.report)
    try:
        output_paths = tuple(
            resolve_project_path(project, name) for name in output_names
        )
    except ValueError as exc:
        emit(
            command_report(command, "usage_error", [Issue("command.invalid", str(exc))])
        )
        return USAGE_ERROR
    if len(set(output_paths)) != len(output_paths) or any(path.exists() or path.is_symlink() for path in output_paths):
        emit(
            command_report(
                command,
                "fail",
                [Issue("output.exists", "workflow output already exists")],
            )
        )
        return VALIDATION_FAILURE
    input_path = resolve_project_path(project, args.input)
    input_bytes = input_path.read_bytes() if input_path.is_file() else None
    request = CodexHostRequest(
        workflow="research-charter",
        projection_digest=digest,
        project=str(project),
        input_name=args.input,
        output_name=args.output,
        report_name=args.report,
        input_sha256=hashlib.sha256(input_bytes).hexdigest() if input_bytes is not None else "",
    )
    core_result: dict[str, object] | None = None
    invocation_open = True

    def fail(code: str, message: str) -> int:
        emit(command_report(command, "fail", [Issue(code, message)]))
        return VALIDATION_FAILURE

    def invoke_core() -> dict[str, object]:
        nonlocal core_result, invocation_open
        if not invocation_open or core_result is not None:
            raise RuntimeError("Codex host may invoke the fixed workflow exactly once")
        invocation_open = False
        if input_bytes is None:
            raise FileNotFoundError(args.input)
        if resolve_project_path(project, args.input).read_bytes() != input_bytes:
            raise ApplicationFailure([Issue('workflow.input_changed', 'host changed explicit request bytes')])
        core_result = research_charter(project, args.input, args.output, args.report, request_bytes=input_bytes)
        return core_result

    try:
        receipt = codex_host(request, invoke_core)
    except ApplicationFailure as exc:
        invocation_open = False
        emit(command_report(command, "fail", exc.issues))
        return exc.exit_code
    except FileExistsError as exc:
        invocation_open = False
        emit(command_report(command, "fail", [Issue("output.exists", str(exc))]))
        return VALIDATION_FAILURE
    except (FileNotFoundError, ValueError, OSError, json.JSONDecodeError) as exc:
        invocation_open = False
        leaf_failure = exc.__class__.__module__.startswith("research_os.workflows")
        emit(command_report(command, "fail" if leaf_failure else "usage_error",
                            [Issue(getattr(exc, "code", "command.invalid"), str(exc))]))
        return VALIDATION_FAILURE if leaf_failure else USAGE_ERROR
    except Exception as exc:
        invocation_open = False
        return fail("codex.host", str(exc))
    invocation_open = False

    if core_result is None or not isinstance(receipt, CodexHostReceipt):
        return fail(
            "codex.host_protocol", "host did not execute the fixed Core workflow"
        )
    try:
        final_projection = load_projection_snapshot(manifest_path)
    except (OSError, json.JSONDecodeError):
        return fail(
            "codex.projection_changed", "Codex projection changed during execution"
        )
    projection_issues = validate_projection_value(
        "codex", final_projection.value, manifest_path, project=project
    )
    if projection_issues or final_projection.sha256 != projection.sha256:
        return fail(
            "codex.projection_changed", "Codex projection changed during execution"
        )
    try:
        expected_receipt = CodexHostReceipt(
            request_digest=request.digest(),
            status=str(core_result["status"]),
            stop_reason=str(core_result["stop_reason"]),
            exit_status=PASS,
        )
    except (KeyError, TypeError) as exc:
        return fail("codex.host_protocol", f"host mutated the Core stop result: {exc}")
    if receipt != expected_receipt:
        return fail(
            "codex.host_protocol",
            "host receipt does not match the fixed request and Core stop result",
        )
    if input_bytes is None or resolve_project_path(project, args.input).read_bytes() != input_bytes:
        return fail('workflow.input_changed', 'explicit request changed during host execution')
    result_issues = verify_research_charter_execution(
        project, args.input, args.output, args.report, core_result, request_bytes=input_bytes
    )
    if result_issues:
        emit(command_report(command, "fail", result_issues))
        return VALIDATION_FAILURE
    emit(core_result)
    return PASS


def _emit_codex_blocked(command: str, issues: list[Issue], digest: object) -> int:
    result = command_report(command, "blocked", issues)
    result.update(
        {
            "status": "stopped",
            "stop_reason": "external_prerequisite_unavailable",
            "next_steps": [],
            "execution": {
                "codex_started": False,
                "direct_cli_fallback": False,
                "projection_digest": digest,
                "artifact_created": False,
                "workflow_report_created": False,
            },
        }
    )
    emit(result)
    return BLOCKED


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-os", exit_on_error=False)
    commands = parser.add_subparsers(dest="command", required=True)

    setup = commands.add_parser("setup-research-os", exit_on_error=False)
    setup.add_argument("--project", type=Path, required=True)

    update = commands.add_parser("update-research-os", exit_on_error=False)
    update.add_argument("--project", type=Path, required=True)
    update.add_argument("--environment", required=True)

    export = commands.add_parser("export-research-os", exit_on_error=False)
    export.add_argument("--project", type=Path, required=True)
    export.add_argument("--commit", required=True)
    export.add_argument("--output", type=Path, required=True)

    migration = commands.add_parser("migrate-artifact", exit_on_error=False)
    migration.add_argument("--project", type=Path, required=True)
    for argument in (
        "input",
        "rules",
        "to-contract",
        "to-type-version",
        "output",
        "receipt",
    ):
        migration.add_argument(f"--{argument}", required=True)

    charter = commands.add_parser("research-charter", exit_on_error=False)
    charter.add_argument("--project", type=Path, required=True)
    charter.add_argument("--input", required=True)
    charter.add_argument("--output", required=True)
    charter.add_argument("--report", required=True)

    validate = commands.add_parser("validate", exit_on_error=False)
    validate.add_argument("--project", type=Path, required=True)
    validate.add_argument("subject")
    validate.add_argument("--context")

    freeze = commands.add_parser("freeze-publication", exit_on_error=False)
    freeze.add_argument("--project", type=Path, required=True)
    freeze.add_argument("--manifest", required=True)
    freeze.add_argument("--principal", required=True)
    freeze.add_argument("--confirm", required=True)

    projection = commands.add_parser("generate-projection", exit_on_error=False)
    projection.add_argument("adapter", choices=ADAPTER_CHOICES)
    projection.add_argument("--output", type=Path, required=True)

    adapter = commands.add_parser("adapter", exit_on_error=False)
    adapter.add_argument("adapter", choices=ADAPTER_CHOICES)
    adapter_commands = adapter.add_subparsers(dest="adapter_command", required=True)
    adapter_validate = adapter_commands.add_parser("validate", exit_on_error=False)
    adapter_validate.add_argument("--project", type=Path, required=True)
    adapter_validate.add_argument("subject")
    adapter_validate.add_argument("--context")
    adapter_charter = adapter_commands.add_parser(
        "research-charter", exit_on_error=False
    )
    adapter_charter.add_argument("--project", type=Path, required=True)
    adapter_charter.add_argument("--input", required=True)
    adapter_charter.add_argument("--output", required=True)
    adapter_charter.add_argument("--report", required=True)
    adapter_charter.add_argument("--confirm")
    for name in ("validate-repository", "validate-ports"):
        check = commands.add_parser(name, exit_on_error=False)
        check.add_argument("--root", type=Path, required=True)
    workflow = commands.add_parser("workflow", exit_on_error=False)
    workflow.add_argument("workflow", choices=WORKFLOW_IDS)
    workflow.add_argument("--project", type=Path, required=True)
    workflow.add_argument("--request", required=True)
    for name in WORKFLOW_IDS:
        if name in {"setup-research-os", "research-charter", "freeze-publication"}:
            continue
        entry = commands.add_parser(name, exit_on_error=False)
        entry.add_argument("--project", type=Path, required=True)
        entry.add_argument("--request", required=True)
    return parser


def run(
    arguments: list[str] | None = None, *, codex_host: CodexHost | None = None
) -> int:
    try:
        args = build_parser().parse_args(arguments)
    except argparse.ArgumentError as exc:
        emit(
            command_report(
                "research-os", "usage_error", [Issue("arguments.invalid", str(exc))]
            )
        )
        return USAGE_ERROR
    except SystemExit as exc:
        return int(exc.code or 0)

    try:
        if args.command in {"validate-repository", "validate-ports"}:
            result = (validate_repository if args.command == "validate-repository" else validate_ports)(args.root)
            emit(result)
            return {"pass": 0, "fail": 1, "blocked": 3}[result.get("verdict", result.get("status"))]
        if args.command == "workflow" or args.command in set(WORKFLOW_IDS) - {"setup-research-os", "research-charter", "freeze-publication"}:
            project = args.project.resolve()
            request = load_json(resolve_project_path(project, args.request))
            result, code = invoke_workflow(args.workflow if args.command == "workflow" else args.command, project, request)
            emit(result)
            return code
        if args.command == "setup-research-os":
            emit(setup_project(args.project.resolve()))
            return PASS
        if args.command == "update-research-os":
            emit(update_project(args.project.resolve(), args.environment))
            return PASS
        if args.command == "export-research-os":
            emit(export_project(args.project.resolve(), args.commit, args.output))
            return PASS
        if args.command == "migrate-artifact":
            emit(
                migrate_artifact(
                    args.project.resolve(),
                    args.input,
                    args.rules,
                    args.to_contract,
                    args.to_type_version,
                    args.output,
                    args.receipt,
                )
            )
            return PASS
        if args.command == "research-charter":
            emit(
                research_charter(
                    args.project.resolve(), args.input, args.output, args.report
                )
            )
            return PASS
        if args.command == "validate":
            return validate_command(args.project.resolve(), args.subject, context_name=args.context)
        if args.command == "adapter":
            if args.adapter_command == "research-charter":
                if args.adapter == "claude-code":
                    return claude_charter_command(args.project.resolve())
                return codex_charter_command(args, codex_host)
            return validate_command(
                args.project.resolve(), args.subject, adapter=args.adapter, context_name=args.context
            )
        if args.command == "generate-projection":
            emit(generate_projection(args.adapter, args.output.resolve()))
            return PASS
        if args.command == "freeze-publication":
            manifest = load_json(resolve_project_path(args.project, args.manifest))
            receipt = freeze_publication(args.project.resolve(), manifest, args.confirm, args.principal)
            emit(command_report(args.command, "pass", [], publication=receipt))
            return PASS
    except ApplicationFailure as exc:
        emit(command_report(args.command, {1: "fail", 2: "usage_error", 3: "blocked"}[exc.exit_code], exc.issues))
        return exc.exit_code
    except TargetUnavailable as exc:
        emit(
            command_report(
                args.command, "blocked", [Issue("target.unavailable", str(exc))]
            )
        )
        return BLOCKED
    except LifecycleFailure as exc:
        emit(
            command_report(args.command, "fail", [Issue("lifecycle.invalid", str(exc))])
        )
        return VALIDATION_FAILURE
    except FileExistsError as exc:
        emit(command_report(args.command, "fail", [Issue("output.exists", str(exc))]))
        return VALIDATION_FAILURE
    except FileNotFoundError as exc:
        emit(
            command_report(
                args.command, "usage_error", [Issue("input.missing", str(exc))]
            )
        )
        return USAGE_ERROR
    except (ValueError, OSError) as exc:
        code = getattr(exc, "code", "command.invalid")
        is_leaf_failure = exc.__class__.__module__.startswith(("research_os.workflows", "research_os.publication"))
        status = VALIDATION_FAILURE if is_leaf_failure else USAGE_ERROR
        emit(command_report(args.command, "fail" if is_leaf_failure else "usage_error", [Issue(code, str(exc))]))
        return status
    except (TypeError, KeyError) as exc:
        emit(command_report(args.command, "usage_error", [Issue("request.invalid", str(exc))]))
        return USAGE_ERROR

    emit(
        command_report(
            "research-os", "usage_error", [Issue("command.invalid", "unknown command")]
        )
    )
    return USAGE_ERROR


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
