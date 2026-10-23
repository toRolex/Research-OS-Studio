from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRITING = ROOT / "skills/writing-cycle"
LEAF_SLUGS = (
    "apply-citation-fixes",
    "citation-audit",
    "claim-stress-test",
    "paper-claim-audit",
    "paper-compile",
    "paper-compile-repair",
    "paper-drafting",
    "paper-plan",
    "paper-talk",
    "paper-writing",
    "rebuttal",
    "resubmit-pipeline",
)
EXCERPT = ROOT / "skills/general/research-os/references/mandate-leaf-excerpt.md"


class Ticket60FlatInstallLinks(unittest.TestCase):
    def test_each_independent_writing_leaf_carries_the_mandate_excerpt(self):
        self.assertTrue(EXCERPT.is_file(), "canonical distribution excerpt is missing")
        canonical_bytes = EXCERPT.read_bytes()

        for slug in LEAF_SLUGS:
            with self.subTest(slug=slug):
                package = WRITING / slug
                skill = (package / "SKILL.md").read_text(encoding="utf-8")
                mandate = package / "references/mandate.md"
                self.assertIn("references/mandate.md", skill)
                self.assertNotIn("../../general/research-os/references/mandate.md", skill)
                self.assertTrue(mandate.is_file(), "co-located mandate is missing")
                self.assertEqual(mandate.read_bytes(), canonical_bytes)

    def test_distribution_excerpt_is_self_contained_and_points_to_authority(self):
        text = EXCERPT.read_text(encoding="utf-8")
        self.assertIn("skills/general/research-os/references/mandate.md", text)
        self.assertIn("唯一规范源", text)
        self.assertIn("不扩大授权", text)
        self.assertNotRegex(text, r"\[[^\]]+\]\((?!https?://|mailto:)[^)]+\)")

    def test_paper_writing_declares_optional_slug_dependencies_and_blocked_branches(self):
        skill = (WRITING / "paper-writing/SKILL.md").read_text(encoding="utf-8")
        dependencies = skill.split("## 单包安装与依赖", 1)
        self.assertEqual(len(dependencies), 2, "dependency boundary must be explicit")
        dependency_text = dependencies[1]
        for slug in (
            "paper-plan",
            "academic-plotting",
            "paper-drafting",
            "paper-compile",
            "paper-compile-repair",
            "paper-claim-audit",
            "citation-audit",
            "apply-citation-fixes",
            "claim-stress-test",
            "proof-review",
        ):
            self.assertIn(f"`{slug}`", dependency_text)
        self.assertIn("blocked", dependency_text)
        self.assertIn("完整写作流程", dependency_text)

    def test_proof_review_route_uses_discoverable_slug_not_source_category_path(self):
        composition = (WRITING / "paper-writing/references/composition-map.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`proof-review`", composition)
        self.assertNotIn("../../../validation-cycle/proof-review/SKILL.md", composition)


if __name__ == "__main__":
    unittest.main()
