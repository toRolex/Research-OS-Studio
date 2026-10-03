"""#37 review regressions: approved Seam A, public checker CLI."""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROUTER = "skills/general/research-os/SKILL.md"
SETUP = "skills/general/setup-research-os/SKILL.md"
LEAF = "skills/writing-cycle/rebuttal/SKILL.md"


def run(root, *args):
    return subprocess.run(["uv", "run", "--no-project", "python",
                           str(root / "scripts/check-skills.py"), *args],
                          cwd=root, capture_output=True, text=True)


class ReviewFixes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        for rel in filter(None, paths):
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)

    def assert_rejected(self, *args):
        result = run(self.root, *args)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_orchestrator_contract_is_explicit(self):
        text = (ROOT / ROUTER).read_text()
        for required in ("逐字抄入 todolist", "逐步跟踪", "编排者自己核实", "当前命中路线是 route-only", "<安装根>/<skill-name>/SKILL.md", "叶 SKILL.md 全文"):
            self.assertIn(required, text)
        self.assertIn("当前入口 SKILL.md 所在 skill 目录的父级", text)
        self.assertNotIn("安装根取当前入口实际路径的父级", text)

    def test_pi_explicit_entry_uses_host_native_skill_command(self):
        # Native pi explicit invocation is /skill:name; /name is not a skill command.
        router = (ROOT / ROUTER).read_text()
        self.assertIn("/skill:research-os", router)
        self.assertNotIn("三宿主都用显式 `/research-os`", router)
        self.assertIn("/skill:setup-research-os", (ROOT / "README.md").read_text())

    def test_leaf_bodies_do_not_claim_implicit_invocation(self):
        for path in (ROOT / "skills").glob("*/*/SKILL.md"):
            if path.parent.name != "setup-research-os":
                self.assertNotIn("model-invoked", path.read_text(), str(path))

    def test_compute_limits_are_per_unit_not_summed(self):
        path = self.root / "skills/general/setup-research-os/templates/compute-policy.md"
        original = path.read_text()
        cases = (
            original.replace("compute_limit: 0", "compute_limit: 1", 1).replace("- compute_limit: 0", "- compute_limit: 100", 1).replace("per_attempt_compute_limit: 0", "per_attempt_compute_limit: 2", 1),
            original.replace("compute_unit: gpu-device-hour", "compute_unit: cpu-core-hour"),
            original.replace("- per_attempt_compute_limit: 0\n", "", 1),
            original + "\n- per_attempt_compute_limit: 0\n",
            original.replace("- compute_unit: gpu-device-hour\n", ""),
            original.replace("compute_limit: 0", "compute_limit: NaN", 1),
        )
        for text in cases:
            with self.subTest(text=text):
                path.write_text(text)
                self.assert_rejected()
        path.write_text(original.replace("compute_limit: 0", "compute_limit: 1"))
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_default_command_checks_role_references(self):
        for rel in ("skills/general/research-os/playbooks/custom.md", "skills/general/setup-research-os/templates/research-log.md"):
            path = self.root / rel
            original = path.read_text()
            path.write_text(original + "\nRole: ghostwriter\n")
            self.assert_rejected()
            path.write_text(original)

    def test_untracked_reference_stays_rejected(self):
        path = self.root / ROUTER
        path.write_text(path.read_text() + "\n读 `references/untracked.md`。\n")
        (path.parent / "references/untracked.md").write_text("# Exists\n")
        self.assert_rejected()

    def test_router_none_does_not_hide_other_declarations(self):
        path = self.root / ROUTER
        original = path.read_text()
        for extra in ("Gates: none", "Gate: bogus | before=write | approval=explicit-user | source=SKILL.md#级联", "Gate: broken", "Gates: invalid"):
            with self.subTest(extra=extra):
                path.write_text(original + "\n" + extra + "\n")
                self.assert_rejected()

    def test_gate_sources_cannot_cross_skill_or_symlink(self):
        for rel, foreign in ((ROUTER, "references/../../setup-research-os/SKILL.md#模型"),
                             (SETUP, "references/../../research-os/SKILL.md#级联"),
                             (LEAF, "references/../../paper-plan/SKILL.md#1-确定材料与权限")):
            path = self.root / rel
            original = path.read_text()
            if rel == ROUTER:
                original += "\nGate: bogus | before=write | approval=explicit-user | source=SKILL.md#级联\n"
            for mode in ("traversal", "symlink"):
                with self.subTest(rel=rel, mode=mode):
                    if mode == "symlink":
                        link = path.parent / "references/foreign.md"
                        link.parent.mkdir(exist_ok=True)
                        link.symlink_to(self.root / "skills/general/research-os/SKILL.md")
                        source = "references/foreign.md#级联"
                        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
                    else:
                        source = foreign
                    path.write_text(re.sub(r"source=\S+", "source=" + source, original))
                    self.assert_rejected()
                    self.assert_rejected("--skip-suite", "--gates-dir", str(path.parent), "--skill-name", path.parent.name)
                    path.write_text(original)


if __name__ == "__main__":
    unittest.main()
