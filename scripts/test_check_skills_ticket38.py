#!/usr/bin/env python3
"""#38：路由表、反引号级联、门声明、旧 router。先于实现写，期望失败。"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    path = ROOT / "scripts" / "check-skills.py"
    source = path.read_text(encoding="utf-8")
    if "\ndef main(" not in source:
        raise AssertionError("check-skills.py 仍在 import 时执行全仓检查")
    spec = importlib.util.spec_from_file_location("check_skills", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VALID = """\
| 路线 | 变体 | 触发词 | 适用条件 | 只读约束 | playbook |
|---|---|---|---|---|---|
| route-only | — | 我该从哪开始、只看推荐 | 只要推荐不要执行 | yes | [route-only](playbooks/route-only.md) |
| custom | — | 没有对应流程 | 无已交付路线匹配 | no | [custom](playbooks/custom.md) |
"""


class RouteTable(unittest.TestCase):
    def test_valid_rows(self):
        mod = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill = root / "skills/general/research-os"
            (skill / "playbooks").mkdir(parents=True)
            (skill / "playbooks/route-only.md").write_text("x", encoding="utf-8")
            (skill / "playbooks/custom.md").write_text("x", encoding="utf-8")
            rows, parse_errors = mod.parse_route_table(VALID)
            self.assertEqual(parse_errors, [])
            problems, hints = mod.route_table_problems(rows, skill)
            self.assertEqual(problems, [])
            self.assertEqual(hints, [])

    def test_duplicate_key(self):
        mod = load()
        text = VALID.replace(
            "| custom | — |",
            "| route-only | — |",
            1,
        )
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d) / "skills/general/research-os"
            (skill / "playbooks").mkdir(parents=True)
            (skill / "playbooks/route-only.md").write_text("x", encoding="utf-8")
            (skill / "playbooks/custom.md").write_text("x", encoding="utf-8")
            rows, parse_errors = mod.parse_route_table(text)
            problems, _hints = mod.route_table_problems(rows, skill)
            self.assertTrue(parse_errors or any("唯一" in p or "重复" in p for p in problems))

    def test_missing_playbook(self):
        mod = load()
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d) / "skills/general/research-os"
            (skill / "playbooks").mkdir(parents=True)
            (skill / "playbooks/route-only.md").write_text("x", encoding="utf-8")
            rows, parse_errors = mod.parse_route_table(VALID)
            self.assertEqual(parse_errors, [])
            problems, _hints = mod.route_table_problems(rows, skill)
            self.assertTrue(any("custom.md" in p for p in problems))

    def test_missing_column(self):
        mod = load()
        text = VALID.replace("| 只读约束 | playbook |", "| playbook |").replace(
            "| yes |", "|"
        ).replace("| no |", "|")
        _rows, parse_errors = mod.parse_route_table(text)
        self.assertTrue(any("只读约束" in p for p in parse_errors))

    def test_duplicate_trigger_is_hint(self):
        mod = load()
        text = VALID.replace("| 没有对应流程 |", "| 我该从哪开始 |")
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d) / "skills/general/research-os"
            (skill / "playbooks").mkdir(parents=True)
            (skill / "playbooks/route-only.md").write_text("x", encoding="utf-8")
            (skill / "playbooks/custom.md").write_text("x", encoding="utf-8")
            rows, parse_errors = mod.parse_route_table(text)
            self.assertEqual(parse_errors, [])
            problems, hints = mod.route_table_problems(rows, skill)
            self.assertEqual(problems, [])
            self.assertTrue(any("我该从哪开始" in h for h in hints))


class Cascade(unittest.TestCase):
    def test_missing_and_present(self):
        mod = load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill = root / "skills/general/research-os"
            (skill / "playbooks").mkdir(parents=True)
            (skill / "references").mkdir()
            (skill / "references/PRODUCT-MAP.md").write_text("map", encoding="utf-8")
            rel = "skills/general/research-os/playbooks/route-only.md"
            text = "读 `references/PRODUCT-MAP.md`，不要读 `references/missing.md`。\n"
            tracked = {
                "skills/general/research-os/references/PRODUCT-MAP.md",
                rel,
            }
            problems = mod.backtick_cascade_problems(rel, text, root, tracked)
            self.assertTrue(any("missing.md" in p for p in problems))
            self.assertFalse(any("PRODUCT-MAP" in p for p in problems))

    def test_filename_without_slash_ignored(self):
        mod = load()
        problems = mod.backtick_cascade_problems(
            "skills/general/research-os/SKILL.md",
            "产出 `IDEA_DISCOVERY.md`。\n",
            ROOT,
            set(),
        )
        self.assertEqual(problems, [])

    def test_upstream_and_brace_skipped(self):
        mod = load()
        text = (
            "上游 `references/checklists.md` 不在本仓。\n"
            "展开 `references/{a,b}.md`。\n"
        )
        problems = mod.backtick_cascade_problems(
            "skills/general/research-os/SKILL.md",
            text,
            ROOT,
            set(),
        )
        self.assertEqual(problems, [])

    def test_outside_research_os_not_scanned_by_repo_helper(self):
        mod = load()
        self.assertFalse(
            mod.cascade_scope("skills/writing-cycle/ml-paper-writing/references/sources.md")
        )
        self.assertTrue(mod.cascade_scope("skills/general/research-os/playbooks/custom.md"))


class Gates(unittest.TestCase):
    def body(self, extra: str) -> str:
        return (
            "# Demo\n\n## 回应策略\n\n先确认。\n\n"
            + extra
            + "\n\n## 数据删除\n\n停。\n"
        )

    def test_matches_expected(self):
        mod = load()
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d)
            (skill / "SKILL.md").write_text("# 回应策略\n", encoding="utf-8")
            (skill / "references").mkdir()
            (skill / "references/delete.md").write_text("# 删除确认\n", encoding="utf-8")
            text = self.body(
                "Gate: strategy-confirm | before=reply-drafting | approval=explicit-user | source=SKILL.md#回应策略\n"
                "Gate: data-delete | before=unlink | approval=explicit-user | source=references/delete.md#删除确认\n"
            )
            problems = mod.gate_problems(
                "demo",
                skill,
                text,
                frozenset({"strategy-confirm", "data-delete"}),
            )
            self.assertEqual(problems, [])

    def test_drop_one(self):
        mod = load()
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d)
            (skill / "SKILL.md").write_text("# 回应策略\n", encoding="utf-8")
            text = self.body(
                "Gate: strategy-confirm | before=reply-drafting | approval=explicit-user | source=SKILL.md#回应策略\n"
            )
            problems = mod.gate_problems(
                "demo", skill, text, frozenset({"strategy-confirm", "data-delete"})
            )
            self.assertTrue(any("data-delete" in p for p in problems))

    def test_all_none(self):
        mod = load()
        problems = mod.gate_problems(
            "demo", ROOT, "Gates: none\n", frozenset({"strategy-confirm"})
        )
        self.assertTrue(problems)

    def test_changed_id(self):
        mod = load()
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d)
            (skill / "SKILL.md").write_text("# 回应策略\n", encoding="utf-8")
            text = self.body(
                "Gate: strategy-ok | before=reply-drafting | approval=explicit-user | source=SKILL.md#回应策略\n"
            )
            problems = mod.gate_problems(
                "demo", skill, text, frozenset({"strategy-confirm"})
            )
            self.assertTrue(any("strategy-confirm" in p or "strategy-ok" in p for p in problems))

    def test_duplicate(self):
        mod = load()
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d)
            (skill / "SKILL.md").write_text("# 回应策略\n", encoding="utf-8")
            line = "Gate: strategy-confirm | before=reply-drafting | approval=explicit-user | source=SKILL.md#回应策略\n"
            problems = mod.gate_problems(
                "demo", skill, self.body(line + line), frozenset({"strategy-confirm"})
            )
            self.assertTrue(any("重复" in p for p in problems))

    def test_bad_source(self):
        mod = load()
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d)
            (skill / "SKILL.md").write_text("# 回应策略\n", encoding="utf-8")
            text = self.body(
                "Gate: strategy-confirm | before=reply-drafting | approval=explicit-user | source=SKILL.md#不存在\n"
            )
            problems = mod.gate_problems(
                "demo", skill, text, frozenset({"strategy-confirm"})
            )
            self.assertTrue(any("不存在" in p or "锚点" in p for p in problems))

    def test_section_removed(self):
        mod = load()
        problems = mod.gate_problems(
            "demo", ROOT, "# Demo\n没有门。\n", frozenset()
        )
        self.assertTrue(any("none" in p for p in problems))

    def test_none_baseline(self):
        mod = load()
        problems = mod.gate_problems("research-os", ROOT, "Gates: none\n", frozenset())
        self.assertEqual(problems, [])


class Legacy(unittest.TestCase):
    def test_product_mention_fails_migration_sentence_ok(self):
        mod = load()
        problems = mod.legacy_router_problems(
            {
                "README.md": "请用 /ask-research-os\n",
                "skills/README.md": "旧入口 ask-research-os 已删除，改用 /research-os 的 route-only。\n",
            }
        )
        self.assertTrue(any("README.md" in p for p in problems))
        self.assertFalse(any("skills/README.md" in p for p in problems))


class Invocation(unittest.TestCase):
    def test_false_ok_true_and_missing_fail(self):
        mod = load()
        self.assertEqual(
            mod.invocation_value_problems("setup-research-os", True, "allow_implicit_invocation: false\n"),
            [],
        )
        self.assertTrue(mod.invocation_value_problems("x", True, "allow_implicit_invocation: true\n"))
        self.assertTrue(mod.invocation_value_problems("x", True, "interface: {}\n"))


IDEA_SKILLS = (
    "skills/idea-cycle/idea-discovery/SKILL.md",
    "skills/idea-cycle/research-lit/SKILL.md",
    "skills/idea-cycle/idea-generation/SKILL.md",
    "skills/idea-cycle/creative-thinking-for-research/SKILL.md",
    "skills/idea-cycle/novelty-check/SKILL.md",
    "skills/idea-cycle/idea-review/SKILL.md",
    "skills/idea-cycle/idea-refinement/SKILL.md",
)


class IdeaDiscoveryRoute(unittest.TestCase):
    def test_route_row_and_playbook_cascade(self):
        mod = load()
        text = (ROOT / "skills/general/research-os/SKILL.md").read_text(encoding="utf-8")
        rows, parse_errors = mod.parse_route_table(text)
        self.assertEqual(parse_errors, [])
        matched = [row for row in rows if row["路线"] == "idea-discovery"]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["只读约束"], "no")
        problems, _hints = mod.route_table_problems(rows, ROOT / "skills/general/research-os")
        self.assertEqual(problems, [])
        playbook = ROOT / "skills/general/research-os/playbooks/idea-discovery.md"
        body = playbook.read_text(encoding="utf-8")
        for rel in IDEA_SKILLS:
            self.assertIn(f"`{rel}`", body)
            self.assertTrue((ROOT / rel).is_file())
        self.assertIn("一次走完", body)
        self.assertIn("new task", body)
        tracked = set(IDEA_SKILLS) | {"skills/general/research-os/playbooks/idea-discovery.md"}
        clean = mod.backtick_cascade_problems(
            "skills/general/research-os/playbooks/idea-discovery.md",
            body,
            ROOT,
            tracked | {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.md") if ".git" not in p.parts},
        )
        self.assertEqual(clean, [])

    def test_damaged_skill_path_fails(self):
        mod = load()
        rel = "skills/general/research-os/playbooks/idea-discovery.md"
        damaged = "读 `skills/idea-cycle/idea-discovery/SKILL.md` 与 `skills/idea-cycle/missing-leaf/SKILL.md`。\n"
        tracked = {
            rel,
            "skills/idea-cycle/idea-discovery/SKILL.md",
        }
        problems = mod.backtick_cascade_problems(rel, damaged, ROOT, tracked)
        self.assertTrue(any("missing-leaf" in p for p in problems))
        self.assertFalse(any("idea-discovery/SKILL.md" in p and "missing" not in p for p in problems))


if __name__ == "__main__":
    unittest.main()
