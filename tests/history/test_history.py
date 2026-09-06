from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.history import HistoryBlocked, inspect_history, restore_history  # noqa: E402
from research_os.install import SourceBundle, build_install_plan, execute_install  # noqa: E402


class HistoryRestoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name) / "repository"
        self.repository.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.test")

    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repository), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return result.stdout.strip()

    def commit_current_install(self) -> str:
        bundle = SourceBundle(
            version="1.0.0",
            source_revision="a" * 40,
            files={"core/skills/example/SKILL.md": b"---\nname: example\n---\nold\n"},
        )
        execute_install(self.repository, build_install_plan(bundle, require_verified_source=False))
        (self.repository / "runs/old/report.json").parent.mkdir(parents=True)
        (self.repository / "runs/old/report.json").write_text('{"status":"failed"}\n')
        self.git("add", ".")
        self.git("commit", "-qm", "old install and failed run")
        return self.git("rev-parse", "HEAD")

    def test_restore_current_install_reads_pinned_commit_and_never_changes_source(self) -> None:
        historical = self.commit_current_install()
        (self.repository / "core/skills/example/SKILL.md").write_text("current drift\n")
        before = {
            path.relative_to(self.repository).as_posix(): path.read_bytes()
            for path in self.repository.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }
        output = Path(self.temporary.name) / "restored"
        result = restore_history(self.repository, historical, output)
        self.assertNotIsInstance(result, HistoryBlocked)
        self.assertIn(b"old", (output / "core/skills/example/SKILL.md").read_bytes())
        self.assertEqual((output / "runs/old/report.json").read_text(), '{"status":"failed"}\n')
        receipt = json.loads((output / ".research-os/history-restore.json").read_text())
        self.assertEqual(receipt["commit"], historical)
        self.assertEqual(receipt["profile"], "project-local-install-v1")
        self.assertTrue(receipt["read_only"])
        after = {
            path.relative_to(self.repository).as_posix(): path.read_bytes()
            for path in self.repository.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }
        self.assertEqual(after, before)
        self.assertEqual(self.git("status", "--porcelain"), "M core/skills/example/SKILL.md")

    def test_restore_supports_legacy_runtime_manifest(self) -> None:
        files = {
            "scripts/research-os.py": b"print('legacy')\n",
            "src/research_os/cli.py": b"VALUE = 'old'\n",
            "uv.lock": b"version = 1\n",
        }
        runtime = self.repository / ".research-os/runtime"
        for name, content in files.items():
            path = runtime / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (runtime / "manifest.json").write_text(
            json.dumps(
                {
                    "contract": {"name": "research-os/runtime-manifest", "version": "1.0.0"},
                    "files": sorted(files),
                }
            )
        )
        (self.repository / "artifacts/old.json").parent.mkdir()
        (self.repository / "artifacts/old.json").write_text("{}\n")
        self.git("add", ".")
        self.git("commit", "-qm", "legacy runtime")
        commit = self.git("rev-parse", "HEAD")
        manifest, _ = inspect_history(self.repository, commit)
        self.assertEqual(manifest.profile, "legacy-self-contained-runtime-v1")
        output = Path(self.temporary.name) / "legacy"
        result = restore_history(self.repository, commit, output)
        self.assertNotIsInstance(result, HistoryBlocked)
        self.assertEqual((output / ".research-os/runtime/src/research_os/cli.py").read_bytes(), files["src/research_os/cli.py"])
        self.assertTrue((output / "artifacts/old.json").is_file())

    def test_restore_rejects_short_floating_missing_and_tree_revisions(self) -> None:
        commit = self.commit_current_install()
        tree = self.git("rev-parse", "HEAD^{tree}")
        for revision in ("HEAD", commit[:12], "f" * 40, tree):
            with self.subTest(revision=revision):
                output = Path(self.temporary.name) / f"out-{revision[:8]}"
                result = restore_history(self.repository, revision, output)
                self.assertIsInstance(result, HistoryBlocked)
                self.assertFalse(output.exists())

    def test_restore_rejects_existing_or_in_repository_destination(self) -> None:
        commit = self.commit_current_install()
        existing = Path(self.temporary.name) / "existing"
        existing.mkdir()
        (existing / "keep").write_text("keep")
        result = restore_history(self.repository, commit, existing)
        self.assertIsInstance(result, HistoryBlocked)
        self.assertEqual((existing / "keep").read_text(), "keep")
        nested = self.repository / "restored"
        result = restore_history(self.repository, commit, nested)
        self.assertIsInstance(result, HistoryBlocked)
        self.assertFalse(nested.exists())

    def test_restore_rejects_symlinked_output_parent(self) -> None:
        commit = self.commit_current_install()
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        linked_parent = Path(self.temporary.name) / "linked-parent"
        linked_parent.symlink_to(outside, target_is_directory=True)
        output = linked_parent / "restored"
        result = restore_history(self.repository, commit, output)
        self.assertIsInstance(result, HistoryBlocked)
        self.assertFalse((outside / "restored").exists())

    def test_restore_detects_output_parent_symlink_swap_before_publish(self) -> None:
        commit = self.commit_current_install()
        parent = Path(self.temporary.name) / "publish-parent"
        parent.mkdir()
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        output = parent / "restored"
        from research_os.history import git_restore as history

        real_publish = history._publish_directory
        swapped = False

        def swap_then_publish(*args, **kwargs) -> None:
            nonlocal swapped
            if not swapped:
                swapped = True
                parent.rename(Path(self.temporary.name) / "detached-parent")
                parent.symlink_to(outside, target_is_directory=True)
            real_publish(*args, **kwargs)

        with patch.object(history, "_publish_directory", side_effect=swap_then_publish):
            result = restore_history(self.repository, commit, output)
        self.assertTrue(swapped)
        self.assertIsInstance(result, HistoryBlocked)
        self.assertEqual(result.exit_code, 1)
        self.assertFalse((outside / "restored").exists())

    def test_restore_final_publish_preserves_concurrently_created_empty_directory(self) -> None:
        from research_os.history import git_restore as history

        commit = self.commit_current_install()
        output = Path(self.temporary.name) / "raced-output"
        original_publish = history._publish_directory
        token = None

        def occupy() -> None:
            nonlocal token
            output.mkdir()
            token = output.stat().st_ino

        def publish_with_race(*args, **kwargs):
            occupy()
            return original_publish(*args, **kwargs)

        with patch.object(history, "_publish_directory", side_effect=publish_with_race):
            result = restore_history(self.repository, commit, output)
        self.assertIsNotNone(token)
        self.assertIsInstance(result, HistoryBlocked)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.to_dict()["verdict"], "fail")
        self.assertEqual(output.stat().st_ino, token)
        self.assertEqual(list(output.iterdir()), [])

    def test_restore_unavailable_atomic_publish_fails_without_fallback(self) -> None:
        commit = self.commit_current_install()
        output = Path(self.temporary.name) / "unsupported"
        with patch("research_os.history.git_restore.ctypes.CDLL", return_value=object()), patch(
            "research_os.history.git_restore.os.replace", side_effect=AssertionError("clobber fallback")
        ):
            result = restore_history(self.repository, commit, output)
        self.assertIsInstance(result, HistoryBlocked)
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(output.exists())
        self.assertIn("history.cleanup_required", {issue["code"] for issue in result.issues})

    def test_restore_rejects_symlinked_ancestor_above_real_parent(self) -> None:
        commit = self.commit_current_install()
        outside = Path(self.temporary.name) / "outside"
        (outside / "real-parent").mkdir(parents=True)
        link = Path(self.temporary.name) / "linked"
        link.symlink_to(outside, target_is_directory=True)
        result = restore_history(self.repository, commit, link / "real-parent/restored")
        self.assertIsInstance(result, HistoryBlocked)
        self.assertFalse((outside / "real-parent/restored").exists())

    def test_restore_replaced_staging_at_publish_never_reports_pass(self) -> None:
        from research_os.history import git_restore as history

        commit = self.commit_current_install()
        output = Path(self.temporary.name) / "staging-race"
        real_publish = history._publish_directory
        replacement_token = None

        def replace_staging(source, destination, *, parent_fd):
            nonlocal replacement_token
            os.rename(source, source + "-original", src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            os.mkdir(source, dir_fd=parent_fd)
            replacement_token = os.stat(source, dir_fd=parent_fd).st_ino
            return real_publish(source, destination, parent_fd=parent_fd)

        with patch.object(history, "_publish_directory", side_effect=replace_staging):
            result = restore_history(self.repository, commit, output)
        self.assertIsInstance(result, HistoryBlocked)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.to_dict()["verdict"], "fail")
        self.assertEqual(output.stat().st_ino, replacement_token)
        self.assertIn("history.cleanup_required", {issue["code"] for issue in result.issues})

    def test_restore_rejects_archived_receipt_before_creating_parent(self) -> None:
        self.commit_current_install()
        receipt = self.repository / ".research-os/history-restore.json"
        receipt.write_bytes(b'{"historical":"must not overwrite"}\n')
        self.git("add", ".")
        self.git("commit", "-qm", "archived restore receipt")
        commit = self.git("rev-parse", "HEAD")
        output = Path(self.temporary.name) / "new-parent/restored"
        result = restore_history(self.repository, commit, output)
        self.assertIsInstance(result, HistoryBlocked)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.to_dict()["verdict"], "fail")
        self.assertEqual(result.issues[0]["code"], "history.preflight")
        self.assertFalse(output.exists())
        self.assertFalse(output.parent.exists())
        self.assertEqual(receipt.read_bytes(), b'{"historical":"must not overwrite"}\n')

    def test_restore_rejects_gitlinks_before_archiving_without_creating_output(self) -> None:
        base = self.commit_current_install()
        for index, name in enumerate(("dependency", "vendor/nested dependency", "vendor/odd\tname\nmodule")):
            with self.subTest(name=name):
                self.git("read-tree", base)
                self.git("update-index", "--add", "--cacheinfo", f"160000,{base},{name}")
                self.git("commit", "-qm", "gitlink fixture")
                commit = self.git("rev-parse", "HEAD")
                self.assertIn("160000 commit", self.git("ls-tree", "-r", commit))
                output = Path(self.temporary.name) / f"new-parent-{index}" / "restored"
                # Trace the real Git boundary: rejection must precede archive generation.
                trace = Path(self.temporary.name) / f"git-trace-{index}"
                with patch.dict(os.environ, {"GIT_TRACE2_EVENT": str(trace)}):
                    result = restore_history(self.repository, commit, output)
                self.assertIsInstance(result, HistoryBlocked)
                self.assertEqual(result.issues[0]["code"], "history.preflight")
                self.assertIn("gitlink", result.issues[0]["message"])
                self.assertIn("160000", result.issues[0]["message"])
                self.assertFalse(output.parent.exists())
                commands = [
                    event["name"]
                    for line in trace.read_text().splitlines()
                    if (event := json.loads(line)).get("event") == "cmd_name"
                ]
                self.assertIn("ls-tree", commands)
                self.assertNotIn("archive", commands)
                self.assertEqual(self.git("rev-parse", "HEAD"), commit)
                self.git("update-index", "--force-remove", name)
                self.git("commit", "-qm", "remove fixture gitlink")
                trace.unlink()

    def test_restore_rejects_symlink_and_incomplete_or_drifted_manifests(self) -> None:
        commit = self.commit_current_install()
        outside = Path(self.temporary.name) / "outside"
        outside.write_text("outside")
        (self.repository / "unsafe").symlink_to(outside)
        self.git("add", "unsafe")
        self.git("commit", "-qm", "unsafe link")
        unsafe = self.git("rev-parse", "HEAD")
        result = restore_history(self.repository, unsafe, Path(self.temporary.name) / "unsafe-output")
        self.assertIsInstance(result, HistoryBlocked)

        self.git("reset", "--hard", commit)
        (self.repository / "core/skills/example/SKILL.md").unlink()
        self.git("add", "-u")
        self.git("commit", "-qm", "incomplete install")
        incomplete = self.git("rev-parse", "HEAD")
        result = restore_history(self.repository, incomplete, Path(self.temporary.name) / "incomplete")
        self.assertIsInstance(result, HistoryBlocked)

        self.git("reset", "--hard", commit)
        (self.repository / "core/skills/example/SKILL.md").write_text("drifted but committed\n")
        self.git("add", ".")
        self.git("commit", "-qm", "drift install")
        drift = self.git("rev-parse", "HEAD")
        result = restore_history(self.repository, drift, Path(self.temporary.name) / "drift")
        self.assertIsInstance(result, HistoryBlocked)


if __name__ == "__main__":
    unittest.main()
