"""#59：持续推进、暂停恢复与项目流程改进的合同。

期望来自 #48 spec 的持续执行、额度、暂停恢复与过程改进决策，以及 #59 票面。
测试只验证可安装文本合同与 checker 登记，不验证模型能真实推进科研。
"""
import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "skills/general/research-os/SKILL.md"
CONTINUATION = ROOT / "skills/general/research-os/playbooks/continuation.md"
IMPROVEMENT = ROOT / "skills/general/research-os/playbooks/improvement.md"
PICKUP = ROOT / "skills/general/research-os/playbooks/pickup.md"
IMPROVEMENT_SKILL = ROOT / "skills/writing-cycle/research-improvement/SKILL.md"
IMPROVEMENT_LOG = ROOT / (
    "skills/writing-cycle/research-improvement/templates/improvement-log.md"
)
BOUNDARY = ROOT / "skills/general/research-os/references/migration-boundary.md"
DEPENDENCIES = ROOT / "skills/writing-cycle/research-improvement/references/dependencies.md"
CHECK = ROOT / "scripts/check-skills.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_skills_t59", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContinuationRoute(unittest.TestCase):
    def test_entry_routes_continuation_without_host_background_promise(self):
        module = load_checker()
        text = ENTRY.read_text(encoding="utf-8")
        rows, parse_errors = module.parse_route_table(text)
        self.assertEqual(parse_errors, [])
        self.assertIn(("continuation", "—"), {(r["路线"], r["变体"]) for r in rows})
        self.assertTrue(CONTINUATION.is_file())
        self.assertNotIn("已命名、文件未交付：continuation", text)
        self.assertNotIn("`/loop`", CONTINUATION.read_text(encoding="utf-8"))

    def test_continuation_playbook_binds_goal_quota_and_safe_pause(self):
        text = CONTINUATION.read_text(encoding="utf-8")
        for marker in (
            "references/mandate.md",
            "可核验收束条件",
            "wall-clock",
            "同一条额度",
            "暂停保存",
            "[pickup](pickup.md)",
            "[improvement](improvement.md)",
            "不把 Skill 文本当后台服务",
            "停滞",
            "真正死路",
        ):
            self.assertIn(marker, text, marker)
        self.assertIn("references/batch-authorization.md", text)


class ResumeContract(unittest.TestCase):
    def test_pickup_restores_target_authorization_evidence_obligations_jobs(self):
        text = PICKUP.read_text(encoding="utf-8")
        for marker in (
            "恢复目标",
            "授权",
            "原始产物",
            "开放义务",
            "活跃作业",
            "旧总结",
            "不延长 `valid_until`",
        ):
            self.assertIn(marker, text, marker)
        self.assertIn("已完成的轮次", text)


class ImprovementMigration(unittest.TestCase):
    def test_research_improvement_inherits_mandate_not_repeated_gate(self):
        text = IMPROVEMENT_SKILL.read_text(encoding="utf-8")
        self.assertNotIn("Gate: loop-authorization", text)
        self.assertNotIn("等待用户明确确认", text)
        self.assertNotIn("逐项列出并等待用户", text)
        self.assertIn("## 委托继承", text)
        for marker in (
            "research-os` 的委托合同",
            "不要求用户再次批准已授权的普通步骤",
            "目标替换",
            "有界首轮",
            "wall-clock",
            "批次授权",
            "公共套件行为",
            "外部 tracker",
        ):
            self.assertIn(marker, text, marker)

    def test_improvement_playbook_uses_delegate_contract_and_cumulative_quota(self):
        text = IMPROVEMENT.read_text(encoding="utf-8")
        self.assertIn("references/mandate.md", text)
        self.assertIn("references/batch-authorization.md", text)
        self.assertNotIn("loop-authorization 门", text)
        self.assertNotIn("experiment-topup 门", text)
        self.assertIn("wall-clock", text)
        self.assertIn("已消耗", text)
        self.assertIn("失败、超时、无效", text)

    def test_improvement_log_records_process_tools_and_public_change_gate(self):
        skill = IMPROVEMENT_SKILL.read_text(encoding="utf-8")
        log = IMPROVEMENT_LOG.read_text(encoding="utf-8")
        for marker in ("流程与工具改进", "公共套件行为", "外部 tracker"):
            self.assertIn(marker, skill, marker)
        for marker in ("流程/工具改进", "公共套件行为", "外部 tracker"):
            self.assertIn(marker, log, marker)

    def test_independent_install_declares_and_resolves_cross_skill_dependencies(self):
        text = DEPENDENCIES.read_text(encoding="utf-8")
        for marker in (
            "mandate.md",
            "batch-authorization.md",
            "<skills-root>/research-os/",
            "composition-map.md",
            "实际存在且可读",
            "blocked",
        ):
            self.assertIn(marker, text, marker)


