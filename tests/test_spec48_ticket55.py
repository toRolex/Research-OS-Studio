"""#55 Slice A: installed math-research recipe composition and contract boundaries.

These checks cover discoverable Skill structure and declared contracts only; they
do not evaluate whether a proof, computation, or formalization is mathematically
correct.
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "skills/general/research-os/SKILL.md"
PLAYBOOK = ROOT / "skills/general/research-os/playbooks/proof.md"
CHECKER = ROOT / "scripts/check-skills.py"
MIGRATED_WRITE_SKILLS = {
    "skills/validation-cycle/proof-writer/SKILL.md",
    "skills/validation-cycle/proof-repair/SKILL.md",
    "skills/validation-cycle/formula-derivation/SKILL.md",
}
INSTALL_CHECK_SKILLS = (
    "skills/validation-cycle/proof-writer",
    "skills/validation-cycle/proof-repair",
    "skills/validation-cycle/formula-derivation",
    "skills/validation-cycle/proof-review",
)
PROOF_REVIEW_MIGRATED_REFERENCES = (
    "references/audit-output-contract.md",
    "references/dispatch-prompts.md",
    "references/independent-review.md",
    "references/lean-methods.md",
    "references/notation-audit.md",
    "references/prompts/continuation.md",
    "references/prompts/explicit-send.md",
    "references/prompts/focused-redo.md",
    "references/prompts/format-repair.md",
    "references/prompts/independent-opinion.md",
    "references/prompts/local-proof.md",
    "references/prompts/manual-handoff.md",
    "references/prompts/return-audit.md",
    "references/proof-audit-rubric.md",
    "references/stress-tests.md",
)

CAPABILITIES = {
    "arena": "skills/organization/arena/SKILL.md",
    "swarm": "skills/general/swarm/SKILL.md",
    "interrogate": "skills/general/interrogate/SKILL.md",
    "formula-derivation": "skills/validation-cycle/formula-derivation/SKILL.md",
    "proof-writer": "skills/validation-cycle/proof-writer/SKILL.md",
    "proof-review": "skills/validation-cycle/proof-review/SKILL.md",
    "proof-repair": "skills/validation-cycle/proof-repair/SKILL.md",
    "create-verification-skill": "skills/validation-cycle/create-verification-skill/SKILL.md",
    "maintain-verification-skill": "skills/validation-cycle/maintain-verification-skill/SKILL.md",
    "create-formal-verification-skill": (
        "skills/validation-cycle/create-formal-verification-skill/SKILL.md"
    ),
    "maintain-formal-verification-skill": (
        "skills/validation-cycle/maintain-formal-verification-skill/SKILL.md"
    ),
    "research-improvement": "skills/writing-cycle/research-improvement/SKILL.md",
}


def load_checker():
    spec = importlib.util.spec_from_file_location("check_skills_ticket55", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contains_any(text: str, alternatives: tuple[str, ...]) -> bool:
    return any(alternative in text for alternative in alternatives)


def install_tracked_skill(skill_dir: str, destination: Path) -> Path:
    """Build a small flat-install snapshot from tracked files only."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", skill_dir],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    tracked = [Path(path.decode()) for path in result.stdout.split(b"\0") if path]
    installed = destination / Path(skill_dir).name
    prefix = Path(skill_dir).parts
    for relative in tracked:
        source = ROOT / relative
        target = installed / Path(*relative.parts[len(prefix) :])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    return installed


def local_markdown_links(path: Path) -> list[Path]:
    links = []
    for raw in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        target = raw.strip().split(maxsplit=1)[0].strip("<>").split("#", 1)[0]
        if not target or target.startswith(("#", "/")) or re.match(r"^[a-z][a-z0-9+.-]*:", target):
            continue
        links.append(Path(os.path.abspath(path.parent / target)))
    return links


def reachable_markdown_files(skill_root: Path) -> set[Path]:
    pending = [skill_root / "SKILL.md"]
    visited: set[Path] = set()
    while pending:
        current = pending.pop()
        if current in visited or not current.is_file():
            continue
        visited.add(current)
        pending.extend(local_markdown_links(current))
    return visited


