"""#49 研究委托合同与最小单入口。

期望来自 #48 spec 与 #49 票面，不从被测脚本反读。
默认结构 scope 不允许任何失败；历史身份严格 scope 另报未验证。
"""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree
from spec48_checker_result import parse_checker_result

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
ENTRY = ROOT / "skills/general/research-os/SKILL.md"
MANDATE = ROOT / "skills/general/research-os/references/mandate.md"
BOUNDARY = ROOT / "skills/general/research-os/references/migration-boundary.md"
LEAF = ROOT / "skills/idea-cycle/research-lit/SKILL.md"
PLAYBOOK = ROOT / "skills/general/research-os/playbooks/literature-review.md"
SKILLS = ROOT / "skills"

MANDATE_SECTIONS = ("目标", "权限", "研究额度", "完成与停止")
README_LIST = re.compile(r"\]\((?:skills/)?([a-z-]+/[a-z0-9-]+)/SKILL\.md\)")


def load():
    spec = importlib.util.spec_from_file_location("check_skills_t49", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discovered() -> set[str]:
    return {f"{p.parent.parent.name}/{p.parent.name}" for p in SKILLS.glob("*/*/SKILL.md")}


def problem_lines(root: Path) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return parse_checker_result(result)


def fresh_problems(root: Path) -> list[str]:
    return problem_lines(root)


def heading_set(text: str) -> set[str]:
    return {match.group(1).strip() for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, re.M)}


SKILL_TEMPLATE = (
    "---\nname: new-capability\ndescription: \"临时能力。\"\n"
    "disable-model-invocation: true\n---\n\n# New\n\nGates: none\n"
)


def add_skill(root: Path, listed: bool) -> Path:
    """在副本里加一个未登记迁移状态的新 Skill；listed 决定是否同步 README 清单。"""
    new_dir = root / "skills/idea-cycle/new-capability"
    (new_dir / "agents").mkdir(parents=True)
    (new_dir / "SKILL.md").write_text(SKILL_TEMPLATE, encoding="utf-8")
    (new_dir / "agents/openai.yaml").write_text(
        'name: "new-capability"\nallow_implicit_invocation: false\n', encoding="utf-8"
    )
    (new_dir / "LICENSE").write_text("MIT\n", encoding="utf-8")
    if listed:
        for name in ("README.md", "skills/README.md"):
            path = root / name
            path.write_text(
                path.read_text(encoding="utf-8")
                + "\n- [new-capability](skills/idea-cycle/new-capability/SKILL.md)\n",
                encoding="utf-8",
            )
    return new_dir


class WorkCopy:
    """可损坏副本：git 初始化后即等价于已追踪工作区。"""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "repo"
        copy_tracked_tree(ROOT, self.path)
        for command in (
            ["git", "init"],
            ["git", "add", "-f", "."],
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base"],
        ):
            subprocess.run(command, cwd=self.path, check=True, capture_output=True)

    def __enter__(self) -> "WorkCopy":
        return self

    def __exit__(self, *_exc) -> None:
        self._tmp.cleanup()

    def stage(self) -> None:
        subprocess.run(["git", "add", "-A"], cwd=self.path, check=True, capture_output=True)


