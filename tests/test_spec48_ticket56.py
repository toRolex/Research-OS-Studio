"""#56 授权内实验执行与远程执行位置。

期望来自 #48 spec（Implementation 8、9、13–17；Testing 8）与 #56 票面。
默认结构 scope 不允许任何失败；历史身份严格 scope 另报未验证。
"""
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree
from spec48_checker_result import parse_checker_result

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
BASE = ROOT / "skills" / "validation-cycle"
EXPERIMENT_SKILLS = (
    "experiment-plan",
    "run-experiment",
    "experiment-queue",
    "monitor-experiment",
    "training-health-check",
    "analyze-results",
    "experiment-audit",
    "result-to-claim",
)
RUN = BASE / "run-experiment"
QUEUE = BASE / "experiment-queue"
BOUNDARY = ROOT / "skills/general/research-os/references/migration-boundary.md"
BRIDGE_PLAYBOOK = ROOT / "skills/general/research-os/playbooks/experiment-bridge.md"
UPSTREAM = ROOT / "docs/upstream-sources-and-licenses.md"

MODEL_PIN = re.compile(
    r"(?i)(gpt-[0-9]|claude-[0-9]|gemini-[0-9]|grok-[0-9]|deepseek-[a-z0-9]|glm-[0-9]|opus|sonnet)"
)
HOST_BINDINGS = ("Cursor", "~/.cursor", ".cursor/", "pstack-models", "/loop")


