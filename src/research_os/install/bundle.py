from __future__ import annotations

import base64
import csv
import io
import json
import os
import re
import secrets
import subprocess
import tarfile
import stat
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Iterable, Mapping

from .model import ProjectionFile, canonical_json, digest_bytes

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_PROJECT_FILES = frozenset(
    {
        "pyproject.toml",
        "uv.lock",
        "requirements.txt",
        "requirements-dev.txt",
        "poetry.lock",
        "pdm.lock",
        "Pipfile",
        "Pipfile.lock",
        "environment.yml",
        "environment.yaml",
        "conda-lock.yml",
        ".python-version",
    }
)
FORBIDDEN_PROJECT_PREFIXES = (
    ".research-os/runtime/",
    ".research-os/lock",
    ".venv/",
    "venv/",
)


def _safe_relative_file(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or value.endswith("/"):
        raise ValueError("bundle path must be a relative file path")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe bundle path: {value}")
    normalized = path.as_posix()
    if normalized in FORBIDDEN_PROJECT_FILES or normalized.startswith(FORBIDDEN_PROJECT_PREFIXES):
        raise ValueError(f"project runtime or lockfile is forbidden: {normalized}")
    return normalized


def _path_has_symlink(path: Path, boundary: Path) -> bool:
    current = path
    while True:
        if current.is_symlink():
            return True
        if current == boundary:
            return False
        if boundary not in current.parents:
            return True
        current = current.parent


def _regular_file(path: Path, *, subject: str, boundary: Path | None = None) -> bytes:
    if boundary is not None and _path_has_symlink(path, boundary):
        raise ValueError(f"{subject} traverses a symlink: {path}")
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{subject} must be a regular file: {path}")
    return path.read_bytes()


def _safe_install_destination(root: Path, name: str) -> Path:
    path = root / name
    if _path_has_symlink(path, root):
        raise ValueError(f"install path traverses a symlink: {name}")
    try:
        root_resolved = root.resolve(strict=True)
        parent_resolved = path.parent.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"install path parent is unavailable: {name}") from exc
    if parent_resolved != root_resolved and root_resolved not in parent_resolved.parents:
        raise ValueError(f"install path escapes project boundary: {name}")
    return path


@contextmanager
def _directory_fd(path: Path, *, create: bool = False):
    """Walk a canonical absolute path without following any symlink component."""
    if not path.is_absolute():
        raise ValueError("directory must be absolute")
    descriptor = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in path.parts[1:]:
            if component in {".", ".."}:
                raise ValueError("unsafe directory component")
            if create:
                try:
                    os.mkdir(component, dir_fd=descriptor)
                except FileExistsError:
                    pass
            child = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor
            )
            os.close(descriptor)
            descriptor = child
        yield descriptor
    finally:
        os.close(descriptor)


def _check_directory_identity(path: Path, descriptor: int) -> None:
    with _directory_fd(path) as current:
        before, after = os.fstat(descriptor), os.fstat(current)
        if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
            raise ValueError(f"directory changed during write: {path}")


def _publish_noreplace(source: str, destination: str, *, source_fd: int, parent_fd: int) -> None:
    os.link(source, destination, src_dir_fd=source_fd, dst_dir_fd=parent_fd, follow_symlinks=False)


def _same_inode(left, right) -> bool:
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