class ContractText(unittest.TestCase):
    def test_mandate_states_goal_permission_quota_and_stop(self):
        text = MANDATE.read_text(encoding="utf-8")
        headings = heading_set(text)
        for section in MANDATE_SECTIONS:
            self.assertIn(section, headings, f"委托合同缺「{section}」")
        for clause in ("目标替换", "只读", "独立调用", "有界首轮"):
            self.assertIn(clause, text, clause)

    def test_entry_points_at_mandate_and_keeps_readonly_and_host_map(self):
        text = ENTRY.read_text(encoding="utf-8")
        self.assertIn("references/mandate.md", text)
        for kept in ("当前命中路线是 route-only", "blocked", "保留编号、原句及子列表"):
            self.assertIn(kept, text, kept)

        def check_writing_routes(router):
            rows = [
                [cell.strip() for cell in line.strip("|").split("|")]
                for line in router.splitlines()
                if line.startswith("| paper-writing |")
            ]
            self.assertEqual(len(rows), 3)
            self.assertEqual({row[1] for row in rows}, {"general", "ml", "systems"})
            for row in rows:
                self.assertEqual(row[5], f"[paper-writing-{row[1]}](playbooks/paper-writing-{row[1]}.md)")
                playbook = ENTRY.parent / f"playbooks/paper-writing-{row[1]}.md"
                body = playbook.read_text(encoding="utf-8")
                self.assertIn("`skills/writing-cycle/paper-writing/SKILL.md`", body)
                for target in re.findall(r"`(skills/[^`]+)`", body):
                    self.assertTrue((ROOT / target).is_file(), target)
                for retired in ("ml-paper-writing", "systems-paper-writing"):
                    self.assertNotIn(f"writing-cycle/{retired}/", body)
                    self.assertNotIn(f"| {retired} |", router)

        check_writing_routes(text)
        # Losing a professional branch or restoring an old controller must fail,
        # even when the prose still says writing has a unified entry.
        for variant in ("ml", "systems"):
            with self.subTest(missing_or_legacy_branch=variant):
                with self.assertRaises(AssertionError):
                    check_writing_routes(text.replace(f"| paper-writing | {variant} |", f"| {variant}-paper-writing | {variant} |"))

        readonly = text.split("## 只读优先", 1)[1].split("\n## ", 1)[0]
        for constraint in ("route-only", "不创建任务", "不联网", "不写文件", "不派子代理"):
            self.assertIn(constraint, readonly)
        host_map = text.split("## 宿主映射", 1)[1].split("\n## ", 1)[0]
        for command in ("/skill:research-os", "/research-os", "$research-os"):
            self.assertIn(command, host_map)
        for host, location in (("pi", ".agents/skills/"), ("Claude Code", ".claude/skills/"), ("Codex", ".agents/skills/")):
            row = next(line for line in host_map.splitlines() if line.startswith(f"| {host} |"))
            self.assertIn(location, row)

    def test_mandate_counts_user_stop_as_stop_not_completion(self):
        text = MANDATE.read_text(encoding="utf-8")
        section = text.split("## 完成与停止", 1)[1].split("\n## ", 1)[0]
        lines = [line for line in section.splitlines() if line.strip()]
        done = next(line for line in lines if line.startswith("- **完成**"))
        stop = next(line for line in lines if line.startswith("- **停止**"))
        self.assertNotIn("用户叫停", done, done)
        self.assertIn("用户叫停", stop, stop)
        for line in lines:
            if "用户叫停" in line:
                self.assertIn("停止", line, line)
        self.assertIn("子代理", text)
        self.assertIn("blocked", text)

    def test_proof_repair_uses_migrated_delegation_contract(self):
        # #55 已迁移 proof-repair；旧 Gate 断言与委托继承合同冲突。
        repair = (SKILLS / "validation-cycle/proof-repair/SKILL.md").read_text(encoding="utf-8")
        rel = "skills/validation-cycle/proof-repair/SKILL.md"
        checker = load()
        self.assertIn("## 委托继承", repair)
        self.assertRegex(repair, r"(?m)^Gates: none$")
        self.assertNotRegex(repair, r"(?m)^Gate:")
        self.assertEqual(checker.MIGRATED_CONTRACT.get(rel), "委托继承")
        self.assertNotIn(rel, checker.LEGACY_LEAF_GATES)


