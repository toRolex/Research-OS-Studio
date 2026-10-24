"""#58 完成研究发现、检索与绘图的随包闭环。

期望来自 #48 spec（US36、ID9-ID11、ID17）与 #58 票面，不从被测脚本反读。
默认结构 scope 不允许任何失败；历史身份严格 scope 另报未验证。
"""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree
from spec48_checker_result import parse_checker_result

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
SKILLS = ROOT / "skills"
DISCOVERY = SKILLS / "general/research-os"
COMPOSITION = DISCOVERY / "references/discovery-composition.md"
PLAYBOOK = DISCOVERY / "playbooks/discovery.md"
BOUNDARY = SKILLS / "general/research-os/references/migration-boundary.md"

MIGRATED_TICKET58 = (
    "skills/idea-cycle/creative-thinking-for-research/SKILL.md",
    "skills/idea-cycle/idea-generation/SKILL.md",
    "skills/idea-cycle/idea-refinement/SKILL.md",
    "skills/idea-cycle/idea-review/SKILL.md",
    "skills/idea-cycle/novelty-check/SKILL.md",
    "skills/writing-cycle/academic-plotting/SKILL.md",
)

PHASE_LEAVES = {
    "文献范围或来源证据不足": "research-lit",
    "缺少候选或探索视角不足": "idea-generation",
    "候选主张尚未对照 prior work": "novelty-check",
    "需要独立挑战与裁决": "idea-review",
    "方法选择/收敛或 Proposal 未完成": "idea-refinement",
}


def load():
    spec = importlib.util.spec_from_file_location("check_skills_t58", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discovered() -> set[str]:
    return {f"{p.parent.parent.name}/{p.parent.name}" for p in SKILLS.glob("*/*/SKILL.md")}


def checker_problems(root: Path) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return parse_checker_result(result)


def fresh_problems(root: Path) -> list[str]:
    return checker_problems(root)


def stage_skill(root: Path) -> None:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)


class WorkCopy:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "repo"
        copy_tracked_tree(ROOT, self.path)
        for command in (
            ["git", "init"],
            ["git", "add", "-A"],
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base"],
        ):
            subprocess.run(command, cwd=self.path, check=True, capture_output=True)

    def __enter__(self) -> "WorkCopy":
        return self

    def __exit__(self, *_exc) -> None:
        self._tmp.cleanup()


class MigratedSet(unittest.TestCase):
    def test_ticket58_leaves_follow_mandate_without_stage_gates(self):
        for rel in MIGRATED_TICKET58:
            with self.subTest(skill=rel):
                text = (ROOT / rel).read_text(encoding="utf-8")
                self.assertRegex(text, r"(?m)^Gates: none$")
                self.assertIn("## 委托继承", text)
                self.assertNotRegex(text, r"(?m)^Gate:")
                self.assertIn("目标替换", text)
                self.assertIn("越权", text)
                self.assertIn("超额", text)

    def test_registration_and_boundary_move_ticket58_leaves(self):
        module = load()
        for rel in MIGRATED_TICKET58:
            self.assertIn(rel, module.MIGRATED_CONTRACT, rel)
            self.assertNotIn(rel, module.LEGACY_LEAF_GATES, rel)
            self.assertIn(Path(rel).parent.name, BOUNDARY.read_text(encoding="utf-8"))


class DiscoveryRecipe(unittest.TestCase):
    def test_discovery_composes_from_current_gaps_and_existing_results(self):
        text = PLAYBOOK.read_text(encoding="utf-8")
        self.assertIn("组合参考", COMPOSITION.read_text(encoding="utf-8"))
        self.assertIn("目标缺口", text)
        self.assertIn("子集", text)
        self.assertIn("重排", text)
        self.assertIn("回访", text)
        self.assertIn("已有成果", text)
        self.assertNotIn("一次委托按下方 Phase", text)

    def test_recipe_preserves_independent_leaf_responsibilities(self):
        text = COMPOSITION.read_text(encoding="utf-8")
        self.assertIn("Required skills", text)
        self.assertEqual(load().discovery_order_problems(text), [])
        for label, leaf in PHASE_LEAVES.items():
            with self.subTest(responsibility=label):
                self.assertIn(label, text)
                self.assertIn(leaf, text)

    def test_entry_playbook_follows_current_goal_and_real_leaves(self):
        text = PLAYBOOK.read_text(encoding="utf-8")
        self.assertIn("缺口", text)
        self.assertIn("重排", text)
        self.assertIn("回访", text)
        for leaf in PHASE_LEAVES.values():
            self.assertIn(leaf, text)


