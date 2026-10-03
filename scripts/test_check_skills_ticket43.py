#!/usr/bin/env python3
"""#43：paper-writing 三变体路由与级联。期望值是本文件字面量，不从 checker 常量回读。"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SHARED = (
    "skills/writing-cycle/paper-plan/SKILL.md",
    "skills/writing-cycle/academic-plotting/SKILL.md",
    "skills/writing-cycle/paper-drafting/SKILL.md",
    "skills/writing-cycle/paper-compile/SKILL.md",
    "skills/writing-cycle/paper-claim-audit/SKILL.md",
    "skills/writing-cycle/citation-audit/SKILL.md",
    "skills/writing-cycle/claim-stress-test/SKILL.md",
    "skills/validation-cycle/proof-review/SKILL.md",
)
REQUIRED = {
    "general": SHARED
    + (
        "skills/writing-cycle/paper-writing/SKILL.md",
        "skills/writing-cycle/paper-writing/references/composition-map.md",
    ),
    "ml": SHARED
    + (
        "skills/writing-cycle/ml-paper-writing/SKILL.md",
        "skills/writing-cycle/ml-paper-writing/references/composition-map.md",
        "skills/writing-cycle/ml-paper-writing/references/experiment-reporting.md",
        "skills/writing-cycle/ml-paper-writing/references/reviewer-expectations.md",
        "skills/writing-cycle/ml-paper-writing/references/venue-checklists.md",
    ),
    "systems": SHARED
    + (
        "skills/writing-cycle/systems-paper-writing/SKILL.md",
        "skills/writing-cycle/systems-paper-writing/references/composition-map.md",
        "skills/writing-cycle/systems-paper-writing/references/systems-writing-methods.md",
        "skills/writing-cycle/systems-paper-writing/references/evaluation-methods.md",
        "skills/writing-cycle/systems-paper-writing/references/checklist.md",
        "skills/writing-cycle/systems-paper-writing/references/venue-and-reviewer.md",
        "skills/writing-cycle/paper-plan/references/systems-blueprints.md",
        "skills/writing-cycle/paper-plan/references/systems-patterns.md",
    ),
}
FORBIDDEN = {
    "general": (
        "skills/writing-cycle/ml-paper-writing/SKILL.md",
        "skills/writing-cycle/systems-paper-writing/SKILL.md",
    ),
    "ml": (
        "skills/writing-cycle/paper-writing/SKILL.md",
        "skills/writing-cycle/systems-paper-writing/SKILL.md",
    ),
    "systems": (
        "skills/writing-cycle/paper-writing/SKILL.md",
        "skills/writing-cycle/ml-paper-writing/SKILL.md",
    ),
}
HARD_STOPS = ("paper-compile-repair", "apply-citation-fixes")


def load():
    path = ROOT / "scripts" / "check-skills.py"
    spec = importlib.util.spec_from_file_location("check_skills_ticket43", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def playbook_text(variant: str, paths: tuple[str, ...], extra: str = "") -> str:
    lines = [
        f"# paper-writing / {variant}",
        "",
        "写入前停在叶 skill 的授权门。",
        "",
    ]
    for path in paths:
        lines.append(f"读 `{path}` 全文。")
    lines.append("硬停止仍须另行点名：`paper-compile-repair` 与 `apply-citation-fixes`。")
    if extra:
        lines.append(extra)
    return "\n".join(lines) + "\n"


def touch_tree(root: Path, paths: tuple[str, ...]) -> None:
    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("leaf\n", encoding="utf-8")


class PaperWritingRoutes(unittest.TestCase):
    def test_repo_three_variants_cascade_and_stay_on_own_entry(self):
        mod = load()
        text = (ROOT / "skills/general/research-os/SKILL.md").read_text(encoding="utf-8")
        rows, errors = mod.parse_route_table(text)
        self.assertEqual(errors, [])
        problems = mod.paper_writing_route_problems(rows, ROOT)
        self.assertEqual(problems, [])
        by_variant = {row["变体"]: row for row in rows if row["路线"] == "paper-writing"}
        self.assertEqual(set(by_variant), {"general", "ml", "systems"})
        for variant, row in by_variant.items():
            self.assertEqual(row["只读约束"], "no")
            playbook = ROOT / "skills/general/research-os" / f"playbooks/paper-writing-{variant}.md"
            body = playbook.read_text(encoding="utf-8")
            for path in REQUIRED[variant]:
                self.assertIn(f"`{path}`", body)
            for path in FORBIDDEN[variant]:
                self.assertNotIn(f"`{path}`", body)
            for name in HARD_STOPS:
                self.assertIn(f"`{name}`", body)
            self.assertIn("授权", body)

    def test_valid_copy_is_clean(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            touch_tree(root, REQUIRED["ml"])
            problems = mod.paper_writing_variant_problems(
                "ml", playbook_text("ml", REQUIRED["ml"]), root
            )
            self.assertEqual(problems, [])

    def test_damaged_copy_missing_citation_fails(self):
        mod = load()
        kept = tuple(path for path in REQUIRED["general"] if not path.endswith("citation-audit/SKILL.md"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            touch_tree(root, REQUIRED["general"])
            problems = mod.paper_writing_variant_problems(
                "general", playbook_text("general", kept), root
            )
            self.assertTrue(any("citation-audit/SKILL.md" in item for item in problems))

    def test_token_present_but_file_missing_fails(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            present = tuple(
                path for path in REQUIRED["systems"] if not path.endswith("proof-review/SKILL.md")
            )
            touch_tree(root, present)
            problems = mod.paper_writing_variant_problems(
                "systems", playbook_text("systems", REQUIRED["systems"]), root
            )
            self.assertTrue(any("proof-review/SKILL.md" in item and "不存在" in item for item in problems))

    def test_professional_entry_must_not_cascade_general_skill(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            touch_tree(root, REQUIRED["ml"] + FORBIDDEN["ml"])
            body = playbook_text(
                "ml",
                REQUIRED["ml"],
                "也读 `skills/writing-cycle/paper-writing/SKILL.md`。",
            )
            problems = mod.paper_writing_variant_problems("ml", body, root)
            self.assertTrue(any("paper-writing/SKILL.md" in item for item in problems))


if __name__ == "__main__":
    unittest.main()
