"""#57 统一写作组织与专项写作能力合同。

本票只验收安装后的结构和委托语义；不宣称真实写作质量、LaTeX 构建效果
或宿主交互行为已经通过。
"""
import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path

from spec48_checker_result import parse_checker_result

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
SKILLS = ROOT / "skills" / "writing-cycle"
BOUNDARY = ROOT / "skills" / "general/research-os/references/migration-boundary.md"
UNIFIED = SKILLS / "paper-writing"
READONLY_AUDITS = ("citation-audit", "paper-claim-audit", "claim-stress-test")
MIGRATED_WRITING = (
    "apply-citation-fixes",
    "citation-audit",
    "claim-stress-test",
    "paper-claim-audit",
    "paper-compile-repair",
    "paper-compile",
    "paper-drafting",
    "paper-plan",
    "paper-talk",
    "paper-writing",
    "rebuttal",
    "resubmit-pipeline",
)


def load():
    spec = importlib.util.spec_from_file_location("check_skills_t57", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checker_problem_lines(root: Path = ROOT) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return parse_checker_result(result)


def fresh_problem_lines(root: Path = ROOT) -> list[str]:
    return checker_problem_lines(root)


class MigrationContract(unittest.TestCase):
    def test_owned_writing_skills_are_migrated_and_others_keep_their_slice(self):
        module = load()
        migrated = set(module.MIGRATED_CONTRACT)
        for name in MIGRATED_WRITING:
            rel = f"skills/writing-cycle/{name}/SKILL.md"
            self.assertIn(rel, migrated, name)
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?m)^Gate: ", name)
            self.assertIn("委托继承", text, name)
        plotting = "skills/writing-cycle/academic-plotting/SKILL.md"
        self.assertIn(plotting, migrated)
        self.assertNotIn(plotting, module.LEGACY_LEAF_GATES)
        improvement = "skills/writing-cycle/research-improvement/SKILL.md"
        self.assertIn(improvement, migrated)
        self.assertNotIn(improvement, module.LEGACY_LEAF_GATES)
        boundary = BOUNDARY.read_text(encoding="utf-8")
        for name in MIGRATED_WRITING:
            self.assertIn(name, boundary, name)

    def test_checker_adds_no_new_problem_beyond_recorded_historical_breaks(self):
        self.assertEqual(fresh_problem_lines(), [])


