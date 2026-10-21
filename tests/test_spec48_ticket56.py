"""#56 授权内实验执行与远程执行位置。

期望来自 #48 spec（Implementation 8、9、13–17；Testing 8）与 #56 票面。
历史基线：`integration/spec-48` 的 `docs/acceptance/**` 链到被 `.gitignore`
忽略的 `evidence/*.tar.gz`，checker 已因此 FAIL；本票只允许这 9 条历史断链。
"""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
BASE = ROOT / "skills" / "validation-cycle"
EXPERIMENT_SKILLS = (
    "experiment-plan",
    "experiment-bridge",
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
BRIDGE = BASE / "experiment-bridge"
BOUNDARY = ROOT / "skills/general/research-os/references/migration-boundary.md"
UPSTREAM = ROOT / "docs/upstream-sources-and-licenses.md"

HISTORICAL = re.compile(
    r"^  - docs/acceptance/[^:]+:\d+: 链接目标不存在或未追踪: evidence/\S+\.tar\.gz$"
)
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
    )
    return [line for line in result.stdout.splitlines() if line.startswith("  - ")]


def fresh_problems(root: Path) -> list[str]:
    return [line for line in problem_lines(root) if not HISTORICAL.match(line)]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class WorkCopy:
    """可损坏副本；git init 后让 checker 的追踪文件检查可运行。"""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "repo"
        shutil.copytree(
            ROOT,
            self.path,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"),
        )
        for command in (
            ["git", "init"],
            ["git", "add", "-A"],
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
    def test_nine_experiment_capabilities_remain_separate(self):
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

    def test_bridge_is_compatibility_pointer_not_duplicate_controller(self):
        bridge = text(BRIDGE / "SKILL.md")
        run = text(RUN / "SKILL.md")
        self.assertIn("兼容入口", bridge)
        self.assertIn("../run-experiment/SKILL.md", bridge)
        self.assertIn("不再重复执行控制", bridge)
        self.assertNotRegex(bridge, r"(?m)^Gate:", bridge)
        for phrase in ("正式与批量运行", "分析审计与 tracker 更新", "授权门"):
            self.assertNotIn(phrase, bridge, phrase)
        self.assertIn("执行控制", run)
        self.assertIn("小批量或队列", run)
        self.assertNotIn("../experiment-bridge/SKILL.md", run)


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

    def test_queue_reuses_same_contract_and_has_recovery(self):
        queue = text(QUEUE / "SKILL.md")
        manifest = text(QUEUE / "templates/batch-manifest.md")
        for phrase in ("输入版本", "工具链", "独立目录", "作业身份", "退出码", "原始日志", "产物"):
            self.assertIn(phrase, queue, phrase)
            self.assertIn(phrase, manifest, phrase)
        for phrase in ("断线", "原作业", "不盲重跑", "旧文件", "作业退出", "产物有效", "科学结论"):
            self.assertIn(phrase, queue, phrase)
        run = text(RUN / "SKILL.md")
        for phrase in ("作业退出", "产物有效", "科学结论", "旧文件"):
            self.assertIn(phrase, run, phrase)

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


class CheckerContract(unittest.TestCase):
    def test_builtin_checker_registers_ticket56_contract(self):
        self.assertEqual(fresh_problems(ROOT), [])

    def test_checker_detects_missing_recovery_contract(self):
        with WorkCopy() as root:
            queue_path = root.path / QUEUE.relative_to(ROOT) / "SKILL.md"
            queue_path.write_text(
                queue_path.read_text(encoding="utf-8").replace("断线", "中断"),
                encoding="utf-8",
            )
            root.stage()
            self.assertIn("断线", "\n".join(fresh_problems(root)))

    def test_checker_detects_missing_remote_contract(self):
        with WorkCopy() as root:
            run_path = root.path / RUN.relative_to(ROOT) / "SKILL.md"
            run_path.write_text(
                run_path.read_text(encoding="utf-8").replace("已有调度", "自建调度"),
                encoding="utf-8",
            )
            root.stage()
            self.assertIn("已有调度", "\n".join(fresh_problems(root)))


if __name__ == "__main__":
    unittest.main()
