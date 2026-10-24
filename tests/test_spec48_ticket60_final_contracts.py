"""Installed public contracts for the #60 proof-review authorization seams."""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_VERSION = "1.7.4"


class InstalledReviewContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cache = subprocess.run(
            ["npm", "config", "get", "cache"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        cls.npm_cache = cache.stdout.strip()

    def install_skill(self, slug: str) -> dict[str, str]:
        with tempfile.TemporaryDirectory(dir="/tmp", prefix=f"ticket60-{slug}-") as tmp:
            project = Path(tmp) / "project"
            home = Path(tmp) / "home"
            project.mkdir()
            home.mkdir()
            result = subprocess.run(
                [
                    "npx", "--offline", "--yes", f"skills@{SKILLS_VERSION}", "add",
                    str(ROOT), "--skill", slug, "--agent", "claude-code", "--copy", "--yes",
                ],
                cwd=project,
                env={
                    **os.environ,
                    "HOME": str(home),
                    "TMPDIR": tmp,
                    "npm_config_cache": self.npm_cache,
                },
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            package = project / ".claude/skills" / slug
            self.assertTrue((package / "SKILL.md").is_file(), slug)
            return {
                path.relative_to(package).as_posix(): path.read_text(encoding="utf-8")
                for path in package.rglob("*.md")
            }

    def test_proof_repair_inherits_authorized_review_cascade_without_weakening_real_gates(self):
        installed = self.install_skill("proof-repair")
        repair = installed["SKILL.md"]
        contract = installed["references/review-contract.md"]

        self.assertIn("本次修复、完整复审", repair)
        self.assertIn("不为阶段切换或已覆盖的重试再次索权", repair)
        self.assertIn("按路径级联读取的 `proof-review`", repair)

        # The installed contract must not contradict its caller by treating
        # metadata-level user invocation as a ban on authorized body-level cascade.
        self.assertNotIn("仅 user-invoked", contract)
        self.assertIn("disable-model-invocation", contract)
        self.assertIn("正文在有效委托内级联", contract)

        # Preserve the capability and evidence gates; wording alone is not execution.
        self.assertIn("宿主", contract)
        self.assertIn("blocked", contract.lower())
        self.assertIn("fresh", contract.lower())
        self.assertIn("原始材料", contract)
        self.assertIn("自查", contract)
        self.assertIn("外发", contract)
        self.assertIn("不得编造调用回执", contract)
        self.assertIn("不安装或切换审查后端", contract)

    def test_independent_opinion_reuses_authorized_scope_and_budget_for_bounded_retry(self):
        installed = self.install_skill("proof-review")
        skill = installed["SKILL.md"]
        opinion = installed["references/independent-review.md"]

        self.assertIn("standalone", skill)
        self.assertIn("composed", skill)
        self.assertNotIn("仅在用户为本轮明确请求第二意见后使用", opinion)
        self.assertNotIn("下一次调用需要用户重新授权", opinion)
        self.assertNotIn("不自动重试、切模型、改路线或升级费用", opinion)
        self.assertIn("独立调用", opinion)
        self.assertIn("有效委托", opinion)
        self.assertIn("每轮再次点名", opinion)
        self.assertIn("同一总额度", opinion)
        self.assertIn("剩余额度", opinion)
        self.assertIn("有界", opinion)
        self.assertIn("同一路线", opinion)
        self.assertIn("新审查上下文", opinion)
        self.assertIn("完整原始材料", opinion)
        self.assertIn("阻断", opinion)

        # Authorization is inherited, not broadened: identity, outbound and cost gates remain.
        self.assertIn("可信运行元数据", opinion)
        self.assertIn("供应商", opinion)
        self.assertIn("外部发送", opinion)
        self.assertIn("费用", opinion)
        self.assertIn("fallback", opinion.lower())
        self.assertIn("不盲目重发", opinion)


if __name__ == "__main__":
    unittest.main()
