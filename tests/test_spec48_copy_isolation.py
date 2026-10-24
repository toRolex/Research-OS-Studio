"""Spec48 可损坏副本只携带 tracked 资产，不吸入本机证据树。"""
import shutil
import stat
import subprocess
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import test_check_skills_policy_gates as policy_gates
import test_spec48_ticket49 as ticket49
import test_spec48_ticket51 as ticket51
import test_spec48_ticket54 as ticket54
import test_spec48_ticket56 as ticket56


class CopyIsolation(unittest.TestCase):
    def test_ticket_copies_keep_tracked_assets_without_ignored_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            source.mkdir()
            assets = {
                ".gitignore": ".agents/\n.venv/\n__pycache__/\n",
                "scripts/check-skills.py": "# checker fixture\n",
                "skills/example/SKILL.md": "# Tracked capability\n",
                "tests/fixture.txt": "tracked test asset\n",
                ".agents/notes/required.md": "tracked note, not disposable evidence\n",
            }
            for name, content in assets.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            (source / "scripts/check-skills.py").chmod(0o755)
            subprocess.run(["git", "init", "-q", str(source)], check=True)
            subprocess.run(
                ["git", "-C", str(source), "add", "-f", "."], check=True
            )
            # The snapshot must use current tracked contents, not just a HEAD archive.
            assets["tests/fixture.txt"] = "working tree edit\n"
            (source / "tests/fixture.txt").write_text(
                assets["tests/fixture.txt"], encoding="utf-8"
            )
            excluded = (
                ".agents/notes/merge-evidence/tmp/nested/sentinel.txt",
                ".venv/cache.txt",
                "__pycache__/cache.txt",
                "untracked.txt",
            )
            for name in excluded:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("must stay in source\n", encoding="utf-8")

            entries = (
                (ticket49, "WorkCopy"),
                (ticket51, "copy_tree"),
                (ticket54, "WorkCopy"),
                (ticket56, "WorkCopy"),
                (policy_gates, "new-destination"),
                (policy_gates, "existing-destination"),
            )
            for module, entry in entries:
                with self.subTest(helper=module.__name__, entry=entry), patch.object(module, "ROOT", source), ExitStack() as cleanup:
                    if module is policy_gates:
                        parent = Path(cleanup.enter_context(tempfile.TemporaryDirectory()))
                        dest = parent if entry == "existing-destination" else parent / "repo"
                        module.copy_worktree(dest)
                    elif module is not ticket51:
                        work = cleanup.enter_context(module.WorkCopy())
                        dest = work.path
                    else:
                        dest = module.copy_tree()
                        cleanup.callback(shutil.rmtree, dest.parent)
                    for name in excluded:
                        self.assertFalse((dest / name).exists(), name)
                        self.assertTrue((source / name).is_file(), name)
                    copied = {
                        path.relative_to(dest).as_posix()
                        for path in dest.rglob("*")
                        if path.is_file() and ".git" not in path.relative_to(dest).parts
                    }
                    self.assertEqual(copied, set(assets))
                    for name, content in assets.items():
                        self.assertEqual((dest / name).read_text(encoding="utf-8"), content)
                    self.assertEqual(
                        stat.S_IMODE((dest / "scripts/check-skills.py").stat().st_mode),
                        0o755,
                    )
                    tracked = subprocess.run(
                        ["git", "ls-files", "-z"], cwd=dest,
                        check=True, capture_output=True, text=True,
                    ).stdout.rstrip("\0").split("\0")
                    self.assertEqual(set(tracked), set(assets))