class NoSubagentCapability(unittest.TestCase):
    """Spec #48 ID16：子代理是支持前提，缺该能力如实 blocked，不引入串行伪降级。"""

    def test_entry_blocks_delegation_without_subagent_capability(self):
        module = load()
        text = ENTRY.read_text(encoding="utf-8")
        self.assertIn("子代理", text)
        self.assertIn("blocked", text)
        self.assertIn("独立调用", text)
        self.assertEqual(module.host_capability_problems(text), [])
        for snippet in module.HOST_SERIAL_SUBSTITUTES:
            self.assertNotIn(snippet, text, snippet)

    def test_entry_drops_serial_stage_execution_promises(self):
        text = ENTRY.read_text(encoding="utf-8")
        for snippet in (
            "无该工具时由编排者串行执行",
            "编排者按 playbook 顺序自己执行",
            "由编排者串行完成这些读取与步骤",
            "请求用户确认串行回退",
            "无 fresh 能力时串行完成可执行阶段",
        ):
            self.assertNotIn(snippet, text, snippet)

    def test_literature_playbook_blocks_instead_of_serial_stepping(self):
        text = PLAYBOOK.read_text(encoding="utf-8")
        self.assertIn("blocked", text)
        self.assertIn("子代理", text)
        self.assertIn("research-lit", text)
        for snippet in ("没有时由编排者串行完成同一合同", "由编排者串行完成同一合同"):
            self.assertNotIn(snippet, text, snippet)

    def test_host_check_is_capability_based_not_brand_pinned(self):
        module = load()
        neutral = (
            "当前会话有子代理工具时按 playbook 分派；没有时该步骤标 blocked，"
            "入口只给只读建议，底层能力仍可独立调用。\n"
        )
        self.assertEqual(module.host_capability_problems(neutral), [])
        for snippet in module.HOST_SERIAL_SUBSTITUTES:
            self.assertTrue(module.host_capability_problems(neutral + f"{snippet}。\n"), snippet)
        self.assertTrue(module.host_capability_problems("| pi | .agents/skills | herdr_spawn_agent | session |\n"))


class MigrationBoundary(unittest.TestCase):
    def test_migrated_and_legacy_sets_partition_the_suite(self):
        module = load()
        migrated = set(module.MIGRATED_CONTRACT)
        legacy = set(module.LEGACY_LEAF_GATES)
        entry = "skills/general/research-os/SKILL.md"
        setup = "skills/general/setup-research-os/SKILL.md"
        leaves = {f"skills/{name}/SKILL.md" for name in discovered()}
        self.assertEqual(migrated | legacy, leaves - {setup}, "每个叶必须登记为已迁移或未迁移")
        self.assertIn(entry, migrated)
        self.assertNotIn(setup, migrated | legacy)
        self.assertEqual(migrated & legacy, set())

    def test_boundary_doc_lists_migrated_skills_and_legacy_remainder(self):
        text = BOUNDARY.read_text(encoding="utf-8")
        module = load()
        for rel in module.MIGRATED_CONTRACT:
            self.assertIn(Path(rel).parent.name, text, rel)
        self.assertIn("未迁移", heading_set(text))
        self.assertIn("LEGACY_LEAF_GATES", text)

    def test_migrated_skills_follow_inheritance_contract(self):
        entry = ENTRY.read_text(encoding="utf-8")
        leaf = LEAF.read_text(encoding="utf-8")
        self.assertRegex(entry, r"(?m)^Gates: none$")
        self.assertRegex(leaf, r"(?m)^Gates: none$")
        self.assertNotRegex(leaf, r"(?m)^Gate: ")
        self.assertIn("委托继承", heading_set(leaf))
        self.assertIn("研究委托", heading_set(entry))


class CompletePath(unittest.TestCase):
    def test_route_row_links_playbook_and_is_a_release_route(self):
        module = load()
        text = ENTRY.read_text(encoding="utf-8")
        rows, errors = module.parse_route_table(text)
        self.assertEqual(errors, [])
        self.assertIn(("literature", "—", "no"), {(row["路线"], row["变体"], row["只读约束"]) for row in rows})
        self.assertEqual(module.release_route_problems(rows), [])
        self.assertTrue(PLAYBOOK.is_file())

    def test_playbook_enters_existing_capability_then_accepts_artifacts(self):
        text = PLAYBOOK.read_text(encoding="utf-8")
        self.assertIn("skills/idea-cycle/research-lit/SKILL.md", text)
        for clause in ("验收", "实际产物", "目标替换", "有界首轮"):
            self.assertIn(clause, text, clause)
        self.assertIsNone(re.search(r"等待批准|批准后再执行|需再次确认", text), text)


