#!/usr/bin/env python3
"""#43：paper-writing 三变体路由与级联。期望值是本文件字面量，不从 checker 常量回读。"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = dict.fromkeys(
    ("general", "ml", "systems"),
    (
        "skills/writing-cycle/paper-writing/SKILL.md",
        "skills/writing-cycle/paper-writing/references/composition-map.md",
        "skills/writing-cycle/paper-writing/references/standards.md",
    ),
)
DOMAIN_RESOURCES = {
    "general": (
        "skills/writing-cycle/paper-writing/references/standards.md",
        "skills/writing-cycle/paper-writing/SKILL.md",
    ),
    "ml": (
        "skills/writing-cycle/paper-writing/references/ml-ai-standards.md",
        "skills/writing-cycle/paper-writing/references/ml-experiment-reporting.md",
        "skills/writing-cycle/paper-writing/references/ml-reviewer-expectations.md",
        "skills/writing-cycle/paper-writing/references/ml-venue-checklists.md",
        "skills/writing-cycle/paper-writing/templates/ml-writing-report.md",
        "skills/writing-cycle/paper-writing/references/sources.md",
        "skills/writing-cycle/paper-writing/LICENSE-ML.txt",
    ),
    "systems": (
        "skills/writing-cycle/paper-writing/references/systems-standards.md",
        "skills/writing-cycle/paper-writing/references/systems-writing-methods.md",
        "skills/writing-cycle/paper-writing/references/systems-evaluation-methods.md",
        "skills/writing-cycle/paper-writing/references/systems-checklist.md",
        "skills/writing-cycle/paper-writing/references/systems-venue-and-reviewer.md",
        "skills/writing-cycle/paper-writing/templates/systems-paper-writing-report.md",
        "skills/writing-cycle/paper-writing/references/sources.md",
        "skills/writing-cycle/paper-writing/LICENSE-ARIS.txt",
        "skills/writing-cycle/paper-writing/LICENSE-Orchestra.txt",
    ),
}
DOMAIN_TARGETS = tuple(
    dict.fromkeys(path for variant in ("ml", "systems") for path in DOMAIN_RESOURCES[variant])
)
STANDARDS_TEXT = (
    "# Standards\n\n"
    "| Domain | Reference |\n|---|---|\n"
    "| ML / AI | [ML/AI standards](ml-ai-standards.md); [experiment reporting](ml-experiment-reporting.md); "
    "[reviewer expectations](ml-reviewer-expectations.md); [venue checklist](ml-venue-checklists.md); "
    "[report template](../templates/ml-writing-report.md) |\n"
    "| Systems | [Systems standards](systems-standards.md); [writing methods](systems-writing-methods.md); "
    "[evaluation](systems-evaluation-methods.md); [checklist](systems-checklist.md); "
    "[venue/reviewer](systems-venue-and-reviewer.md); [report template](../templates/systems-paper-writing-report.md) |\n"
    "\n[Sources and licenses](sources.md)\n"
)
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
    lines.append("已授权的委托内修复继承范围：`paper-compile-repair` 与 `apply-citation-fixes`。")
    if extra:
        lines.append(extra)
    return "\n".join(lines) + "\n"


def touch_tree(root: Path, paths: tuple[str, ...]) -> None:
    for path in paths:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.endswith("references/standards.md"):
            content = STANDARDS_TEXT
        elif path.endswith("references/sources.md"):
            content = "../LICENSE-ML.txt ../LICENSE-ARIS.txt ../LICENSE-Orchestra.txt\n"
        else:
            content = "leaf\n"
        target.write_text(content, encoding="utf-8")


class PaperWritingRoutes(unittest.TestCase):
    def test_repo_three_variants_route_to_unified_entry_and_load_domain_resources(self):
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
            self.assertIn("委托", body)
            if variant != "general":
                self.assertIn("统一 `paper-writing` 入口", body)
            else:
                self.assertIn("composition map", body)
            standards = ROOT / "skills/writing-cycle/paper-writing/references/standards.md"
            self.assertTrue(standards.is_file())
            standards_text = standards.read_text(encoding="utf-8")
            for path in DOMAIN_RESOURCES[variant]:
                target = ROOT / path
                self.assertTrue(target.is_file(), path)
                if variant != "general" and path in DOMAIN_TARGETS and "/LICENSE-" not in path:
                    self.assertIn(Path(path).name, standards_text, path)
            self.assertIn("授权", body)

    def test_valid_copy_is_clean(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            touch_tree(root, (*REQUIRED["ml"], *DOMAIN_TARGETS))
            problems = mod.paper_writing_variant_problems(
                "ml", playbook_text("ml", REQUIRED["ml"]), root
            )
            self.assertEqual(problems, [])

    def test_damaged_copy_missing_unified_entry_fails(self):
        mod = load()
        kept = ("skills/writing-cycle/paper-writing/references/composition-map.md",)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            touch_tree(root, REQUIRED["general"])
            problems = mod.paper_writing_variant_problems(
                "general", playbook_text("general", kept), root
            )
            self.assertTrue(any("paper-writing/SKILL.md" in item for item in problems))

    def test_unified_entry_reference_must_exist(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            present = ("skills/writing-cycle/paper-writing/SKILL.md",)
            touch_tree(root, present)
            body = playbook_text("systems", REQUIRED["systems"])
            problems = mod.paper_writing_variant_problems("systems", body, root)
            self.assertTrue(any("composition-map.md" in item for item in problems))

    def test_professional_standard_pointer_must_be_reachable(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            touch_tree(root, (*REQUIRED["ml"], *DOMAIN_TARGETS))
            standards = root / "skills/writing-cycle/paper-writing/references/standards.md"
            standards.write_text(
                STANDARDS_TEXT.replace("[ML/AI standards](ml-ai-standards.md)", "ML/AI standards"),
                encoding="utf-8",
            )
            problems = mod.paper_writing_variant_problems(
                "ml", playbook_text("ml", REQUIRED["ml"]), root
            )
            self.assertTrue(any("ml-ai-standards.md" in item for item in problems))

    def test_professional_standard_target_must_exist(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            touch_tree(root, (*REQUIRED["ml"], *DOMAIN_TARGETS))
            (root / DOMAIN_TARGETS[0]).unlink()
            problems = mod.paper_writing_variant_problems(
                "ml", playbook_text("ml", REQUIRED["ml"]), root
            )
            self.assertTrue(any("ml-ai-standards.md" in item for item in problems))

    def test_domain_standards_ship_inside_the_unified_skill(self):
        for variant, resources in DOMAIN_RESOURCES.items():
            with self.subTest(variant=variant):
                for path in resources:
                    self.assertTrue((ROOT / path).is_file(), path)

    def test_professional_resources_and_licenses_have_one_owner(self):
        for path in DOMAIN_TARGETS:
            self.assertTrue((ROOT / path).is_file(), path)
        for name in ("ml-paper-writing", "systems-paper-writing"):
            self.assertFalse((ROOT / "skills/writing-cycle" / name / "SKILL.md").exists(), name)


if __name__ == "__main__":
    unittest.main()
