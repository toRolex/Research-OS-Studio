"""#51 arena 候选比较与整合能力。

期望来自 #48 spec 与 #51 票面：保留 Frame/Fan-out/Cross-judge/Pick/Graft/Verify
职责与完整候选阅读、预先 rubric、输出隔离、交叉评判与主编排者综合、数学整合后
重查假设/记号/依赖闭合、胜出不等于原命题成立、独立于 swarm、缺子代理 blocked、
不固定品牌模型或个人路径、随包 MIT 归属。静态结构合同；不冒称科研质量。
默认结构 scope 不允许任何失败，历史身份另列。
"""
import importlib.util
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree
from spec48_checker_result import parse_checker_result

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
ARENA = ROOT / "skills/organization/arena"
SKILL = ARENA / "SKILL.md"
LICENSE = ARENA / "LICENSE"
ENTRY = ROOT / "skills/general/research-os/SKILL.md"
BOUNDARY = ROOT / "skills/general/research-os/references/migration-boundary.md"
SOURCE_RECORD = ROOT / "docs/upstream-sources-and-licenses.md"

PHASES = ("Frame", "Fan-out", "Cross-judge", "Pick", "Graft", "Verify")
FORBIDDEN_PERSONAL = ("~/.cursor", "/Users/", "pstack-models.mdc", "poteto-mode")
FORBIDDEN_BRANDS = ("claude-opus", "grok-4.7", "composer-", "cursor-grok")


