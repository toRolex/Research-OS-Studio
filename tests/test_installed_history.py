from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstalledHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory()
        cls.outside = Path(cls.workspace.name)
        cls.env = os.environ.copy()
        cls.env.pop("PYTHONPATH", None)
        cls.env.update(
            UV_OFFLINE="1", UV_NO_MANAGED_PYTHON="1", PYTHONDONTWRITEBYTECODE="1"
        )
        cls.execute(
            "uv", "build", "--wheel", "--out-dir", str(cls.outside / "dist"), str(ROOT)
        )
        cls.execute("uv", "venv", str(cls.outside / "venv"))
        cls.python = cls.outside / "venv/bin/python"
        cls.execute(
            "uv",
            "pip",
            "install",
            "--python",
            str(cls.python),
            str(next((cls.outside / "dist").glob("*.whl"))),
        )
        cls.cli = cls.outside / "venv/bin/research-os"

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    @classmethod
    def execute(cls, *args):
        result = subprocess.run(
            args, cwd=cls.outside, env=cls.env, capture_output=True, text=True
        )
        if result.returncode:
            raise AssertionError(f"{args}: {result.stdout}\n{result.stderr}")
        return result.stdout

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=self.outside)
        self.addCleanup(self.directory.cleanup)
        self.project = Path(self.directory.name) / "project"
        self.project.mkdir()

    def invoke(self, *args):
        return subprocess.run(
            ["uv", "run", "--no-project", str(self.cli), *args],
            cwd=self.outside,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def succeed(self, *args):
        result = self.invoke(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def git(self, *args):
        return self.execute("git", "-C", str(self.project), *args).strip()

    def snapshot(self, project=None):
        root = project or self.project
        return {
            p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(root).parts
        }

    def test_sdist_rebuild_wheel_contains_complete_resources_and_subpackages(self):
        import tarfile
        import zipfile
        self.execute('uv', 'build', '--sdist', '--out-dir', str(self.outside/'sdist'), str(ROOT))
        archive = next((self.outside/'sdist').glob('*.tar.gz'))
        unpacked = Path(self.directory.name)/'unpacked'
        unpacked.mkdir()
        with tarfile.open(archive) as stream:
            stream.extractall(unpacked, filter='data')
        source = next(unpacked.iterdir())
        self.execute('uv','build','--wheel','--out-dir',str(self.outside/'rebuilt'),str(source))
        wheel = next((self.outside/'rebuilt').glob('*.whl'))
        with zipfile.ZipFile(wheel) as stream:
            names = set(stream.namelist())
        for name in ('validation/foundation/registry.py','validation/semantics/assurance.py',
                     'install/bundle.py','history/git_restore.py','publication/workflow.py',
                     'remote/adapter.py','workflows/outer/runner.py','workflows/computational/workflows.py',
                     'workflows/mathematical/lean.py','_core/catalog.json','_templates/outer/research-charter.input.json',
                     '_adapters/codex.json','_reference_projects/computational/experiment.py',
                     '_reference_projects/mathematical/lean-toolchain'):
            self.assertIn('research_os/'+name,names)
        self.assertFalse(any('/_runtime/' in name for name in names))

    def test_installed_setup_copies_resources_idempotently(self):
        self.succeed("setup-research-os", "--project", str(self.project))
        before = self.snapshot()
        self.succeed("setup-research-os", "--project", str(self.project))
        self.assertEqual(self.snapshot(), before)
        self.assertIn("core/catalog.json", before)
        self.assertIn("core/contracts/artifact-1.0.0.schema.json", before)
        self.assertIn(".research-os/install-manifest.json", before)
        manifest = json.loads(before['.research-os/install-manifest.json'])
        self.assertIsNone(manifest['source_revision'])
        self.assertEqual(manifest['provenance']['profile'], 'packaged-artifact')
        self.assertRegex(manifest['provenance']['record_digest'], r'^[0-9a-f]{64}$')
        self.assertFalse(any(name.startswith(".research-os/runtime/") for name in before))
        self.assertNotIn("uv.lock", before)

    def create_charter_request(self, name):
        value = {"contract": {"name": "research-os/artifact", "version": "1.1.0"},
                 "target": {"kind": "git", "path": "question.json"},
                 "type": {"name": "research-question", "version": "1.0.0"},
                 "spec": {"question": "Can history be reproduced?", "boundaries": ["local fixture"],
                          "success_criteria": [], "budget": {}, "invariants": []}}
        raw = json.dumps(value).encode()
        (self.project / "question.json").write_bytes(raw)
        (self.project / name).write_text(json.dumps({"inputs": [{"path": "question.json", "sha256": hashlib.sha256(raw).hexdigest()}]}))

    def initialize_history(self):
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.test")
        self.succeed("setup-research-os", "--project", str(self.project))
        # Explicit typed source/request replaces the old unpinned prose tracer.
        self.create_charter_request("question.txt")
        self.succeed(
            "research-charter", "--project", str(self.project), "--input", "question.txt",
            "--output", "artifacts/charter.json", "--report", "runs/charter/report.json",
        )
        # Historical Publication bytes are opaque immutable records, not a new
        # freeze request. Complete current Publication behavior has its own suite.
        publication = self.project / "publications/p1/publication.json"
        publication.parent.mkdir(parents=True)
        publication.write_text('{"historical_publication": true}\n')
        self.git("add", ".")
        self.git("commit", "-qm", "固定旧环境与研究记录")
        return self.git("rev-parse", "HEAD")

    def test_installed_update_export_and_old_runtime_replay_preserve_history(self):
        historical = self.initialize_history()
        before = self.snapshot()
        update = self.succeed(
            "update-research-os",
            "--project",
            str(self.project),
            "--environment",
            "v-next",
        )
        self.assertEqual(
            update["stop_reason"], "installed_explicit_activation_required"
        )
        self.assertEqual(update["next_steps"], [])
        for name, data in before.items():
            self.assertEqual((self.project / name).read_bytes(), data, name)
        self.assertTrue(
            (
                self.project
                / update["environment"]
                / ".research-os/install-manifest.json"
            ).is_file()
        )
        # Make current files invalid, proving export selects the commit, not live bytes.
        (self.project / "artifacts/charter.json").write_text("{}")
        (self.project / "core/catalog.json").write_text("{}")
        current = self.snapshot()
        restored = Path(self.directory.name) / "historical"
        exported = self.succeed(
            "export-research-os",
            "--project",
            str(self.project),
            "--commit",
            historical,
            "--output",
            str(restored),
        )
        self.assertEqual(exported["commit"], historical)
        self.assertEqual(exported["next_steps"], [])
        restored_before = self.snapshot(restored)
        self.assertEqual({name: data for name, data in restored_before.items() if name != ".research-os/history-restore.json"}, before)
        self.assertTrue(exported["read_only"])
        self.assertEqual(self.snapshot(), current)
        replay = self.invoke("validate", "--project", str(restored), "artifacts/charter.json")
        self.assertEqual(replay.returncode, 0, replay.stdout + replay.stderr)
        self.assertEqual(json.loads(replay.stdout)["verdict"], "pass")
        self.assertEqual(self.snapshot(restored), restored_before)
        self.assertEqual(self.snapshot(), current)

    def test_legacy_runtime_history_is_read_only_never_executed(self):
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.test")
        runtime = self.project / ".research-os/runtime"
        (runtime / "scripts").mkdir(parents=True)
        script = "raise RuntimeError('historical code must never execute')\n"
        (runtime / "scripts/research-os.py").write_text(script)
        (runtime / "uv.lock").write_text("historical opaque lock bytes")
        (runtime / "manifest.json").write_text(json.dumps({
            "contract": {"name": "research-os/runtime-manifest", "version": "1.0.0"},
            "files": ["scripts/research-os.py", "uv.lock"],
        }))
        self.git("add", ".")
        self.git("commit", "-qm", "historical fixture")
        revision = self.git("rev-parse", "HEAD")
        before = self.snapshot()
        destination = Path(self.directory.name) / "legacy-restored"
        result = self.succeed("export-research-os", "--project", str(self.project),
                              "--commit", revision, "--output", str(destination))
        self.assertTrue(result["read_only"])
        self.assertEqual(result["profile"], "legacy-self-contained-runtime-v1")
        self.assertEqual((destination / ".research-os/runtime/scripts/research-os.py").read_text(), script)
        self.assertEqual(self.snapshot(), before)

    def test_export_rejects_incomplete_runtime_manifest(self):
        self.initialize_history()
        manifest_path = self.project / ".research-os/runtime/manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest = {"contract": {"name": "research-os/runtime-manifest", "version": "1.0.0"}, "files": ["missing.py"]}
        manifest_path.write_text(json.dumps(manifest))
        self.git("add", ".research-os/runtime")
        self.git("commit", "-qm", "固定不可启动的历史运行时")
        incomplete = self.git("rev-parse", "HEAD")
        destination = Path(self.directory.name) / "incomplete"

        result = self.invoke(
            "export-research-os",
            "--project",
            str(self.project),
            "--commit",
            incomplete,
            "--output",
            str(destination),
        )

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse(destination.exists())

    def test_installed_migration_records_new_commits_without_activating_environment(
        self,
    ):
        historical = self.initialize_history()
        before = self.snapshot()
        target = {"kind": "git", "path": "artifacts/charter.json", "commit": historical}
        rule = {
            "name": "charter-compatible-envelope",
            "version": "1.0.0",
            "operation": "preserve-spec",
            "source": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
            "destination": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
        }
        (self.project / "input.json").write_text(json.dumps(target))
        (self.project / "rules.json").write_text(json.dumps([rule]))
        self.git("add", ".")
        self.git("commit", "-qm", "固定显式迁移输入和规则")
        prior = self.git("rev-parse", "HEAD")
        result = self.succeed(
            "migrate-artifact",
            "--project",
            str(self.project),
            "--input",
            "input.json",
            "--rules",
            "rules.json",
            "--to-contract",
            "1.1.0",
            "--to-type-version",
            "1.0.0",
            "--output",
            "artifacts/charter-v2.json",
            "--receipt",
            "receipts/migration.json",
        )
        self.assertEqual(result["next_steps"], [])
        receipt = json.loads((self.project / "receipts/migration.json").read_text())
        self.assertEqual(receipt["input"], target)
        self.assertEqual(receipt["source"], rule["source"])
        self.assertEqual(receipt["destination"], rule["destination"])
        self.assertEqual(receipt["rule"], rule)
        self.assertEqual(
            receipt["migrator"], {"name": "preserve-spec", "version": "1.0.0"}
        )
        for name in ("input_validator", "output_validator"):
            self.assertEqual(
                receipt[name],
                {"name": "artifact", "version": "1.0.0", "verdict": "pass"},
            )
        revision = receipt["output"]["commit"]
        self.assertNotEqual(revision, prior)
        migrated = json.loads(self.git("show", f"{revision}:artifacts/charter-v2.json"))
        self.assertEqual(migrated["contract"]["version"], "1.1.0")
        self.assertEqual(
            migrated["spec"], json.loads(before["artifacts/charter.json"])["spec"]
        )
        self.assertEqual(migrated["provenance"][-1]["target"], target)
        self.assertNotIn("assurance", migrated)
        self.assertEqual(self.git("status", "--porcelain"), "")
        for name, data in before.items():
            self.assertEqual((self.project / name).read_bytes(), data, name)
        self.assertFalse((self.project / ".research-os/environments").exists())
        self.succeed(
            "validate", "--project", str(self.project), "artifacts/charter-v2.json"
        )

    def test_migration_preflights_ignored_receipt_without_writes(
        self,
    ):
        historical = self.initialize_history()
        target = {"kind": "git", "path": "artifacts/charter.json", "commit": historical}
        rule = {
            "name": "preserve-charter",
            "version": "1.0.0",
            "operation": "preserve-spec",
            "source": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
            "destination": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
        }
        (self.project / "input.json").write_text(json.dumps(target))
        (self.project / "rules.json").write_text(json.dumps([rule]))
        (self.project / ".gitignore").write_text("receipts/\n")
        self.git("add", ".")
        self.git("commit", "-qm", "固定不可提交回执样例")
        before = self.snapshot()
        revision = self.git("rev-parse", "HEAD")

        result = self.invoke(
            "migrate-artifact",
            "--project",
            str(self.project),
            "--input",
            "input.json",
            "--rules",
            "rules.json",
            "--to-contract",
            "1.1.0",
            "--to-type-version",
            "1.0.0",
            "--output",
            "artifacts/charter-v2.json",
            "--receipt",
            "receipts/migration.json",
        )

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(self.git("rev-parse", "HEAD"), revision)
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.snapshot(), before)

    def test_migration_from_project_subdirectory_reads_the_pinned_project_artifact(
        self,
    ):
        repository = self.project.parent / "repository"
        repository.mkdir()
        self.execute("git", "-C", str(repository), "init", "-q")
        self.execute("git", "-C", str(repository), "config", "user.name", "Fixture")
        self.execute(
            "git", "-C", str(repository), "config", "user.email", "fixture@example.test"
        )
        self.project = repository / "nested"
        self.project.mkdir()
        self.succeed("setup-research-os", "--project", str(self.project))
        self.create_charter_request("question.txt")
        self.succeed(
            "research-charter",
            "--project",
            str(self.project),
            "--input",
            "question.txt",
            "--output",
            "artifacts/charter.json",
            "--report",
            "runs/charter/report.json",
        )
        self.git("add", ".")
        self.git("commit", "-qm", "固定子目录旧环境")
        historical = self.git("rev-parse", "HEAD")
        root_artifact = repository / "artifacts/charter.json"
        root_artifact.parent.mkdir()
        root_artifact.write_text("{}")
        self.execute("git", "-C", str(repository), "add", "artifacts/charter.json")
        self.execute(
            "git", "-C", str(repository), "commit", "-qm", "固定仓库根冲突文件"
        )
        target = {"kind": "git", "path": "artifacts/charter.json", "commit": historical}
        rule = {
            "name": "preserve-charter",
            "version": "1.0.0",
            "operation": "preserve-spec",
            "source": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
            "destination": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
        }
        (self.project / "input.json").write_text(json.dumps(target))
        (self.project / "rules.json").write_text(json.dumps([rule]))
        self.git("add", ".")
        self.git("commit", "-qm", "固定子目录迁移输入")

        result = self.succeed(
            "migrate-artifact",
            "--project",
            str(self.project),
            "--input",
            "input.json",
            "--rules",
            "rules.json",
            "--to-contract",
            "1.1.0",
            "--to-type-version",
            "1.0.0",
            "--output",
            "artifacts/charter-v2.json",
            "--receipt",
            "receipts/migration.json",
        )

        migrated = json.loads((self.project / "artifacts/charter-v2.json").read_text())
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(migrated["type"]["name"], "research-charter")

    def test_export_rejects_floating_revisions_existing_destinations_and_unsafe_trees(
        self,
    ):
        historical = self.initialize_history()
        before = self.snapshot()
        destination = Path(self.directory.name) / "exported"
        for revision in (
            "HEAD",
            historical[:12],
            "a" * 40,
            self.git("rev-parse", "HEAD^{tree}"),
        ):
            result = self.invoke(
                "export-research-os",
                "--project",
                str(self.project),
                "--commit",
                revision,
                "--output",
                str(destination),
            )
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertFalse(destination.exists())
            self.assertEqual(self.snapshot(), before)
        destination.mkdir()
        (destination / "keep.txt").write_text("keep")
        result = self.invoke(
            "export-research-os",
            "--project",
            str(self.project),
            "--commit",
            historical,
            "--output",
            str(destination),
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual((destination / "keep.txt").read_text(), "keep")
        result = self.invoke(
            "export-research-os",
            "--project",
            str(self.project),
            "--commit",
            historical,
            "--output",
            str(self.project / "publications/export"),
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(self.snapshot(), before)
        (self.project / "unsafe").symlink_to("../outside")
        self.git("add", "unsafe")
        self.git("commit", "-qm", "固定不支持的符号链接")
        unsafe = self.git("rev-parse", "HEAD")
        result = self.invoke(
            "export-research-os",
            "--project",
            str(self.project),
            "--commit",
            unsafe,
            "--output",
            str(Path(self.directory.name) / "unsafe-export"),
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse((Path(self.directory.name) / "unsafe-export").exists())

    def test_migration_rolls_back_artifact_commit_when_receipt_commit_fails(self):
        historical = self.initialize_history()
        target = {"kind": "git", "path": "artifacts/charter.json", "commit": historical}
        rule = {
            "name": "preserve-charter",
            "version": "1.0.0",
            "operation": "preserve-spec",
            "source": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
            "destination": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
        }
        (self.project / "input.json").write_text(json.dumps(target))
        (self.project / "rules.json").write_text(json.dumps([rule]))
        hook = self.project / ".git/hooks/pre-commit"
        hook.write_text(
            "#!/bin/sh\n"
            'if git diff --cached --name-only | grep -qx "receipts/migration.json"; then\n'
            "  exit 1\n"
            "fi\n"
        )
        hook.chmod(0o755)
        self.git("add", ".")
        self.git("commit", "-qm", "固定回滚测试输入")
        before = self.snapshot()
        revision = self.git("rev-parse", "HEAD")

        result = self.invoke(
            "migrate-artifact",
            "--project",
            str(self.project),
            "--input",
            "input.json",
            "--rules",
            "rules.json",
            "--to-contract",
            "1.1.0",
            "--to-type-version",
            "1.0.0",
            "--output",
            "artifacts/charter-v2.json",
            "--receipt",
            "receipts/migration.json",
        )

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(self.git("rev-parse", "HEAD"), revision)
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.project / "receipts").exists())

    def test_migration_rejects_rules_input_and_output_conflicts_without_writes(self):
        historical = self.initialize_history()
        target = {"kind": "git", "path": "artifacts/charter.json", "commit": historical}
        rule = {
            "name": "preserve-charter",
            "version": "1.0.0",
            "operation": "preserve-spec",
            "source": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
            "destination": {
                "contract": "1.1.0",
                "type": "research-charter",
                "version": "1.0.0",
            },
        }
        cases = [
            (target, [], "new.json", "receipt.json"),
            (target, [rule, rule], "new.json", "receipt.json"),
            ({**target, "commit": "HEAD"}, [rule], "new.json", "receipt.json"),
            ({**target, "path": "question.txt"}, [rule], "new.json", "receipt.json"),
            (target, [rule], "new.json", "artifacts/charter.json"),
            (target, [rule], "new.json", "new.json/receipt.json"),
            (target, [rule], "new.json", "question.txt/receipt.json"),
            (target, [rule], "publications/p1/new.json", "receipt.json"),
            (target, [rule], ".research-os/runtime/new.json", "receipt.json"),
            (target, [rule], ".git/new.json", "receipt.json"),
        ]
        for selected, rules, output, receipt in cases:
            with self.subTest(
                output=output, receipt=receipt, target=selected, rules=len(rules)
            ):
                (self.project / "input.json").write_text(json.dumps(selected))
                (self.project / "rules.json").write_text(json.dumps(rules))
                self.git("add", ".")
                self.git("commit", "--allow-empty", "-qm", "固定迁移拒绝样例")
                before = self.snapshot()
                revision = self.git("rev-parse", "HEAD")
                result = self.invoke(
                    "migrate-artifact",
                    "--project",
                    str(self.project),
                    "--input",
                    "input.json",
                    "--rules",
                    "rules.json",
                    "--to-contract",
                    "1.1.0",
                    "--to-type-version",
                    "1.0.0",
                    "--output",
                    output,
                    "--receipt",
                    receipt,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.git("rev-parse", "HEAD"), revision)
                self.assertEqual(self.git("status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