class CounterRelationship(unittest.TestCase):
    def test_no_fixed_skill_count_and_manifests_match_discovery(self):
        self.assertNotIn("EXPECTED_COUNT", CHECK.read_text(encoding="utf-8"))
        actual = discovered()
        for name in ("README.md", "skills/README.md"):
            listed = set(README_LIST.findall((ROOT / name).read_text(encoding="utf-8")))
            self.assertEqual(listed, actual, name)

    def test_current_tree_has_no_new_breakage(self):
        self.assertEqual(fresh_problems(ROOT), [])

    def test_unlisted_new_skill_is_red(self):
        with WorkCopy() as work:
            add_skill(work.path, listed=False)
            work.stage()
            self.assertIn("清单缺", "\n".join(problem_lines(work.path)))

    def test_registered_but_unclassified_skill_is_red(self):
        with WorkCopy() as work:
            add_skill(work.path, listed=True)
            work.stage()
            self.assertIn("缺少门声明基线", "\n".join(problem_lines(work.path)))

    def test_migrated_skill_regaining_a_gate_is_red(self):
        with WorkCopy() as work:
            leaf = work.path / LEAF.relative_to(ROOT)
            leaf.write_text(
                leaf.read_text(encoding="utf-8").replace(
                    "Gates: none",
                    "Gate: write-path | before=report-write | approval=explicit-user "
                    "| source=SKILL.md#scope-and-authorization",
                    1,
                ),
                encoding="utf-8",
            )
            work.stage()
            blob = "\n".join(problem_lines(work.path))
            self.assertIn("research-lit", blob)

    def test_dropped_mandate_section_is_red(self):
        with WorkCopy() as work:
            mandate = work.path / MANDATE.relative_to(ROOT)
            mandate.write_text(
                mandate.read_text(encoding="utf-8").replace("## 研究额度", "## Quota", 1),
                encoding="utf-8",
            )
            work.stage()
            self.assertIn("研究额度", "\n".join(problem_lines(work.path)))

    def test_boundary_doc_without_migrated_skill_is_red(self):
        with WorkCopy() as work:
            boundary = work.path / BOUNDARY.relative_to(ROOT)
            boundary.write_text(
                boundary.read_text(encoding="utf-8").replace("research-lit", "文献能力", 1),
                encoding="utf-8",
            )
            work.stage()
            self.assertIn("research-lit", "\n".join(problem_lines(work.path)))


class FlatInstall(unittest.TestCase):
    """可丢弃目录的扁平安装：入口与代表能力可发现、可读取、共置资源可达。"""

    def test_entry_and_leaf_survive_flat_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("general/research-os", "idea-cycle/research-lit"):
                shutil.copytree(SKILLS / name, root / Path(name).name)
            entry = (root / "research-os/SKILL.md").read_text(encoding="utf-8")
            leaf_dir = root / "research-lit"
            leaf = (leaf_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("literature-review", entry)
            self.assertIn("references/mandate.md", entry)
            for rel in ("references/mandate.md", "references/migration-boundary.md",
                        "playbooks/literature-review.md"):
                self.assertTrue((root / "research-os" / rel).is_file(), rel)
            self.assertTrue((leaf_dir / "references/source-verification.md").is_file())
            self.assertTrue((leaf_dir / "references/source-methods.md").is_file())
            self.assertTrue((leaf_dir / "templates/literature-report.md").is_file())
            link = re.findall(r"\[source verification\]\(([^)]+)\)", leaf)
            self.assertEqual(len(link), 1)
            self.assertTrue((leaf_dir / link[0].split("#")[0]).is_file())

    def test_playbook_pointers_map_to_flat_layout(self):
        text = PLAYBOOK.read_text(encoding="utf-8")
        targets = set(re.findall(r"`(skills/[\w-]+/[\w-]+/SKILL\.md)`", text))
        self.assertIn("skills/idea-cycle/research-lit/SKILL.md", targets)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for target in targets:
                parts = Path(target).parts
                skill = parts[-2]
                copy = root / skill
                if not copy.exists():
                    shutil.copytree(SKILLS / parts[1] / skill, copy)
                self.assertTrue((copy / "SKILL.md").is_file(), target)


if __name__ == "__main__":
    unittest.main()
