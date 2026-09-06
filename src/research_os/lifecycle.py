from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.request import urlopen

from .contracts import (
    COMMIT,
    resolve_project_path,
    validate_artifact,
    validate_publication_id,
    validate_target,
)
from .core import (
    _atomic_write_project,
    _json_bytes,
    _unlink_project_file,
    load_json,
    setup_project,
)


class LifecycleFailure(ValueError):
    pass


class TargetUnavailable(OSError):
    pass


def git(project: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(project), *args], capture_output=True, timeout=60
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise TargetUnavailable("Git is unavailable or timed out") from exc
    if result.returncode:
        raise LifecycleFailure(result.stderr.decode(errors="replace"))
    return result.stdout


def git_path_ignored(project: Path, path: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(project), "check-ignore", "-q", "--", path],
            capture_output=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise TargetUnavailable("Git is unavailable or timed out") from exc
    if result.returncode not in {0, 1}:
        raise LifecycleFailure(result.stderr.decode(errors="replace"))
    return result.returncode == 0


def update_project(project: Path, environment: str) -> dict:
    from .core import installation_plan, _install_result
    from .install import execute_install, verify_install
    _, issues = verify_install(project)
    if issues:
        raise LifecycleFailure(str(issues))
    return _install_result(execute_install(project, installation_plan(), environment=environment))


def _git_prefix(project: Path) -> str:
    prefix = git(project, "rev-parse", "--show-prefix").decode().strip().rstrip("/")
    return f"{prefix}/" if prefix else ""


def _project_tree_path(project: Path, path: str) -> str:
    return f"{_git_prefix(project)}{path}"


def export_project(project: Path, commit: str, output: Path) -> dict:
    from .history import restore_history
    if output.is_symlink():
        raise LifecycleFailure("history output must not be a symlink")
    result = restore_history(project, commit, output)
    value = result.to_dict()
    if value["verdict"] != "pass":
        raise LifecycleFailure(str(value["issues"]))
    return value


def read_target(project: Path, target: object, *, pinned: bool = True) -> bytes:
    issues = validate_target(target)
    if issues:
        raise LifecycleFailure("; ".join(issue.message for issue in issues))
    if (target["kind"] == "uri" or target.get("repository")) and os.environ.get(
        "RESEARCH_OS_OFFLINE"
    ) == "1":
        raise TargetUnavailable("external target unavailable while offline")
    if target["kind"] == "uri":
        try:
            with urlopen(target["uri"], timeout=15) as response:
                data = response.read()
        except OSError as exc:
            raise TargetUnavailable(str(exc)) from exc
        if hashlib.sha256(data).hexdigest() != target["sha256"]:
            raise LifecycleFailure("URI SHA-256 drift")
        return data
    commit = target.get("commit")
    if pinned and not commit:
        raise LifecycleFailure("workflow input must use a pinned target")
    repository = target.get("repository")
    if repository:
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory)
            git(checkout, "init", "--bare", "-q")
            try:
                git(
                    checkout,
                    "-c",
                    "protocol.file.allow=never",
                    "fetch",
                    repository,
                    commit,
                )
            except LifecycleFailure as exc:
                raise TargetUnavailable(str(exc)) from exc
            return _read_git_blob(checkout, commit, target["path"])
    if commit:
        return _read_git_blob(project, commit, target["path"])
    return resolve_project_path(project, target["path"]).read_bytes()


def _read_git_blob(project: Path, commit: str, path: str) -> bytes:
    if git(project, "cat-file", "-t", commit).strip() != b"commit":
        raise LifecycleFailure("revision must identify a commit object")
    tree_path = _project_tree_path(project, path)
    entry = (
        git(project, "ls-tree", "--full-tree", commit, "--", tree_path).decode().strip()
    )
    if not entry.startswith(("100644 blob ", "100755 blob ")):
        raise LifecycleFailure(
            "target must identify a regular Git file, not directory or symlink"
        )
    return git(project, "show", f"{commit}:{tree_path}")


def preflight_new_files(project: Path, names: list[str]) -> None:
    if len(set(names)) != len(names):
        raise LifecycleFailure("output files must be distinct")
    for name in names:
        path = resolve_project_path(project, name)
        if path.exists():
            raise FileExistsError(name)
        if any(part.casefold() == ".git" for part in name.split("/")):
            raise LifecycleFailure("reserved Git metadata path")
        if name.split("/")[0].casefold() in {
            "publications",
            "runs",
            ".research-os",
            ".claude",
            ".agents",
        }:
            raise LifecycleFailure("reserved output path")
        if any(other.startswith(name + "/") for other in names):
            raise LifecycleFailure("output file cannot also be an output directory")
        parent = project / name
        while parent != project:
            if parent.is_symlink():
                raise LifecycleFailure("output paths must not contain symlinks")
            if parent != project / name and parent.exists() and not parent.is_dir():
                raise LifecycleFailure("output parent must be a directory")
            parent = parent.parent


