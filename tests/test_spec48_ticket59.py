"""#59：持续推进、暂停恢复与项目流程改进的合同。

期望来自 #48 spec 的持续执行、额度、暂停恢复与过程改进决策，以及 #59 票面。
测试只验证可安装文本合同与 checker 登记，不验证模型能真实推进科研。
"""
import importlib.util
import re
import shutil
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
LOOP_METHODS = ROOT / "skills/writing-cycle/research-improvement/references/loop-methods.md"
COMPOSITION = ROOT / "skills/writing-cycle/research-improvement/references/composition-map.md"
LICENSE = ROOT / "skills/writing-cycle/research-improvement/UPSTREAM-LICENSE.md"
IMPROVEMENT_NOTICE = ROOT / "skills/writing-cycle/research-improvement/NOTICE.md"
ENTRY_NOTICE = ROOT / "skills/general/research-os/NOTICE-PSTACK.md"
ENTRY_LICENSE = ROOT / "skills/general/research-os/LICENSE-PSTACK"

CONTRACT_FILES = (
    CONTINUATION,
    PICKUP,
    IMPROVEMENT_SKILL,
    DEPENDENCIES,
    LOOP_METHODS,
    COMPOSITION,
    LICENSE,
    IMPROVEMENT_NOTICE,
    ENTRY_NOTICE,
    ENTRY_LICENSE,
)


