"""Final review regressions: expectations from approved contract, not checker."""
import runpy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NS = runpy.run_path(str(ROOT / "scripts/check-skills.py"))
POLICY = (ROOT / "skills/general/setup-research-os/templates/compute-policy.md").read_text()
ROLES = {"orchestrator", "literature", "ideator", "implementer", "analyst", "prover", "writer", "reviewer"}


class FinalContracts(unittest.TestCase):
    def policy_errors(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "policy.md"
            p.write_text(text)
            NS["problems"].clear()
            NS["check_policy"](p)
            return list(NS["problems"])

    def test_policy_types_uniqueness_and_dates(self):
        mutations = {
            "empty currency": POLICY.replace("currency: 未指定", "currency:"),
            "empty scope": POLICY.replace("scope: 未指定", "scope:"),
            "bad expiry": POLICY.replace("valid_until: 未指定", "valid_until: tomorrow"),
            "no timezone": POLICY.replace("valid_until: 未指定", "valid_until: 2030-01-01T00:00:00"),
            "bad calendar": POLICY.replace("valid_until: 未指定", "valid_until: 2030-02-30T00:00:00Z"),
            "bad offset": POLICY.replace("valid_until: 未指定", "valid_until: 2030-01-01T00:00:00+01:99"),
            "nontext scope": POLICY.replace("scope: 未指定", "scope: 123"),
            "duplicate cost": POLICY + "\n- cost_limit: 0\n",
            "duplicate scope": POLICY + "\n- scope: 未指定\n",
            "empty expiry": POLICY.replace("valid_until: 未指定", "valid_until:"),
            "empty count basis": POLICY.replace("run_count_basis: planned-run", "run_count_basis:"),
            "bad currency type": POLICY.replace("currency: 未指定", "currency: 23"),
            "empty compute unit": POLICY.replace("compute_unit: cpu-core-hour", "compute_unit:"),
            "NaN retry": POLICY.replace("retry_limit: 0", "retry_limit: NaN"),
            "duplicate expiry": POLICY + "\n- valid_until: 未指定\n",
            "fraction count": POLICY.replace("run_limit: 0", "run_limit: 0.5"),
            "unexplained NA": POLICY.replace("currency: 未指定", "currency: not-applicable"),
            "executable concurrency zero": POLICY.replace("run_limit: 0", "run_limit: 1"),
        }
        for name, text in mutations.items():
            with self.subTest(name=name):
                self.assertTrue(self.policy_errors(text), name)
        for value in ("2030-01-01T00:00:00Z", "2020-01-01T00:00:00+08:00"):
            self.assertFalse(self.policy_errors(POLICY.replace("valid_until: 未指定", "valid_until: " + value)))
        self.assertFalse(self.policy_errors(POLICY))
        self.assertFalse(self.policy_errors(POLICY.replace("currency: 未指定", "currency: not-applicable") + "\n因为仅符号证明无费用。\n"))

    def test_dot_cascade_is_not_blanket_exemption(self):
        rel = "skills/general/research-os/playbooks/improvement.md"
        for target in ("./references/MISSING.md", "../references/MISSING.md"):
            self.assertTrue(NS["backtick_cascade_problems"](rel, "读 `" + target + "`。", ROOT, NS["tracked"]))
        self.assertFalse(NS["backtick_cascade_problems"](rel, "项目配置示例 `.agents/research-os-models.md`。", ROOT, NS["tracked"]))
        self.assertFalse(NS["backtick_cascade_problems"](rel, "读 `../references/batch-authorization.md`。", ROOT, NS["tracked"]))

    def test_migration_is_per_reference(self):
        good = "Breaking change: ask-research-os 已删除，迁移到 /research-os。"
        self.assertFalse(NS["legacy_router_problems"]({"README.md": good}))
        for bad in (good + "\n\n请使用 /ask-research-os。", "迁移说明。\n请使用 /ask-research-os。", good + " 请使用 /ask-research-os。"):
            self.assertTrue(NS["legacy_router_problems"]({"README.md": bad}))

    def test_improvement_batch_contract(self):
        text = (ROOT / "skills/general/research-os/playbooks/improvement.md").read_text()
        for token in ("batch-authorization.md", "run_count_basis=attempt", "valid_until", "scope", "累计", "预留", "per_attempt", "concurrency_limit", "retry_limit"):
            self.assertIn(token, text)
        reference = (ROOT / "skills/general/research-os/references/batch-authorization.md").read_text()
        self.assertIn("attempt 名额", reference)

    def test_real_roles_cover_all_eight(self):
        import re
        paths = list((ROOT / "skills/general/research-os/playbooks").glob("*.md"))
        found = set()
        for p in paths:
            found.update(re.findall(r"(?m)^Role: ([a-z]+)$", p.read_text()))
        self.assertEqual(found, ROLES)
        self.assertRegex((ROOT / "skills/general/research-os/SKILL.md").read_text(), r"(?m)^Role: orchestrator$")

    def test_full_cli_damaged_declarations_refs_and_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
            for rel in tracked:
                src, dst = ROOT / rel, work / rel
                if not src.is_file():
                    continue
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.suffix in {".md", ".py", ".yaml"}:
                    shutil.copyfile(src, dst)
                else:
                    dst.touch()
            subprocess.run(["git", "init", "-q"], cwd=work, check=True)
            subprocess.run(["git", "add", "-A"], cwd=work, check=True)
            skill = work / "skills/general/research-os/SKILL.md"
            yaml = work / "skills/general/research-os/agents/openai.yaml"
            playbook = work / "skills/general/research-os/playbooks/improvement.md"
            readme = work / "README.md"
            cases = [
                (skill, "disable-model-invocation: true", "disable-model-invocation: true\ndisable-model-invocation: false"),
                (skill, "disable-model-invocation: true", "other: disable-model-invocation: true"),
                (skill, "name: research-os", "name: research-os\nname: research-os"),
                (skill, "disable-model-invocation: true", "disable-model-invocation: false\ndisable-model-invocation: true"),
                (skill, "description:", "description: ignored\ndescription:"),
                (yaml, "allow_implicit_invocation: false", "allow_implicit_invocation: false\n  allow_implicit_invocation: true"),
                (yaml, "allow_implicit_invocation: false", "allow_implicit_invocation: true\n  allow_implicit_invocation: false"),
                (playbook, "# improvement", "# improvement\n\nRole: ghostwriter"),
                (playbook, "# improvement", "# improvement\n\n读 `./references/MISSING.md`。"),
                (readme, "", "\n请使用 /ask-research-os。\n"),
            ]
            def check():
                return subprocess.run(["uv", "run", "--no-project", "python", "scripts/check-skills.py"], cwd=work, text=True, capture_output=True)
            self.assertEqual(check().returncode, 0)
            for path, old, new in cases:
                with self.subTest(path=path.name, mutation=new):
                    original = path.read_text()
                    path.write_text(original.replace(old, new, 1) if old else original + new)
                    result = check()
                    path.write_text(original)
                    self.assertNotEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