def write_new_files(project: Path, files: dict[str, bytes]) -> None:
    preflight_new_files(project, list(files))
    written = []
    try:
        for name, data in files.items():
            _atomic_write_project(project, name, data)
            written.append(name)
    except Exception:
        for name in reversed(written):
            _unlink_project_file(project, name)
        raise


def _project_parent_directories(project: Path, names: list[str]) -> set[Path]:
    directories: set[Path] = set()
    for name in names:
        parent = resolve_project_path(project, name).parent
        while parent != project:
            if parent.exists():
                directories.add(parent)
            parent = parent.parent
    return directories


def _remove_new_empty_parents(
    project: Path, names: list[str], existing: set[Path]
) -> None:
    parents = {
        parent
        for name in names
        for parent in resolve_project_path(project, name).parents
        if parent != project and project in parent.parents and parent not in existing
    }
    for parent in sorted(parents, key=lambda path: len(path.parts), reverse=True):
        try:
            parent.rmdir()
        except (FileNotFoundError, OSError):
            pass


def _rollback_migration(
    project: Path,
    revision: str,
    names: list[str],
    existing_parents: set[Path],
) -> None:
    git(project, "reset", "--mixed", revision)
    for name in names:
        _unlink_project_file(project, name)
    _remove_new_empty_parents(project, names, existing_parents)


def migrate_artifact(
    project: Path,
    input_name: str,
    rules_name: str,
    contract_version: str,
    type_version: str,
    output_name: str,
    receipt_name: str,
) -> dict:
    if git(project, "status", "--porcelain").strip():
        raise LifecycleFailure("migration requires a clean Git project")
    preflight_new_files(project, [output_name, receipt_name])
    target = load_json(resolve_project_path(project, input_name))
    artifact = json.loads(read_target(project, target))
    if validate_artifact(artifact):
        raise LifecycleFailure("migration input validation failed")
    rules = load_json(resolve_project_path(project, rules_name))
    if not isinstance(rules, list) or any(not isinstance(rule, dict) for rule in rules):
        raise LifecycleFailure("rules must be an array of objects")
    source = {
        "contract": artifact["contract"]["version"],
        "type": artifact["type"]["name"],
        "version": artifact["type"]["version"],
    }
    destination = {
        "contract": contract_version,
        "type": artifact["type"]["name"],
        "version": type_version,
    }
    matches = [
        rule
        for rule in rules
        if rule.get("source") == source and rule.get("destination") == destination
    ]
    if len(matches) != 1:
        raise LifecycleFailure("migration requires exactly one matching rule")
    rule = matches[0]
    from .contracts import is_exact_semver

    if (
        not rule.get("name")
        or not is_exact_semver(rule.get("version"))
        or rule.get("operation") != "preserve-spec"
    ):
        raise LifecycleFailure("unsupported migration rule")
    output = {
        **artifact,
        "contract": {"name": "research-os/artifact", "version": contract_version},
        "type": {"name": artifact["type"]["name"], "version": type_version},
        "target": {"kind": "git", "path": output_name},
    }
    output.pop("assurance", None)
    output["provenance"] = [
        *artifact.get("provenance", []),
        {"target": target, "purpose": "migration input"},
    ]
    if validate_artifact(output):
        raise LifecycleFailure("migration output validation failed")
    if git_path_ignored(project, output_name) or git_path_ignored(
        project, receipt_name
    ):
        raise LifecycleFailure("migration output and receipt must not be ignored")
    names = [output_name, receipt_name]
    original_revision = git(project, "rev-parse", "HEAD").decode().strip()
    existing_parents = _project_parent_directories(project, names)
    try:
        write_new_files(project, {output_name: _json_bytes(output)})
        git(project, "add", "--", output_name)
        git(project, "commit", "-m", "迁移 Artifact，保留旧固定版本", "--", output_name)
        revision = git(project, "rev-parse", "HEAD").decode().strip()
        receipt = {
            "contract": {"name": "research-os/migration-receipt", "version": "1.0.0"},
            "input": target,
            "output": {**output["target"], "commit": revision},
            "source": source,
            "destination": destination,
            "rule": rule,
            "migrator": {"name": "preserve-spec", "version": "1.0.0"},
            "input_validator": {
                "name": "artifact",
                "version": "1.0.0",
                "verdict": "pass",
            },
            "output_validator": {
                "name": "artifact",
                "version": "1.0.0",
                "verdict": "pass",
            },
        }
        write_new_files(project, {receipt_name: _json_bytes(receipt)})
        git(project, "add", "--", receipt_name)
        git(project, "commit", "-m", "记录固定迁移回执", "--", receipt_name)
    except Exception:
        _rollback_migration(project, original_revision, names, existing_parents)
        raise
    return {
        "status": "stopped",
        "receipt": receipt_name,
        "output": receipt["output"],
        "next_steps": [],
    }
