"""#39 seam：调用策略值、叶 skill 门声明基线、损坏副本必须报错。

期望来自共享合同与人工盘点，不从被测脚本反读。
"""
import importlib.util
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "check-skills.py"
SKILLS = ROOT / "skills"

SETUP = "skills/general/setup-research-os/SKILL.md"
ROUTER = "skills/general/ask-research-os/SKILL.md"
HISTORICAL_CHECKER_PROBLEM = re.compile(
    r"^  - docs/acceptance/[^:]+:\d+: 链接目标不存在或未追踪: evidence/\S+\.tar\.gz$"
)
# 仅为 #60 恢复归档策略前的过渡基线；修复证据后须删除此允许集和替换诊断测试。
HISTORICAL_CHECKER_PROBLEMS = frozenset(
    {
        "  - docs/acceptance/v2-release-host-regression.md:93: 链接目标不存在或未追踪: evidence/v2-release-host-regression.tar.gz",
        "  - docs/acceptance/v2-final-contract-fixes.md:53: 链接目标不存在或未追踪: evidence/v2-final-contract-fixes.tar.gz",
        "  - docs/acceptance/v2-release-gate-combinations.md:49: 链接目标不存在或未追踪: evidence/v2-release-gate-combinations.tar.gz",
        "  - docs/acceptance/v2-merged-host-smoke.md:54: 链接目标不存在或未追踪: evidence/v2-merged-host-smoke.tar.gz",
        "  - docs/acceptance/v2-accept-validation.md:98: 链接目标不存在或未追踪: evidence/v2-accept-validation.tar.gz",
        "  - docs/acceptance/v2-accept-hosts.md:9: 链接目标不存在或未追踪: evidence/v2-accept-hosts.tar.gz",
        "  - docs/acceptance/v2-final-contract-independent-verify.md:41: 链接目标不存在或未追踪: evidence/v2-final-contract-independent-verify.tar.gz",
        "  - docs/acceptance/v2-final-contract-independent-verify.md:53: 链接目标不存在或未追踪: evidence/v2-merged-host-smoke.tar.gz",
        "  - docs/acceptance/v2-accept-remediation.md:92: 链接目标不存在或未追踪: evidence/v2-accept-remediation.tar.gz",
    }
)
# 本票拥有的叶。入口与 setup 基线由后续票并入同一 checker。
# #49 起 research-lit 已迁移；#57 起 writing-cycle 中 academic-plotting/#58 与 research-improvement/#59 外的写作能力已迁移；
# 迁移状态由对应票测试与 check-skills.py 的 MIGRATED_CONTRACT 校验。
LEAF_GATES = {
    "skills/idea-cycle/creative-thinking-for-research/SKILL.md": {"write-path"},
    "skills/idea-cycle/idea-discovery/SKILL.md": {"stage-checkpoint", "output-path"},
    "skills/idea-cycle/idea-generation/SKILL.md": {"write-path"},
    "skills/idea-cycle/idea-refinement/SKILL.md": {"anchor-clarify"},
    "skills/idea-cycle/idea-review/SKILL.md": {"scope-clarify"},
    "skills/idea-cycle/novelty-check/SKILL.md": set(),
    "skills/validation-cycle/formula-derivation/SKILL.md": {"write-authorization"},
    "skills/validation-cycle/proof-orchestrator/SKILL.md": {"round-scope", "external-action"},
    "skills/validation-cycle/proof-repair/SKILL.md": {
        "repair-contract",
        "assumption-or-claim-change",
        "compile-authorization",
    },
    "skills/validation-cycle/proof-review/SKILL.md": set(),
    "skills/validation-cycle/proof-writer/SKILL.md": {"write-authorization"},
    "skills/writing-cycle/academic-plotting/SKILL.md": {"figure-choice", "external-resource"},
}


def run_check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "python", str(root / "scripts" / "check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
    )


