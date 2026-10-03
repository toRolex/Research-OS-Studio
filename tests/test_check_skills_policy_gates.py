"""#39 seam：调用策略值、叶 skill 门声明基线、损坏副本必须报错。

期望来自共享合同与人工盘点，不从被测脚本反读。
"""
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
# 本票拥有的叶。入口与 setup 基线由后续票并入同一 checker。
LEAF_GATES = {
    "skills/idea-cycle/creative-thinking-for-research/SKILL.md": {"write-path"},
    "skills/idea-cycle/idea-discovery/SKILL.md": {"stage-checkpoint", "output-path"},
    "skills/idea-cycle/idea-generation/SKILL.md": {"write-path"},
    "skills/idea-cycle/idea-refinement/SKILL.md": {"anchor-clarify"},
    "skills/idea-cycle/idea-review/SKILL.md": {"scope-clarify"},
    "skills/idea-cycle/novelty-check/SKILL.md": set(),
    "skills/idea-cycle/research-lit/SKILL.md": {"write-path"},
    "skills/validation-cycle/analyze-results/SKILL.md": {"write-path"},
    "skills/validation-cycle/experiment-audit/SKILL.md": {"write-path"},
    "skills/validation-cycle/experiment-bridge/SKILL.md": {"run-authorization"},
    "skills/validation-cycle/experiment-plan/SKILL.md": {"output-path"},
    "skills/validation-cycle/experiment-queue/SKILL.md": {"batch-authorization", "precondition-block"},
    "skills/validation-cycle/formula-derivation/SKILL.md": {"write-authorization"},
    "skills/validation-cycle/monitor-experiment/SKILL.md": {"write-path"},
    "skills/validation-cycle/proof-orchestrator/SKILL.md": {"round-scope", "external-action"},
    "skills/validation-cycle/proof-repair/SKILL.md": {
        "repair-contract",
        "assumption-or-claim-change",
        "compile-authorization",
    },
    "skills/validation-cycle/proof-review/SKILL.md": set(),
    "skills/validation-cycle/proof-writer/SKILL.md": {"write-authorization"},
    "skills/validation-cycle/result-to-claim/SKILL.md": {"write-path"},
    "skills/validation-cycle/run-experiment/SKILL.md": {"run-authorization", "milestone-start"},
    "skills/validation-cycle/training-health-check/SKILL.md": {"write-path"},
    "skills/writing-cycle/academic-plotting/SKILL.md": {"figure-choice", "external-resource"},
    "skills/writing-cycle/apply-citation-fixes/SKILL.md": {"apply-authorization"},
    "skills/writing-cycle/citation-audit/SKILL.md": {"audit-scope"},
    "skills/writing-cycle/claim-stress-test/SKILL.md": {"report-target"},
    "skills/writing-cycle/ml-paper-writing/SKILL.md": {"workflow-authorization"},
    "skills/writing-cycle/paper-claim-audit/SKILL.md": {"report-target"},
    "skills/writing-cycle/paper-compile-repair/SKILL.md": {"repair-scope", "round-diff"},
    "skills/writing-cycle/paper-compile/SKILL.md": {"build-scope"},
    "skills/writing-cycle/paper-drafting/SKILL.md": {"boundary-confirm", "venue-conflict"},
    "skills/writing-cycle/paper-plan/SKILL.md": {"write-authorization", "framing-confirm"},
    "skills/writing-cycle/paper-talk/SKILL.md": {"talk-authorization", "outline-confirm"},
    "skills/writing-cycle/paper-writing/SKILL.md": {"workflow-authorization"},
    "skills/writing-cycle/rebuttal/SKILL.md": {"strategy-confirm", "wording-confirm"},
    "skills/writing-cycle/research-improvement/SKILL.md": {"loop-authorization", "experiment-topup"},
    "skills/writing-cycle/resubmit-pipeline/SKILL.md": {"adaptation-scope", "change-confirm"},
    "skills/writing-cycle/systems-paper-writing/SKILL.md": {"workflow-authorization"},
}


def run_check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "python", str(root / "scripts" / "check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
    )


class PolicyAndGates(unittest.TestCase):
    def test_checker_green_and_leaf_baseline(self) -> None:
        result = run_check(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("调用策略", result.stdout)
        self.assertIn("门声明", result.stdout)
        for rel, expected in LEAF_GATES.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            found = set(re.findall(r"^Gate: ([a-z0-9-]+) \|", text, re.M))
            self.assertEqual(found, expected, rel)
            if not expected:
                self.assertRegex(text, r"(?m)^Gates: none$")
        for rel in (SETUP, ROUTER):
            self.assertNotIn(rel, LEAF_GATES)

    def test_readme_says_explicit_except_setup(self) -> None:
        text = (ROOT / "skills" / "README.md").read_text(encoding="utf-8")
        self.assertIn("除 setup 外全部显式调用", text)
        self.assertNotIn("均 model-invoked", text)

    def test_damaged_copies_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._damaged(Path(tmp))

    def _damaged(self, work: Path) -> None:
        leaf = SKILLS / "writing-cycle" / "rebuttal" / "SKILL.md"
        cases = {
            "drop-one-gate": lambda text: text.replace(
                "Gate: wording-confirm |", "Gate-removed: wording-confirm |", 1
            ),
            "all-none": lambda text: "\n".join(
                line for line in text.splitlines() if not line.startswith("Gate:")
            )
            + "\nGates: none\n",
            "rename-id": lambda text: text.replace("strategy-confirm", "strategy-ok", 1),
            "duplicate-id": lambda text: text.replace(
                "Gate: strategy-confirm |",
                "Gate: strategy-confirm |\nGate: strategy-confirm | before=reply-drafting | approval=explicit-user | source=SKILL.md#回应策略",
                1,
            ),
            "bad-source": lambda text: text.replace(
                "source=SKILL.md#3-制定策略交用户选择",
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
        yaml = work / "skills/writing-cycle/rebuttal/agents/openai.yaml"
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
            self.assertTrue("rebuttal" in blob or "allow_implicit_invocation" in blob, name + blob)


if __name__ == "__main__":
    unittest.main()