class MathRecipeComposition(unittest.TestCase):
    def setUp(self):
        self.entry = ENTRY.read_text(encoding="utf-8")
        self.recipe = PLAYBOOK.read_text(encoding="utf-8")

    def test_existing_math_work_routes_to_the_composable_proof_recipe(self):
        checker = load_checker()
        rows, errors = checker.parse_route_table(self.entry)
        self.assertEqual([], errors)
        proof = next(row for row in rows if row["路线"] == "proof")
        self.assertEqual("no", proof["只读约束"])
        self.assertIn("playbooks/proof.md", proof["playbook"])
        self.assertTrue(
            contains_any(
                proof["适用条件"],
                ("已有数学成果", "已有证明或推导", "推广障碍"),
            ),
            "proof route should accept existing mathematical work, not only a fixed obligation",
        )
        self.assertTrue(PLAYBOOK.is_file())

    def test_recipe_names_real_composable_skills_and_preserves_their_interfaces(self):
        for slug, relative_path in CAPABILITIES.items():
            skill_path = ROOT / relative_path
            with self.subTest(skill=slug):
                self.assertTrue(skill_path.is_file(), f"missing installable Skill: {relative_path}")
                self.assertIn(f"`{slug}`", self.recipe)
                frontmatter = skill_path.read_text(encoding="utf-8").split("---", 2)[1]
                self.assertRegex(frontmatter, rf"(?m)^name:\s*{re.escape(slug)}\s*$")

    def test_method_choice_is_evidence_led_and_can_alternate(self):
        self.assertTrue(
            contains_any(self.recipe, ("按证据", "证据变化", "当前缺口")),
            "the next activity should follow the target and current evidence",
        )
        self.assertTrue(
            contains_any(self.recipe, ("交替", "来回切换", "返回另一条路线")),
            "the recipe should allow method changes rather than require a single phase order",
        )
        self.assertTrue(
            contains_any(self.recipe, ("不要求每次全部调用", "按需", "不是必经")),
            "method branches should be composed as needed, not treated as a checklist",
        )
        for method_family in (
            ("推导", "公式推导"),
            ("构造", "显式构造"),
            ("计算", "计算核验"),
            ("独立审查", "独立挑战"),
            ("修复", "finding"),
            ("形式化", "定理编码"),
        ):
            with self.subTest(method_family=method_family):
                self.assertTrue(contains_any(self.recipe, method_family))

    def test_unproved_equivalent_obligations_and_failed_routes_remain_open(self):
        self.assertTrue(
            contains_any(
                self.recipe,
                ("等强未证引理", "同等强度的未证引理", "等强引理"),
            ),
            "an equally strong unproved lemma must not be counted as progress",
        )
        self.assertTrue(
            contains_any(self.recipe, ("失败原因", "为什么失败", "失败路线"))
            and contains_any(self.recipe, ("新证据", "新工具", "新机制"))
            and "重开" in self.recipe,
            "record both why a route failed and what new information would justify reopening it",
        )

    def test_counterexample_numeric_and_goal_replacement_boundaries_are_distinct(self):
        self.assertTrue(contains_any(self.recipe, ("严格反例", "经严格核验的反例")))
        self.assertTrue(contains_any(self.recipe, ("原问题", "原命题")))
        self.assertTrue(contains_any(self.recipe, ("数值异常", "数值候选", "数值结果")))
        self.assertTrue(contains_any(self.recipe, ("候选", "尚待严格核验")))
        self.assertTrue(contains_any(self.recipe, ("主要目标替换", "替换主要目标")))
        self.assertTrue(
            contains_any(
                self.recipe,
                (
                    "其他原目标分支继续",
                    "其他原目标工作继续",
                    "不阻塞其他原目标",
                ),
            )
        )

    def test_one_mandate_controls_quota_resumption_and_improvement(self):
        for reference in (
            "../references/mandate.md",
            "continuation.md",
            "pickup.md",
            "improvement.md",
        ):
            with self.subTest(reference=reference):
                self.assertIn(reference, self.recipe)
        for reference in (
            ROOT / "skills/general/research-os/references/mandate.md",
            ROOT / "skills/general/research-os/playbooks/continuation.md",
            ROOT / "skills/general/research-os/playbooks/pickup.md",
            ROOT / "skills/general/research-os/playbooks/improvement.md",
        ):
            self.assertTrue(reference.is_file(), str(reference))

    def test_writer_repair_and_derivation_inherit_the_mandate_without_leaf_gates(self):
        checker = load_checker()
        for relative_path in sorted(MIGRATED_WRITE_SKILLS):
            with self.subTest(skill=relative_path):
                self.assertEqual("委托继承", checker.MIGRATED_CONTRACT.get(relative_path))
                self.assertNotIn(relative_path, checker.LEGACY_LEAF_GATES)
                leaf = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertRegex(leaf, r"(?m)^## 委托继承$")
                self.assertRegex(leaf, r"(?m)^Gates: none$")
                self.assertNotRegex(leaf, r"(?m)^Gate:")
                self.assertIn("disable-model-invocation: true", leaf)
                self.assertTrue(contains_any(leaf, ("独立调用", "standalone")))

    def test_delegated_writes_cover_new_files_and_retries_without_reapproval(self):
        for relative_path in sorted(MIGRATED_WRITE_SKILLS):
            leaf = (ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(skill=relative_path):
                self.assertTrue(contains_any(leaf, ("写域", "写入范围")))
                self.assertTrue(contains_any(leaf, ("新文件", "新建文件", "新研究文件")))
                self.assertTrue(contains_any(leaf, ("重试", "下一轮", "后续阶段")))
                self.assertTrue(contains_any(leaf, ("继承", "无需再次", "不重置")))

    def test_original_claim_and_assumptions_still_require_user_confirmation_to_change(self):
        writer = (ROOT / "skills/validation-cycle/proof-writer/SKILL.md").read_text(
            encoding="utf-8"
        )
        repair = (ROOT / "skills/validation-cycle/proof-repair/SKILL.md").read_text(
            encoding="utf-8"
        )
        derivation = (
            ROOT / "skills/validation-cycle/formula-derivation/SKILL.md"
        ).read_text(encoding="utf-8")
        for skill, leaf in (("writer", writer), ("repair", repair), ("derivation", derivation)):
            with self.subTest(skill=skill):
                self.assertIn("原命题", leaf)
                self.assertIn("假设", leaf)
                self.assertTrue(contains_any(leaf, ("用户确认", "用户决定")))

    def test_repair_remains_finding_scoped_and_compile_side_effects_stay_bounded(self):
        repair = (ROOT / "skills/validation-cycle/proof-repair/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("finding", repair.lower())
        self.assertTrue(contains_any(repair, ("编译副产物", "编译输出", "编译范围")))
        self.assertTrue(contains_any(repair, ("命令", "副产物")))
        self.assertTrue(contains_any(repair, ("授权范围", "委托范围", "写入范围")))

    def test_proof_review_stays_fresh_read_only_and_separate_from_repair(self):
        review = (ROOT / "skills/validation-cycle/proof-review/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertRegex(review, r"(?m)^Gates: none$")
        self.assertTrue(contains_any(review, ("fresh review", "fresh", "freshly")))
        self.assertTrue(contains_any(review, ("只读", "零写入")))
        self.assertTrue(contains_any(review, ("不自动启动修复", "不调用它", "不开始下一轮")))
        self.assertIn("证明义务", review)
        self.assertTrue(contains_any(review, ("反例尝试", "反例核实")))

    def test_proof_review_owns_specialized_audit_and_handoff_references(self):
        checker = load_checker()
        self.assertNotIn("skills/validation-cycle/proof-orchestrator/SKILL.md", checker.MIGRATED_CONTRACT)
        review = (ROOT / CAPABILITIES["proof-review"]).read_text(encoding="utf-8")
        self.assertIn("按需数学方法与交接参考", review)
        for reference in PROOF_REVIEW_MIGRATED_REFERENCES:
            with self.subTest(reference=reference):
                self.assertTrue((ROOT / "skills/validation-cycle/proof-review" / reference).is_file())
        self.assertFalse((ROOT / "skills/validation-cycle/proof-orchestrator/SKILL.md").exists())

    def test_missing_capabilities_block_only_their_branch(self):
        self.assertIn("缺少某能力只阻塞依赖它的分支", self.recipe)
        self.assertIn("缺少 `proof-review` 只阻塞独立证明审查", self.recipe)

    def test_validation_map_attributes_methods_to_proof_review(self):
        validation = (
            ROOT / "skills/general/research-os/references/validation.md"
        ).read_text(encoding="utf-8")
        self.assertIn("`proof-review`", validation)
        self.assertIn("按 proof-review 索引读取随包方法", validation)
        self.assertNotIn("references/lean-methods.md", validation)
        self.assertNotIn("proof-orchestrator", validation)

    def test_revised_skills_keep_their_local_resources_reachable_when_flat_installed(self):
        with tempfile.TemporaryDirectory(prefix="ticket55-install-") as temporary:
            install_root = Path(temporary)
            installed = {
                skill_dir: install_tracked_skill(
                    skill_dir, install_root / Path(skill_dir).name
                )
                for skill_dir in INSTALL_CHECK_SKILLS
            }
            for skill_dir, skill_root in installed.items():
                with self.subTest(skill=skill_dir):
                    reachable = reachable_markdown_files(skill_root)
                    self.assertIn(Path(os.path.abspath(skill_root / "SKILL.md")), reachable)
                    for document in reachable:
                        for target in local_markdown_links(document):
                            self.assertTrue(
                                target.is_file(),
                                f"{skill_dir}: local install link escapes its bundle: {target}",
                            )

            review_root = installed["skills/validation-cycle/proof-review"]
            reachable = reachable_markdown_files(review_root)
            for relative in PROOF_REVIEW_MIGRATED_REFERENCES:
                with self.subTest(reference=relative):
                    self.assertIn(Path(os.path.abspath(review_root / relative)), reachable)

    def test_research_os_flat_install_has_no_cross_skill_file_link(self):
        with tempfile.TemporaryDirectory(prefix="ticket55-entry-install-") as temporary:
            installed = install_tracked_skill(
                "skills/general/research-os", Path(temporary) / "flat"
            )
            for document in reachable_markdown_files(installed):
                for target in local_markdown_links(document):
                    self.assertTrue(
                        target.is_file(),
                        f"research-os standalone package links outside its bundle: {target}",
                    )

    def test_product_recipe_has_no_slice_status_or_unread_case_implementation_copy(self):
        self.assertNotRegex(self.recipe, r"(?i)\bSlice\s+[ABC]\b")
        self.assertNotIn("未阅读或复制未缓存", self.recipe)
        self.assertIn("不认证候选证明", self.recipe)
        self.assertIn("原命题", self.recipe)
        self.assertIn("proof-review 每次 fresh", self.recipe)


if __name__ == "__main__":
    unittest.main()