def load_checker():
    spec = importlib.util.spec_from_file_location("check_skills_policy_gates", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def has_only_historical_checker_problems(result: subprocess.CompletedProcess[str]) -> bool:
    problems = [line for line in result.stdout.splitlines() if line.startswith("  - ")]
    return (
        result.returncode == 1
        and len(problems) == 9
        and set(problems) == HISTORICAL_CHECKER_PROBLEMS
    )


class PolicyAndGates(unittest.TestCase):
    def test_checker_has_only_recorded_tarball_gaps_and_leaf_baseline(self) -> None:
        result = run_check(ROOT)
        self.assertTrue(has_only_historical_checker_problems(result), result.stdout + result.stderr)
        module = load_checker()
        for rel, expected in LEAF_GATES.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            found = set(re.findall(r"^Gate: ([a-z0-9-]+) \|", text, re.M))
            self.assertEqual(found, expected, rel)
            if not expected:
                self.assertRegex(text, r"(?m)^Gates: none$")
        migrated = set(module.MIGRATED_CONTRACT)
        writing_skills = {
            f"skills/writing-cycle/{name}/SKILL.md"
            for name in (
                "apply-citation-fixes", "citation-audit", "claim-stress-test",
                "ml-paper-writing", "paper-claim-audit", "paper-compile-repair",
                "paper-compile", "paper-drafting", "paper-plan", "paper-talk",
                "paper-writing", "rebuttal", "resubmit-pipeline", "systems-paper-writing",
            )
        }
        self.assertTrue(writing_skills <= migrated)
        self.assertIn("skills/writing-cycle/academic-plotting/SKILL.md", module.LEGACY_LEAF_GATES)
        improvement = "skills/writing-cycle/research-improvement/SKILL.md"
        self.assertIn(improvement, migrated)
        self.assertNotIn(improvement, module.LEGACY_LEAF_GATES)
        for rel in (SETUP, ROUTER):
            self.assertNotIn(rel, LEAF_GATES)

    def test_checker_historical_allowlist_rejects_replaced_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "repo"
            shutil.copytree(
                ROOT,
                work,
                ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"),
            )
            subprocess.run(["git", "init"], cwd=work, check=True, capture_output=True)
            subprocess.run(["git", "add", "-A"], cwd=work, check=True, capture_output=True)
            subprocess.run(
                ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base"],
                cwd=work,
                check=True,
                capture_output=True,
            )
            doc = work / "docs/acceptance/v2-release-host-regression.md"
            original = doc.read_text(encoding="utf-8")
            replaced = original.replace(
                "](evidence/v2-release-host-regression.tar.gz)",
                "](evidence/v2-release-host-regression-replaced.tar.gz)",
                1,
            )
            self.assertNotEqual(original, replaced)
            doc.write_text(replaced, encoding="utf-8")

            result = run_check(work)
            problems = [line for line in result.stdout.splitlines() if line.startswith("  - ")]
            self.assertEqual(len(problems), 9, result.stdout + result.stderr)
            self.assertTrue(
                all(HISTORICAL_CHECKER_PROBLEM.fullmatch(line) for line in problems),
                result.stdout + result.stderr,
            )
            self.assertFalse(has_only_historical_checker_problems(result), result.stdout + result.stderr)

    def test_readme_says_explicit_except_setup(self) -> None:
        text = (ROOT / "skills" / "README.md").read_text(encoding="utf-8")
        self.assertIn("除 setup 外全部显式调用", text)
        self.assertNotIn("均 model-invoked", text)

    def test_damaged_copies_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._damaged(Path(tmp))

    def _damaged(self, work: Path) -> None:
        # #57 迁移 rebuttal；损坏副本反例改用仍由 #58 负责的未迁移绘图叶。
        leaf = SKILLS / "writing-cycle" / "academic-plotting" / "SKILL.md"
        cases = {
            "drop-one-gate": lambda text: text.replace(
                "Gate: figure-choice |", "Gate-removed: figure-choice |", 1
            ),
            "all-none": lambda text: "\n".join(
                line for line in text.splitlines() if not line.startswith("Gate:")
            )
            + "\nGates: none\n",
            "rename-id": lambda text: text.replace("figure-choice", "figure-ok", 1),
            "duplicate-id": lambda text: text.replace(
                "Gate: figure-choice |",
                "Gate: figure-choice |\nGate: figure-choice | before=figure-select | approval=explicit-user | source=SKILL.md#盘点并选图",
                1,
            ),
            "bad-source": lambda text: text.replace(
                "source=SKILL.md#1-盘点并选图",
                "source=SKILL.md#不存在的锚点",
                1,
            ),
            "drop-section": lambda text: "\n".join(
                line for line in text.splitlines() if not line.startswith(("Gate:", "Gates:"))
            )
            + "\n",
            "yaml-true": None,
            "drop-disable": lambda text: text.replace("disable-model-invocation: true\n", "", 1),
        }
        shutil.copytree(
            ROOT,
            work,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"),
        )
        subprocess.run(["git", "init"], cwd=work, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=work, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base"],
            cwd=work,
            check=True,
            capture_output=True,
        )
        original = (work / leaf.relative_to(ROOT)).read_text(encoding="utf-8")
        yaml = work / "skills/writing-cycle/academic-plotting/agents/openai.yaml"
        yaml_original = yaml.read_text(encoding="utf-8")
        for name, mutate in cases.items():
            target = work / leaf.relative_to(ROOT)
            target.write_text(original, encoding="utf-8")
            yaml.write_text(yaml_original, encoding="utf-8")
            if name == "yaml-true":
                yaml.write_text(yaml_original.replace("false", "true"), encoding="utf-8")
            else:
                target.write_text(mutate(original), encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=work, check=True, capture_output=True)
            result = run_check(work)
            self.assertNotEqual(result.returncode, 0, name)
            blob = result.stdout + result.stderr
            self.assertTrue("academic-plotting" in blob or "allow_implicit_invocation" in blob, name + blob)


if __name__ == "__main__":
    unittest.main()
