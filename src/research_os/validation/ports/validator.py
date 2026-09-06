from __future__ import annotations

import hashlib
import json
import re
import stat
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from ..foundation.schema import LocalSchemaValidator

VERSION = "1.0.0"
FIXTURE = "fixture-only/not-shippable"
# Conservative v1 SPDX profile, not a claim to implement the entire SPDX grammar.
# Expanding the profile requires an explicit contract/validator revision.
SPDX_IDS = frozenset({
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0",
    "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later",
    "LGPL-2.1-only", "LGPL-2.1-or-later", "LGPL-3.0-only", "LGPL-3.0-or-later",
    "AGPL-3.0-only", "AGPL-3.0-or-later", "CC0-1.0", "CC-BY-4.0",
    "CC-BY-SA-4.0", "Unlicense", "LicenseRef-ResearchOS-Fixture-Only",
})


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def tree_digest(files: list[dict[str, str]]) -> str:
    """Hash sorted relative paths and SHA-256s, not platform metadata or mtimes."""
    return hashlib.sha256(_canonical(sorted(files, key=lambda item: item["path"]))).hexdigest()


def _path(value: object) -> bool:
    return (
        isinstance(value, str) and bool(value) and not value.startswith("/")
        and all(part not in {"", ".", ".."} for part in value.split("/"))
        and not any(ord(char) < 32 or char in "\\:?#%" or ord(char) == 127 for char in value)
        and value == value.strip()
    )


def _time(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False


def _url(value: object) -> bool:
    if not isinstance(value, str) or any(char.isspace() for char in value):
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
                and not parsed.password and not parsed.query and not parsed.fragment
                and parsed.port in {None, 443} and "\\" not in value)
    except ValueError:
        return False


def _spdx(value: object) -> bool:
    if not isinstance(value, str):
        return False
    # V1 accepts one listed identifier, or a flat same-operator AND/OR expression.
    parts = re.split(r" (AND|OR) ", value)
    return (all(item in SPDX_IDS for item in parts[::2])
            and len(set(parts[1::2])) <= 1 and len(set(parts[::2])) == len(parts[::2]))


def _schema_root() -> Path:
    # Both source checkout and hatch's packaged core are supported, offline only.
    package = Path(__file__).resolve().parents[2]
    packaged = package / "_core/contracts/ports"
    return packaged if packaged.is_dir() else package.parents[1] / "core/contracts/ports"


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError("non-finite JSON number")


