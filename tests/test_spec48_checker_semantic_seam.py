"""S6A-F1: real structure CLI positives paired with actual contract violations."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from spec48_checker_result import parse_checker_result
from spec48_workcopy import copy_tracked_tree
from test_spec48_ticket58 import load

ROOT = Path(__file__).resolve().parents[1]
COMPOSITION = "skills/general/research-os/references/discovery-composition.md"
ARENA = "skills/organization/arena/SKILL.md"
CONTINUATION = "skills/general/research-os/playbooks/continuation.md"


class SemanticSeamCLI(unittest.TestCase):
    def test_explicit_phase_gates_and_dependencies_remain_rejected(self):
        checker = load()
        for directive in ("必须每个阶段获得用户批准。", "本配方是第二总控。"):
            with self.subTest(directive=directive):
                self.assertTrue(checker.discovery_order_problems(directive))
        self.assertIn("swarm", checker.arena_required_dependencies("必须先运行 swarm。"))
        for valid in ("不得固定顺序执行全部职责。", "不要求每个阶段获得用户批准。", "本配方不是第二总控。"):
            with self.subTest(valid=valid):
                self.assertEqual(checker.discovery_order_problems(valid), [])

    def test_unknown_text_is_not_accepted_as_a_shared_quota_contract(self):
        checker = load()
        self.assertTrue(checker.shared_quota_contract_problems("unrelated prose"))
        self.assertEqual(checker.shared_quota_contract_problems(
            "按[委托](../references/mandate.md)；并行、换线程、重试、恢复和子代理共享同一份预算，不得恢复时从零重置额度。"), [])

    def run_change(self, relative, before, after):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            copy_tracked_tree(ROOT, root)
            path = root / relative
            text = path.read_text(encoding="utf-8")
            self.assertIn(before, text)
            path.write_text(text.replace(before, after, 1), encoding="utf-8")
            for command in (["git", "init", "-q"], ["git", "add", "-f", "."]):
                subprocess.run(command, cwd=root, check=True, capture_output=True, timeout=30)
            result = subprocess.run([sys.executable, str(root / "scripts/check-skills.py")],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            problems = parse_checker_result(result)
            return result, problems

    def test_legal_negated_order_and_independence_statement_pass(self):
        for relative, before, after in (
            (COMPOSITION, "# Discovery 组合参考", "# Discovery 组合参考：不得固定顺序执行"),
            (ARENA, "# Arena\n", "# Arena（本能力不依赖 swarm）\n"),
        ):
            with self.subTest(relative=relative):
                result, problems = self.run_change(relative, before, after)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(problems, [])

    def test_equivalent_shared_quota_verbs_pass(self):
        before = "并行、换线程、重试、恢复和子代理消耗**同一条额度**，不重置"
        for after in (
            "并行、换线程、重试、恢复和子代理共享**同一条额度**，不重置",
            "并行、换线程、重试、恢复和子代理共用同一份预算，累计核算且不清零",
        ):
            with self.subTest(after=after):
                result, problems = self.run_change(CONTINUATION, before, after)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(problems, [])

    def test_real_required_swarm_dependency_is_rejected(self):
        result, problems = self.run_change(ARENA, "# Arena\n", "# Arena\n\n## Required skills\n- `swarm`\n")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("arena" in p and "依赖" in p for p in problems), problems)

    def test_real_mandatory_total_order_is_rejected(self):
        result, problems = self.run_change(COMPOSITION, "# Discovery 组合参考", "# Discovery 组合参考\n\n必须固定顺序执行全部五项职责，不得跳过任何阶段。")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("固定顺序" in p for p in problems), problems)

    def test_real_quota_reset_is_rejected_even_if_shared_clause_remains(self):
        result, problems = self.run_change(CONTINUATION, "# continuation", "# continuation\n\n恢复时从零重置额度。")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("重置" in p for p in problems), problems)

    def test_missing_required_install_dependency_is_rejected(self):
        result, problems = self.run_change(COMPOSITION,
            "--skill research-os research-lit idea-generation novelty-check idea-review idea-refinement",
            "--skill research-os research-lit idea-generation novelty-check idea-refinement")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(any("Required skills" in p and "idea-review" in p for p in problems), problems)