class UnifiedWritingOrganization(unittest.TestCase):
    def test_ac1_unified_entry_selects_domain_standards_on_demand(self):
        text = (UNIFIED / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("ML", text)
        self.assertIn("Systems", text)
        self.assertIn("references/standards.md", text)
        standards = (UNIFIED / "references/standards.md").read_text(encoding="utf-8")
        self.assertIn("ml-ai-standards.md", standards)
        self.assertIn("systems-standards.md", standards)
        for stale in ("不经通用入口", "请用户点名 `paper-compile-repair`"):
            self.assertNotIn(stale, text)

    def test_ac2_all_writing_purposes_remain_independent_capabilities(self):
        for name in (
            "paper-plan",
            "paper-drafting",
            "academic-plotting",
            "paper-compile",
            "paper-compile-repair",
            "citation-audit",
            "apply-citation-fixes",
            "paper-claim-audit",
            "claim-stress-test",
            "rebuttal",
            "paper-talk",
            "resubmit-pipeline",
        ):
            self.assertTrue((SKILLS / name / "SKILL.md").is_file(), name)
        for name in ("paper-plan", "paper-drafting", "academic-plotting", "paper-compile", "rebuttal", "paper-talk", "resubmit-pipeline"):
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: " + name, text.split("---", 2)[1], name)

    def test_unified_map_allows_delegated_repair_without_independent_naming(self):
        text = (UNIFIED / "references/composition-map.md").read_text(encoding="utf-8")
        for phrase in ("委托内继承", "paper-compile-repair", "apply-citation-fixes"):
            self.assertIn(phrase, text, phrase)
        self.assertNotIn("各自需要用户另行点名", text)

    def test_ac3_delegated_repairs_inherit_but_audits_remain_readonly(self):
        for name in ("paper-compile-repair", "apply-citation-fixes"):
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("委托继承", text, name)
            self.assertIn("不要求再次独立点名", text, name)
        for name in READONLY_AUDITS:
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("只读", text, name)
            self.assertIn("不修改", text, name)

    def test_research_os_playbooks_route_into_unified_writing_without_old_gates(self):
        playbooks = ROOT / "skills/general/research-os/playbooks"
        for name in ("paper-writing-general", "paper-writing-ml", "paper-writing-systems"):
            text = (playbooks / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn("skills/writing-cycle/paper-writing/SKILL.md", text, name)
            self.assertIn("skills/writing-cycle/paper-writing/references/composition-map.md", text, name)
            self.assertNotIn("停在该文件的授权门", text, name)
            self.assertNotIn("paper-compile-repair` 与 `apply-citation-fixes` 由用户另行点名", text, name)
        for name, stale in (
            ("rebuttal", "停在 strategy-confirm"),
            ("resubmit", "停在 adaptation-scope"),
            ("paper-talk", "停在 outline-confirm"),
        ):
            text = (playbooks / f"{name}.md").read_text(encoding="utf-8")
            self.assertNotIn(stale, text, name)


class WritingBoundaries(unittest.TestCase):
    def test_readonly_audits_stay_readonly(self):
        for name in READONLY_AUDITS:
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("只读", text, name)
            self.assertIn("不修改", text, name)
            self.assertNotRegex(text, r"(?m)^Gate: ", name)

    def test_ac4_evidence_gaps_can_be_repaired_inside_authorization_without_fabrication(self):
        for name in ("paper-writing",):
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("证据缺口", text, name)
            self.assertIn("不捏造", text, name)
            self.assertIn("授权内", text, name)
        self.assertNotIn("写作永远不能补查", (UNIFIED / "SKILL.md").read_text(encoding="utf-8"))

    def test_authorized_checks_precede_pausing_unresolved_conflicts(self):
        expected = "先在当前委托允许范围内补查或补分析；仅在仍无法解决或需改变目标/结论范围时暂停受影响部分。"
        for name in ("paper-writing", "paper-drafting", "paper-talk"):
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(expected, text, name)

    def test_resubmit_description_reserves_user_decisions_for_goal_or_scope_changes(self):
        text = (SKILLS / "resubmit-pipeline" / "SKILL.md").read_text(encoding="utf-8")
        description = text.split("---", 2)[1]
        self.assertNotIn("冲突取舍与是否投稿由用户决定", description)
        self.assertIn("不自动投稿", description)
        self.assertIn("只暂停影响既定目标或授权的冲突", description)

    def test_ac5_writing_stops_before_external_submission_or_scope_expansion(self):
        for name in ("paper-writing", "rebuttal", "resubmit-pipeline", "paper-talk"):
            text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("不自动投稿", text, name)
        unified = (UNIFIED / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("不启动跨研究改进循环", unified)
        self.assertIn("#58", unified)

    def test_unified_skill_resource_links_resolve_at_source(self):
        link = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
        for source in (
            UNIFIED / "SKILL.md",
            UNIFIED / "references/composition-map.md",
            UNIFIED / "references/standards.md",
            UNIFIED / "references/sources.md",
            UNIFIED / "references/ml-experiment-reporting.md",
            UNIFIED / "references/ml-reviewer-expectations.md",
            UNIFIED / "references/ml-venue-checklists.md",
            UNIFIED / "references/systems-writing-methods.md",
            UNIFIED / "references/systems-evaluation-methods.md",
            UNIFIED / "references/systems-checklist.md",
            UNIFIED / "references/systems-venue-and-reviewer.md",
            UNIFIED / "templates/ml-writing-report.md",
            UNIFIED / "templates/systems-paper-writing-report.md",
        ):
            for line_no, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
                for target in link.findall(line):
                    if target.startswith(("http:", "https:", "#", "mailto:")):
                        continue
                    resolved = (source.parent / target.split("#", 1)[0]).resolve()
                    self.assertTrue(resolved.is_file(), f"{source}:{line_no}: {target}")