class CheckerRegistration(unittest.TestCase):
    def test_research_improvement_is_registered_as_migrated(self):
        module = load_checker()
        rel = "skills/writing-cycle/research-improvement/SKILL.md"
        self.assertEqual(module.MIGRATED_CONTRACT.get(rel), "委托继承")
        self.assertNotIn(rel, module.LEGACY_LEAF_GATES)
        boundary = BOUNDARY.read_text(encoding="utf-8")
        self.assertIn("research-improvement", boundary)
        self.assertIn("委托继承", boundary)

    def test_continuation_checker_reports_missing_assets_and_contract_drift(self):
        module = load_checker()
        self.assertTrue(hasattr(module, "continuation_contract_problems"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            problems = module.continuation_contract_problems(root, set())
        joined = "\\n".join(problems)
        for marker in (
            "持续执行配方不存在",
            "NOTICE.md: 来源说明不存在",
            "UPSTREAM-LICENSE.md: 许可证不存在",
        ):
            self.assertIn(marker, joined, marker)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            playbook = root / "skills/general/research-os/playbooks/continuation.md"
            playbook.parent.mkdir(parents=True)
            playbook.write_text("blocked\\n", encoding="utf-8")
            notice = root / "skills/writing-cycle/research-improvement/NOTICE.md"
            notice.parent.mkdir(parents=True)
            notice.write_text("partial source attribution", encoding="utf-8")
            problems = module.continuation_contract_problems(
                root,
                {"skills/general/research-os/playbooks/continuation.md",
                 "skills/writing-cycle/research-improvement/NOTICE.md"},
            )
        joined = "\\n".join(problems)
        self.assertIn("NOTICE.md: 缺来源记录 cursor/plugins", joined)
        self.assertIn("UPSTREAM-LICENSE.md: 许可证不存在", joined)
        self.assertIn("dependencies.md: 安装依赖映射不存在", joined)

    def test_continuation_checker_rejects_missing_quota_and_host_neutrality(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            playbook = root / "skills/general/research-os/playbooks/continuation.md"
            playbook.parent.mkdir(parents=True)
            playbook.write_text("持续执行配方 ~/.cursor /loop blocked\\n", encoding="utf-8")
            problems = module.continuation_contract_problems(root, set())
        self.assertTrue(any("缺「wall-clock」" in problem for problem in problems))
        self.assertTrue(any("宿主绑定残留" in problem for problem in problems))


class InstalledLayout(unittest.TestCase):
    def test_cross_skill_links_are_declared_as_install_dependencies(self):
        package = IMPROVEMENT_SKILL.parent
        dependency_map = DEPENDENCIES.read_text(encoding="utf-8")
        for markdown in package.rglob("*.md"):
            for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)", markdown.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                local_target = target.split("#", 1)[0]
                if not local_target:
                    continue
                resolved = (markdown.parent / local_target).resolve()
                if resolved.is_relative_to(package.resolve()):
                    self.assertTrue(resolved.is_file(), f"{markdown}: {target}")
                else:
                    installed_root = next(
                        (parent for parent in resolved.parents if (parent / "SKILL.md").is_file()),
                        None,
                    )
                    if installed_root is None:
                        self.fail(f"unresolved skill dependency: {markdown}: {target}")
                    self.assertTrue(
                        any(f"<skills-root>/{installed_root.name}/" in line
                            for line in dependency_map.splitlines()),
                        f"undeclared dependency: {markdown}: {target}",
                    )

    def test_required_resources_are_co_located(self):
        for path in (
            CONTINUATION,
            IMPROVEMENT,
            PICKUP,
            IMPROVEMENT_SKILL,
            IMPROVEMENT_LOG,
            ROOT / "skills/writing-cycle/research-improvement/NOTICE.md",
            ROOT / "skills/writing-cycle/research-improvement/UPSTREAM-LICENSE.md",
            DEPENDENCIES,
        ):
            self.assertTrue(path.is_file(), path)


if __name__ == "__main__":
    unittest.main()
