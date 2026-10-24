"""#60 discovery slice: the installed research-os package is the public seam."""

import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
RESEARCH_OS = SKILLS / "general/research-os"
ENTRY = RESEARCH_OS / "SKILL.md"
PLAYBOOK = RESEARCH_OS / "playbooks/discovery.md"
COMPOSITION = RESEARCH_OS / "references/discovery-composition.md"
TEMPLATES = RESEARCH_OS / "templates"
LICENSE = RESEARCH_OS / "licenses/idea-cycle/LICENSE"

REQUIRED = (
    "research-lit",
    "idea-generation",
    "novelty-check",
    "idea-review",
    "idea-refinement",
)

EXPECTED_SHA256 = {
    "LICENSE": "e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5",
}

ACTIVE_CALLER_FILES = (
    "README.md",
    "docs/README-en.md",
    "skills/README.md",
    "skills/general/research-os/SKILL.md",
    "skills/general/research-os/playbooks/discovery.md",
    "skills/general/research-os/playbooks/literature-review.md",
    "skills/general/research-os/references/PRODUCT-MAP.md",
    "skills/general/research-os/references/idea-cycle.md",
    "skills/general/research-os/references/migration-boundary.md",
    "docs/assets/README.md",
    "docs/assets/demo-script.sh",
    "docs/assets/workflow-diagrams.md",
    "docs/user-acceptance-guide.md",
)


class DiscoveryPackageContract(unittest.TestCase):
    def assertContains(self, text: str, marker: str) -> None:
        self.assertTrue(marker in text, f"missing public contract marker: {marker}")

    def test_installed_entry_and_source_record_use_only_current_routes(self):
        if shutil.which("npx") is None:
            self.skipTest("npx is not installed")

        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            project = Path(tmp)
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
            if version.returncode != 0:
                self.skipTest("skills@1.7.4 is not available in the npm cache")
            self.assertEqual(version.stdout.strip(), "1.7.4")

            install = subprocess.run(
                [
                    "npx", "--offline", "--yes", "skills@1.7.4", "add", str(ROOT),
                    "--skill", "research-os", "--agent", "claude-code", "--copy", "--yes",
                ],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            installed = project / ".claude/skills/research-os"
            self.assertTrue((installed / "SKILL.md").is_file())
            installed_entry = (installed / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("旧专业入口作为兼容调用保留", installed_entry)
            self.assertContains(installed_entry, "| discovery |")
            self.assertContains(installed_entry, "[discovery](playbooks/discovery.md)")
            self.assertContains(installed_entry, "paper-writing")
            self.assertTrue((installed / "playbooks/discovery.md").is_file())
            self.assertTrue((installed / "references/discovery-composition.md").is_file())
            self.assertTrue((installed / "licenses/idea-cycle/LICENSE").is_file())

            source_record = (ROOT / "docs/upstream-sources-and-licenses.md").read_text(
                encoding="utf-8"
            )
            idea_history = source_record.split("## 已采用的 Idea Discovery Workflow", 1)[1]
            idea_history = idea_history.split("\n## ", 1)[0]
            self.assertContains(idea_history, "0472e530251cdbd3364c33b110063c58f819edd7")
            self.assertContains(idea_history, "skills/idea-cycle/idea-discovery/")
            self.assertNotIn("本仓当前的 Idea Discovery 主入口", idea_history)
            self.assertNotIn("阶段间默认阻塞等用户确认", idea_history)
            for current_path in (
                "skills/general/research-os/SKILL.md",
                "skills/general/research-os/playbooks/discovery.md",
                "skills/general/research-os/references/discovery-composition.md",
                "skills/writing-cycle/paper-writing/SKILL.md",
                "skills/general/research-os/licenses/idea-cycle/LICENSE",
            ):
                with self.subTest(current_path=current_path):
                    self.assertContains(idea_history, current_path)
                    self.assertTrue((ROOT / current_path).is_file(), current_path)

    def test_research_os_reaches_complete_gap_composable_discovery(self):
        entry = ENTRY.read_text(encoding="utf-8")
        self.assertContains(entry, "| discovery |")
        self.assertContains(entry, "从研究方向到 Proposal")
        self.assertContains(entry, "[discovery](playbooks/discovery.md)")

        playbook = PLAYBOOK.read_text(encoding="utf-8")
        composition = COMPOSITION.read_text(encoding="utf-8")
        self.assertContains(playbook, "方向到 Proposal")
        self.assertContains(playbook, "references/discovery-composition.md")
        self.assertContains(playbook, "templates/research-brief.md")
        self.assertContains(playbook, "templates/discovery-report.md")
        self.assertContains(playbook, "按用户目标")
        self.assertContains(composition, "licenses/idea-cycle/LICENSE")
        self.assertContains(playbook, "完整且独立可交付")

        self.assertContains(composition, "## Required skills")
        for skill in REQUIRED:
            with self.subTest(required_skill=skill):
                self.assertContains(composition, f"`{skill}`")
        self.assertContains(composition, "creative-thinking-for-research")
        self.assertContains(composition, "可选")
        for marker in (
            "目标缺口", "子集", "重排", "回访", "DEPENDENCY MISSING / BLOCKED",
            "只阻塞受影响职责", "fresh 独立评审",
        ):
            with self.subTest(composition_rule=marker):
                self.assertContains(composition, marker)
        self.assertContains(composition, "原始回复")
        self.assertNotIn("stage-checkpoint", composition + playbook)

        brief = (TEMPLATES / "research-brief.md").read_text(encoding="utf-8")
        report = (TEMPLATES / "discovery-report.md").read_text(encoding="utf-8")
        for marker in ("## 问题陈述", "## 约束", "## 期望产出", "## 已有结果"):
            self.assertIn(marker, brief)
        for marker in (
            "## 文献 Landscape", "## 候选池与筛选", "## 查新结论", "## 独立评审",
            "## 收敛与 Proposal", "## 淘汰与未解决问题", "## 交付与停止",
        ):
            self.assertIn(marker, report)
        self.assertNotIn("用户阶段确认", report)
        self.assertNotIn("每阶段继续", report)

        self.assertTrue(LICENSE.is_file(), LICENSE)
        actual = hashlib.sha256(LICENSE.read_bytes()).hexdigest()
        self.assertEqual(actual, EXPECTED_SHA256["LICENSE"])

        old_controller = SKILLS / "idea-cycle/idea-discovery"
        self.assertFalse((old_controller / "SKILL.md").exists())
        self.assertFalse((old_controller / "agents/openai.yaml").exists())
        self.assertFalse((RESEARCH_OS / "playbooks/idea-discovery.md").exists())
        for rel in ACTIVE_CALLER_FILES:
            with self.subTest(active_caller=rel):
                self.assertNotIn("idea-discovery", (ROOT / rel).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