def load():
    spec = importlib.util.spec_from_file_location("check_skills_t51", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def problem_lines(root: Path) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return parse_checker_result(result)


def fresh_problems(root: Path) -> list[str]:
    return problem_lines(root)


def _force_rmtree(func, path, _exc):
    os.chmod(path, stat.S_IRWXU)
    func(path)


def copy_tree() -> Path:
    tmp = Path(tempfile.mkdtemp())
    dest = tmp / "repo"
    copy_tracked_tree(ROOT, dest)
    for command in (
        ["git", "init"],
        ["git", "add", "-f", "."],
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base"],
    ):
        subprocess.run(command, cwd=dest, check=True, capture_output=True)
    return dest

class ArenaCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

    def test_skill_exists_with_explicit_invocation_and_license(self):
        self.assertTrue(SKILL.is_file())
        self.assertTrue(LICENSE.is_file())
        license_text = LICENSE.read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Lauren Tan", license_text)
        self.assertIn("disable-model-invocation: true", self.text)
        yaml_text = (ARENA / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", yaml_text)

    def test_upstream_attribution_records_source_repo_and_revision(self):
        self.assertIn("cursor/plugins", self.text)
        self.assertIn("88d47514b82e7c44f00f2b2a72ff6dd12158038c", self.text)
        self.assertIn("pstack", self.text)

    def test_central_source_record_names_arena_asset_and_packaged_license(self):
        record = SOURCE_RECORD.read_text(encoding="utf-8")
        required = (
            "pstack/skills/arena/SKILL.md",
            "skills/organization/arena/LICENSE",
            "88d47514b82e7c44f00f2b2a72ff6dd12158038c",
        )
        missing = [item for item in required if item not in record]
        self.assertFalse(missing, f"central arena source record is missing: {missing}")

    def test_six_phases_preserved_with_full_reading_and_rubric_first(self):
        for phase in PHASES:
            self.assertIn(phase, self.text, phase)
        frame = self.text.split("## Phase A: Frame", 1)[1].split("## Phase B: Fan-out", 1)[0]
        self.assertLess(frame.index("先声明 rubric"), frame.index("候选运行之前"))
        self.assertIn("候选只看任务本身，不看 rubric", frame)
        self.assertLess(self.text.index("## Phase B: Fan-out"), self.text.index("## Phase C: Cross-judge"))
        cross_judge = self.text.split("## Phase C: Cross-judge", 1)[1].split("## Phase D: Pick", 1)[0]
        self.assertIn("候选还在写的时候不要派评判者", cross_judge)
        pick = self.text.split("## Phase D: Pick", 1)[1].split("## Phase E: Graft", 1)[0]
        self.assertIn("完整阅读每一个候选全文", pick)
        self.assertIn("逐项打分", pick)

    def test_output_isolation_and_cross_judge_independence(self):
        fan_out = self.text.split("## Phase A: Frame", 1)[1].split("## Phase B: Fan-out", 1)[0]
        self.assertIn("候选之间不共享写入", fan_out)
        self.assertIn("不读到彼此输出", fan_out)
        self.assertIn("交叉评判者", self.text)
        self.assertIn("作者与派发顺序", self.text)

    def test_orchestrator_synthesizes_not_mechanical(self):
        pick = self.text.split("## Phase D: Pick", 1)[1].split("## Phase E: Graft", 1)[0]
        graft = self.text.split("## Phase E: Graft", 1)[1].split("## 数学整合后的重查", 1)[0]
        self.assertIn("把独立评判的打分与推荐摆在一起比较", pick)
        self.assertIn("不做整体印象判断", pick)
        self.assertIn("手工改写融入基座", graft)
        self.assertIn("不机械拼接段落", graft)

    def test_independent_invocation_defines_authorization_scope(self):
        self.assertIn("独立调用时，以用户给定的任务及其明确范围为授权", self.text)
        self.assertIn("用户未给候选数时，默认两个", self.text)
        self.assertIn("不覆盖既有材料的独立目录", self.text)

    def test_math_recheck_and_win_is_not_proof(self):
        math_recheck = self.text.split("## 数学整合后的重查", 1)[1].split("## Phase F: Verify", 1)[0]
        self.assertIn("假设是否仍然成立且被声明", math_recheck)
        self.assertIn("记号是否全篇一致无冲突", math_recheck)
        self.assertIn("依赖是否闭合", math_recheck)
        self.assertIn("胜出不等于命题成立", math_recheck)

    def test_subagent_prerequisite_blocks_without_host_support(self):
        self.assertIn("子代理", self.text)
        self.assertIn("blocked", self.text)

    def test_no_brand_pinning_or_personal_paths(self):
        for token in FORBIDDEN_PERSONAL + FORBIDDEN_BRANDS:
            self.assertNotIn(token, self.text, token)

    def test_independent_of_swarm(self):
        self.assertNotIn("swarm", load().arena_required_dependencies(self.text))

    def test_registered_as_migrated_contract(self):
        module = load()
        arena_rel = "skills/organization/arena/SKILL.md"
        self.assertIn(arena_rel, module.MIGRATED_CONTRACT)
        self.assertNotIn(arena_rel, module.LEGACY_LEAF_GATES)
        self.assertIn("organization/arena", BOUNDARY.read_text(encoding="utf-8"))

    def test_entry_discovers_arena_by_installed_skill_name(self):
        entry_text = ENTRY.read_text(encoding="utf-8")
        self.assertIn("打开 `arena` Skill", entry_text)
        self.assertNotIn("organization/arena/SKILL.md", entry_text)

    def test_readme_manifests_match_skill_directory(self):
        actual = {
            path.relative_to(ROOT / "skills").as_posix()
            for path in (ROOT / "skills").rglob("SKILL.md")
        }
        for name in ("README.md", "skills/README.md"):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                listed = re.findall(
                    r"\]\((?:skills/)?([a-z-]+/[a-z0-9-]+/SKILL\.md)\)", text
                )
                self.assertEqual(len(listed), len(set(listed)))
                self.assertEqual(set(listed), actual)
                self.assertIn("organization/arena/SKILL.md", text, name)

    def test_count_free_readme_manifest_is_accepted(self):
        tmp = copy_tree()
        try:
            readme = tmp / "README.md"
            text = readme.read_text(encoding="utf-8")
            text, badge_count = re.subn(
                r"https://img\.shields\.io/badge/skills-(?:\d+|suite)-green\.svg",
                "https://img.shields.io/badge/skills-suite-green.svg",
                text,
            )
            text, toc_count = re.subn(
                r"(?m)^- \[(?:\d+ 个 )?Skill 能力清单\]\(#(?:\d+-个-)?skill-能力清单\)$",
                "- [Skill 能力清单](#skill-能力清单)",
                text,
            )
            text, heading_count = re.subn(
                r"(?m)^## (?:\d+ 个 )?Skill 能力清单$",
                "## Skill 能力清单",
                text,
            )
            text, description_count = re.subn(
                r"(?:全套包含 \d+ 个独立技能。根据触发机制分为两类：|本仓库提供可独立使用的技能，按触发机制分为两类：)",
                "本仓库提供可独立使用的技能，按触发机制分为两类：",
                text,
            )
            self.assertEqual(
                (badge_count, toc_count, heading_count, description_count), (1, 1, 1, 1)
            )
            readme.write_text(text, encoding="utf-8")
            self.assertEqual(fresh_problems(tmp), [])
        finally:
            shutil.rmtree(tmp.parent, onexc=_force_rmtree)


class ArenaCheckerRegressionTests(unittest.TestCase):
    def test_current_tree_has_no_new_breakage(self):
        self.assertEqual(fresh_problems(ROOT), [])

    def test_missing_contract_section_is_red(self):
        tmp = copy_tree()
        try:
            skill = tmp / "skills/organization/arena/SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8").replace("## 委托继承", "## 其他"),
                encoding="utf-8",
            )
            self.assertTrue(fresh_problems(tmp))
        finally:
            shutil.rmtree(tmp.parent, onexc=_force_rmtree)

    def test_dropped_phase_is_red(self):
        tmp = copy_tree()
        try:
            skill = tmp / "skills/organization/arena/SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8").replace("Cross-judge", "裁决"),
                encoding="utf-8",
            )
            problems = "\n".join(fresh_problems(tmp))
            self.assertIn("Cross-judge", problems)
        finally:
            shutil.rmtree(tmp.parent, onexc=_force_rmtree)

    def test_missing_skill_from_readme_manifest_is_red(self):
        tmp = copy_tree()
        try:
            readme = tmp / "README.md"
            text = readme.read_text(encoding="utf-8")
            text, replacement_count = re.subn(
                r"(?m)^\|[^\n]*\[arena\]\(skills/organization/arena/SKILL\.md\)[^\n]*\n",
                "",
                text,
            )
            self.assertEqual(replacement_count, 1)
            readme.write_text(text, encoding="utf-8")
            problems = "\n".join(fresh_problems(tmp))
            self.assertIn("README.md: 清单缺", problems)
            self.assertIn("organization/arena", problems)
        finally:
            shutil.rmtree(tmp.parent, onexc=_force_rmtree)


if __name__ == "__main__":
    unittest.main()
