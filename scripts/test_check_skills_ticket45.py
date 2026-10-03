#!/usr/bin/env python3
"""#45：proof / improvement / pickup 路由行与级联。先于实现写，期望失败。"""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/general/research-os"
ROUTES = ("proof", "improvement", "pickup")


def load():
    path = ROOT / "scripts" / "check-skills.py"
    spec = importlib.util.spec_from_file_location("check_skills_t45", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tracked() -> set[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return {line.strip() for line in out.splitlines() if line.strip()}


class Ticket45Routes(unittest.TestCase):
    def test_three_rows_and_files(self):
        mod = load()
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        rows, parse_errors = mod.parse_route_table(text)
        self.assertEqual(parse_errors, [])
        keys = {(row["路线"], row["变体"]) for row in rows}
        for route in ROUTES:
            self.assertIn((route, "—"), keys)
            row = next(item for item in rows if item["路线"] == route)
            self.assertEqual(row["只读约束"], "no")
        problems, _hints = mod.route_table_problems(rows, SKILL)
        self.assertEqual(problems, [])
        pending = text.split("已命名、文件未交付", 1)[-1].split("。", 1)[0]
        for route in ROUTES:
            self.assertNotIn(route, pending)

    def test_positive_cascade_and_corrupt_copy(self):
        mod = load()
        files = [
            "skills/general/research-os/playbooks/proof.md",
            "skills/general/research-os/playbooks/improvement.md",
            "skills/general/research-os/playbooks/pickup.md",
            "skills/general/research-os/PHASE-BOUNDARIES.md",
            "skills/general/research-os/playbooks/route-only.md",
        ]
        known = tracked()
        for rel in files:
            self.assertTrue((ROOT / rel).is_file(), rel)
            problems = mod.backtick_cascade_problems(
                rel,
                (ROOT / rel).read_text(encoding="utf-8"),
                ROOT,
                known | set(files),
            )
            self.assertEqual(problems, [], problems)
        proof = (SKILL / "playbooks/proof.md").read_text(encoding="utf-8")
        damaged = proof.replace(
            "`skills/validation-cycle/proof-orchestrator/SKILL.md`",
            "`skills/validation-cycle/proof-orchestrator/references/missing-handoff.md`",
            1,
        )
        self.assertNotEqual(damaged, proof)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rel = "skills/general/research-os/playbooks/proof.md"
            target = root / rel
            target.parent.mkdir(parents=True)
            target.write_text(damaged, encoding="utf-8")
            problems = mod.backtick_cascade_problems(rel, damaged, root, {rel})
            self.assertTrue(any("missing-handoff.md" in item for item in problems))

    def test_pickup_rechecks_exact_write_and_tool_permissions(self):
        pickup = (SKILL / "playbooks/pickup.md").read_text(encoding="utf-8")
        self.assertIn("逐个绝对路径", pickup)
        self.assertIn("修正误写位置也不授权删除", pickup)
        self.assertIn("普通数学授权不自动包含", pickup)

    def test_route_only_points_at_shipped_boundaries(self):
        text = (SKILL / "playbooks/route-only.md").read_text(encoding="utf-8")
        self.assertNotIn("不在本发行", text)
        self.assertIn("PHASE-BOUNDARIES.md", text)
        phase = (SKILL / "PHASE-BOUNDARIES.md").read_text(encoding="utf-8")
        for option in ("Continue", "/clear", "/handoff", "Subagent", "/compact"):
            self.assertIn(option, phase)
        self.assertIn("pickup", phase)
        pickup = (SKILL / "playbooks/pickup.md").read_text(encoding="utf-8")
        self.assertIn("valid_until", pickup)
        self.assertIn("research-log", pickup)
        for field in (
            "user_confirmation",
            "authorization_status",
            "actual_consumption",
            "skills/general/setup-research-os/templates/compute-policy.md",
            "skills/general/setup-research-os/templates/research-log.md",
        ):
            self.assertIn(field, pickup)