def copy_contract_fixture(root: Path) -> set[str]:
    """Copy the #59 contract and all dependency-map targets to an isolated fixture."""
    files = {path.relative_to(ROOT).as_posix() for path in CONTRACT_FILES}
    dependency_text = DEPENDENCIES.read_text(encoding="utf-8")
    files.update(re.findall(r"^\|\s*[^|]+\|\s*`(skills/[^`]+)`", dependency_text, re.M))
    pickup_text = PICKUP.read_text(encoding="utf-8")
    files.update(re.findall(r"`(skills/[^`]+)`", pickup_text))
    for relative in files:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return files


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

    def test_unconfigured_nonpaid_resume_is_allowed_but_job_branches_need_setup(self):
        text = PICKUP.read_text(encoding="utf-8")
        self.assertIn("普通研究恢复不要求 setup-research-os", text)
        self.assertIn("仅进入作业、费用或资源批次时", text)
        self.assertIn("不要求恢复会话另有本轮批准清单", text)
        self.assertNotIn("user_confirmation", text)
        dependencies = DEPENDENCIES.read_text(encoding="utf-8")
        self.assertIn("仅作业/费用批次分支依赖", dependencies)
        self.assertIn(
            "<skills-root>/setup-research-os/templates/compute-policy.md",
            dependencies,
        )
        self.assertIn(
            "<skills-root>/setup-research-os/templates/research-log.md",
            dependencies,
        )


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

    def test_direct_invocation_and_delegated_inheritance_are_distinct(self):
        text = IMPROVEMENT_SKILL.read_text(encoding="utf-8")
        self.assertIn("独立显式调用本能力时", text)
        self.assertIn("由已授权的 research-os 委托级联时", text)
        self.assertIn("只核对原委托的最大轮数、当前轮次、剩余额度与写域", text)
        self.assertNotIn("没有任何未经再次确认的新轮次", text)
        pickup = PICKUP.read_text(encoding="utf-8")
        self.assertIn("原委托来源", pickup)
        self.assertIn("剩余额度", pickup)
        composition = COMPOSITION.read_text(encoding="utf-8")
        self.assertIn("已迁移能力不要求另行点名", composition)
        self.assertIn("未迁移叶仍执行其自身门", composition)

    def test_unavailable_reviewer_blocks_the_review_repair_round(self):
        for path in (IMPROVEMENT_SKILL, LOOP_METHODS, DEPENDENCIES):
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("reviewer 不可用", text)
                self.assertIn("blocked", text)
                self.assertIn("只读自查", text)
                self.assertIn("不计为 fresh 独立审查", text)
        self.assertIn(
            "不得降级为单执行者评估后将本轮记为完成",
            LOOP_METHODS.read_text(encoding="utf-8"),
        )

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

    def test_checker_rejects_missing_entry_package_pstack_assets(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracked = copy_contract_fixture(root)
            (root / ENTRY_LICENSE.relative_to(ROOT)).unlink()
            (root / ENTRY_NOTICE.relative_to(ROOT)).unlink()
            problems = module.continuation_contract_problems(root, tracked)
        joined = "\n".join(problems)
        self.assertIn("LICENSE-PSTACK: 许可证不存在", joined)
        self.assertIn("NOTICE-PSTACK.md: 来源说明不存在", joined)

    def test_entry_package_license_is_complete_and_byte_identical(self):
        module = load_checker()
        entry_license_rel = ENTRY_LICENSE.relative_to(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracked = copy_contract_fixture(root)
            entry_license = root / entry_license_rel
            source_license = root / LICENSE.relative_to(ROOT)
            self.assertEqual(entry_license.read_bytes(), source_license.read_bytes())
            self.assertEqual(module.continuation_contract_problems(root, tracked), [])

            # Truncate the shipped copy: marker-only checks must not accept it.
            entry_license.write_bytes(entry_license.read_bytes()[:-1])
            problems = module.continuation_contract_problems(root, tracked)
            joined = "\n".join(problems)
            self.assertIn("完整 pstack MIT 字节不一致", joined)
            self.assertIn("research-improvement 上游 MIT 字节不一致", joined)

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

    def test_ticket59_contract_checker_catches_reported_semantic_mutants(self):
        module = load_checker()
        self.assertTrue(hasattr(module, "ticket59_contract_problems"))
        mutations = (
            (
                CONTINUATION.relative_to(ROOT).as_posix(),
                "不重置；未知消耗保留预留，不按 0 释放。",
                "恢复时从零重置；未知消耗按 0 释放。",
                "未知消耗保留预留",
            ),
            (
                PICKUP.relative_to(ROOT).as_posix(),
                "必须回到**原始产物**和原始命令核对，旧总结的成功标签不能直接当事实。",
                "无需回到**原始产物**和原始命令核对，旧总结的成功标签可以直接当事实。",
                "原始产物",
            ),
            (
                IMPROVEMENT_SKILL.relative_to(ROOT).as_posix(),
                "先展示拟改内容并等用户确认",
                "自动修改公共套件并创建外部 tracker，无需用户确认。",
                "先展示拟改内容",
            ),
            (
                LICENSE.relative_to(ROOT).as_posix(),
                LICENSE.read_text(encoding="utf-8"),
                "MIT License\n\nCopyright (c) 2026 Lauren Tan\n",
                "许可证",
            ),
            (
                DEPENDENCIES.relative_to(ROOT).as_posix(),
                "<skills-root>/paper-compile/SKILL.md",
                "<skills-root>/missing-paper-compile/SKILL.md",
                "paper-compile",
            ),
        )
        for relative, before, after, expected in mutations:
            with self.subTest(mutant=expected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                tracked = copy_contract_fixture(root)
                target = root / relative
                text = target.read_text(encoding="utf-8")
                self.assertIn(before, text)
                target.write_text(text.replace(before, after), encoding="utf-8")
                problems = module.ticket59_contract_problems(root, tracked)
                self.assertIn(expected, "\n".join(problems))

    def test_ticket59_contract_checker_accepts_complete_contract_fixture(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracked = copy_contract_fixture(root)
            self.assertEqual(module.ticket59_contract_problems(root, tracked), [])

    def test_ticket59_contract_checker_rejects_reintroduced_conflicts(self):
        module = load_checker()
        conflicts = (
            (
                IMPROVEMENT_SKILL.relative_to(ROOT).as_posix(),
                "没有任何未经再次确认的新轮次",
            ),
            (
                PICKUP.relative_to(ROOT).as_posix(),
                "文件不存在就停",
            ),
            (
                LOOP_METHODS.relative_to(ROOT).as_posix(),
                "审查者不可用或独立性无法建立时，标 `independent review not performed` 并降级为单执行者评估",
            ),
            (
                COMPOSITION.relative_to(ROOT).as_posix(),
                "以下均为 user-invoked，只能由用户另行显式调用",
            ),
        )
        for relative, obsolete_clause in conflicts:
            with self.subTest(clause=obsolete_clause), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                tracked = copy_contract_fixture(root)
                target = root / relative
                target.write_text(
                    target.read_text(encoding="utf-8") + f"\n\n{obsolete_clause}\n",
                    encoding="utf-8",
                )
                problems = module.ticket59_contract_problems(root, tracked)
                self.assertIn(obsolete_clause, "\n".join(problems))


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