def _atomic_write(path: Path, content: bytes, *, boundary: Path) -> None:
    path.relative_to(boundary)
    staging = f".install-{secrets.token_hex(16)}"
    with _directory_fd(path.parent, create=True) as parent:
        os.mkdir(staging, mode=0o700, dir_fd=parent)
        private = os.open(staging, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            descriptor = os.open(
                "payload", os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o644, dir_fd=private,
            )
            with os.fdopen(descriptor, "w+b") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
                token = os.fstat(stream.fileno())
                _check_directory_identity(path.parent, parent)
                _publish_noreplace("payload", path.name, source_fd=private, parent_fd=parent)
                published = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
                with os.fdopen(published, "rb") as installed:
                    if not _same_inode(token, os.fstat(installed.fileno())) or installed.read() != content:
                        raise ValueError(f"install destination changed during publish: {path}")
                _check_directory_identity(path.parent, parent)
                # Only the private 0700 staging is cleaned. This assumes no
                # malicious same-UID actor; public destination names stay intact.
                payload_token = os.stat("payload", dir_fd=private, follow_symlinks=False)
                staging_token = os.stat(staging, dir_fd=parent, follow_symlinks=False)
                stream.seek(0)
                if not _same_inode(token, payload_token) or stream.read() != content or not _same_inode(
                    os.fstat(private), staging_token
                ):
                    raise ValueError(f"staging identity changed; inspect {path.parent / staging}")
                os.unlink("payload", dir_fd=private)
                os.rmdir(staging, dir_fd=parent)
        except (OSError, ValueError) as exc:
            raise ValueError(f"{exc}; inspect private staging {path.parent / staging}") from exc
        finally:
            os.close(private)


def _canonical_resource_name(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or path.as_posix() != value or "\\" in value or ".." in path.parts:
        raise ValueError(f"unsafe or aliased resource path: {value}")
    return value


def _located_record_path(distribution, name: str) -> Path:
    if not name or PurePosixPath(name).is_absolute() or "\\" in name:
        raise ValueError(f"unsafe RECORD path: {name}")
    parts = name.split("/")
    if any(part in {"", "."} for part in parts):
        raise ValueError(f"aliased RECORD path: {name}")
    # Installed console scripts legitimately use leading ../../../bin entries.
    suffix = parts[:]
    while suffix and suffix[0] == "..":
        suffix.pop(0)
    if not suffix or ".." in suffix:
        raise ValueError(f"aliased RECORD traversal: {name}")
    if parts[0] == "..":
        # The only cross-site installed-layout exception is a venv console
        # script. It is verified as non-resource and never copied or executed.
        base = Path(distribution.locate_file("")).absolute()
        prefix = base.parent.parent.parent
        if (
            parts[:3] != ["..", "..", ".."] or len(parts) != 5
            or parts[3] != "bin" or base.name != "site-packages"
            or not base.parent.name.startswith("python") or base.parent.parent.name != "lib"
            or not (prefix / "pyvenv.cfg").is_file()
        ):
            raise ValueError(f"external RECORD path is not an installed console script: {name}")
    located = Path(distribution.locate_file(name)).absolute()
    # Validate every existing traversal component before lexical normalization.
    current = Path(located.anchor)
    for component in located.parts[1:]:
        if component == "..":
            current = current.parent
        else:
            current /= component
            if current.is_symlink():
                raise ValueError(f"RECORD traverses a symlink: {name}")
    return current


def _required_packaged_bytes(path: Path) -> bytes:
    content = _preflight_bytes(path)
    if content is None:
        raise ValueError(f"missing packaged file: {path}")
    return content


@dataclass(frozen=True, slots=True)
class SourceBundle:
    version: str
    source_revision: str | None
    files: Mapping[str, bytes]
    source_verified: bool = field(default=False, init=False, repr=False)
    provenance: Mapping[str, object] | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        if not SEMVER.fullmatch(self.version):
            raise ValueError("bundle version must be exact SemVer")
        if self.source_revision is not None and not re.fullmatch(r"[0-9a-f]{40}", self.source_revision):
            raise ValueError("source_revision must be a full lowercase Git object ID")
        normalized: dict[str, bytes] = {}
        for name, content in self.files.items():
            path = _safe_relative_file(name)
            if not isinstance(content, bytes):
                raise ValueError(f"bundle content must be bytes: {path}")
            normalized[path] = content
        if not normalized:
            raise ValueError("source bundle must contain at least one file")
        object.__setattr__(self, "files", MappingProxyType(dict(sorted(normalized.items()))))

    @classmethod
    def from_directory(
        cls,
        root: Path,
        *,
        version: str,
        source_revision: str,
        include: Iterable[str],
    ) -> SourceBundle:
        root = root.resolve(strict=True)
        files: dict[str, bytes] = {}
        for selected in sorted(set(include)):
            name = _safe_relative_file(selected)
            files[name] = _regular_file(
                root / name,
                subject="bundle source",
                boundary=root,
            )
        return cls(
            version=version,
            source_revision=source_revision,
            files=files,
        )

    @classmethod
    def from_repository(
        cls,
        repository: Path,
        *,
        version: str,
        source_revision: str,
        include: Iterable[str],
    ) -> SourceBundle:
        try:
            repository = repository.resolve(strict=True)
        except OSError as exc:
            raise ValueError("source repository is unavailable") from exc
        if not (repository / ".git").exists():
            check = subprocess.run(
                ["git", "-C", str(repository), "rev-parse", "--git-dir"],
                check=False,
                capture_output=True,
            )
            if check.returncode:
                raise ValueError("source must be a Git repository")
        resolved = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "--verify", f"{source_revision}^{{commit}}"],
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        if resolved.returncode or resolved.stdout.strip() != source_revision:
            raise ValueError("source_revision must resolve exactly to a local commit")
        selected: list[str] = []
        for item in sorted(set(include)):
            selected.append(_safe_relative_file(item))
        if not selected:
            raise ValueError("source bundle must contain at least one file")
        result = subprocess.run(
            ["git", "-C", str(repository), "archive", "--format=tar", source_revision, *selected],
            check=False,
            capture_output=True,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        if result.returncode:
            raise ValueError(result.stderr.decode("utf-8", errors="replace").strip() or "git archive failed")
        files: dict[str, bytes] = {}
        with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
            for member in archive.getmembers():
                if member.isdir():
                    continue
                name = _safe_relative_file(member.name)
                if not member.isfile():
                    raise ValueError(f"source contains a non-regular file: {name}")
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError(f"cannot read pinned source file: {name}")
                files[name] = stream.read()
        if set(files) != set(selected):
            missing = ", ".join(sorted(set(selected) - set(files)))
            raise ValueError(f"pinned source inventory is incomplete: {missing}")
        bundle = cls(version=version, source_revision=source_revision, files=files)
        object.__setattr__(bundle, "source_verified", True)
        return bundle

    @classmethod
    def from_installed_distribution(
        cls, distribution, package_root: Path, logical_mapping: Mapping[str, str | Path],
        *, baseline_revision: str | None = None,
    ) -> SourceBundle:
        """Verify installed RECORD bytes; this is artifact integrity, not Git identity."""
        package_root = package_root.absolute()
        with _directory_fd(package_root):
            pass
        entries = distribution.files
        if not entries:
            raise ValueError("installed distribution has no RECORD inventory")
        records = [entry for entry in entries if str(entry).endswith(".dist-info/RECORD")]
        if len(records) != 1:
            raise ValueError("distribution must contain exactly one RECORD")
        record_path = _located_record_path(distribution, str(records[0]))
        raw_record = _required_packaged_bytes(record_path)
        rows = list(csv.reader(io.StringIO(raw_record.decode("utf-8")), strict=True))
        inventory: dict[Path, bytes] = {}
        names: set[str] = set()
        inode_names: set[tuple[int, int]] = set()
        for row in rows:
            if len(row) != 3:
                raise ValueError("RECORD row must contain path, hash, size")
            name, encoded_hash, size = row
            if name in names:
                raise ValueError(f"duplicate RECORD entry: {name}")
            names.add(name)
            path = _located_record_path(distribution, name)
            if path in inventory:
                raise ValueError(f"aliased RECORD entry: {name}")
            content = _required_packaged_bytes(path)
            token = path.stat(follow_symlinks=False)
            inode = (token.st_dev, token.st_ino)
            if inode in inode_names:
                raise ValueError(f"hardlinked RECORD alias: {name}")
            inode_names.add(inode)
            if path == record_path:
                if encoded_hash or size or content != raw_record:
                    raise ValueError("RECORD self entry must have empty hash and size")
            else:
                expected = "sha256=" + base64.urlsafe_b64encode(bytes.fromhex(digest_bytes(content))).rstrip(b"=").decode("ascii")
                if encoded_hash != expected or size != str(len(content)):
                    raise ValueError(f"RECORD sha256/size mismatch: {name}")
            if path.suffix == ".pth" or "editable" in path.name.lower():
                raise ValueError("editable distributions are not packaged artifacts")
            if path.name == "direct_url.json":
                direct_url = json.loads(content)
                if direct_url.get("dir_info", {}).get("editable"):
                    raise ValueError("editable distributions are not packaged artifacts")
            inventory[path] = content
        if set(str(entry) for entry in entries) != names or record_path not in inventory:
            raise ValueError("RECORD inventory is incomplete")
        metadata_path = record_path.parent / "METADATA"
        if metadata_path not in inventory or record_path.parent / "WHEEL" not in inventory:
            raise ValueError("distribution lacks recorded METADATA/WHEEL")
        from email.parser import BytesParser
        metadata = BytesParser().parsebytes(inventory[metadata_path])
        distribution_name, version = metadata.get("Name"), metadata.get("Version")
        if not distribution_name or not version or distribution_name != distribution.metadata["Name"] or version != distribution.version:
            raise ValueError("distribution identity does not match recorded METADATA")
        files: dict[str, bytes] = {}
        mapped: set[Path] = set()
        resources: dict[str, str] = {}
        critical_roots = {"_core", "_adapters", "_templates", "_reference_projects"}
        for logical, selected in logical_mapping.items():
            logical = _canonical_resource_name(logical)
            _safe_relative_file(logical)
            selected = _canonical_resource_name(str(selected))
            path = package_root / selected
            if path in mapped:
                raise ValueError(f"logical resource alias: {selected}")
            if path not in inventory:
                raise ValueError(f"resource is absent from RECORD: {selected}")
            content = _required_packaged_bytes(path)
            if content != inventory[path]:
                raise ValueError(f"resource changed after RECORD verification: {selected}")
            mapped.add(path)
            files[logical] = content
            resources[logical] = digest_bytes(content)
        for resource_root in critical_roots:
            subtree = package_root / resource_root
            if subtree.is_symlink():
                raise ValueError(f"symlinked resource root: {resource_root}")
            if subtree.exists():
                if not subtree.is_dir():
                    raise ValueError(f"critical resource root must be a directory: {subtree}")
                for path in subtree.rglob("*"):
                    token = path.lstat()
                    if stat.S_ISDIR(token.st_mode):
                        continue
                    if not stat.S_ISREG(token.st_mode) or path not in mapped:
                        raise ValueError(f"undeclared or non-regular critical resource: {path}")
        for path in inventory:
            if path.is_relative_to(package_root) and path.relative_to(package_root).parts[0] in critical_roots and path not in mapped:
                raise ValueError(f"unmapped recorded critical resource: {path}")
        bundle = cls(version=version, source_revision=None, files=files)
        provenance = {
            "profile": "packaged-artifact",
            "distribution_name": distribution_name,
            "distribution_version": version,
            "record_digest": digest_bytes(raw_record),
            "resource_inventory_digest": digest_bytes(canonical_json(resources)),
            "baseline_revision": baseline_revision,
            "non_resource_record_count": len(inventory) - len(mapped),
        }
        _validate_packaged_provenance(provenance)
        object.__setattr__(bundle, "provenance", MappingProxyType(provenance))
        object.__setattr__(bundle, "source_verified", True)
        return bundle


def _validate_packaged_provenance(value: Mapping[str, object]) -> None:
    if set(value) != {"profile", "distribution_name", "distribution_version", "record_digest",
                      "resource_inventory_digest", "baseline_revision", "non_resource_record_count"}:
        raise ValueError("invalid packaged provenance fields")
    if value["profile"] != "packaged-artifact" or not isinstance(value["distribution_name"], str) or not value["distribution_name"]:
        raise ValueError("invalid packaged provenance identity")
    if not isinstance(value["distribution_version"], str) or not SEMVER.fullmatch(value["distribution_version"]):
        raise ValueError("invalid packaged provenance version")
    for name in ("record_digest", "resource_inventory_digest"):
        if not isinstance(value[name], str) or not SHA256.fullmatch(value[name]):
            raise ValueError(f"invalid packaged provenance {name}")
    baseline = value["baseline_revision"]
    if baseline is not None and (not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-f]{40}", baseline)):
        raise ValueError("baseline_revision must be informational full Git revision or null")
    if type(value["non_resource_record_count"]) is not int or value["non_resource_record_count"] < 0:
        raise ValueError("invalid non-resource RECORD count")


@dataclass(frozen=True, slots=True)
class InstallManifest:
    version: str
    source_revision: str | None
    files: Mapping[str, str]
    bundle_digest: str
    provenance: Mapping[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        value = {
            "contract": {"name": "research-os/install-manifest", "version": "1.0.0"},
            "version": self.version,
            "source_revision": self.source_revision,
            "files": dict(self.files),
            "bundle_digest": self.bundle_digest,
            "runtime": "none",
            "lockfile": "none",
            "activation": "explicit",
        }
        if self.provenance is not None:
            value["provenance"] = dict(self.provenance)
        return value

    @classmethod
    def from_bytes(cls, raw: bytes) -> InstallManifest:
        try:
            value = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("install manifest is not valid UTF-8 JSON") from exc
        if not isinstance(value, dict) or set(value) - {"provenance"} != {
            "contract",
            "version",
            "source_revision",
            "files",
            "bundle_digest",
            "runtime",
            "lockfile",
            "activation",
        }:
            raise ValueError("install manifest has invalid fields")
        if "provenance" in value and not isinstance(value["provenance"], dict):
            raise ValueError("install provenance must be an object")
        if value["contract"] != {"name": "research-os/install-manifest", "version": "1.0.0"}:
            raise ValueError("install manifest contract is unsupported")
        if value["runtime"] != "none" or value["lockfile"] != "none" or value["activation"] != "explicit":
            raise ValueError("install manifest requests a forbidden runtime, lockfile, or activation")
        if not isinstance(value["files"], dict):
            raise ValueError("install manifest files must be an object")
        files: dict[str, str] = {}
        for name, digest in value["files"].items():
            normalized = _safe_relative_file(name)
            if not isinstance(digest, str) or not SHA256.fullmatch(digest):
                raise ValueError(f"invalid digest for {normalized}")
            files[normalized] = digest
        manifest = cls(
            version=value["version"],
            source_revision=value["source_revision"],
            files=MappingProxyType(dict(sorted(files.items()))),
            bundle_digest=value["bundle_digest"],
            provenance=MappingProxyType(value["provenance"]) if isinstance(value.get("provenance"), dict) else None,
        )
        if not SEMVER.fullmatch(manifest.version):
            raise ValueError("install manifest version must be exact SemVer")
        if manifest.provenance is not None:
            _validate_packaged_provenance(manifest.provenance)
            if manifest.source_revision is not None or manifest.version != manifest.provenance["distribution_version"]:
                raise ValueError("packaged manifest must not claim an exact Git revision")
        elif not isinstance(manifest.source_revision, str) or not re.fullmatch(r"[0-9a-f]{40}", manifest.source_revision):
            raise ValueError("install manifest source_revision is invalid")
        if not isinstance(manifest.bundle_digest, str) or not SHA256.fullmatch(manifest.bundle_digest):
            raise ValueError("install manifest bundle_digest is invalid")
        unsigned = {
            "version": manifest.version,
            "source_revision": manifest.source_revision,
            "files": dict(manifest.files),
        }
        if manifest.provenance is not None:
            unsigned["provenance"] = dict(manifest.provenance)
        if digest_bytes(canonical_json(unsigned)) != manifest.bundle_digest:
            raise ValueError("install manifest bundle_digest does not match inventory")
        return manifest


@dataclass(frozen=True, slots=True)
class InstallPlan:
    manifest: InstallManifest
    files: tuple[ProjectionFile, ...]


@dataclass(frozen=True, slots=True)
class InstallBlocked:
    issues: tuple[dict[str, str], ...]
    exit_code: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": {"name": "research-os/install-result", "version": "1.0.0"},
            "verdict": "fail",
            "status": "stopped",
            "stop_reason": "install_preflight_failed",
            "issues": [dict(issue) for issue in self.issues],
            "outputs": [],
            "next_steps": [],
        }


@dataclass(frozen=True, slots=True)
class InstallResult:
    manifest: InstallManifest
    installed_files: tuple[str, ...]
    preserved_files: tuple[str, ...]
    environment: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "contract": {"name": "research-os/install-result", "version": "1.0.0"},
            "verdict": "pass",
            "status": "stopped",
            "stop_reason": "installed_explicit_activation_required" if self.environment else "setup_complete",
            "version": self.manifest.version,
            "source_revision": self.manifest.source_revision,
            "environment": self.environment,
            "installed_files": list(self.installed_files),
            "preserved_files": list(self.preserved_files),
            "runtime": "none",
            "lockfile": "none",
            "next_steps": [],
        }


def build_install_plan(
    bundle: SourceBundle,
    extra_files: Iterable[ProjectionFile] = (),
    *,
    require_verified_source: bool = True,
) -> InstallPlan:
    if require_verified_source and not bundle.source_verified:
        raise ValueError("install source has no mechanically verified provenance")
    files = {name: content for name, content in bundle.files.items()}
    for item in extra_files:
        name = _safe_relative_file(item.path)
        existing = files.get(name)
        if existing is not None and existing != item.content:
            raise ValueError(f"duplicate install path has different bytes: {name}")
        files[name] = item.content
    digests = {name: digest_bytes(content) for name, content in sorted(files.items())}
    unsigned = {"version": bundle.version, "source_revision": bundle.source_revision, "files": digests}
    if bundle.provenance is not None:
        unsigned["provenance"] = dict(bundle.provenance)
    manifest = InstallManifest(
        version=bundle.version,
        source_revision=bundle.source_revision,
        files=MappingProxyType(digests),
        bundle_digest=digest_bytes(canonical_json(unsigned)),
        provenance=bundle.provenance,
    )
    payload = tuple(ProjectionFile(path=name, content=content) for name, content in sorted(files.items()))
    return InstallPlan(manifest=manifest, files=payload)


def _destination(project: Path, environment: str | None) -> tuple[Path, str]:
    if environment is None:
        return project, ".research-os/install-manifest.json"
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", environment):
        raise ValueError("environment name is invalid")
    prefix = f".research-os/environments/{environment}"
    return project / prefix, f"{prefix}/.research-os/install-manifest.json"


def _preflight_bytes(path: Path) -> bytes | None:
    try:
        with _directory_fd(path.parent) as parent:
            try:
                expected = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                return None
            if not stat.S_ISREG(expected.st_mode):
                raise ValueError(f"install path must be a regular file: {path}")
            try:
                descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
            except FileNotFoundError as exc:
                raise ValueError(f"install file disappeared during preflight: {path}") from exc
            with os.fdopen(descriptor, "rb") as stream:
                token = os.fstat(stream.fileno())
                if not stat.S_ISREG(token.st_mode) or not _same_inode(expected, token):
                    raise ValueError(f"install file changed during preflight: {path}")
                content = stream.read()
                try:
                    current = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                    _check_directory_identity(path.parent, parent)
                except FileNotFoundError as exc:
                    raise ValueError(f"install file disappeared during preflight: {path}") from exc
                if not _same_inode(token, current):
                    raise ValueError(f"install file changed during preflight: {path}")
                return content
    except FileNotFoundError:
        # Only an absent directory is an absent destination. File-open races
        # above are deliberately converted to failures rather than new installs.
        return None


def execute_install(
    project: Path,
    plan: InstallPlan,
    *,
    environment: str | None = None,
) -> InstallResult | InstallBlocked:
    try:
        project = project.resolve(strict=True)
    except OSError as exc:
        return InstallBlocked(({"code": "install.project", "message": str(exc)},))
    if not project.is_dir():
        return InstallBlocked(
            ({"code": "install.project", "message": "project must be an existing directory"},)
        )
    try:
        root, manifest_relative = _destination(project, environment)
    except ValueError as exc:
        return InstallBlocked(({"code": "install.environment", "message": str(exc)},))
    desired = {item.path: item.content for item in plan.files}
    desired[manifest_relative if environment is None else ".research-os/install-manifest.json"] = canonical_json(
        plan.manifest.to_dict()
    )
    conflicts: list[dict[str, str]] = []
    installed: list[str] = []
    preserved: list[str] = []
    for name, content in desired.items():
        path = root / name
        try:
            existing = _preflight_bytes(path)
        except (OSError, ValueError) as exc:
            conflicts.append({"code": "install.preflight", "message": str(exc)})
            continue
        if existing is None:
            installed.append(name)
        elif existing == content:
            preserved.append(name)
        else:
            conflicts.append({"code": "install.conflict", "message": f"existing file has different bytes: {name}"})
    if conflicts:
        return InstallBlocked(tuple(conflicts))
    attempted: list[Path] = []
    try:
        for name in installed:
            path = root / name
            attempted.append(path)
            _atomic_write(path, desired[name], boundary=project)
    except (OSError, ValueError) as exc:
        # Neither POSIX unlinkat nor the supported platforms offer an atomic
        # inode-and-bytes-conditional unlink. Even a matching token followed by
        # unlink could delete a concurrent replacement. Keep public names intact.
        return InstallBlocked((
            {"code": "install.write", "message": str(exc)},
            {
                "code": "install.cleanup_required",
                "message": "No rollback deletion attempted; inspect possibly partial paths: "
                + ", ".join(str(path) for path in attempted),
            },
        ))
    prefix = "" if environment is None else f".research-os/environments/{environment}/"
    return InstallResult(
        manifest=plan.manifest,
        installed_files=tuple(prefix + name for name in installed),
        preserved_files=tuple(prefix + name for name in preserved),
        environment=None if environment is None else f".research-os/environments/{environment}",
    )


def verify_install(project: Path, *, environment: str | None = None) -> tuple[InstallManifest | None, tuple[dict[str, str], ...]]:
    project = project.resolve(strict=True)
    try:
        root, manifest_relative = _destination(project, environment)
    except ValueError as exc:
        return None, ({"code": "install.manifest", "message": str(exc)},)
    manifest_path = project / manifest_relative
    issues: list[dict[str, str]] = []
    try:
        raw = _regular_file(
            manifest_path,
            subject="install manifest",
            boundary=project,
        )
        manifest = InstallManifest.from_bytes(raw)
    except (OSError, ValueError) as exc:
        return None, ({"code": "install.manifest", "message": str(exc)},)
    for name, expected in manifest.files.items():
        path = root / name
        try:
            actual = digest_bytes(
                _regular_file(path, subject="installed file", boundary=root)
            )
        except (OSError, ValueError) as exc:
            issues.append({"code": "install.file", "message": str(exc)})
            continue
        if actual != expected:
            issues.append({"code": "install.drift", "message": f"installed file digest mismatch: {name}"})
    return manifest, tuple(issues)