class SharedAssets(unittest.TestCase):
    def test_existing_retrieval_and_plotting_assets_are_reused(self):
        module = load()
        names = {Path(rel).parent.name for rel in MIGRATED_TICKET58}
        self.assertEqual(names, {"creative-thinking-for-research", "idea-generation", "idea-refinement", "idea-review", "novelty-check", "academic-plotting"})
        self.assertIn("skills/idea-cycle/research-lit/SKILL.md", module.MIGRATED_CONTRACT)
        self.assertIn("skills/writing-cycle/academic-plotting/SKILL.md", module.MIGRATED_CONTRACT)

    def test_bundled_sources_licenses_and_resources_resolve(self):
        required = {
            "research-lit": [
                "LICENSE",
                "references/source-methods.md",
                "references/source-verification.md",
                "templates/literature-report.md",
            ],
            "novelty-check": [
                "LICENSE",
                "references/source-verification.md",
            ],
            "creative-thinking-for-research": [
                "LICENSE-Orchestra.txt",
                "references/creative-frameworks.md",
            ],
            "research-os": [
                "references/discovery-composition.md",
                "templates/research-brief.md",
                "templates/discovery-report.md",
                "licenses/idea-cycle/LICENSE",
            ],
            "academic-plotting": [
                "LICENSE-ARIS.txt",
                "LICENSE-Orchestra.txt",
                "references/data-visualization.md",
                "references/diagram-generation.md",
                "references/diagram-styles.md",
                "references/style-guide.md",
                "references/table-and-review.md",
                "templates/figure-note.md",
            ],
        }
        roots = {
            "research-lit": SKILLS / "idea-cycle/research-lit",
            "novelty-check": SKILLS / "idea-cycle/novelty-check",
            "creative-thinking-for-research": SKILLS / "idea-cycle/creative-thinking-for-research",
            "research-os": SKILLS / "general/research-os",
            "academic-plotting": SKILLS / "writing-cycle/academic-plotting",
        }
        for name, rels in required.items():
            for rel in rels:
                with self.subTest(asset=f"{name}/{rel}"):
                    self.assertTrue((roots[name] / rel).is_file())
        for name in ("research-lit", "novelty-check"):
            license_text = (roots[name] / "LICENSE").read_text(encoding="utf-8")
            self.assertIn("MIT License", license_text)
            self.assertIn("Copyright (c) 2026 wanshuiyin", license_text)
        discovery_license = (roots["research-os"] / "licenses/idea-cycle/LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", discovery_license)
        self.assertIn("Copyright (c) 2026 wanshuiyin", discovery_license)

    def test_external_services_and_writes_stay_authorized(self):
        research = (SKILLS / "idea-cycle/research-lit/SKILL.md").read_text(encoding="utf-8")
        novelty = (SKILLS / "idea-cycle/novelty-check/SKILL.md").read_text(encoding="utf-8")
        plotting = (SKILLS / "writing-cycle/academic-plotting/SKILL.md").read_text(encoding="utf-8")
        for text in (research, novelty):
            self.assertRegex(text, r"(?i)(?:pay|paid|paying)(?: for)? services")
            self.assertIn("new credentials", text)
            self.assertIn("remote writes", text)
        for marker in ("远程上传", "付费", "授权"):
            self.assertIn(marker, plotting)
        self.assertIn("授权来源", plotting)
        self.assertIn("已有环境", plotting)


