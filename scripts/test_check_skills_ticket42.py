#!/usr/bin/env python3
"""#42：Validation 两条路由行与批次授权引用。先于路由落地写，期望失败。"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/general/research-os/SKILL.md"
PLAYBOOKS = ROOT / "skills/general/research-os/playbooks"
GRANT = ROOT / "skills/general/research-os/references/batch-authorization.md"


def load():
    path = ROOT / "scripts" / "check-skills.py"
    spec = importlib.util.spec_from_file_location("check_skills", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ValidationRoutes(unittest.TestCase):
    def test_plan_and_bridge_rows_resolve(self):
        mod = load()
        text = SKILL.read_text(encoding="utf-8")
        rows, parse_errors = mod.parse_route_table(text)
        self.assertEqual(parse_errors, [])
        by_route = {row["路线"]: row for row in rows}
        self.assertIn("experiment-plan", by_route)
        self.assertIn("experiment-bridge", by_route)
        self.assertEqual(by_route["experiment-plan"]["变体"], "—")
        self.assertEqual(by_route["experiment-bridge"]["变体"], "—")
        self.assertEqual(by_route["experiment-plan"]["只读约束"], "no")
        self.assertEqual(by_route["experiment-bridge"]["只读约束"], "no")
        self.assertIn("设计实验", by_route["experiment-plan"]["触发词"])
        self.assertIn("跑完这个实验并分析", by_route["experiment-bridge"]["触发词"])
        problems, _hints = mod.route_table_problems(rows, SKILL.parent)
        self.assertEqual(problems, [])
        self.assertTrue((PLAYBOOKS / "experiment-plan.md").is_file())
        self.assertTrue((PLAYBOOKS / "experiment-bridge.md").is_file())

    def test_grant_reference_is_tracked_cascade(self):
        mod = load()
        self.assertTrue(GRANT.is_file())
        text = (PLAYBOOKS / "experiment-bridge.md").read_text(encoding="utf-8")
        self.assertIn("references/batch-authorization.md", text)
        tracked = mod.git_tracked()
        problems = mod.backtick_cascade_problems(
            "skills/general/research-os/playbooks/experiment-bridge.md",
            text,
            ROOT,
            tracked,
        )
        self.assertEqual(problems, [])

    def test_leaf_skills_unchanged_by_contract_pointer(self):
        bridge = (PLAYBOOKS / "experiment-bridge.md").read_text(encoding="utf-8")
        plan = (PLAYBOOKS / "experiment-plan.md").read_text(encoding="utf-8")
        self.assertIn("skills/validation-cycle/experiment-bridge/SKILL.md", bridge)
        self.assertIn("skills/validation-cycle/experiment-plan/SKILL.md", plan)
        grant = GRANT.read_text(encoding="utf-8")
        for phrase in (
            "默认政策",
            "planned-run",
            "run_count_basis",
            "未知",
            "concurrency_limit",
            "retry_limit",
            "valid_until",
        ):
            self.assertIn(phrase, grant)


if __name__ == "__main__":
    unittest.main()
