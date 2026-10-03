#!/usr/bin/env python3
"""#46：14 行路由组合、旧承诺 sweep、串行降级。先于实现写，期望失败。"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ROUTES = (
    ("route-only", "—", "yes"),
    ("idea-discovery", "—", "no"),
    ("experiment-plan", "—", "no"),
    ("experiment-bridge", "—", "no"),
    ("paper-writing", "general", "no"),
    ("paper-writing", "ml", "no"),
    ("paper-writing", "systems", "no"),
    ("proof", "—", "no"),
    ("rebuttal", "—", "no"),
    ("resubmit", "—", "no"),
    ("paper-talk", "—", "no"),
    ("improvement", "—", "no"),
    ("pickup", "—", "no"),
    ("custom", "—", "no"),
)


def load():
    path = ROOT / "scripts" / "check-skills.py"
    spec = importlib.util.spec_from_file_location("check_skills_t46", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ReleaseGate(unittest.TestCase):
    def test_fourteen_routes_are_complete(self):
        mod = load()
        text = (ROOT / "skills/general/research-os/SKILL.md").read_text(encoding="utf-8")
        rows, errors = mod.parse_route_table(text)
        self.assertEqual(errors, [])
        problems = mod.release_route_problems(rows)
        self.assertEqual(problems, [])
        keys = {(row["路线"], row["变体"], row["只读约束"]) for row in rows}
        self.assertEqual(keys, set(REQUIRED_ROUTES))

    def test_damaged_route_copy_is_red(self):
        mod = load()
        text = (ROOT / "skills/general/research-os/SKILL.md").read_text(encoding="utf-8")
        rows, _errors = mod.parse_route_table(text.replace("| pickup |", "| dropped-pickup |", 1))
        problems = mod.release_route_problems(rows)
        self.assertTrue(any("pickup" in item for item in problems))

    def test_stale_stop_promise_is_red(self):
        mod = load()
        files = {
            "README.md": "人在回路：顶层工作流完成后立即停止，绝不自动跳转到下一阶段。",
            "docs/README-en.md": "No Automatic Chaining: workflows stop after delivering.",
        }
        problems = mod.stale_promise_problems(files)
        self.assertEqual(len(problems), 2)

    def test_real_readme_stale_promises_are_red(self):
        mod = load()
        cases = (
            (
                "README.md",
                "2. **",
                "2. **流程不自动串联**：顶层工作流交付产物后立即结束，不会自动触发后续流程。",
            ),
            (
                "docs/README-en.md",
                "- **Human in the Loop**:",
                "- **Human in the Loop**: Top-level workflows stop upon completion and never transition to subsequent stages without explicit instruction.",
            ),
        )
        for name, prefix, stale_line in cases:
            with self.subTest(document=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                current_line = next(line for line in text.splitlines() if line.startswith(prefix))
                damaged = text.replace(current_line, stale_line, 1)
                problems = mod.stale_promise_problems({name: damaged})
                self.assertTrue(any(item.startswith(f"{name}:") for item in problems))

    def test_leaf_delivery_stops_remain_valid(self):
        mod = load()
        files = {
            "README.md": "交付 IDEA_DISCOVERY.md 与 RESEARCH_PROPOSAL.md 后停止\n交付实验审计与 Claim 报告（停止）",
            "docs/README-en.md": "Deliver IDEA_DISCOVERY.md and RESEARCH_PROPOSAL.md, then stop\nDelivers a candidate manuscript and audit report (stops)",
        }
        self.assertEqual(mod.stale_promise_problems(files), [])

    def test_current_docs_have_no_stale_stop_promise(self):
        mod = load()
        names = (
            "README.md",
            "docs/README-en.md",
            "skills/README.md",
            "docs/user-acceptance-guide.md",
        )
        files = {name: (ROOT / name).read_text(encoding="utf-8") for name in names}
        self.assertEqual(mod.stale_promise_problems(files), [])

    def test_host_map_names_serial_fallback(self):
        mod = load()
        text = (ROOT / "skills/general/research-os/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(mod.host_fallback_problems(text), [])

    def test_host_map_without_fallback_is_red(self):
        mod = load()
        text = "| pi | .agents/skills | herdr_spawn_agent | session |\n"
        problems = mod.host_fallback_problems(text)
        self.assertTrue(problems)


if __name__ == "__main__":
    unittest.main()
