#!/usr/bin/env python3
"""#44：rebuttal / resubmit / paper-talk 路由行先于 playbook 存在。"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = {
    ("rebuttal", "—"): "playbooks/rebuttal.md",
    ("resubmit", "—"): "playbooks/resubmit.md",
    ("paper-talk", "—"): "playbooks/paper-talk.md",
}

CASCADE = {
    "skills/general/research-os/playbooks/rebuttal.md": (
        "skills/writing-cycle/rebuttal/SKILL.md",
        "skills/writing-cycle/rebuttal/references/response-methods.md",
        "skills/writing-cycle/rebuttal/templates/working-documents.md",
    ),
    "skills/general/research-os/playbooks/resubmit.md": (
        "skills/writing-cycle/resubmit-pipeline/SKILL.md",
        "skills/writing-cycle/resubmit-pipeline/references/adaptation-methods.md",
        "skills/writing-cycle/resubmit-pipeline/templates/adaptation-report.md",
        "skills/writing-cycle/paper-compile/SKILL.md",
        "skills/writing-cycle/citation-audit/SKILL.md",
    ),
    "skills/general/research-os/playbooks/paper-talk.md": (
        "skills/writing-cycle/paper-talk/SKILL.md",
        "skills/writing-cycle/paper-talk/references/story-and-delivery.md",
        "skills/writing-cycle/paper-talk/references/slide-templates.md",
        "skills/writing-cycle/paper-talk/references/talk-audit.md",
        "skills/writing-cycle/paper-talk/references/visual-polish.md",
        "skills/writing-cycle/paper-talk/templates/talk-materials.md",
        "skills/writing-cycle/paper-talk/templates/talk-report.md",
    ),
}


def load():
    path = ROOT / "scripts" / "check-skills.py"
    spec = importlib.util.spec_from_file_location("check_skills", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Ticket44Routes(unittest.TestCase):
    def test_three_delivery_routes_resolve(self):
        mod = load()
        skill = ROOT / "skills/general/research-os"
        rows, errors = mod.parse_route_table((skill / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(errors, [])
        by_key = {(row["路线"], row["变体"]): row for row in rows}
        for key, playbook in REQUIRED.items():
            self.assertIn(key, by_key)
            self.assertIn(playbook, by_key[key]["playbook"])
            self.assertEqual(by_key[key]["只读约束"], "no")
        problems, _hints = mod.route_table_problems(rows, skill)
        self.assertEqual(problems, [])


class Ticket44Cascade(unittest.TestCase):
    def test_playbooks_cite_real_skills(self):
        mod = load()
        tracked = {path for paths in CASCADE.values() for path in paths}
        for rel, paths in CASCADE.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            for path in paths:
                self.assertIn(f"`{path}`", text)
                self.assertTrue((ROOT / path).is_file(), path)
            problems = mod.backtick_cascade_problems(rel, text, ROOT, tracked | {rel})
            self.assertEqual(problems, [])

    def test_damaged_copy_reports_missing_target(self):
        mod = load()
        rel = "skills/general/research-os/playbooks/rebuttal.md"
        text = (ROOT / rel).read_text(encoding="utf-8").replace(
            "skills/writing-cycle/rebuttal/SKILL.md",
            "skills/writing-cycle/rebuttal/references/missing.md",
            1,
        )
        problems = mod.backtick_cascade_problems(rel, text, ROOT, set())
        self.assertTrue(any("missing.md" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
