from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
from importlib.metadata import Distribution
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.install import (  # noqa: E402
    InstallBlocked,
    ProjectionFile,
    SourceBundle,
    build_install_plan,
    execute_install,
    verify_install,
)


class PackagedBundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.site = Path(self.temporary.name).resolve()
        self.package = self.site / "research_os"
        self.metadata = self.site / "research_os-1.2.3.dist-info"
        self.mapping = {"core/skills/example/SKILL.md": "_core/skills/example/SKILL.md"}
        self.payload = {
            "research_os/__init__.py": b"",
            "research_os/_core/skills/example/SKILL.md": b"verified wheel resource\n",
            "research_os-1.2.3.dist-info/METADATA": b"Metadata-Version: 2.1\nName: research-os\nVersion: 1.2.3\n",
            "research_os-1.2.3.dist-info/WHEEL": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        }
        self.write_wheel()

    def write_wheel(self):
        rows = []
        for name, content in self.payload.items():
            path = self.site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            encoded = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
            rows.append((name, "sha256=" + encoded, str(len(content))))
        rows.append(("research_os-1.2.3.dist-info/RECORD", "", ""))
        with (self.metadata / "RECORD").open("w", newline="") as stream:
            csv.writer(stream).writerows(rows)
        self.distribution = Distribution.at(self.metadata)

    def test_wheel_record_verified_resource_installs_with_packaged_provenance(self):
        bundle = SourceBundle.from_installed_distribution(
            self.distribution, self.package, self.mapping, baseline_revision="a" * 40
        )
        self.assertTrue(bundle.source_verified)
        self.assertIsNone(bundle.source_revision)
        self.assertEqual(bundle.files["core/skills/example/SKILL.md"], b"verified wheel resource\n")
        provenance = dict(bundle.provenance)
        self.assertEqual(provenance["profile"], "packaged-artifact")
        self.assertEqual(provenance["distribution_name"], "research-os")
        self.assertEqual(provenance["distribution_version"], "1.2.3")
        self.assertEqual(provenance["record_digest"], hashlib.sha256((self.metadata / "RECORD").read_bytes()).hexdigest())
        self.assertEqual(provenance["baseline_revision"], "a" * 40)
        plan = build_install_plan(bundle)
        project = self.site / "project"
        project.mkdir()
        self.assertNotIsInstance(execute_install(project, plan), InstallBlocked)
        manifest, issues = verify_install(project)
        self.assertEqual(issues, ())
        self.assertEqual(manifest.to_dict()["provenance"], provenance)
        self.assertIsNone(manifest.to_dict()["source_revision"])


    def test_rejects_tampered_missing_weak_hash_editable_and_no_record(self):
        for case in ("tampered-resource", "tampered-code", "missing", "weak-hash", "wrong-size", "editable", "no-record", "extra-resource", "symlink", "hardlink", "duplicate-record", "unmapped-recorded"):
            with self.subTest(case=case):
                self.write_wheel()
                resource = self.package / "_core/skills/example/SKILL.md"
                record = self.metadata / "RECORD"
                extra = self.package / "_core/extra.txt"
                try:
                    if case == "tampered-resource":
                        resource.write_bytes(b"tampered\n")
                    elif case == "tampered-code":
                        (self.package / "__init__.py").write_bytes(b"tampered\n")
                    elif case == "missing":
                        resource.unlink()
                    elif case == "weak-hash":
                        record.write_text(record.read_text().replace("sha256=", "md5=", 1))
                    elif case == "wrong-size":
                        record.write_text(record.read_text().replace(",0\n", ",999\n", 1))
                    elif case == "editable":
                        self.payload["research_os-1.2.3.dist-info/direct_url.json"] = b'{"dir_info":{"editable":true}}'
                        self.write_wheel()
                    elif case == "no-record":
                        record.unlink()
                    elif case == "extra-resource":
                        extra.write_bytes(b"unrecorded")
                    elif case == "symlink":
                        resource.unlink()
                        resource.symlink_to(self.package / "__init__.py")
                    elif case == "hardlink":
                        resource.unlink()
                        os.link(self.package / "__init__.py", resource)
                    elif case == "duplicate-record":
                        record.write_text(record.read_text() + record.read_text().splitlines()[0] + "\n")
                    elif case == "unmapped-recorded":
                        self.payload["research_os/_core/extra.txt"] = b"recorded extra"
                        self.write_wheel()
                    with self.assertRaises((ValueError, OSError)):
                        SourceBundle.from_installed_distribution(self.distribution, self.package, self.mapping)
                finally:
                    if resource.is_symlink() or resource.exists():
                        resource.unlink()
                    extra.unlink(missing_ok=True)
                    (self.metadata / "direct_url.json").unlink(missing_ok=True)
                    self.payload.pop("research_os-1.2.3.dist-info/direct_url.json", None)
                    self.payload.pop("research_os/_core/extra.txt", None)

    def test_rejects_mapping_aliases_escape_and_caller_verified_claim(self):
        for mapping in (
            {"core//example": "_core/skills/example/SKILL.md"},
            {"core/example": "_core/../__init__.py"},
            {"core/example": "../research_os/__init__.py"},
            {"core/example": str(self.package / "__init__.py")},
            {"core/a": "_core/skills/example/SKILL.md", "core/b": "_core/skills/example/SKILL.md"},
        ):
            with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                SourceBundle.from_installed_distribution(self.distribution, self.package, mapping)
        with self.assertRaises(TypeError):
            SourceBundle(version="1.2.3", source_revision="a" * 40, files={"core/a": b"a"}, source_verified=True)

    def test_uv_installed_wheel_verifies_console_script_without_copying_it(self):
        import zipfile

        self.payload["research_os-1.2.3.dist-info/entry_points.txt"] = b"[console_scripts]\nfixture-research-os = research_os:main\n"
        self.write_wheel()
        wheel = self.site / "research_os-1.2.3-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            for path in (*[self.site / name for name in self.payload], self.metadata / "RECORD"):
                archive.write(path, path.relative_to(self.site).as_posix())
        target = self.site / "installed"
        subprocess.run(["uv", "pip", "install", "--no-deps", "--no-compile-bytecode", "--target", str(target), str(wheel)], check=True, capture_output=True)
        distribution = Distribution.at(target / "research_os-1.2.3.dist-info")
        bundle = SourceBundle.from_installed_distribution(distribution, target / "research_os", self.mapping)
        self.assertTrue(bundle.source_verified)
        self.assertEqual(set(bundle.files), set(self.mapping))
        self.assertTrue((target / "bin/fixture-research-os").is_file())
        self.assertGreater(bundle.provenance["non_resource_record_count"], 0)


    def test_record_path_alias_and_symlinked_package_are_rejected(self):
        record = self.metadata / "RECORD"
        raw = record.read_text()
        for alias in ("research_os/../research_os/__init__.py", "research_os//__init__.py", "/absolute/__init__.py"):
            with self.subTest(alias=alias):
                record.write_text(raw.replace("research_os/__init__.py", alias, 1))
                with self.assertRaises(ValueError):
                    SourceBundle.from_installed_distribution(self.distribution, self.package, self.mapping)
        record.write_text(raw)
        alias = self.site / "package-alias"
        alias.symlink_to(self.package, target_is_directory=True)
        with self.assertRaises((ValueError, OSError)):
            SourceBundle.from_installed_distribution(self.distribution, alias, self.mapping)

    def test_critical_roots_reject_non_directory_roots_and_special_entries(self):
        root_file = self.package / "_templates"
        root_file.write_bytes(b"undeclared root")
        with self.assertRaises(ValueError):
            SourceBundle.from_installed_distribution(self.distribution, self.package, self.mapping)
        root_file.unlink()
        fifo = self.package / "_core/unrecorded-pipe"
        os.mkfifo(fifo)
        with self.assertRaises(ValueError):
            SourceBundle.from_installed_distribution(self.distribution, self.package, self.mapping)

    def test_record_rejects_arbitrary_external_file_even_with_valid_hash(self):
        outside = self.site.parent / (self.site.name + "-outside")
        outside.write_bytes(b"external")
        self.addCleanup(outside.unlink)
        digest = base64.urlsafe_b64encode(hashlib.sha256(b"external").digest()).rstrip(b"=").decode()
        with (self.metadata / "RECORD").open("a", newline="") as stream:
            csv.writer(stream).writerow(("../" + outside.name, "sha256=" + digest, "8"))
        with self.assertRaises(ValueError):
            SourceBundle.from_installed_distribution(self.distribution, self.package, self.mapping)

    def test_uv_venv_wheel_verifies_external_console_script_record(self):
        import sysconfig
        import zipfile

        self.payload["research_os-1.2.3.dist-info/entry_points.txt"] = b"[console_scripts]\nfixture-research-os = research_os:main\n"
        self.write_wheel()
        wheel = self.site / "research_os-1.2.3-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            for path in (*[self.site / name for name in self.payload], self.metadata / "RECORD"):
                archive.write(path, path.relative_to(self.site).as_posix())
        environment = self.site / "venv"
        subprocess.run(["uv", "venv", "--python", sys.executable, str(environment)], check=True, capture_output=True)
        subprocess.run(["uv", "pip", "install", "--python", str(environment / "bin/python"), "--no-deps", "--no-compile-bytecode", str(wheel)], check=True, capture_output=True)
        site = Path(sysconfig.get_path("purelib", vars={"base": str(environment), "platbase": str(environment)}))
        distribution = Distribution.at(site / "research_os-1.2.3.dist-info")
        self.assertIn("../../../bin/fixture-research-os", distribution.read_text("RECORD"))
        bundle = SourceBundle.from_installed_distribution(distribution, site / "research_os", self.mapping)
        self.assertEqual(set(bundle.files), set(self.mapping))
        self.assertTrue(bundle.source_verified)
        (environment / "bin/fixture-research-os").write_bytes(b"tampered script")
        with self.assertRaises(ValueError):
            SourceBundle.from_installed_distribution(distribution, site / "research_os", self.mapping)


class InstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()
        self.bundle = SourceBundle(
            version="1.2.3",
            source_revision="a" * 40,
            files={
                "core/skills/example/SKILL.md": b"---\nname: example\n---\nbody\n",
                "core/contracts/example.json": b"{}\n",
            },
        )

    def snapshot(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.project).as_posix(): path.read_bytes()
            for path in self.project.rglob("*")
            if path.is_file()
        }

    def test_new_install_is_project_local_runtime_free_and_idempotent(self) -> None:
        plan = build_install_plan(
            self.bundle,
            [ProjectionFile(".claude/skills/example/SKILL.md", b"projection\n")],
            require_verified_source=False,
        )
        first = execute_install(self.project, plan)
        self.assertNotIsInstance(first, InstallBlocked)
        before = self.snapshot()
        second = execute_install(self.project, plan)
        self.assertNotIsInstance(second, InstallBlocked)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.project / "pyproject.toml").exists())
        self.assertFalse((self.project / "uv.lock").exists())
        self.assertFalse((self.project / ".research-os/runtime").exists())
        manifest = json.loads((self.project / ".research-os/install-manifest.json").read_bytes())
        self.assertEqual(manifest["runtime"], "none")
        self.assertEqual(manifest["lockfile"], "none")
        self.assertEqual(manifest["activation"], "explicit")
        self.assertEqual(verify_install(self.project)[1], ())

    def test_source_bundle_rejects_project_runtime_and_lockfiles(self) -> None:
        for name in (
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
            ".venv/pyvenv.cfg",
            ".research-os/runtime/cli.py",
            ".research-os/lock",
            ".research-os/lock.json",
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                SourceBundle(version="1.0.0", source_revision="a" * 40, files={name: b"x"})

    def test_source_bundle_from_directory_rejects_symlinked_source_ancestors(self) -> None:
        source = Path(self.temporary.name) / "source"
        source.mkdir()
        outside = Path(self.temporary.name) / "outside"
        (outside / "skill").mkdir(parents=True)
        (outside / "skill/SKILL.md").write_bytes(b"outside\n")
        (source / "core").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            SourceBundle.from_directory(
                source,
                version="1.0.0",
                source_revision="a" * 40,
                include=["core/skill/SKILL.md"],
            )

    def test_source_bundle_from_repository_reads_pinned_commit_not_worktree(self) -> None:
        source = Path(self.temporary.name) / "source-repository"
        source.mkdir()
        for arguments in (
            ("init", "-q"),
            ("config", "user.name", "Fixture"),
            ("config", "user.email", "fixture@example.test"),
        ):
            subprocess.run(["git", "-C", str(source), *arguments], check=True)
        tracked = source / "core/skills/example/SKILL.md"
        tracked.parent.mkdir(parents=True)
        tracked.write_bytes(b"pinned\n")
        subprocess.run(["git", "-C", str(source), "add", "."], check=True)
        subprocess.run(["git", "-C", str(source), "commit", "-qm", "pinned"], check=True)
        commit = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        tracked.write_bytes(b"worktree drift\n")
        bundle = SourceBundle.from_repository(
            source,
            version="1.0.0",
            source_revision=commit,
            include=["core/skills/example/SKILL.md"],
        )
        self.assertEqual(bundle.files["core/skills/example/SKILL.md"], b"pinned\n")
        build_install_plan(bundle)

    def test_install_plan_rejects_self_reported_unverified_source_pin(self) -> None:
        with self.assertRaises(ValueError):
            build_install_plan(self.bundle)

    def test_install_detects_symlink_swap_before_writing_outside_project(self) -> None:
        plan = build_install_plan(self.bundle, require_verified_source=False)
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        original_atomic_write = __import__(
            "research_os.install.bundle", fromlist=["_atomic_write"]
        )._atomic_write
        swapped = False

        def swap_then_write(path: Path, content: bytes, **kwargs) -> None:
            nonlocal swapped
            if not swapped:
                swapped = True
                core = self.project / "core"
                if core.exists():
                    core.rmdir()
                core.symlink_to(outside, target_is_directory=True)
            return original_atomic_write(path, content, **kwargs)

        with patch("research_os.install.bundle._atomic_write", side_effect=swap_then_write):
            result = execute_install(self.project, plan)
        self.assertIsInstance(result, InstallBlocked)
        self.assertFalse((outside / "skills/example/SKILL.md").exists())
        self.assertFalse((outside / "contracts/example.json").exists())

    def test_concurrent_destination_creation_is_not_overwritten(self) -> None:
        from research_os.install import bundle as installer

        target = self.project / "core/contracts/example.json"
        real_publish = installer._publish_noreplace
        triggered = False

        def publish_with_race(source, destination, **kwargs):
            nonlocal triggered
            if not triggered and destination == target.name:
                triggered = True
                target.write_bytes(b"concurrent owner\n")
            return real_publish(source, destination, **kwargs)

        with patch.object(installer, "_publish_noreplace", side_effect=publish_with_race):
            result = execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        self.assertTrue(triggered)
        self.assertIsInstance(result, InstallBlocked)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.to_dict()["verdict"], "fail")
        self.assertEqual(target.read_bytes(), b"concurrent owner\n")

    def test_parent_swap_at_atomic_publish_never_writes_through_symlink(self) -> None:
        from research_os.install import bundle as installer

        target = self.project / "core/contracts/example.json"
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        real_publish = installer._publish_noreplace
        triggered = False

        def swap_parent(*args, **kwargs):
            nonlocal triggered
            if not triggered:
                triggered = True
                target.parent.rename(self.project / "detached-contracts")
                target.parent.symlink_to(outside, target_is_directory=True)
            return real_publish(*args, **kwargs)

        with patch.object(installer, "_publish_noreplace", side_effect=swap_parent):
            result = execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        self.assertTrue(triggered)
        self.assertIsInstance(result, InstallBlocked)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_failure_never_unlinks_concurrent_replacement_even_with_same_bytes(self) -> None:
        from research_os.install import bundle as installer

        for replacement_bytes in (b"concurrent replacement\n", b"{}\n"):
            with self.subTest(replacement_bytes=replacement_bytes), tempfile.TemporaryDirectory() as directory:
                project = Path(directory).resolve()
                first = project / "core/contracts/example.json"
                real_write = installer._atomic_write
                replacement_token = None

                def replace_first_then_fail(path, content, **kwargs):
                    nonlocal replacement_token
                    if path.name == "SKILL.md":
                        replacement = first.with_name("replacement")
                        replacement.write_bytes(replacement_bytes)
                        os.replace(replacement, first)
                        replacement_token = first.stat().st_ino
                        raise OSError("deterministic second write failure")
                    return real_write(path, content, **kwargs)

                with patch.object(installer, "_atomic_write", side_effect=replace_first_then_fail):
                    result = execute_install(project, build_install_plan(self.bundle, require_verified_source=False))
                self.assertIsInstance(result, InstallBlocked)
                self.assertEqual(result.exit_code, 1)
                self.assertEqual(first.read_bytes(), replacement_bytes)
                self.assertEqual(first.stat().st_ino, replacement_token)
                self.assertIn("install.cleanup_required", {issue["code"] for issue in result.issues})

    def test_directory_swap_during_traversal_creates_nothing_outside(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        core = self.project / "core"
        core.mkdir()
        real_open = os.open
        triggered = False

        def swap_component(path, flags, *args, **kwargs):
            nonlocal triggered
            if not triggered and flags & os.O_DIRECTORY and path == "core":
                triggered = True
                core.rename(self.project / "old-core")
                core.symlink_to(outside, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)

        with patch("research_os.install.bundle.os.open", side_effect=swap_component):
            result = execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        self.assertTrue(triggered)
        self.assertIsInstance(result, InstallBlocked)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_partial_write_failure_preserves_public_name_and_reports_cleanup(self) -> None:
        target = self.project / "core/contracts/example.json"
        with patch("research_os.install.bundle.os.fsync", side_effect=OSError("disk failure")):
            result = execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        self.assertIsInstance(result, InstallBlocked)
        self.assertEqual(result.to_dict()["verdict"], "fail")
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(target.exists())
        self.assertTrue(list(target.parent.glob(".install-*/payload")))
        self.assertIn("install.cleanup_required", {issue["code"] for issue in result.issues})
        self.assertFalse((self.project / ".research-os/install-manifest.json").exists())

    def test_file_is_absent_until_complete_atomic_publish(self) -> None:
        target = self.project / "core/contracts/example.json"
        real_fsync = os.fsync
        observed = False

        def observe_before_publish(descriptor):
            nonlocal observed
            if not observed:
                observed = True
                self.assertFalse(target.exists(), "incomplete final name was exposed")
            return real_fsync(descriptor)

        with patch("research_os.install.bundle.os.fsync", side_effect=observe_before_publish):
            result = execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        self.assertTrue(observed)
        self.assertNotIsInstance(result, InstallBlocked)
        self.assertEqual(target.read_bytes(), b"{}\n")

    def test_preflight_open_races_fail_without_reading_external_or_blocking_fifo(self) -> None:
        import io

        for replacement in ("deleted", "symlink", "fifo"):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as directory:
                project = Path(directory).resolve()
                target = project / "core/contracts/example.json"
                target.parent.mkdir(parents=True)
                target.write_bytes(b"{}\n")
                outside = project / "outside"
                outside.write_bytes(b"{}\n")
                real_open, real_io_open = os.open, io.open
                triggered = False

                def swap():
                    nonlocal triggered
                    triggered = True
                    target.unlink()
                    if replacement == "symlink":
                        target.symlink_to(outside)
                    elif replacement == "fifo":
                        os.mkfifo(target)

                def fd_open(path, flags, *args, **kwargs):
                    if not triggered and Path(path).name == target.name:
                        swap()
                        self.assertTrue(flags & os.O_NOFOLLOW)
                        self.assertTrue(flags & os.O_NONBLOCK)
                    return real_open(path, flags, *args, **kwargs)

                def unsafe_io_open(path, *args, **kwargs):
                    if not triggered and not isinstance(path, int) and Path(path) == target:
                        swap()
                        self.fail("preflight uses a path read vulnerable to replacement")
                    return real_io_open(path, *args, **kwargs)

                with patch("research_os.install.bundle.os.open", side_effect=fd_open), patch(
                    "io.open", side_effect=unsafe_io_open
                ):
                    result = execute_install(project, build_install_plan(self.bundle, require_verified_source=False))
                self.assertTrue(triggered)
                self.assertIsInstance(result, InstallBlocked)
                self.assertEqual(result.exit_code, 1)
                self.assertEqual(result.to_dict()["verdict"], "fail")
                self.assertEqual(outside.read_bytes(), b"{}\n")

    def test_conflict_blocks_all_writes_and_preserves_existing_bytes(self) -> None:
        conflict = self.project / "core/contracts/example.json"
        conflict.parent.mkdir(parents=True)
        conflict.write_bytes(b"custom\n")
        before = self.snapshot()
        result = execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        self.assertIsInstance(result, InstallBlocked)
        self.assertEqual(result.to_dict()["issues"][0]["code"], "install.conflict")
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.project / "core/skills/example/SKILL.md").exists())

    def test_explicit_update_creates_isolated_environment_without_overwrite(self) -> None:
        original = execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        self.assertNotIsInstance(original, InstallBlocked)
        old = self.snapshot()
        updated = SourceBundle(
            version="2.0.0",
            source_revision="b" * 40,
            files={"core/skills/example/SKILL.md": b"---\nname: example\n---\nnew\n"},
        )
        result = execute_install(self.project, build_install_plan(updated, require_verified_source=False), environment="v2")
        self.assertNotIsInstance(result, InstallBlocked)
        for name, content in old.items():
            self.assertEqual((self.project / name).read_bytes(), content, name)
        environment = self.project / ".research-os/environments/v2"
        self.assertIn(b"new", (environment / "core/skills/example/SKILL.md").read_bytes())
        self.assertFalse((environment / "pyproject.toml").exists())
        self.assertEqual(verify_install(self.project, environment="v2")[1], ())

    def test_update_conflict_does_not_touch_active_install_or_partial_environment(self) -> None:
        execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        active = self.snapshot()
        conflict = self.project / ".research-os/environments/v2/core/contracts/example.json"
        conflict.parent.mkdir(parents=True)
        conflict.write_bytes(b"owner\n")
        before = self.snapshot()
        result = execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False), environment="v2")
        self.assertIsInstance(result, InstallBlocked)
        self.assertEqual(self.snapshot(), before)
        for name, content in active.items():
            self.assertEqual((self.project / name).read_bytes(), content)

    def test_verify_rejects_symlinked_manifest_ancestors(self) -> None:
        for environment, ancestors in (
            (None, (".research-os",)),
            ("v2", (".research-os", ".research-os/environments", ".research-os/environments/v2", ".research-os/environments/v2/.research-os")),
        ):
            for ancestor in ancestors:
                for external in (False, True):
                    with self.subTest(environment=environment, ancestor=ancestor, external=external):
                        with tempfile.TemporaryDirectory(dir=self.temporary.name) as directory:
                            project = Path(directory) / "project"
                            project.mkdir()
                            execute_install(project, build_install_plan(self.bundle, require_verified_source=False), environment=environment)
                            self.assertEqual(verify_install(project, environment=environment)[1], ())
                            original = project / ancestor
                            relocated = (Path(directory) if external else project) / "relocated"
                            original.rename(relocated)
                            original.symlink_to(relocated, target_is_directory=True)
                            manifest, issues = verify_install(project, environment=environment)
                            self.assertIsNone(manifest)
                            self.assertEqual(issues[0]["code"], "install.manifest")

    def test_verify_rejects_symlinked_resource_ancestors_with_matching_bytes(self) -> None:
        for environment in (None, "v2"):
            for ancestor in ("core", "core/skills", "core/skills/example"):
                for external in (False, True):
                    with self.subTest(environment=environment, ancestor=ancestor, external=external):
                        with tempfile.TemporaryDirectory(dir=self.temporary.name) as directory:
                            project = Path(directory) / "project"
                            project.mkdir()
                            execute_install(project, build_install_plan(self.bundle, require_verified_source=False), environment=environment)
                            root = project if environment is None else project / ".research-os/environments/v2"
                            original = root / ancestor
                            relocated = (Path(directory) if external else root) / "relocated"
                            original.rename(relocated)
                            original.symlink_to(relocated, target_is_directory=True)
                            manifest, issues = verify_install(project, environment=environment)
                            self.assertIsNotNone(manifest)
                            self.assertTrue(issues)
                            self.assertEqual({issue["code"] for issue in issues}, {"install.file"})

    def test_verify_detects_missing_drifted_and_symlinked_files(self) -> None:
        execute_install(self.project, build_install_plan(self.bundle, require_verified_source=False))
        target = self.project / "core/contracts/example.json"
        target.write_bytes(b"changed\n")
        self.assertEqual(verify_install(self.project)[1][0]["code"], "install.drift")
        target.unlink()
        outside = Path(self.temporary.name) / "outside"
        outside.write_bytes(b"{}\n")
        target.symlink_to(outside)
        self.assertEqual(verify_install(self.project)[1][0]["code"], "install.file")


if __name__ == "__main__":
    unittest.main()
