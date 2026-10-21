"""#58 完成研究发现、检索与绘图的随包闭环。

期望来自 #48 spec（US36、ID9-ID11、ID17）与 #58 票面，不从被测脚本反读。
历史基线：`docs/acceptance/**` 的 9 条 evidence tarball 断链与 7 个既有测试
失败不由本票修复；本票不得新增回归。
"""
import importlib.util
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
SKILLS = ROOT / "skills"
DISCOVERY = SKILLS / "idea-cycle/idea-discovery"
COMPOSITION = DISCOVERY / "references/composition-notes.md"
PLAYBOOK = SKILLS / "general/research-os/playbooks/idea-discovery.md"
BOUNDARY = SKILLS / "general/research-os/references/migration-boundary.md"
HISTORICAL = re.compile(
    r"^  - docs/acceptance/[^:]+:\d+: 链接目标不存在或未追踪: evidence/\S+\.tar\.gz$"
)

MIGRATED_TICKET58 = (
    "skills/idea-cycle/creative-thinking-for-research/SKILL.md",
    "skills/idea-cycle/idea-discovery/SKILL.md",
    "skills/idea-cycle/idea-generation/SKILL.md",
    "skills/idea-cycle/idea-refinement/SKILL.md",
    "skills/idea-cycle/idea-review/SKILL.md",
    "skills/idea-cycle/novelty-check/SKILL.md",
    "skills/writing-cycle/academic-plotting/SKILL.md",
)

PHASE_LEAVES = {
    "文献 Landscape": "research-lit",
    "候选生成与筛选": "idea-generation",
    "查新": "novelty-check",
    "独立评审": "idea-review",
    "固定边界收敛": "idea-refinement",
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
        [sys.executable if False else "uv", "run", "python", str(root / "scripts/check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.startswith("  - ")]


def fresh_problems(root: Path) -> list[str]:
    return [line for line in checker_problems(root) if not HISTORICAL.match(line)]


def stage_skill(root: Path) -> None:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)


class WorkCopy:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "repo"
        shutil.copytree(
            ROOT,
            self.path,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"),
        )
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
    def test_discovery_is_composable_in_one_mandate(self):
        text = (DISCOVERY / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("一次委托", text)
        self.assertIn("组合配方", text)
        self.assertNotIn("stage-checkpoint", text)
        self.assertNotIn("默认停下", text)
        self.assertIn("Phase 1", text)
        self.assertIn("Phase 4.5", text)

    def test_recipe_preserves_independent_leaf_requirements(self):
        text = COMPOSITION.read_text(encoding="utf-8")
        self.assertIn("各叶 SKILL.md", text)
        for phase, leaf in PHASE_LEAVES.items():
            with self.subTest(phase=phase):
                self.assertIn(phase, text)
                self.assertIn(leaf, text)
        self.assertIn("不得跳过", text)
        self.assertIn("目标替换", text)

    def test_entry_playbook_follows_mandate_and_real_leaves(self):
        text = PLAYBOOK.read_text(encoding="utf-8")
        self.assertIn("Gates: none", text)
        self.assertIn("一次委托", text)
        self.assertNotIn("stage-checkpoint", text)
        for leaf in PHASE_LEAVES.values():
            self.assertIn(leaf, text)


class SharedAssets(unittest.TestCase):
    def test_existing_retrieval_and_plotting_assets_are_reused(self):
        module = load()
        names = {Path(rel).parent.name for rel in MIGRATED_TICKET58}
        self.assertEqual(names, {"creative-thinking-for-research", "idea-discovery", "idea-generation", "idea-refinement", "idea-review", "novelty-check", "academic-plotting"})
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


class FlatInstall(unittest.TestCase):
    def test_core_bundle_survives_flat_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (
                "general/research-os",
                "idea-cycle/idea-discovery",
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
            discovery = root / "idea-discovery"
            plotting = root / "academic-plotting"
            research = root / "research-lit"
            self.assertTrue((discovery / "references/composition-notes.md").is_file())
            self.assertTrue((plotting / "references/data-visualization.md").is_file())
            self.assertTrue((research / "references/source-methods.md").is_file())
            self.assertTrue((research / "LICENSE").is_file())
            text = (discovery / "references/composition-notes.md").read_text(encoding="utf-8")
            self.assertNotIn("skills/", text)


if __name__ == "__main__":
    unittest.main()
