"""Checker filesystem boundary: ignored trees cannot affect tracked diagnostics."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUARDED_RUN = r'''
import os
from pathlib import Path
import runpy
import sys

root = Path.cwd()
blocked = [root / '.pi', root / '.agents/evidence']
scandir = os.scandir
def guarded(path):
    if isinstance(path, (str, bytes, os.PathLike)):
        candidate = Path(os.fsdecode(path)).absolute()
        if any(candidate == item or candidate.is_relative_to(item) for item in blocked):
            raise AssertionError('checker entered ignored tree: ' + str(candidate))
    return scandir(path)
os.scandir = guarded
sys.argv = [str(root / 'scripts/check-skills.py')]
runpy.run_path(sys.argv[0], run_name='__main__')
'''


class TrackedMarkdownScanTests(unittest.TestCase):
    def test_ignored_trees_are_not_entered_and_tracked_damage_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = {
                '.gitignore': '.pi/\n.agents/\n',
                'README.md': '# Fixture\n',
                'skills/README.md': '# Skills\n',
                '.agents/notes/keep.md': '[bad](missing.md)\n',
                '.agents/notes/deleted.md': '# Tracked but deleted\n',
                'docs/z.md': '[bad](missing.md)\n[escape](../../outside.md)\n',
                'docs/a.md': '[untracked](../.pi/hidden.md)\n[ok](../README.md)\n',
                'skills/general/wrong/SKILL.md': '---\nname: other\ndescription: fixture\n---\n',
            }
            for relative, content in assets.items():
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding='utf-8')
            (root / 'scripts').mkdir()
            shutil.copy2(ROOT / 'scripts/check-skills.py', root / 'scripts/check-skills.py')
            for command in (['git', 'init', '-q'], ['git', 'add', '-f', '.']):
                subprocess.run(command, cwd=root, check=True, capture_output=True, timeout=15)
            (root / '.agents/notes/deleted.md').unlink()
            for relative in ('.pi/hidden.md', '.agents/evidence/nested/hidden.md'):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('[ignored](not-a-product-problem.md)\n', encoding='utf-8')
            # Capture the pre-fix observable ordering on this tiny, owned fixture only.
            order = [p.relative_to(root).as_posix() for p in root.rglob('*.md')
                     if p.relative_to(root).as_posix() in assets]
            result = subprocess.run(
                [sys.executable, '-c', GUARDED_RUN], cwd=root, capture_output=True,
                text=True, timeout=30,
            )
            self.assertEqual(result.stderr, '', result.stderr)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn('.agents/notes/keep.md:1: 链接目标不存在或未追踪: missing.md', result.stdout)
            self.assertIn('docs/z.md:1: 链接目标不存在或未追踪: missing.md', result.stdout)
            self.assertIn('docs/z.md:2: 链接越出仓库: ../../outside.md', result.stdout)
            self.assertIn('docs/a.md:1: 链接目标不存在或未追踪: ../.pi/hidden.md', result.stdout)
            self.assertIn("skills/general/wrong/SKILL.md: name 'other' 与目录名 'wrong' 不一致", result.stdout)
            self.assertNotIn('not-a-product-problem', result.stdout)
            self.assertNotIn('deleted.md', result.stdout)
            diagnostics = [line.split(':', 1)[0].removeprefix('  - ')
                           for line in result.stdout.splitlines()
                           if ': 链接' in line]
            self.assertEqual(diagnostics, [rel for rel in order for _ in range(
                2 if rel == 'docs/z.md' else 1 if rel in {
                    '.agents/notes/keep.md', 'docs/a.md'} else 0)])
