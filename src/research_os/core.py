"""Application boundary. One explicit invocation, one leaf, no workflow state."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import secrets
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from . import __version__, SOURCE_REVISION
from .contracts import Issue, resolve_project_path, normalize_issues
from .install import (SourceBundle, SkillDescriptor, SkillKind, ProjectionBlocked,
                      build_install_plan, build_projection, execute_install, load_adapter_definition)
from .install.model import canonical_json

PACKAGE = Path(__file__).resolve().parent
PACKAGED = PACKAGE.parent.name != "src"
RESOURCE_ROOT = PACKAGE if PACKAGED else PACKAGE.parents[1]
CORE = RESOURCE_ROOT / ("_core" if PACKAGED else "core")
ADAPTERS = RESOURCE_ROOT / ("_adapters" if PACKAGED else "adapters")
TEMPLATES = RESOURCE_ROOT / ("_templates" if PACKAGED else "templates")
REFERENCES = RESOURCE_ROOT / ("_reference_projects" if PACKAGED else "reference-projects")
WORKFLOW_IDS = (
    "setup-research-os", "research-charter", "research-literature", "research-gap",
    "research-idea", "research-novelty", "research-reflect", "design-experiment",
    "prepare-experiment", "run-experiment", "analyze-experiment", "assess-result-to-claim",
    "math-proof", "lean-formalize", "freeze-publication",
)
DISCIPLINE_IDS = (
    "experiment-audit", "statistical-check", "training-health-check", "environment-check",
    "independent-proof-review", "trusted-statement-comparison", "publication-claim-audit",
    "citation-reference-audit",
)
_DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
_FILE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)


class ApplicationFailure(ValueError):
    def __init__(self, issues, exit_code=1):
        self.issues = normalize_issues(issues)
        self.exit_code = exit_code
        super().__init__("; ".join(issue.message for issue in self.issues))


def _json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def load_json(path):
    return json.loads(path.read_bytes())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


@dataclass(frozen=True)
class ProjectionSnapshot:
    value: object
    sha256: str


def load_projection_snapshot(path):
    data = path.read_bytes()
    return ProjectionSnapshot(json.loads(data), hashlib.sha256(data).hexdigest())


def _open_project_directory(project, parts, *, create):
    fd = os.open(project, _DIRECTORY_FLAGS)
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, mode=0o755, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, _DIRECTORY_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _atomic_write_project(project, relative_path, data):
    resolve_project_path(project, relative_path)
    parts = PurePosixPath(relative_path).parts
    fd = _open_project_directory(project, parts[:-1], create=True)
    temp = f".{parts[-1]}.{secrets.token_hex(8)}.tmp"
    linked = False
    token = None
    try:
        out = os.open(temp, _FILE_FLAGS, 0o600, dir_fd=fd)
        with os.fdopen(out, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            token = os.fstat(stream.fileno())
        os.link(temp, parts[-1], src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
        linked = True
        os.fsync(fd)
    except BaseException:
        if linked:
            current = os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
            if (current.st_dev, current.st_ino) == (token.st_dev, token.st_ino):
                os.unlink(parts[-1], dir_fd=fd)
        raise
    finally:
        try:
            os.unlink(temp, dir_fd=fd)
        except FileNotFoundError:
            pass
        os.close(fd)


def _unlink_project_file(project, relative_path):
    parts = PurePosixPath(relative_path).parts
    try:
        fd = _open_project_directory(project, parts[:-1], create=False)
    except FileNotFoundError:
        return
    try:
        os.unlink(parts[-1], dir_fd=fd)
    except FileNotFoundError:
        pass
    finally:
        os.close(fd)


def install_workflow_outputs(project, outputs):
    paths = [resolve_project_path(project, name) for name in outputs]
    if len(paths) != len(set(paths)) or any(path.exists() for path in paths):
        raise FileExistsError("workflow outputs must be new and distinct")
    created = []
    try:
        for name, data in outputs.items():
            _atomic_write_project(project, name, data)
            stat = (project / name).stat(follow_symlinks=False)
            created.append((name, stat.st_dev, stat.st_ino))
    except BaseException:
        for name, device, inode in reversed(created):
            try:
                path = resolve_project_path(project, name)
                stat = path.stat(follow_symlinks=False)
                if (stat.st_dev, stat.st_ino) == (device, inode):
                    _unlink_project_file(project, name)
            except (ValueError, FileNotFoundError):
                pass
        raise


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError(f"missing frontmatter: {path}")
    header, _ = text[4:].split("\n---\n", 1)
    fields = {}
    for line in header.splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            raise ValueError(f"frontmatter must contain flat fields: {path}")
        key, value = line.split(":", 1)
        if key in fields:
            raise ValueError(f"duplicate frontmatter field: {path}")
        fields[key] = value.strip()
    if set(fields) - {"name", "description", "license", "compatibility"}:
        raise ValueError(f"unknown/provider-specific canonical frontmatter: {path}")
    if fields.get("name") != path.parent.name or not fields.get("description"):
        raise ValueError(f"skill directory/name/description mismatch: {path}")
    return fields


def rebuild_catalog(root=None):
    core = Path(root) / "core" if root is not None else CORE
    entries = []
    for path in sorted((core / "skills").glob("*/SKILL.md")):
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError(f"canonical skill must not be symlinked: {path}")
        fields = _frontmatter(path)
        name = fields["name"]
        if name in WORKFLOW_IDS:
            kind = "workflow"
        elif name in DISCIPLINE_IDS:
            kind = "discipline"
        else:
            raise ValueError(f"unknown P0 skill: {name}")
        entries.append({"id": name, "kind": kind, "version": "1.0.0",
                        "path": f"core/skills/{name}/SKILL.md",
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return {"contract": {"name": "research-os/catalog", "version": "1.0.0"}, "skills": entries}


def validate_ports(root):
    try:
        module = importlib.import_module("research_os.validation.ports")
    except (ImportError, SyntaxError) as exc:
        return {"status": "fail", "verdict": "fail", "exit_code": 1,
                "issues": [{"code": "ports.unavailable", "message": str(exc)}]}
    validator = getattr(module, "validate_ports", None)
    if not callable(validator):
        return {"status": "fail", "verdict": "fail", "exit_code": 1,
                "issues": [{"code": "ports.unavailable", "message": "ports validator is not implemented"}]}
    result = validator(Path(root), inventory="ports/inventory.json",
                       release_inventory="ports/release.json", product_root="ports/products", mode="release")
    if not isinstance(result, dict) or result.get("verdict", result.get("status")) not in {"pass", "fail", "blocked"}:
        raise ApplicationFailure([Issue("ports.protocol", "ports validator returned an invalid verdict")])
    return result


def validate_repository(root):
    from .validation.foundation import ValidationReportBuilder
    root = Path(root)
    report = ValidationReportBuilder("repository", "1.0.0", {"kind": "git", "path": "core/catalog.json"})
    try:
        derived = rebuild_catalog(root)
        recorded = load_json(root / "core/catalog.json")
        if recorded != derived:
            report.add_issue(Issue("catalog.drift", "catalog must equal rebuild_catalog output"))
        kinds = {kind: {item["id"] for item in derived["skills"] if item["kind"] == kind}
                 for kind in ("workflow", "discipline")}
        for kind, expected in (("workflow", WORKFLOW_IDS), ("discipline", DISCIPLINE_IDS)):
            missing = sorted(set(expected) - kinds[kind])
            if missing:
                report.add_issue(Issue(f"catalog.{kind}.missing", "missing required skills: " + ", ".join(missing)))
        report.add_evidence("catalog.inventory", "canonical inventory rebuilt",
                            data={kind: sorted(names) for kind, names in kinds.items()})
    except (ValueError, OSError) as exc:
        report.add_issue(Issue("catalog.invalid", str(exc)))
    for path in sorted((root / "core/skills").rglob("*")):
        if path.is_symlink():
            report.add_issue(Issue("core.symlink", str(path.relative_to(root))))
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if "implementation-notes" in path.name.lower():
            report.add_issue(Issue("core.implementation_notes", f"implementation notes cannot ship in canonical skill: {relative}"))
        if path.suffix in {".md", ".json", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            if re.search(r"(?i)(\.claude/|\.agents/|\bclaude\b|\bcodex\b|\bmcp\b|^\s*(?:tools|model|hooks|permissions):)", text, re.M):
                report.add_issue(Issue("core.provider_leak", relative))
    ports = validate_ports(root)
    verdict = ports.get("verdict", ports.get("status"))
    if verdict != "pass":
        report.add_issue(Issue("ports.not_accepted", "release ports are missing or not accepted", data={"report": ports}))
    else:
        for item in derived["skills"]:
            if item["kind"] != "discipline":
                continue
            product = root / "ports" / "products" / item["id"] / "SKILL.md"
            try:
                digest = hashlib.sha256(product.read_bytes()).hexdigest()
            except OSError as exc:
                report.add_issue(Issue("ports.catalog_binding", f"missing port product for discipline {item['id']}: {exc}"))
                continue
            if digest != item["sha256"]:
                report.add_issue(Issue("ports.catalog_binding", f"port product differs from canonical discipline: {item['id']}"))
    report.add_evidence("ports.executed", "release port admission checked", data={"verdict": verdict})
    result = report.build()
    return {"status": result["verdict"], "exit_code": 0 if result["verdict"] == "pass" else 1,
            "report": result, "issues": result["issues"]}


def _canonical_skill_descriptors(bundle=None):
    if bundle is None:
        catalog = rebuild_catalog()
        read_skill = lambda item: (CORE / "skills" / item["id"] / "SKILL.md").read_bytes()
    else:
        try:
            catalog = json.loads(bundle.files["core/catalog.json"])
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApplicationFailure([Issue("catalog.bundle", f"invalid bundled catalog: {exc}")]) from exc
        read_skill = lambda item: bundle.files[f"core/skills/{item['id']}/SKILL.md"]
    try:
        descriptors = tuple(
            SkillDescriptor(
                name=item["id"],
                version=item["version"],
                kind=SkillKind(item["kind"]),
                sha256=item["sha256"],
                content=read_skill(item),
            )
            for item in catalog["skills"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ApplicationFailure([Issue("catalog.bundle", f"bundled catalog does not bind skill bytes: {exc}")]) from exc
    by_name = {skill.name: skill for skill in descriptors}
    if len(by_name) != len(descriptors) or set(by_name) != set(WORKFLOW_IDS) | set(DISCIPLINE_IDS):
        raise ApplicationFailure([Issue("catalog.bundle", "bundled catalog skill inventory is incomplete or duplicated")])
    if any(by_name[name].kind is not SkillKind.WORKFLOW for name in WORKFLOW_IDS):
        raise ApplicationFailure([Issue("catalog.bundle", "bundled catalog misclassifies a workflow")])
    if any(by_name[name].kind is not SkillKind.DISCIPLINE for name in DISCIPLINE_IDS):
        raise ApplicationFailure([Issue("catalog.bundle", "bundled catalog misclassifies a discipline")])
    return descriptors


def _projection_plan(adapter, *, scope="complete", bundle=None):
    skills = _canonical_skill_descriptors(bundle)
    if bundle is None:
        definition, digest = load_adapter_definition(ADAPTERS / f"{adapter}.json")
    else:
        try:
            raw = bundle.files[f"adapters/{adapter}.json"]
            value = json.loads(raw)
            from .install import AdapterDefinition
            definition, digest = AdapterDefinition.from_dict(value), hashlib.sha256(raw).hexdigest()
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise ApplicationFailure([Issue("projection.adapter", f"invalid bundled adapter: {exc}")]) from exc
    if scope == "complete":
        plan = build_projection(definition, digest, skills)
    elif scope == "workflow-only" and adapter == "codex":
        workflows = tuple(skill for skill in skills if skill.kind is SkillKind.WORKFLOW)
        disciplines = tuple(skill for skill in skills if skill.kind is SkillKind.DISCIPLINE)
        plan = build_projection(
            definition,
            digest,
            workflows,
            excluded_skills=disciplines,
            projection_scope="workflow-only",
            blocked_capabilities=("discipline_private_visibility",),
        )
    else:
        raise ApplicationFailure([Issue("projection.scope", f"unsupported projection scope: {adapter}/{scope}")], 2)
    if isinstance(plan, ProjectionBlocked):
        raise ApplicationFailure([Issue("projection.capability", str(plan.to_dict()))], 3)
    return plan


def _source_bundle():
    import importlib.metadata
    import subprocess
    mapping = {}
    for prefix, root in (("core", CORE), ("templates", TEMPLATES), ("adapters", ADAPTERS), ("reference-projects", REFERENCES)):
        if not root.is_dir():
            raise ApplicationFailure([Issue("resources.missing", f"missing resource tree: {prefix}")])
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                raise ApplicationFailure([Issue("resources.symlink", str(path))])
            if path.is_file():
                logical = f"{prefix}/{path.relative_to(root).as_posix()}"
                mapping[logical] = path.relative_to(PACKAGE).as_posix() if PACKAGED else logical
    try:
        if PACKAGED:
            distribution = importlib.metadata.distribution("research-os")
            return SourceBundle.from_installed_distribution(
                distribution, PACKAGE, mapping, baseline_revision=SOURCE_REVISION,
            )
        repository = CORE.parent
        status = subprocess.run(['git', '-C', str(repository), 'status', '--porcelain', '--untracked-files=all'], capture_output=True)
        if status.returncode or status.stdout.strip():
            raise ApplicationFailure([Issue('resources.dirty_checkout', 'setup requires a clean Git tree or an installed RECORD-verified distribution')])
        revision = subprocess.check_output(['git','-C',str(repository),'rev-parse','HEAD'], text=True).strip()
        return SourceBundle.from_repository(repository, version=__version__, source_revision=revision, include=mapping)
    except (ValueError, OSError, importlib.metadata.PackageNotFoundError) as exc:
        if isinstance(exc, ApplicationFailure):
            raise
        raise ApplicationFailure([Issue('resources.provenance', str(exc))]) from exc


def _verify_bundled_port_attestation(bundle):
    try:
        raw = bundle.files["core/port-release-attestation.json"]
        value = json.loads(raw)
        catalog_bytes = bundle.files["core/catalog.json"]
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApplicationFailure([Issue("ports.bundle_attestation", f"missing or invalid bundled port attestation: {exc}")]) from exc
    expected_keys = {
        "contract", "validator", "inventory", "release", "catalog",
        "acceptance_request", "products", "status", "release_authorized",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise ApplicationFailure([Issue("ports.bundle_attestation", "bundled port attestation has invalid fields")])
    if value["contract"] != {"name": "research-os/port-release-attestation", "version": "1.0.0"}:
        raise ApplicationFailure([Issue("ports.bundle_attestation", "bundled port attestation contract is unsupported")])
    if value["status"] != "pass" or value["release_authorized"] is not True:
        raise ApplicationFailure([Issue("ports.bundle_attestation", "bundled ports are not release-authorized")])
    if value["catalog"] != {
        "path": "core/catalog.json",
        "sha256": hashlib.sha256(catalog_bytes).hexdigest(),
    }:
        raise ApplicationFailure([Issue("ports.bundle_attestation", "bundled port attestation does not bind catalog bytes")])
    catalog = json.loads(catalog_bytes)
    expected_products = {
        f"ports/products/{item['id']}/SKILL.md": item["sha256"]
        for item in catalog["skills"]
        if item["kind"] == "discipline"
    }
    products = {item["path"]: item["sha256"] for item in value["products"]}
    if products != expected_products:
        raise ApplicationFailure([Issue("ports.bundle_attestation", "bundled port products do not bind every canonical discipline")])
    for path, digest in products.items():
        logical = "core/skills/" + path.removeprefix("ports/products/")
        try:
            actual = hashlib.sha256(bundle.files[logical]).hexdigest()
        except KeyError as exc:
            raise ApplicationFailure([Issue("ports.bundle_attestation", f"missing canonical discipline: {logical}")]) from exc
        if actual != digest:
            raise ApplicationFailure([Issue("ports.bundle_attestation", f"canonical discipline differs from accepted port product: {logical}")])


def installation_plan():
    bundle = _source_bundle()
    _verify_bundled_port_attestation(bundle)
    projections = [
        item
        for adapter, scope in (("claude-code", "complete"), ("codex", "workflow-only"))
        for item in _projection_plan(adapter, scope=scope, bundle=bundle).files
    ]
    return build_install_plan(bundle, projections)


def _install_result(result):
    value = result.to_dict()
    if value.get("verdict") != "pass":
        raise ApplicationFailure([Issue(item["code"], item["message"]) for item in value["issues"]], result.exit_code)
    return value


def setup_project(project):
    project.mkdir(parents=True, exist_ok=True)
    return _install_result(execute_install(project, installation_plan()))


def generate_projection(adapter, output):
    from .install import ProjectionFile
    bundle = _source_bundle()
    plan = _projection_plan(adapter, bundle=bundle)
    files = [*plan.files, ProjectionFile('manifest.json', canonical_json(plan.manifest.to_dict()))]
    output.mkdir(parents=True, exist_ok=True)
    _install_result(execute_install(output, build_install_plan(bundle, files)))
    return plan.manifest.to_dict()


def validate_projection(adapter, manifest_path, *, project=None):
    try:
        snapshot = load_projection_snapshot(manifest_path)
    except (OSError, ValueError) as exc:
        return [Issue("projection.read", str(exc))]
    return validate_projection_value(adapter, snapshot.value, manifest_path, project=project)


def validate_projection_value(adapter, manifest, manifest_path, *, project=None):
    try:
        scope = manifest.get("projection_scope") if isinstance(manifest, dict) else None
        plan = _projection_plan(adapter, scope=scope or "complete")
    except ApplicationFailure as exc:
        return exc.issues
    if manifest != plan.manifest.to_dict():
        return [Issue("projection.digest", "projection differs from canonical sources/capability profile")]
    root = project if project is not None else manifest_path.parent
    issues = []
    expected_projection_files = {
        item.path
        for item in plan.files
        if item.path.startswith(".claude/skills/" if adapter == "claude-code" else ".agents/skills/")
    }
    skill_root = Path(root) / (".claude/skills" if adapter == "claude-code" else ".agents/skills")
    if skill_root.exists() or skill_root.is_symlink():
        try:
            actual_projection_files = {
                path.relative_to(root).as_posix()
                for path in skill_root.rglob("*")
                if path.is_file() or path.is_symlink()
            }
            if actual_projection_files != expected_projection_files:
                issues.append(Issue("projection.inventory", "projected skill tree contains missing, extra, or unsafe files"))
        except OSError as exc:
            issues.append(Issue("projection.inventory", str(exc)))
    if adapter == "codex" and plan.manifest.projection_scope == "workflow-only":
        for item in plan.manifest.excluded_canonical_skills:
            relative = f".agents/skills/{item['name']}"
            candidate = Path(root) / relative
            if candidate.exists() or candidate.is_symlink():
                issues.append(Issue("projection.excluded", f"excluded discipline is present in Codex skill directory: {relative}"))
    for item in plan.files:
        try:
            data = resolve_project_path(root, item.path).read_bytes()
            if data != item.content:
                issues.append(Issue("projection.file", f"projection file drift: {item.path}"))
        except (OSError, ValueError) as exc:
            issues.append(Issue("projection.file", str(exc)))
    return issues


def invoke_workflow(workflow, project, request):
    """Request is explicit user input, not a plan. Never invokes the next workflow."""
    from .workflows.outer import InputPin, run_outer_workflow
    from .workflows.outer.models import WORKFLOWS
    from .workflows import computational
    from .workflows.mathematical import run_math_proof, run_lean_formalize
    if not isinstance(request, dict):
        raise ValueError("workflow request must be an object")
    arguments = dict(request)
    if workflow in WORKFLOWS:
        arguments["inputs"] = [InputPin(**pin) for pin in arguments["inputs"]]
        result = run_outer_workflow(workflow, project=project, **arguments)
        return dict(result.report), 0
    computational_calls = {
        "design-experiment": computational.design_experiment,
        "prepare-experiment": computational.prepare_experiment,
        "run-experiment": computational.run_experiment,
        "analyze-experiment": computational.analyze_experiment,
        "assess-result-to-claim": computational.assess_result_to_claim,
    }
    if workflow in computational_calls:
        if workflow == 'analyze-experiment':
            analysis = arguments.pop('analysis_candidate')
            # Fixed candidate data, not an executable model/tool callback from JSON.
            arguments['analyzer'] = lambda data, spec: json.loads(json.dumps(analysis))
        result = computational_calls[workflow](project, **arguments).as_dict()
        success = result["stop_reason"] in {"candidate_created", "preparation_complete", "run_complete", "analysis_complete", "assessment_complete", "workflow_complete"}
        blocked = result['stop_reason'] in {'external_prerequisite_unavailable', 'blocked', 'tooling_blocked'}
        return result, 0 if success else 3 if blocked else 1
    if workflow == "math-proof":
        pin = arguments.pop("statement_input")
        output, report_path = arguments.pop("output"), arguments.pop("report")
        if resolve_project_path(project, output) == resolve_project_path(project, report_path):
            raise FileExistsError('Artifact and report paths must be distinct')
        raw = resolve_project_path(project, pin["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ApplicationFailure([Issue("input.pin", "statement digest mismatch")])
        statement = json.loads(raw)
        if statement.get("type") != {"name": "mathematical-statement", "version": "1.0.0"}:
            raise ApplicationFailure([Issue("input.type", "statement input must be a mathematical-statement Artifact")])
        record = run_math_proof(statement=statement["spec"], **arguments)
        artifact = {"contract": {"name": "research-os/artifact", "version": "1.1.0"},
                    "target": {"kind": "git", "path": output}, "type": {"name": "math-proof-run", "version": "1.0.0"},
                    "spec": record, "provenance": [{"target": statement["target"], "sha256": pin["sha256"], "purpose": "explicit statement input"}]}
        report = {"workflow": workflow, "status": "stopped", "stop_reason": record["stop_reason"],
                  "next_steps": record["next_steps"], "automatic_next_workflow": False,
                  "inputs": [pin], "outputs": [output, report_path]}
        install_workflow_outputs(project, {output: _json_bytes(artifact), report_path: _json_bytes(report)})
        return report, 0 if record["result"] == "candidate" else 1
    if workflow == "lean-formalize":
        pins = {}
        for field in ('statement', 'proof', 'review'):
            pin = arguments.pop(field + '_input')
            raw = resolve_project_path(project, pin['path']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != pin['sha256']:
                raise ApplicationFailure([Issue('input.pin', f'{field} digest mismatch')])
            arguments[field] = json.loads(raw)
            pins[field] = pin
        report_path = arguments.pop('report')
        result = run_lean_formalize(project=project, **arguments)
        report = {**result.report, 'inputs': pins, 'automatic_next_workflow': False}
        install_workflow_outputs(project, {report_path: _json_bytes(report)})
        return report, result.exit_code
    raise ApplicationFailure([Issue("workflow.unavailable", f"no application entrypoint: {workflow}")])


def research_charter(project, input_name, output_name, report_name, *, request_bytes=None):
    # The file contains the complete explicit pinned request, not a loose question.
    request = json.loads(request_bytes) if request_bytes is not None else load_json(resolve_project_path(project, input_name))
    request = {**request, "output_path": output_name, "report_path": report_name}
    if output_name == report_name:
        raise FileExistsError("workflow Artifact and report outputs must be distinct")
    result, code = invoke_workflow("research-charter", project, request)
    if code:
        raise ApplicationFailure([Issue("workflow.failed", str(result))], code)
    return result


def verify_research_charter_execution(project, input_name, output_name, report_name, result, *, request_bytes=None):
    from .workflows.outer.builders import build_research_charter
    from .workflows.outer.models import PinnedInput
    try:
        request = json.loads(request_bytes) if request_bytes is not None else load_json(resolve_project_path(project, input_name))
        pin = request["inputs"][0]
        raw = resolve_project_path(project, pin["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            return [Issue("workflow.input", "host changed pinned input")]
        source = json.loads(raw)
        expected = build_research_charter((PinnedInput("question", pin["path"], pin["sha256"], source),), request.get("candidate"))
        artifact = load_json(resolve_project_path(project, output_name))
        report = load_json(resolve_project_path(project, report_name))
        if artifact["spec"] != dict(expected.spec) or report != result:
            return [Issue("workflow.output", "host changed canonical candidate/report")]
        digest = hashlib.sha256(resolve_project_path(project, output_name).read_bytes()).hexdigest()
        if report["outputs"][0]["sha256"] != digest:
            return [Issue("workflow.artifact", "candidate digest differs from canonical report")]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [Issue("workflow.output", str(exc))]
    return []


def freeze_publication(project, manifest, confirmation, principal):
    from .publication import freeze_publication as freeze
    return freeze(project, manifest, confirmation, principal)