class _Validation:
    def __init__(self, root: Path, mode: str, product_root: str) -> None:
        self.root = root
        self.mode = mode
        self.product_root = product_root
        self.issues: list[dict[str, str]] = []
        self.evidence: list[dict[str, str]] = []
        self.ports: list[dict[str, str]] = []
        self.loaded: dict[str, dict] = {}
        self.rejected: list[bytes] = []
        self.schema = LocalSchemaValidator(_schema_root(), formats={
            "port-path": _path, "port-timestamp": _time,
            "port-source-url": _url, "port-spdx": _spdx,
        })

    def issue(self, code: str, path: str, message: str, *, blocked: bool = False) -> None:
        self.issues.append({"code": code, "path": path, "message": message,
                            "status": "blocked" if blocked else "fail"})

    def safe(self, relative: str) -> Path:
        if not _path(relative):
            raise ValueError("noncanonical relative path")
        current = self.root
        for part in PurePosixPath(relative).parts:
            current /= part
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError("symlink is forbidden")
        if not current.resolve().is_relative_to(self.root):
            raise ValueError("path escapes validation root")
        return current

    def read(self, relative: str) -> bytes | None:
        try:
            file = self.safe(relative)
            if not stat.S_ISREG(file.stat().st_mode):
                raise ValueError("expected regular file")
            return file.read_bytes()
        except (OSError, ValueError):
            self.issue("file.unreadable", relative, "missing, unsafe, or non-regular local evidence")
            return None

    def json_bytes(self, data: bytes, relative: str) -> object | None:
        try:
            document = json.loads(data, object_pairs_hook=_unique_pairs, parse_constant=_invalid_constant)
            # JSON escapes can encode lone surrogates that are not valid UTF-8.
            # Reject them before paths, digests, or diagnostics use their values.
            _canonical(document)
            return document
        except (ValueError, UnicodeError, RecursionError):
            self.issue("json.invalid", relative, "invalid JSON, duplicate key, or non-finite number")
            return None

    def document(self, relative: str, schema: str) -> dict | None:
        data = self.read(relative)
        if data is None:
            return None
        document = self.json_bytes(data, relative)
        findings = self.schema.validate_file(_schema_root() / schema, document)
        for finding in findings:
            self.issue("structure." + finding.code, relative + "#" + finding.instance_path, finding.message)
        if findings:
            return None
        self.evidence.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "kind": "document"})
        return document

    def file(self, item: dict, *, prefix: str = "", kind: str = "file") -> bytes | None:
        relative = f"{prefix}/{item['path']}" if prefix else item["path"]
        data = self.read(relative)
        if data is None:
            return None
        digest = hashlib.sha256(data).hexdigest()
        if digest != item["sha256"]:
            self.issue("hash.drift", relative, "local bytes do not match declared SHA-256")
        self.evidence.append({"path": relative, "sha256": digest, "kind": kind})
        return data

    def scan(self, relative: str) -> dict[str, bytes]:
        result = {}
        try:
            directory = self.safe(relative)
            if not directory.is_dir():
                raise ValueError("expected directory")
            self._scan_directory(directory, relative, result)
        except (OSError, ValueError):
            self.issue("tree.unreadable", relative, "missing or unsafe tree")
        return result

    def _scan_directory(self, directory: Path, relative: str, result: dict[str, bytes]) -> None:
        for child in sorted(directory.iterdir()):
            child_relative = child.relative_to(self.root).as_posix()
            mode = child.lstat().st_mode
            if stat.S_ISDIR(mode):
                self._scan_directory(child, relative, result)
            elif stat.S_ISREG(mode):
                data = self.read(child_relative)
                if data is not None:
                    result[child.relative_to(self.root / relative).as_posix()] = data
            else:
                self.issue("tree.unsafe", child_relative, "symlink or special file is forbidden")

    def tree(self, value: dict) -> dict[str, str]:
        declared = {}
        for item in value["files"]:
            if item["path"] in declared:
                self.issue("tree.duplicate", value["path"], "duplicate tree file path")
            declared[item["path"]] = item["sha256"]
        actual = self.scan(value["path"])
        if set(actual) != set(declared):
            self.issue("tree.inventory", value["path"], "tree must enumerate every file exactly once")
        for relative, data in actual.items():
            digest = hashlib.sha256(data).hexdigest()
            if relative in declared and declared[relative] != digest:
                self.issue("hash.drift", f"{value['path']}/{relative}", "tree bytes differ from declared SHA-256")
            self.evidence.append({"path": f"{value['path']}/{relative}", "sha256": digest, "kind": "tree-file"})
        return declared

    def manifest(self, relative: str) -> None:
        start = len(self.issues)
        manifest = self.document(relative, "port-1.0.0.schema.json")
        if manifest is None:
            return
        port_id = manifest["id"]
        if port_id in self.loaded:
            self.issue("port.duplicate", relative, "duplicate port ID")
        else:
            self.loaded[port_id] = manifest
        fixture = manifest["origin"] == FIXTURE
        if self.mode == "release" and fixture:
            self.issue("release.fixture", relative, "fixture-only/not-shippable ports cannot enter release inventory")
        if not fixture and manifest["review"]["principal"].startswith("fixture:"):
            self.issue("review.fixture", relative, "external port requires a non-fixture reviewer principal")
        source = manifest["source"]
        licensing = manifest["licensing"]
        for name, value in (("source", source), ("licensing", licensing)):
            if value["status"] == "unavailable":
                self.issue(f"{name}.unavailable", relative + "#/" + name, value["reason"], blocked=True)
        trees = {name: self.tree(manifest[name]) for name in ("snapshot", "baseline", "adapted")}
        tree_paths = [manifest[name]["path"] for name in trees]
        for index, left in enumerate(tree_paths):
            for right in tree_paths[index + 1:]:
                if _overlap(left, right):
                    self.issue("tree.overlap", relative, "snapshot, baseline, and adapted trees must be disjoint")
        if trees["snapshot"] != trees["baseline"]:
            self.issue("baseline.changed", relative, "baseline must exactly preserve the source snapshot")
        if source["status"] == "available":
            host = (urlsplit(source["url"]).hostname or "").rstrip(".")
            reserved = host.endswith((".invalid", ".test", ".localhost", ".example", ".example.com", ".example.org", ".example.net")) or host in {"localhost", "example.com", "example.org", "example.net"}
            if fixture and source["url"] != "https://research-os.invalid/fixtures/local-only":
                self.issue("source.fixture", relative, "fixture source must explicitly name the local-only reserved URL")
            if not fixture and (reserved or not any(char != "0" for char in source["commit"])):
                self.issue("source.synthetic", relative, "external source cannot use reserved fixture provenance")
            evidence = self.file(source["evidence"], kind="source-receipt")
            if evidence is not None:
                expected = {key: source[key] for key in ("url", "commit", "path", "retrieved_at")}
                expected.update({"origin": manifest["origin"], "snapshot_sha256": tree_digest(manifest["snapshot"]["files"])})
                if self.json_bytes(evidence, source["evidence"]["path"]) != expected:
                    self.issue("source.receipt", relative, "source receipt does not bind provenance and snapshot")
            if manifest["review"]["reviewed_at"] < source["retrieved_at"]:
                self.issue("review.chronology", relative, "review predates source retrieval")
        if licensing["status"] == "available":
            if ("LicenseRef-ResearchOS-Fixture-Only" in licensing["spdx"]) != fixture:
                self.issue("license.fixture", relative, "fixture license and origin must agree")
            license_bytes = self.file(licensing["license"], kind="license")
            if license_bytes == b"":
                self.issue("license.empty", relative, "license evidence cannot be empty")
            notice = licensing["notice"]
            if notice["status"] == "included":
                if self.file(notice["file"], kind="notice") == b"":
                    self.issue("notice.empty", relative, "NOTICE evidence cannot be empty")
        if self.file(manifest["original"]["behavior"], kind="original-behavior") == b"":
            self.issue("behavior.empty", relative, "original behavior evidence cannot be empty")
        dependencies = manifest["original"]["dependencies"]
        if len({item["name"] for item in dependencies}) != len(dependencies):
            self.issue("dependencies.duplicate", relative, "dependency names must be unique")
        self.ledger(manifest, trees, relative)
        self.evaluations(manifest, relative)
        bundle_value = {
            key: manifest[key]
            for key in (
                "contract", "id", "origin", "source", "licensing", "snapshot", "baseline",
                "adapted", "original", "ledger", "evaluation", "review", "decision",
                "decision_principal", "product",
            )
        }
        admission_digest = hashlib.sha256(_canonical(bundle_value)).hexdigest()
        decision_evidence = self.file(manifest["decision_evidence"], kind="decision-evidence")
        if decision_evidence is not None:
            expected_decision = {
                "port_id": port_id,
                "principal": manifest["decision_principal"],
                "decision": manifest["decision"],
                "reviewed_at": manifest["review"]["reviewed_at"],
                "product": manifest["product"],
                "admission_digest": admission_digest,
            }
            if self.json_bytes(decision_evidence, manifest["decision_evidence"]["path"]) != expected_decision:
                self.issue("decision.receipt", relative, "human decision receipt does not bind port, principal, decision, review time, and product")
        product = manifest["product"]
        if manifest["decision"] == "reject":
            if product is not None:
                self.issue("decision.rejected_product", relative, "rejected port cannot declare a product")
            for name in trees:
                self.rejected.extend(data for data in self.scan(manifest[name]["path"]).values() if data)
        else:
            if product is None:
                self.issue("product.required", relative, "preserve/adapt requires canonical product path and digest")
            else:
                if not PurePosixPath(product["path"]).is_relative_to(PurePosixPath(self.product_root)) or product["path"] == self.product_root:
                    self.issue("product.path", relative, "canonical product must be inside product_root")
                for tree_path in tree_paths:
                    if _overlap(product["path"], tree_path):
                        self.issue("product.overlap", relative, "canonical product must be separate from evidence trees")
                product_bytes = self.file(product, kind="canonical-product")
                if product_bytes is not None and hashlib.sha256(product_bytes).hexdigest() != product["sha256"]:
                    self.issue("product.digest_mismatch", product["path"], "canonical product digest mismatch")
                if product["sha256"] not in trees["adapted"].values():
                    self.issue("product.unbound", relative, "canonical product must match an adapted file digest")
        own = self.issues[start:]
        status = _status(own)
        self.ports.append({"id": port_id, "manifest": relative, "decision": manifest["decision"],
                           "status": status, "admission": "rejected" if manifest["decision"] == "reject" else "accepted" if status == "pass" else "not-admitted",
                           "scope": manifest["origin"]})

    def ledger(self, manifest: dict, trees: dict, relative: str) -> None:
        before, after = trees["baseline"], trees["adapted"]
        expected = {}
        for path in sorted(before.keys() | after.keys()):
            expected[path] = ("add" if path not in before else "delete" if path not in after
                              else "keep" if before[path] == after[path] else "modify")
        actual = {item["path"]: item["action"] for item in manifest["ledger"]}
        if len(actual) != len(manifest["ledger"]) or actual != expected:
            self.issue("ledger.contradiction", relative, "ledger must cover every file exactly once with byte-consistent actions")
        if manifest["decision"] == "preserve" and any(action != "keep" for action in expected.values()):
            self.issue("decision.preserve_changed", relative, "preserve forbids modified, added, or deleted bytes")
        if manifest["decision"] == "adapt" and all(action == "keep" for action in expected.values()):
            self.issue("decision.adapt_unchanged", relative, "adapt requires a byte-level change")

    def evaluations(self, manifest: dict, relative: str) -> None:
        evaluation = manifest["evaluation"]
        for name in ("harness", "environment"):
            if self.file(evaluation[name], kind=name) == b"":
                self.issue("evaluation.empty", relative, "evaluation harness/environment cannot be empty")
        ids, paths, times = set(), set(), set()
        for side in ("baseline", "adapted"):
            digest = tree_digest(manifest[side]["files"])
            for run in evaluation[side]:
                if run["run_id"] in ids or run["evidence"]["path"] in paths or run["executed_at"] in times:
                    self.issue("evaluation.duplicate", relative, "each run requires distinct ID, evidence path, and execution time")
                ids.add(run["run_id"])
                paths.add(run["evidence"]["path"])
                times.add(run["executed_at"])
                if run["subject_sha256"] != digest:
                    self.issue("evaluation.subject", relative, "evaluation subject digest must match its tree")
                if manifest["decision"] != "reject" and run["result"] != "pass":
                    self.issue("evaluation.failed", relative, "accepted port requires passing baseline and adapted runs")
                if run["executed_at"] > manifest["review"]["reviewed_at"]:
                    self.issue("review.chronology", relative, "review predates evaluation")
                if manifest["source"]["status"] == "available" and run["executed_at"] < manifest["source"]["retrieved_at"]:
                    self.issue("evaluation.chronology", relative, "evaluation predates retrieval")
                detail = self.file(run["detail"], kind="evaluation-detail")
                if detail is not None:
                    detail_value = self.json_bytes(detail, run["detail"]["path"])
                    findings = self.schema.validate_file(_schema_root() / "evaluation-detail-1.0.0.schema.json", detail_value)
                    for finding in findings:
                        self.issue("evaluation.detail_structure", run["detail"]["path"] + "#" + finding.instance_path, finding.message)
                    checks = detail_value.get("checks", []) if isinstance(detail_value, dict) else []
                    derived_result = "pass" if checks and all(item.get("pass") is True for item in checks if isinstance(item, dict)) and len(checks) == sum(isinstance(item, dict) for item in checks) else "fail"
                    if (
                        not isinstance(detail_value, dict)
                        or detail_value.get("tree_sha256") != run["subject_sha256"]
                        or detail_value.get("result") != run["result"]
                        or detail_value.get("result") != derived_result
                    ):
                        self.issue("evaluation.detail", relative, "evaluation detail must bind tree digest and derive result from all checks")
                data = self.file(run["evidence"], kind="evaluation-receipt")
                if data is not None:
                    expected = {key: run[key] for key in ("run_id", "executed_at", "subject_sha256", "result")}
                    expected.update({"side": side, "harness_sha256": evaluation["harness"]["sha256"],
                                     "environment_sha256": evaluation["environment"]["sha256"], "origin": manifest["origin"]})
                    if self.json_bytes(data, run["evidence"]["path"]) != expected:
                        self.issue("evaluation.receipt", relative, "run receipt does not bind run, side, subject, harness, and environment")

    def release(self, relative: str | None) -> None:
        # Scan even without a release document: rejected bytes cannot hide behind it.
        product_directory = self.root / self.product_root
        actual = self.scan(self.product_root) if product_directory.exists() or product_directory.is_symlink() else {}
        for path, data in actual.items():
            canonical = f"{self.product_root}/{path}"
            if any(rejected in data for rejected in self.rejected):
                self.issue("release.rejected_bytes", canonical, "rejected bytes occur in product tree")
            if self.mode == "release" and FIXTURE.encode() in data:
                self.issue("release.fixture_bytes", canonical, "fixture-only/not-shippable bytes cannot ship")
        if self.mode != "release":
            return
        if relative is None:
            self.issue("release.required", "", "release mode requires an explicit release inventory and allowlist")
            return
        release = self.document(relative, "release-1.0.0.schema.json")
        if release is None:
            return
        products = {item["path"]: item["sha256"] for item in release["products"]}
        if len(products) != len(release["products"]):
            self.issue("release.duplicate", relative, "duplicate release product path")
        actual_hashes = {f"{self.product_root}/{path}": hashlib.sha256(data).hexdigest() for path, data in actual.items()}
        if not actual_hashes:
            self.issue("release.empty", relative, "empty product inventory cannot pass")
        if actual_hashes != products:
            self.issue("release.inventory", relative, "release inventory must equal all actual product paths and digests")
        allowed = {}
        for entry in release["allowlist"]:
            path = entry["path"]
            if path in allowed:
                self.issue("release.duplicate", relative, "duplicate allowlist path")
            allowed[path] = entry["sha256"]
            port = self.loaded.get(entry["port_id"])
            outcome = next((item for item in self.ports if item["id"] == entry["port_id"]), None)
            if port is None or outcome is None:
                self.issue("release.unknown_port", path, "allowlist references an unknown port")
                continue
            if port["origin"] == FIXTURE:
                self.issue("release.fixture", path, "fixture-only/not-shippable accepted fixtures cannot ship")
            if port["decision"] == "reject":
                self.issue("release.rejected", path, "allowlist cannot admit a rejected port")
            # Unavailable prerequisites remain BLOCKED, not an invented structural failure.
            if outcome["status"] == "fail":
                self.issue("release.not_admitted", path, "allowlist references a failing port")
            if port["product"] != {"path": path, "sha256": entry["sha256"]}:
                self.issue("release.binding", path, "allowlist must bind the exact canonical product and digest")
        if allowed != products:
            self.issue("release.allowlist", relative, "allowlist and release inventory must match exactly")
        canonical = [port["product"]["path"] for port in self.loaded.values() if port["product"] is not None]
        if len(canonical) != len(set(canonical)):
            self.issue("release.ambiguous", relative, "multiple ports claim one canonical product")

    def report(self) -> dict:
        issues = sorted(self.issues, key=lambda item: (item["path"], item["code"], item["message"], item["status"]))
        status = _status(issues)
        evidence = sorted({(item["path"], item["kind"], item["sha256"]) for item in self.evidence})
        return {
            "contract": {"name": "research-os/port-validation-report", "version": VERSION},
            "validator": {"name": "port-admission", "version": VERSION},
            "mode": self.mode, "status": status, "exit_code": {"pass": 0, "fail": 1, "blocked": 3}[status],
            "release_authorized": self.mode == "release" and status == "pass",
            "ports": sorted(self.ports, key=lambda item: (item["id"], item["manifest"])),
            "evidence": [{"path": path, "kind": kind, "sha256": digest} for path, kind, digest in evidence],
            "issues": issues,
        }


