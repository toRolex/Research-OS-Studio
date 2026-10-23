"""#39 seam：调用策略值、叶 skill 门声明基线、损坏副本必须报错。

期望来自共享合同与人工盘点，不从被测脚本反读。
"""
import importlib.util
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree

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
LEAF_GATES = {
    "skills/validation-cycle/proof-review/SKILL.md": set(),
}


def copy_worktree(work: Path) -> None:
    """Prepare the tracked workcopy used by both damaged-checker entry points."""
    copy_tracked_tree(ROOT, work)
    for command in (
        ["git", "init"],
        ["git", "add", "-f", "."],
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base"],
    ):
        subprocess.run(command, cwd=work, check=True, capture_output=True)


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
        migrated_proof_skills = {
            "skills/validation-cycle/formula-derivation/SKILL.md",
            "skills/validation-cycle/proof-writer/SKILL.md",
            "skills/validation-cycle/proof-repair/SKILL.md",
        }
        self.assertTrue(migrated_proof_skills <= migrated)
        self.assertTrue(migrated_proof_skills.isdisjoint(module.LEGACY_LEAF_GATES))
        for rel in migrated_proof_skills:
            self.assertEqual(module.MIGRATED_CONTRACT[rel], "委托继承")
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?m)^Gate:")
            self.assertRegex(text, r"(?m)^Gates: none$")
            self.assertRegex(text, r"(?m)^## 委托继承$")
        self.assertNotIn("skills/validation-cycle/proof-orchestrator/SKILL.md", migrated)
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
        idea_cycle_skills = {
            f"skills/idea-cycle/{name}/SKILL.md"
            for name in (
                "creative-thinking-for-research", "idea-generation",
                "idea-refinement", "idea-review", "novelty-check",
            )
        }
        self.assertTrue(idea_cycle_skills <= migrated)
        self.assertNotIn("skills/idea-cycle/idea-discovery/SKILL.md", migrated)
        self.assertFalse((ROOT / "skills/idea-cycle/idea-discovery/SKILL.md").exists())
        academic_plotting = "skills/writing-cycle/academic-plotting/SKILL.md"
        self.assertIn(academic_plotting, migrated)
        self.assertNotIn(academic_plotting, module.LEGACY_LEAF_GATES)
        improvement = "skills/writing-cycle/research-improvement/SKILL.md"
        self.assertIn(improvement, migrated)
        self.assertNotIn(improvement, module.LEGACY_LEAF_GATES)
        for rel in (SETUP, ROUTER):
            self.assertNotIn(rel, LEAF_GATES)

    def test_checker_historical_allowlist_rejects_replaced_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "repo"
            copy_worktree(work)
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
            self._damaged(Path(tmp) / "repo")

    def _damaged(self, work: Path) -> None:
        # #55 已迁移 proof-repair；负例破坏新委托合同，不把它退回旧门基线。
        leaf = SKILLS / "validation-cycle" / "proof-repair" / "SKILL.md"
        cases = {
            "drop-gates-none": lambda text: text.replace("Gates: none\n", "", 1),
            "reintroduce-legacy-gate": lambda text: text.replace(
                "Gates: none",
                "Gate: repair-contract | before=repair-write | approval=explicit-user | source=SKILL.md#1-确认修复契约",
                1,
            ),
            "drop-delegation-section": lambda text: text.replace(
                "## 委托继承", "## 缺失的授权", 1
            ),
            "duplicate-gates-none": lambda text: text.replace(
                "Gates: none\n", "Gates: none\nGates: none\n", 1
            ),
            "yaml-true": None,
            "drop-disable": lambda text: text.replace("disable-model-invocation: true\n", "", 1),
        }
        copy_worktree(work)
        original = (work / leaf.relative_to(ROOT)).read_text(encoding="utf-8")
        yaml = work / "skills/validation-cycle/proof-repair/agents/openai.yaml"
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
            self.assertTrue("proof-repair" in blob or "allow_implicit_invocation" in blob, name + blob)


if __name__ == "__main__":
    unittest.main()