class Ticket58ReviewRegressions(unittest.TestCase):
    def test_discovery_recipe_is_gap_driven_not_a_locked_route(self):
        text = PLAYBOOK.read_text(encoding="utf-8")
        for marker in ("目标缺口", "子集", "重排", "回访"):
            with self.subTest(marker=marker):
                self.assertIn(marker, text + COMPOSITION.read_text(encoding="utf-8"))
        self.assertEqual(load().discovery_order_problems(text), [])
        composition = COMPOSITION.read_text(encoding="utf-8")
        self.assertEqual(load().discovery_order_problems(composition), [])
        playbook = PLAYBOOK.read_text(encoding="utf-8")
        self.assertNotIn("匹配后跨 turn 保持本路线", playbook)

    def test_discovery_playbook_resolves_required_reads_from_installed_skill_roots(self):
        playbook = PLAYBOOK.read_text(encoding="utf-8")
        self.assertNotIn("skills/idea-cycle/", playbook)
        self.assertIn("按安装后的 Skill 名称定位其目录", playbook)
        roots = {
            "research-lit": SKILLS / "idea-cycle/research-lit",
            "idea-generation": SKILLS / "idea-cycle/idea-generation",
            "creative-thinking-for-research": SKILLS / "idea-cycle/creative-thinking-for-research",
            "novelty-check": SKILLS / "idea-cycle/novelty-check",
            "idea-review": SKILLS / "idea-cycle/idea-review",
            "idea-refinement": SKILLS / "idea-cycle/idea-refinement",
        }
        resources = {
            "research-lit": ("SKILL.md", "references/source-methods.md", "references/source-verification.md", "references/file-capability-audit.md"),
            "idea-generation": ("SKILL.md", "references/generation-methods.md", "references/ideation-frameworks.md"),
            "creative-thinking-for-research": ("SKILL.md", "references/creative-frameworks.md"),
            "novelty-check": ("SKILL.md", "references/source-verification.md"),
            "idea-review": ("SKILL.md", "references/review-task.md"),
            "idea-refinement": ("SKILL.md", "references/method-development.md", "references/method-review.md", "templates/proposal.md"),
        }
        for skill, required in resources.items():
            with self.subTest(skill=skill):
                self.assertIn(f"`{skill}`", playbook)
                for resource in required:
                    self.assertIn(resource, playbook)
                    candidate = roots[skill] / ("SKILL.md" if resource == "SKILL.md" else resource)
                    self.assertTrue(candidate.is_file(), f"{skill}/{resource}")

    def test_composed_plotting_and_discovery_paths_inherit_authorization(self):
        plotting = (SKILLS / "writing-cycle/academic-plotting/SKILL.md").read_text(encoding="utf-8")
        discovery = PLAYBOOK.read_text(encoding="utf-8")
        self.assertIn("已授权材料位置自行确定有依据的图表", plotting)
        self.assertIn("只在授权目录写入不冲突的新产物", discovery)
        self.assertNotIn("提出候选图表并确认选择", plotting)
        self.assertNotIn("路径由用户确认", discovery)

    def test_dependency_contract_and_group_install_are_user_reachable(self):
        text = COMPOSITION.read_text(encoding="utf-8")
        readme = (SKILLS / "README.md").read_text(encoding="utf-8")
        dependencies = ("research-lit", "idea-generation", "novelty-check", "idea-review", "idea-refinement")
        for name in dependencies:
            with self.subTest(dependency=name):
                self.assertIn("## Required skills", text)
                self.assertIn(name, text)
                self.assertIn(name, readme)
                self.assertIn(name, COMPOSITION.read_text(encoding="utf-8"))
        self.assertIn("DEPENDENCY MISSING / BLOCKED", text)
        install = next(line for line in readme.splitlines() if "--skill research-os" in line)
        self.assertIn("多选只安装列出的 Skills", readme)
        for name in dependencies:
            self.assertIn(name, install)

    def test_file_capability_audit_covers_scope_and_host_prerequisites(self):
        audit = (SKILLS / "idea-cycle/research-lit/references/file-capability-audit.md").read_text(encoding="utf-8")
        for marker in ("plain text", "PDF", "OCR", "connector", "plotting", "export", "host prerequisite", "not bundled"):
            with self.subTest(marker=marker):
                self.assertIn(marker, audit)
        self.assertIn("No additional external asset is selected in this ticket", audit)
        self.assertIn("a target host and concrete gap", audit)
        self.assertIn("license, resource reachability and dependencies", audit)

