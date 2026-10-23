"""#55 Slice A: installed math-research recipe composition and contract boundaries.

These checks cover discoverable Skill structure and declared contracts only; they
do not evaluate whether a proof, computation, or formalization is mathematically
correct.
"""
from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "skills/general/research-os/SKILL.md"
PLAYBOOK = ROOT / "skills/general/research-os/playbooks/proof.md"
CHECKER = ROOT / "scripts/check-skills.py"

CAPABILITIES = {
    "arena": "skills/organization/arena/SKILL.md",
    "swarm": "skills/general/swarm/SKILL.md",
    "interrogate": "skills/general/interrogate/SKILL.md",
    "formula-derivation": "skills/validation-cycle/formula-derivation/SKILL.md",
    "proof-writer": "skills/validation-cycle/proof-writer/SKILL.md",
    "proof-review": "skills/validation-cycle/proof-review/SKILL.md",
    "proof-repair": "skills/validation-cycle/proof-repair/SKILL.md",
    "proof-orchestrator": "skills/validation-cycle/proof-orchestrator/SKILL.md",
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
                self.assertIn(f"`{relative_path}`", self.recipe)
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
            "../references/migration-boundary.md",
        ):
            with self.subTest(reference=reference):
                self.assertIn(reference, self.recipe)
        for reference in (
            ROOT / "skills/general/research-os/references/mandate.md",
            ROOT / "skills/general/research-os/playbooks/continuation.md",
            ROOT / "skills/general/research-os/playbooks/pickup.md",
            ROOT / "skills/general/research-os/playbooks/improvement.md",
            ROOT / "skills/general/research-os/references/migration-boundary.md",
        ):
            self.assertTrue(reference.is_file(), str(reference))

    def test_unmigrated_leaf_gates_are_not_overridden_by_the_center_recipe(self):
        checker = load_checker()
        legacy_paths = (
            "skills/validation-cycle/formula-derivation/SKILL.md",
            "skills/validation-cycle/proof-repair/SKILL.md",
            "skills/validation-cycle/proof-writer/SKILL.md",
        )
        for relative_path in legacy_paths:
            with self.subTest(skill=relative_path):
                self.assertIn(relative_path, checker.LEGACY_LEAF_GATES)
                leaf = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertRegex(leaf, r"(?m)^Gate:")
        self.assertTrue(
            contains_any(
                self.recipe,
                ("叶级门", "叶 Skill 自身的门", "未迁移能力的门"),
            ),
            "the recipe must preserve the still-active leaf contract",
        )


if __name__ == "__main__":
    unittest.main()
