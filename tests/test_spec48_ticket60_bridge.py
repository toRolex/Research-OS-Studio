"""#60 W2：bridge 资源并入唯一 run-experiment 执行控制。"""

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "skills/validation-cycle/run-experiment"
LEGACY = ROOT / "skills/validation-cycle/experiment-bridge"
ROUTE = ROOT / "skills/general/research-os/playbooks/experiment-bridge.md"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

ACTIVE_DOCS = (
    ROOT / "README.md",
    ROOT / "docs/README-en.md",
    ROOT / "docs/user-acceptance-guide.md",
    ROOT / "skills/README.md",
    ROOT / "skills/general/research-os/SKILL.md",
    ROOT / "skills/general/research-os/references/PRODUCT-MAP.md",
    ROOT / "skills/general/research-os/references/validation.md",
    ROUTE,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BridgeRetirement(unittest.TestCase):
    def test_legacy_controller_and_install_slug_are_removed(self):
        self.assertFalse((LEGACY / "SKILL.md").exists(), "retired Skill must not be discoverable/installable")
        self.assertFalse(any(path.is_file() for path in LEGACY.rglob("*")))
        for path in ACTIVE_DOCS:
            body = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotIn("skills/validation-cycle/experiment-bridge/SKILL.md", body)
                self.assertNotRegex(body, r"(?m)^\s*/experiment-bridge\b")
                self.assertNotRegex(body, r"-s\s+experiment-bridge\b")

    def test_run_experiment_owns_mapped_assets_and_keeps_sibling_roles_separate(self):
        run = (RUN / "SKILL.md").read_text(encoding="utf-8")
        composition = RUN / "references/composition-map.md"
        report = RUN / "templates/run-report.md"
        self.assertTrue(composition.is_file())
        self.assertTrue(report.is_file())
        self.assertIn("references/composition-map.md", run)

        # Exact-byte duplicates are intentionally retained once under the canonical package.
        self.assertEqual(
            sha256(RUN / "LICENSE"),
            "e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5",
        )
        self.assertEqual(
            sha256(RUN / "references/mandate.md"),
            "88aa76af938dfbcf4baf680c51389c17ed6639bd39328fc3b36ef99e692e04e1",
        )

        composition_text = composition.read_text(encoding="utf-8")
        for name in (
            "run-experiment", "experiment-plan", "experiment-queue", "monitor-experiment",
            "training-health-check", "analyze-results", "experiment-audit", "result-to-claim",
            "blocked",
        ):
            self.assertIn(name, composition_text)

        report_text = report.read_text(encoding="utf-8")
        for marker in (
            "作业身份", "退出码", "原始日志", "产物", "Artifact validity",
            "先按本次作业身份查询原任务", "不要盲目重跑", "Monitoring and Health",
            "Analysis and Independent Audit",
            "Tracker Update", "Optional Ablation Suggestions",
        ):
            self.assertIn(marker, report_text)
        for marker in ("输入版本", "工具链", "独立目录", "失败原因", "Scientific conclusion"):
            self.assertIn(marker, report_text)

        self.assertIn("执行控制", run)
        self.assertIn("run_count_basis=planned-run", run)
        self.assertIn("最坏预留", run)
        self.assertIn("断线先查原作业", run)
        self.assertIn("数学", run)
        self.assertIn("是唯一执行控制", composition_text)
        self.assertIn("单装 `run-experiment` 时", run)
        self.assertIn("只将该批量分支标为 `blocked`", run)
        self.assertIn("独立小批次不受影响", composition_text)

    def test_research_os_recipe_routes_execution_only_to_run_experiment(self):
        playbook = ROUTE.read_text(encoding="utf-8")
        self.assertIn("skills/validation-cycle/run-experiment/SKILL.md", playbook)
        self.assertIn("只在用户委托要求时", playbook)
        for skill in (
            "monitor-experiment", "training-health-check", "analyze-results",
            "experiment-audit", "result-to-claim",
        ):
            with self.subTest(skill=skill):
                self.assertIn(f"`{skill}`", playbook)
        self.assertNotIn("skills/validation-cycle/experiment-bridge/", playbook)
        self.assertNotIn("run_count_basis=planned-run", playbook)
        self.assertNotIn("每个 attempt 先记最坏预留", playbook)
        composition = (RUN / "references/composition-map.md").read_text(encoding="utf-8")
        monitor_row = next(line for line in composition.splitlines() if "`monitor-experiment`" in line)
        self.assertIn("观察运行状态", monitor_row)
        self.assertIn("不控制作业或作科学判断", monitor_row)
        self.assertIn("该分支 `blocked`", monitor_row)


class InstalledRunExperiment(unittest.TestCase):
    def test_skills_cli_single_install_contains_migrated_package_assets(self):
        if shutil.which("npx") is None:
            self.fail("npx is required for the real Skills CLI public-seam contract")

        with tempfile.TemporaryDirectory(dir="/tmp") as directory:
            project = Path(directory)
            home = project / "home"
            home.mkdir()
            env = {
                **os.environ,
                "HOME": str(home),
                "TMPDIR": "/tmp",
                "npm_config_cache": str(Path.home() / ".npm"),
            }
            version = subprocess.run(
                ["npx", "--offline", "--yes", "skills@1.7.4", "--version"],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(version.returncode, 0, version.stdout + version.stderr)
            self.assertEqual(version.stdout.strip(), "1.7.4")

            result = subprocess.run(
                [
                    "npx", "--offline", "--yes", "skills@1.7.4", "add", str(ROOT),
                    "--skill", "run-experiment", "--agent", "claude-code", "--copy", "--yes",
                ],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            installed_root = project / ".claude/skills"
            installed = installed_root / "run-experiment"
            self.assertEqual(
                sorted(path.name for path in installed_root.iterdir() if path.is_dir()),
                ["run-experiment"],
            )
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue((installed / "LICENSE").is_file())
            self.assertTrue((installed / "references/composition-map.md").is_file())
            self.assertTrue((installed / "templates/run-report.md").is_file())

            expected_files = {
                path.relative_to(RUN).as_posix(): path.read_bytes()
                for path in RUN.rglob("*")
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

            for markdown in installed.rglob("*.md"):
                for target in LINK.findall(markdown.read_text(encoding="utf-8")):
                    if target.startswith(("http:", "https:", "mailto:")):
                        continue
                    file_part = unquote(target.split("#", 1)[0])
                    resolved = (markdown.parent / file_part).resolve() if file_part else markdown
                    self.assertIn(installed.resolve(), resolved.parents, f"{markdown}: {target}")
                    self.assertTrue(resolved.is_file(), f"{markdown}: {target}")

            # An isolated install does not silently imply the queue or other independent duties.
            run_text = (installed / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("只将该批量分支标为 `blocked`", run_text)
            self.assertIn("experiment-queue` 未安装或不可调用", run_text)
            self.assertFalse((installed_root / "experiment-queue").exists())


if __name__ == "__main__":
    unittest.main()