def load():
    spec = importlib.util.spec_from_file_location("check_skills_t56", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def problem_lines(root: Path) -> list[str]:
    root_dir = root.path if hasattr(root, "path") else root
    result = subprocess.run(
        [sys.executable, str(root_dir / "scripts/check-skills.py")],
        cwd=root_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return parse_checker_result(result)


def fresh_problems(root: Path) -> list[str]:
    return problem_lines(root)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class WorkCopy:
    """可损坏副本；git init 后让 checker 的追踪文件检查可运行。"""

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


class OwnershipAndMandate(unittest.TestCase):
    def test_eight_experiment_skills_remain_separate(self):
        mod = load()
        for name in EXPERIMENT_SKILLS:
            skill_dir = BASE / name
            self.assertTrue((skill_dir / "SKILL.md").is_file(), name)
            self.assertTrue((skill_dir / "LICENSE").is_file(), name)
            self.assertTrue((skill_dir / "agents/openai.yaml").is_file(), name)
            self.assertIn(
                f"skills/validation-cycle/{name}/SKILL.md",
                mod.MIGRATED_CONTRACT,
                f"{name}: 未登记委托继承",
            )
            body = text(skill_dir / "SKILL.md")
            self.assertIn("## 委托继承", body, name)
            self.assertNotRegex(body, r"(?m)^Gate:", name)
            self.assertTrue(BOUNDARY.is_file() and name in text(BOUNDARY), name)
            self.assertIn(name, text(UPSTREAM), name)

    def test_bridge_recipe_is_not_an_installable_controller(self):
        run = text(RUN / "SKILL.md")
        playbook = text(BRIDGE_PLAYBOOK)
        self.assertFalse((BASE / "experiment-bridge/SKILL.md").exists())
        self.assertIn("skills/validation-cycle/run-experiment/SKILL.md", playbook)
        self.assertIn("唯一执行控制", playbook)
        self.assertNotIn("skills/validation-cycle/experiment-bridge/SKILL.md", playbook)
        self.assertNotRegex(playbook, r"(?m)^\s*/experiment-bridge\b")
        self.assertIn("是唯一实验执行控制", run)
        self.assertIn("小批量或队列", run)
        self.assertIn("仓库中的 `experiment-queue`", run)
        self.assertIn("单装 `run-experiment` 时", run)
        composition = text(RUN / "references/composition-map.md")
        self.assertIn("`monitor-experiment`", composition)
        self.assertIn("`analyze-results`", composition)
        self.assertIn("`experiment-audit`", composition)
        self.assertIn("只阻塞其自身职责", composition)


class ExecutionContract(unittest.TestCase):
    def test_run_records_full_job_contract(self):
        run = text(RUN / "SKILL.md")
        report = text(RUN / "templates/run-report.md")
        for phrase in (
            "输入版本", "工具链", "独立目录", "作业身份", "退出码", "原始日志", "产物",
        ):
            self.assertIn(phrase, run, phrase)
            self.assertIn(phrase, report, phrase)
        self.assertIn("references/execution-contract.md", run)
        self.assertTrue((RUN / "references/execution-contract.md").is_file())
        for relative in (
            "references/composition-map.md", "templates/run-report.md",
        ):
            self.assertTrue((RUN / relative).is_file(), relative)

    def test_queue_reuses_same_contract_and_has_recovery(self):
        queue = text(QUEUE / "SKILL.md")
        self.assertIn("不因进入队列或新波次重复索权", queue)
        self.assertIn("同一个 `research-log.md` 批次", queue)
        manifest = text(QUEUE / "templates/batch-manifest.md")
        for phrase in ("输入版本", "工具链", "独立目录", "作业身份", "退出码", "原始日志", "产物"):
            self.assertIn(phrase, queue, phrase)
            self.assertIn(phrase, manifest, phrase)
        for phrase in ("断线", "原作业", "不盲重跑", "旧文件", "作业退出", "产物有效", "科学结论"):
            self.assertIn(phrase, queue, phrase)
        run = text(RUN / "SKILL.md")
        for phrase in ("作业退出", "产物有效", "科学结论", "旧文件"):
            self.assertIn(phrase, run, phrase)

    def test_queue_completion_distinguishes_stale_failed_and_complete_attempts(self):
        queue = text(QUEUE / "SKILL.md")
        for case in (
            "只有同时满足以下条件才标 `completed`",
            "缺少作业身份或退出证据 → `unknown`",
            "上次遗留 `output.csv` + 本次 attempt 非零退出 → `failed_other`；旧文件不算本次产物",
            "本次 attempt 成功退出（退出码为 0）+ 身份关联且完整的预期产物 → `completed`",
            "成功退出但产物缺失、部分写入或完整性检查失败 → 不得标 `completed`",
            "会话清理仅在授权明确覆盖该清理动作时执行",
        ):
            self.assertIn(case, queue, case)
        self.assertNotIn("预期输出存在 → 标 `completed`", queue)

    def test_plan_does_not_force_training_baseline_on_math(self):
        plan = text(BASE / "experiment-plan/SKILL.md")
        self.assertIn("数学计算", plan)
        self.assertIn("不硬套训练 baseline", plan)
        self.assertIn("计划声明的对照", plan)


class RemoteAndRecovery(unittest.TestCase):
    def test_remote_is_execution_location_with_ssh_or_existing_scheduler(self):
        reference = text(RUN / "references/remote-execution.md")
        for phrase in (
            "远程只是执行位置", "SSH", "已有调度", "不新造执行引擎", "不锁定供应商",
            "凭据", "独立目录", "作业身份", "原作业",
        ):
            self.assertIn(phrase, reference, phrase)
        run = text(RUN / "SKILL.md")
        self.assertIn("远程只是执行位置", run)
        self.assertIn("SSH", run)
        self.assertIn("已有调度", run)

    def test_experiment_contract_is_host_neutral(self):
        for name in EXPERIMENT_SKILLS:
            body = text(BASE / name / "SKILL.md")
            for binding in HOST_BINDINGS:
                self.assertNotIn(binding, body, f"{name}: {binding}")
            self.assertIsNone(MODEL_PIN.search(body), name)


class UnifiedController(unittest.TestCase):
    def test_run_experiment_owns_batch_authorization_and_accounting(self):
        run = text(RUN / "SKILL.md")
        for phrase in (
            "research-log.md", "valid_until", "累计额度", "run_count_basis",
            "最坏预留", "本批已确认", "不按 milestone 重复索取",
        ):
            self.assertIn(phrase, run, phrase)
        self.assertNotIn("用户仍确认", run)
        self.assertNotIn("用户确认后才启动", run)

    def test_research_os_bridge_playbook_is_a_pointer_not_a_second_controller(self):
        playbook = text(BRIDGE_PLAYBOOK)
        self.assertIn("run-experiment", playbook)
        self.assertIn("只在用户委托要求时", playbook)
        self.assertIn("analyze-results", playbook)
        self.assertIn("experiment-audit", playbook)
        self.assertNotIn("run_count_basis=planned-run", playbook)
        self.assertNotIn("每个 attempt 先记最坏预留", playbook)
        self.assertIn("run_count_basis", text(RUN / "SKILL.md"))


class WorkflowRemediation(unittest.TestCase):
    def test_each_single_install_bundles_core_mandate_rules(self):
        authority = text(ROOT / "skills/general/research-os/references/mandate.md")
        required_files = {
            "experiment-plan": ("references/block-checks.md", "templates/experiment-plan.md"),
            "run-experiment": (
                "references/execution-contract.md", "references/remote-execution.md",
                "references/batch-authorization.md", "references/composition-map.md",
                "templates/run-report.md",
            ),
            "experiment-queue": ("templates/batch-manifest.md",),
            "monitor-experiment": (
                "references/observation-sources.md", "templates/run-status-report.md",
            ),
            "training-health-check": ("references/health-signals.md", "templates/health-report.md"),
            "analyze-results": ("references/statistical-checks.md", "templates/analysis-report.md"),
            "experiment-audit": ("references/integrity-checks.md", "templates/audit-report.md"),
            "result-to-claim": ("references/claim-judgment.md", "templates/claim-report.md"),
        }
        core_rules = (
            "叶能力、下一阶段或一次审查完成都不重置授权",
            "用户明确只要推荐、只审查、只规划或不要执行时，保持该范围",
            "越权、超额、未授权的破坏性动作",
            "项目内的依赖、工具与缓存可在授权内自动准备",
            "有界首轮",
            "并行、换线程、重试与恢复都消耗同一份额度，不重置",
            "用户叫停是停止，不是完成",
            "委托的验收看实际产物，不看执行者的自述",
            "额度、权限与目标互不推导",
        )
        reference_contract = None
        for name in EXPERIMENT_SKILLS:
            skill = BASE / name
            body = text(skill / "SKILL.md")
            bundled = skill / "references/mandate.md"
            self.assertTrue(bundled.is_file(), f"{name}: missing packaged mandate rules")
            contract = text(bundled)
            with self.subTest(skill=name):
                self.assertIn("references/mandate.md", body)
                for rel in required_files[name]:
                    self.assertTrue((skill / rel).is_file(), f"{name}: missing {rel}")
                if reference_contract is None:
                    reference_contract = contract
                else:
                    self.assertEqual(contract, reference_contract)
                for rule in core_rules:
                    self.assertIn(rule, authority, f"canonical mandate missing {rule}")
                    self.assertIn(rule, contract, f"{name}: packaged mandate missing {rule}")
                self.assertIn("不覆盖本叶以外的授权", contract)

    def test_cross_skill_references_declare_group_dependencies_and_blocking(self):
        dependencies = {
            "experiment-queue": ("run-experiment",),
            "result-to-claim": ("analyze-results",),
        }
        for name, companions in dependencies.items():
            body = text(BASE / name / "SKILL.md")
            with self.subTest(skill=name):
                self.assertTrue("## 联装能力依赖" in body, f"{name}: missing dependency section")
                section = body.split("## 联装能力依赖", 1)[1].split("\n## ", 1)[0]
                for companion in companions:
                    self.assertTrue(f"`{companion}`" in section, f"{name}: missing {companion}")
                self.assertTrue("缺失时标为 `blocked`" in section, f"{name}: missing blocked behavior")
                self.assertTrue("npx skills add <repo>" in section, f"{name}: missing install command")

    def test_authorized_new_outputs_do_not_request_redundant_path_confirmation(self):
        plan = text(BASE / "experiment-plan/SKILL.md")
        claim = text(BASE / "result-to-claim/SKILL.md")
        queue_template = text(
            BASE / "experiment-queue/templates/batch-manifest.md"
        )
        for name, body in (
            ("experiment-plan", plan),
            ("result-to-claim", claim),
            ("batch-manifest", queue_template),
        ):
            with self.subTest(document=name):
                for marker in ("已授权写域内", "新文件", "直接写", "写域不明", "覆盖既有成果"):
                    self.assertTrue(marker in body, f"{name}: missing {marker}")
        self.assertNotIn("提出具体路径并确认", plan)
        self.assertNotIn("提出具体路径并确认", claim)
        self.assertNotIn("实际执行前与用户确认", queue_template)

    def test_math_plan_never_inherits_training_baseline_gate(self):
        plan = text(BASE / "experiment-plan/SKILL.md")
        template = text(BASE / "experiment-plan/templates/experiment-plan.md")
        phase3 = plan.split("### Phase 3:", 1)[1].split("### Phase 4:", 1)[0]
        phase4 = plan.split("### Phase 4:", 1)[1].split("### Phase 5:", 1)[0]
        training = phase4.split("2. **Training branch", 1)[1].split(
            "3. **Math/non-training branch", 1
        )[0]
        math = phase4.split("3. **Math/non-training branch", 1)[1].split(
            "4. **Main method", 1
        )[0]
        self.assertIn("strongest baseline", training)
        self.assertIn("valid baseline", training)
        self.assertIn("same evaluation surface", training)
        self.assertIn("certificate", math.lower())
        self.assertIn("不要求训练 baseline", math)
        self.assertIn("数学/非训练", phase3)
        self.assertIn("training fields not applicable", phase3)
        self.assertIn("仅训练实验填写", template)
        self.assertIn("数学/非训练工作不要求训练 baseline", template)
        self.assertNotIn(
            "Sanity and valid baseline gate candidate runs",
            template,
            "the checklist must not impose the training-only gate on math work",
        )
        self.assertIn("Training-route candidate runs have valid same-surface baseline evidence", template)
        self.assertIn("without requiring a training baseline", template)


class CheckerContract(unittest.TestCase):
    def test_builtin_checker_registers_ticket56_contract(self):
        self.assertEqual(problem_lines(ROOT), [])
        self.assertEqual(fresh_problems(ROOT), [])

    def test_checker_accepts_equivalent_interruption_wording(self):
        with WorkCopy() as root:
            queue_path = root.path / QUEUE.relative_to(ROOT) / "SKILL.md"
            queue_path.write_text(
                queue_path.read_text(encoding="utf-8").replace("断线", "中断"),
                encoding="utf-8",
            )
            root.stage()
            self.assertEqual(fresh_problems(root), [])

    def test_checker_detects_blind_rerun_without_original_job_lookup(self):
        with WorkCopy() as root:
            queue_path = root.path / QUEUE.relative_to(ROOT) / "SKILL.md"
            lines = queue_path.read_text(encoding="utf-8").splitlines()
            lines = [
                "- **可恢复**：断线后直接创建新作业并盲重跑，不查询旧任务。旧文件、作业退出、产物有效和科学结论分别记录。"
                if line.startswith("- **可恢复**：") else line
                for line in lines
            ]
            queue_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            root.stage()
            problems = "\n".join(fresh_problems(root))
            self.assertIn("experiment-queue/SKILL.md", problems)
            self.assertIn("不盲重跑", problems)

    def test_checker_detects_missing_remote_contract(self):
        with WorkCopy() as root:
            run_path = root.path / RUN.relative_to(ROOT) / "SKILL.md"
            run_path.write_text(
                run_path.read_text(encoding="utf-8").replace("已有调度", "自建调度"),
                encoding="utf-8",
            )
            root.stage()
            self.assertIn("已有调度", "\n".join(fresh_problems(root)))

    def test_checker_detects_missing_remote_execution_resource(self):
        with WorkCopy() as root:
            remote_path = root.path / RUN.relative_to(ROOT) / "references/remote-execution.md"
            remote_path.unlink()
            root.stage()
            self.assertIn("缺少实验执行资产", "\n".join(fresh_problems(root)))

    def test_checker_detects_empty_remote_execution_contract(self):
        with WorkCopy() as root:
            remote_path = root.path / RUN.relative_to(ROOT) / "references/remote-execution.md"
            remote_path.write_text("# Remote Execution Position\n", encoding="utf-8")
            root.stage()
            self.assertIn(
                "remote-execution.md: 缺「远程只是执行位置」",
                "\n".join(fresh_problems(root)),
            )

    def test_checker_detects_missing_real_batch_authorization_marker(self):
        with WorkCopy() as root:
            auth_path = root.path / RUN.relative_to(ROOT) / "references/batch-authorization.md"
            auth_path.write_text(
                auth_path.read_text(encoding="utf-8").replace(
                    "run_count_basis: planned-run", "run_count_basis: attempt"
                ),
                encoding="utf-8",
            )
            root.stage()
            self.assertIn(
                "batch-authorization.md: 缺「run_count_basis: planned-run」",
                "\n".join(fresh_problems(root)),
            )

    def test_checker_detects_missing_batch_authorization_contract(self):
        with WorkCopy() as root:
            run_path = root.path / RUN.relative_to(ROOT) / "SKILL.md"
            run_path.write_text(
                run_path.read_text(encoding="utf-8").replace("valid_until", "expiry_time"),
                encoding="utf-8",
            )
            root.stage()
            self.assertIn("批次授权合同", "\n".join(fresh_problems(root)))

    def test_checker_detects_duplicate_bridge_authorization_controller(self):
        with WorkCopy() as root:
            playbook_path = root.path / BRIDGE_PLAYBOOK.relative_to(ROOT)
            playbook_path.write_text(
                playbook_path.read_text(encoding="utf-8") + "\nrun_count_basis=planned-run\n",
                encoding="utf-8",
            )
            root.stage()
            self.assertIn("桥接 playbook 重复执行控制合同", "\n".join(fresh_problems(root)))

    def test_checker_detects_dead_experiment_plan_fragment(self):
        with WorkCopy() as root:
            plan_path = root.path / (BASE / "experiment-plan/SKILL.md").relative_to(ROOT)
            plan_path.write_text(
                plan_path.read_text(encoding="utf-8").replace(
                    "#委托继承", "#missing-authorization-anchor"
                ),
                encoding="utf-8",
            )
            root.stage()
            self.assertIn("无效 Markdown fragment", "\n".join(fresh_problems(root)))

    def test_checker_detects_missing_packaged_mandate_resource(self):
        with WorkCopy() as root:
            mandate_path = root.path / (
                BASE / "experiment-plan/references/mandate.md"
            ).relative_to(ROOT)
            mandate_path.unlink()
            root.stage()
            self.assertIn(
                "references/mandate.md: 缺少实验执行资产",
                "\n".join(fresh_problems(root)),
            )

    def test_checker_detects_missing_other_single_install_resource(self):
        with WorkCopy() as root:
            resource = root.path / (
                BASE / "run-experiment/references/composition-map.md"
            ).relative_to(ROOT)
            resource.unlink()
            root.stage()
            self.assertIn(
                "run-experiment/references/composition-map.md: 缺少实验执行资产",
                "\n".join(fresh_problems(root)),
            )

    def test_checker_detects_damaged_packaged_mandate_contract(self):
        with WorkCopy() as root:
            mandate_path = root.path / (
                BASE / "experiment-plan/references/mandate.md"
            ).relative_to(ROOT)
            mandate_path.write_text(
                mandate_path.read_text(encoding="utf-8").replace(
                    "用户叫停是停止，不是完成", "用户叫停代表完成"
                ),
                encoding="utf-8",
            )
            root.stage()
            self.assertIn(
                "单装合同缺「用户叫停是停止，不是完成」",
                "\n".join(fresh_problems(root)),
            )

    def test_checker_detects_cross_skill_markdown_links_that_break_single_installs(self):
        with WorkCopy() as root:
            plan_path = root.path / (BASE / "experiment-plan/SKILL.md").relative_to(ROOT)
            with plan_path.open("a", encoding="utf-8") as stream:
                stream.write("\n参见 [run-experiment](../run-experiment/SKILL.md)。\n")
            root.stage()
            self.assertIn(
                "单装时不可解析的跨叶 Markdown 引用",
                "\n".join(fresh_problems(root)),
            )


if __name__ == "__main__":
    unittest.main()