class CheckerCounterexamples(unittest.TestCase):
    def test_current_tree_has_no_new_breakage(self):
        self.assertEqual(fresh_problems(ROOT), [])

    def test_dropped_discovery_recipe_is_red(self):
        with WorkCopy() as work:
            path = work.path / COMPOSITION.relative_to(ROOT)
            path.unlink()
            stage_skill(work.path)
            problems = fresh_problems(work.path)
            self.assertTrue(any("组合说明" in item for item in problems), problems)

    def test_dropped_shared_asset_is_red(self):
        with WorkCopy() as work:
            path = work.path / "skills/idea-cycle/research-lit/references/source-methods.md"
            path.unlink()
            stage_skill(work.path)
            problems = fresh_problems(work.path)
            self.assertTrue(any("source-methods.md" in item for item in problems), problems)

    def test_locked_discovery_route_is_red(self):
        with WorkCopy() as work:
            path = work.path / "skills/general/research-os/playbooks/discovery.md"
            text = path.read_text(encoding="utf-8").replace(
                "按缺口组合五项 Required 能力",
                "必须固定顺序执行全部五项职责",
            )
            path.write_text(text, encoding="utf-8")
            stage_skill(work.path)
            problems = fresh_problems(work.path)
            self.assertTrue(any("组合行为" in item or "固定顺序" in item for item in problems), problems)

    def test_unapproved_plot_choice_is_red(self):
        with WorkCopy() as work:
            path = work.path / "skills/writing-cycle/academic-plotting/SKILL.md"
            text = path.read_text(encoding="utf-8").replace(
                "composed 遵循父委托内的图数与范围，在已授权材料位置自行确定有依据的图表并记录选择理由；",
                "没有计划时提出候选图表并确认选择。composed 遵循父委托内的图数与范围，在已授权材料位置自行确定有依据的图表并记录选择理由；",
            )
            path.write_text(text, encoding="utf-8")
            stage_skill(work.path)
            problems = fresh_problems(work.path)
            self.assertTrue(any("无条件要求确认普通选图" in item for item in problems), problems)

    def test_incomplete_discovery_install_command_is_red(self):
        with WorkCopy() as work:
            path = work.path / COMPOSITION.relative_to(ROOT)
            text = path.read_text(encoding="utf-8").replace(
                "--skill research-os research-lit idea-generation novelty-check idea-review idea-refinement",
                "--skill research-os research-lit idea-generation novelty-check idea-review",
            )
            path.write_text(text, encoding="utf-8")
            stage_skill(work.path)
            problems = fresh_problems(work.path)
            self.assertTrue(any("成组安装命令缺 Required skills" in item for item in problems), problems)

    def test_missing_file_capability_audit_is_red(self):
        with WorkCopy() as work:
            path = work.path / "skills/idea-cycle/research-lit/references/file-capability-audit.md"
            path.unlink()
            stage_skill(work.path)
            problems = fresh_problems(work.path)
            self.assertTrue(any("缺文件能力缺口审计" in item or "file-capability-audit.md" in item for item in problems), problems)

    def test_missing_scanned_pdf_audit_row_is_red(self):
        with WorkCopy() as work:
            path = work.path / "skills/idea-cycle/research-lit/references/file-capability-audit.md"
            lines = path.read_text(encoding="utf-8").splitlines()
            removed = [line for line in lines if line.startswith("| Read scanned PDFs / image-only documents |")]
            self.assertEqual(len(removed), 1)
            path.write_text("\n".join(line for line in lines if line not in removed) + "\n", encoding="utf-8")
            stage_skill(work.path)
            problems = fresh_problems(work.path)
            self.assertTrue(any("缺文件能力审计条目" in item and "scanned PDFs" in item for item in problems), problems)

    def test_discovery_playbook_source_tree_path_is_red(self):
        with WorkCopy() as work:
            path = work.path / "skills/general/research-os/playbooks/discovery.md"
            text = path.read_text(encoding="utf-8").replace(
                "## 执行与交付",
                "读取 `skills/idea-cycle/research-lit/SKILL.md`。\n\n## 执行与交付",
            )
            path.write_text(text, encoding="utf-8")
            stage_skill(work.path)
            problems = fresh_problems(work.path)
            self.assertTrue(any("仓库源码路径" in item for item in problems), problems)


class FlatInstall(unittest.TestCase):
    def test_core_bundle_survives_flat_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (
                "general/research-os",
                "idea-cycle/research-lit",
                "idea-cycle/idea-generation",
                "idea-cycle/novelty-check",
                "idea-cycle/idea-review",
                "idea-cycle/idea-refinement",
                "idea-cycle/creative-thinking-for-research",
                "writing-cycle/academic-plotting",
            ):
                parts = Path(rel).parts
                shutil.copytree(SKILLS / rel, root / parts[-1])
            discovery = root / "research-os"
            plotting = root / "academic-plotting"
            research = root / "research-lit"
            self.assertTrue((discovery / "references/discovery-composition.md").is_file())
            self.assertTrue((discovery / "templates/research-brief.md").is_file())
            self.assertTrue((discovery / "templates/discovery-report.md").is_file())
            self.assertTrue((discovery / "licenses/idea-cycle/LICENSE").is_file())
            self.assertTrue((plotting / "references/data-visualization.md").is_file())
            self.assertTrue((research / "references/source-methods.md").is_file())
            self.assertTrue((research / "LICENSE").is_file())
            text = (discovery / "references/discovery-composition.md").read_text(encoding="utf-8")
            self.assertNotIn("skills/", text)


if __name__ == "__main__":
    unittest.main()
