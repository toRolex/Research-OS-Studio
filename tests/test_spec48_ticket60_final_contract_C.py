"""Installed-skill contract seam for ticket #60 findings C03/C05/C06."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "research-improvement",
    "idea-refinement",
    "idea-generation",
    "claim-stress-test",
    "paper-talk",
    "resubmit-pipeline",
    "rebuttal",
)


class FinalContractCInstalled(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if shutil.which("npx") is None:
            raise unittest.SkipTest("npx is required for the installed-package seam")

        cls.tmp = tempfile.TemporaryDirectory(prefix="spec48-ticket60-C-", dir="/tmp")
        project = Path(cls.tmp.name)
        source = project / "source"
        install = project / "install"
        home = project / "home"
        install.mkdir()
        home.mkdir()

        # The fixture deliberately contains only Git-tracked files; ignored evidence
        # archives and local work products must not enter the package install.
        copy_tracked_tree(ROOT, source)
        env = {
            **os.environ,
            "HOME": str(home),
            "TMPDIR": "/tmp",
            "npm_config_cache": str(Path.home() / ".npm"),
        }
        version = subprocess.run(
            ["npx", "--offline", "--yes", "skills@1.7.4", "--version"],
            cwd=install,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if version.returncode != 0:
            raise unittest.SkipTest("skills@1.7.4 is unavailable in the offline npm cache")
        if version.stdout.strip() != "1.7.4":
            raise AssertionError(f"unexpected skills CLI version: {version.stdout!r}")

        command = [
            "npx", "--offline", "--yes", "skills@1.7.4", "add", str(source),
        ]
        for skill in SKILLS:
            command.extend(("--skill", skill))
        command.extend(("--agent", "claude-code", "--copy", "--yes"))
        installed = subprocess.run(
            command,
            cwd=install,
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if installed.returncode != 0:
            raise AssertionError(installed.stdout + installed.stderr)

        cls.installed = install / ".claude/skills"
        for skill in SKILLS:
            if not (cls.installed / skill / "SKILL.md").is_file():
                raise AssertionError(f"missing installed skill: {skill}")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def text(self, skill: str, relative: str = "SKILL.md") -> str:
        return (self.installed / skill / relative).read_text(encoding="utf-8")

    def assertNoObsoleteGate(self, text: str, *clauses: str) -> None:
        for clause in clauses:
            with self.subTest(obsolete_clause=clause):
                if clause in text:
                    self.fail(f"obsolete contract clause remains: {clause}")

    def assertContract(self, text: str, clause: str) -> None:
        if clause not in text:
            self.fail(f"missing contract: {clause}")

    def assertContractPattern(self, text: str, pattern: str) -> None:
        if re.search(pattern, text) is None:
            self.fail(f"missing contract pattern: {pattern}")

    def test_c03_composition_inherits_authority_without_removing_real_gates(self):
        text = self.text("research-improvement", "references/composition-map.md")
        self.assertNoObsoleteGate(
            text,
            "以下均为 user-invoked 顶层入口，只能由用户另行显式调用",
            "交回用户，由用户另行点名",
        )
        for contract in (
            "原委托",
            "调用者",
            "有效 batch 授权",
            "fresh 独立审查",
            "blocked",
            "只读",
        ):
            with self.subTest(contract=contract):
                self.assertContract(text, contract)
        self.assertContract(text, "`run-experiment`")
        self.assertContract(text, "超出原委托授权")

    def test_c05_ordinary_interruption_resumes_only_after_revalidating_mandate(self):
        text = self.text("idea-refinement")
        self.assertNoObsoleteGate(text, "中断后仅在用户要求继续时")
        self.assertContractPattern(text, r"普通(?:上下文或工具)?中断.{0,100}原委托.{0,100}剩余预算")
        self.assertContractPattern(text, r"用户明确(?:叫停|停止).{0,80}(?:不得|不能).{0,30}恢复")
        self.assertContract(text, "只有目标替换才停下确认")
        self.assertContract(text, "未参与生成/修订的实际可用 reviewer")

    def test_c06_idea_generation_returns_other_roles_to_authorized_caller(self):
        text = self.text("idea-generation")
        self.assertNoObsoleteGate(text, "Validation 与写论文由用户另行点名")
        for clause in (
            "只交付候选与 handoff", "既有授权", "原委托", "只有目标替换才停下确认",
            "外部检索", "付费",
        ):
            self.assertContract(text, clause)

    def test_c06_claim_stress_test_remains_read_only_but_does_not_reauthorize_caller(self):
        text = self.text("claim-stress-test")
        self.assertNoObsoleteGate(text, "其他专项审计由用户另行点名")
        for clause in ("稿件与支撑材料只读", "调用者", "原委托", "独立"):
            self.assertContract(text, clause)

    def test_c06_paper_talk_accepts_authorized_cascade_without_external_side_effects(self):
        text = self.text("paper-talk")
        self.assertNoObsoleteGate(
            text,
            "不由论文写作自动启动",
            "不接受其他顶层 Workflow 自动发起",
        )
        for clause in (
            "已授权", "调用者", "源论文、数据、BibTeX、既有演讲材料始终只读",
            "不自动发布、上传、投稿",
        ):
            self.assertContract(text, clause)

    def test_c06_resubmit_preserves_old_draft_and_allows_scoped_handoff(self):
        text = self.text("resubmit-pipeline")
        self.assertNoObsoleteGate(
            text,
            "不自动调用 `rebuttal`、`paper-talk` 或任何其他顶层 Workflow；需要时交用户另行点名。",
            "composed 不适用（本 Skill 不被其他 Workflow 自动调用）",
        )
        for clause in (
            "已授权写作/修复职责", "委托已授权修复时", "调用者",
            "旧投稿目录及其中一切文件始终只读", "不向任何外部投稿系统提交、上传或发布",
        ):
            self.assertContract(text, clause)

    def test_c06_rebuttal_never_executes_experiments_but_can_handoff_valid_batch(self):
        text = self.text("rebuttal")
        self.assertNoObsoleteGate(
            text,
            "即使用户给出自动实验选项，也先交还用户另行启动适当流程",
        )
        for clause in (
            "不亲自实验、补证明、投稿或上传", "调用者", "有效 batch 授权",
            "目标替换", "付费",
        ):
            self.assertContract(text, clause)


if __name__ == "__main__":
    unittest.main()
