"""Installed-package regression for the #60 C01 repair authorization seam."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree

ROOT = Path(__file__).resolve().parents[1]
SKILL_REL = Path("skills/writing-cycle/paper-compile-repair")
BASELINE_FIXTURE = ROOT / "tests/fixtures/spec48-ticket60-c01-baseline"


class InstalledCompileRepairAuthorization(unittest.TestCase):
    def test_installed_contract_distinguishes_standalone_and_delegated_repairs(self):
        if shutil.which("npx") is None:
            self.fail("npx is required for the installed C01 contract seam")

        with tempfile.TemporaryDirectory(prefix="spec48-c01-") as scratch:
            temp_root = Path(scratch)
            source = temp_root / "source"
            copy_tracked_tree(ROOT, source)
            if os.environ.get("SPEC48_C01_BASELINE_FIXTURE"):
                for relative in (Path("SKILL.md"), Path("references/bounded-repair.md")):
                    fixture_relative = relative.with_suffix(".fixture")
                    content = (BASELINE_FIXTURE / fixture_relative).read_bytes()
                    (source / SKILL_REL / relative).write_bytes(content)
            project = temp_root / "project"
            project.mkdir()
            home = temp_root / "home"
            home.mkdir()
            env = {
                **os.environ,
                "HOME": str(home),
                "TMPDIR": str(temp_root),
                "npm_config_cache": str(Path.home() / ".npm"),
            }

            version = subprocess.run(
                ["npx", "--offline", "--yes", "skills@1.7.4", "--version"],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                timeout=75,
            )
            self.assertEqual(version.returncode, 0, version.stdout + version.stderr)
            self.assertEqual(version.stdout.strip(), "1.7.4")

            installed = project / ".claude/skills/paper-compile-repair"
            install = subprocess.run(
                [
                    "npx", "--offline", "--yes", "skills@1.7.4", "add", str(source),
                    "--skill", "paper-compile-repair", "--agent", "claude-code",
                    "--copy", "--yes",
                ],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                timeout=75,
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            skill = installed / "SKILL.md"
            bounded = installed / "references/bounded-repair.md"
            self.assertTrue(skill.is_file())
            self.assertTrue(bounded.is_file())
            skill_text = skill.read_text(encoding="utf-8")
            bounded_text = bounded.read_text(encoding="utf-8")

            # Reject the old universal gate before checking replacement wording.
            # SPEC48_C01_BASELINE_FIXTURE runs this same install seam against the
            # checked-in pre-fix counterexample, without requiring a local commit.
            stale_universal_gates = (
                "原稿仅应用本轮用户明确认可的具体 diff",
                "先让用户单独认可命令",
                "展示并等待用户明确认可",
                "尚未形成的后续 diff 必须当轮展示再认可",
                "本轮所有拟修改文件、完整 diff、构建和剩余预算均由用户明确认可",
                "缺任何一项即停在这里，零应用",
                "用户认可 → 应用",
            )
            for stale in stale_universal_gates:
                self.assertNotIn(stale, skill_text + "\n" + bounded_text, stale)

            self.assertIn("[有界修复](references/bounded-repair.md)", skill_text)
            source_skill = source / SKILL_REL
            expected_files = {
                path.relative_to(source_skill).as_posix(): path.read_bytes()
                for path in source_skill.rglob("*")
                if path.is_file()
            }
            installed_files = {
                path.relative_to(installed).as_posix(): path.read_bytes()
                for path in installed.rglob("*")
                if path.is_file()
            }
            self.assertEqual(installed_files.keys(), expected_files.keys())
            for relative, expected in expected_files.items():
                self.assertEqual(installed_files[relative], expected, relative)

            # The installed step contract must explain both authorization sources;
            # the reference cannot be the only place that grants delegation.
            self.assertIn("独立调用", skill_text)
            self.assertIn("已授权父委托", skill_text)
            self.assertIn("不要求再次独立点名", skill_text)
            self.assertIn("授权覆盖", skill_text)
            self.assertIn("完整 unified diff", skill_text)
            self.assertIn("完整 unified diff", bounded_text)
            self.assertIn("授权来源", skill_text)
            authorization_step = skill_text.split("## 3. ", 1)[1].split("## 4. ", 1)[0]
            for required in (
                "独立调用",
                "已授权父委托",
                "缺项处理",
                "仅当独立请求缺少必要许可",
                "未获明确许可的源写入或构建不执行",
                "不要求未来每个普通 diff 再获用户批准",
            ):
                self.assertIn(required, authorization_step, required)

            # Ordinary in-scope work is executable under a live parent grant;
            # changes of target/effects/scope still stop for a decision.
            for retained in (
                "尚未形成的 diff",
                "不逐 diff",
                "主要目标、命题或假设",
                "新副作用",
                "写域",
                "真实",
                "不重置",
                "不付费",
                "不远程执行",
                "对外发送",
                "算力/作业名额批次",
                "不由普通修复授权推导",
            ):
                self.assertIn(retained, skill_text + "\n" + bounded_text, retained)

            # Existing TeX and source-concurrency protections remain part of the
            # installed contract rather than being traded away for delegation.
            for retained in (
                "现有可验证 sandbox",
                "TeX 输入闭合性",
                "并发变化",
                "基线",
                "构建目录",
                "副产物",
                "资源/时间预算",
            ):
                self.assertIn(retained, skill_text + "\n" + bounded_text, retained)


if __name__ == "__main__":
    unittest.main()