def _status(issues: list[dict[str, str]]) -> str:
    return "fail" if any(item["status"] == "fail" for item in issues) else "blocked" if issues else "pass"


def _overlap(left: str, right: str) -> bool:
    return PurePosixPath(left).is_relative_to(PurePosixPath(right)) or PurePosixPath(right).is_relative_to(PurePosixPath(left))


def validate_ports(
    root: str | Path, *, inventory: str = "inventory.json",
    release_inventory: str | None = None, mode: str = "release", product_root: str = "products",
) -> dict:
    """Validate explicit local manifests and optional release inventory, deterministically.

    Structural/integrity failures dominate declared unavailable prerequisites.
    No timestamps, absolute root paths, network calls, or executed evals are added.
    Default release mode fails closed; fixture admission requires explicit opt-in.
    """
    validation = _Validation(Path(root).resolve(), mode, product_root)
    if mode not in {"release", "admission"} or not _path(product_root):
        validation.issue("input.invalid", "", "mode must be release/admission and product_root must be canonical")
        return validation.report()
    if mode == "admission" and release_inventory is not None:
        validation.issue("input.invalid", "", "admission mode cannot accept a release inventory")
    document = validation.document(inventory, "inventory-1.0.0.schema.json")
    if document is not None:
        manifests = document["manifests"]
        if len(manifests) != len(set(manifests)):
            validation.issue("inventory.duplicate", inventory, "duplicate manifest path")
        for relative in sorted(set(manifests)):
            validation.manifest(relative)
    validation.release(release_inventory)
    return validation.report()
