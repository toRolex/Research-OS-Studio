#!/usr/bin/env python3
"""配置合同正反例。先于实现写成，经 scripts/check-skills.py 的 CLI 执行。"""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "check-skills.py"
SETUP = ROOT / "skills" / "general" / "setup-research-os"

ROLES = (
    "orchestrator",
    "literature",
    "ideator",
    "implementer",
    "analyst",
    "prover",
    "writer",
    "reviewer",
)

GOOD_ROLES = "\n".join(f"{role}: cliproxy/grok-4.7 | medium" for role in ROLES) + "\n"

GOOD_POLICY = """# 默认算力政策

本文件是默认政策模板，不是运行授权。

- scope: 未指定
- cost_limit: 0
- currency: 未指定
- compute_limit: 0
- compute_unit: cpu-core-hour
- compute_limit: 0
- compute_unit: gpu-device-hour
- run_limit: 0
- run_count_basis: planned-run
- per_attempt_cost_limit: 0
- per_attempt_compute_limit: 0
- per_attempt_compute_limit: 0
- concurrency_limit: 0
- retry_limit: 0
- valid_for_hours: 0
- valid_until: 未指定
"""

LOG_EXTRAS = (
    "batch_id",
    "plan",
    "mode",
    "user_confirmation",
    "confirmed_at",
    "confirmation_basis",
    "authorization_status",
    "run_id",
    "attempt_id",
    "worst_case_estimate",
    "started_at",
    "finished_at",
    "actual_consumption",
    "result_status",
    "artifact_paths",
)
POLICY_KEYS = (
    "scope",
    "cost_limit",
    "currency",
    "compute_limit",
    "compute_unit",
    "run_limit",
    "run_count_basis",
    "per_attempt_cost_limit",
    "per_attempt_compute_limit",
    "concurrency_limit",
    "retry_limit",
    "valid_for_hours",
    "valid_until",
)


def good_log() -> str:
    lines = ["# 研究日志", ""]
    for key in POLICY_KEYS + LOG_EXTRAS:
        lines.append(f"- {key}:")
    lines.append("")
    return "\n".join(lines)


GOOD_GATES = """# Setup

## 确认模型

Gate: model-confirm | before=role-table-write | approval=explicit-user | source=SKILL.md#确认模型

停下，直到本轮清单里的每个角色都经用户确认。

## 确认写入

Gate: write-confirm | before=workspace-write | approval=explicit-user | source=SKILL.md#确认写入

停下，直到用户明确同意整份草稿。
"""


FOREIGN_LINK = "paper-compile/references/diagnostics.md"


def run_check(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "--no-project", "python", str(CHECK), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def contract_output(result: subprocess.CompletedProcess[str]) -> str:
    lines = [
        line
        for line in (result.stdout + result.stderr).splitlines()
        if FOREIGN_LINK not in line
    ]
    return "\n".join(lines)


class ConfigContractTests(unittest.TestCase):
    def assert_fail(self, result: subprocess.CompletedProcess[str], needle: str) -> None:
        text = contract_output(result)
        self.assertNotEqual(result.returncode, 0, text)
        self.assertIn(needle, text)

    def assert_contract_ok(self, result: subprocess.CompletedProcess[str]) -> None:
        text = contract_output(result)
        self.assertNotIn("  - ", text, text)
        if FOREIGN_LINK not in result.stdout:
            self.assertEqual(result.returncode, 0, text)

    def test_valid_role_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roles.md"
            path.write_text(GOOD_ROLES, encoding="utf-8")
            result = run_check(["--role-file", str(path)])
        self.assert_contract_ok(result)

    def test_invalid_role_reference_and_incomplete_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_role = Path(tmp) / "roles.md"
            bad_role.write_text("orchestrator: cliproxy/grok-4.7 | medium\n", encoding="utf-8")
            bad_ref = Path(tmp) / "body.md"
            bad_ref.write_text("派给 Role: ghostwriter 做审查。\n", encoding="utf-8")
            role = run_check(["--role-file", str(bad_role)])
            ref = run_check(["--role-refs", str(bad_ref)])
        self.assert_fail(role, "literature")
        self.assert_fail(ref, "ghostwriter")

    def test_illegal_policy_values(self) -> None:
        cases = (
            ("unlimited", GOOD_POLICY.replace("cost_limit: 0", "cost_limit: unlimited")),
            ("-1", GOOD_POLICY.replace("run_limit: 0", "run_limit: -1")),
            ("NaN", GOOD_POLICY.replace("compute_limit: 0", "compute_limit: NaN", 1)),
            ("无单位", GOOD_POLICY.replace("compute_unit: cpu-core-hour", "compute_unit: tokens")),
            (
                "单次超过累计",
                GOOD_POLICY.replace("per_attempt_cost_limit: 0", "per_attempt_cost_limit: 1"),
            ),
            ("not-applicable", GOOD_POLICY.replace("currency: 未指定", "currency: not-applicable")),
        )
        for needle, text in cases:
            with self.subTest(needle=needle):
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "policy.md"
                    path.write_text(text, encoding="utf-8")
                    result = run_check(["--policy-file", str(path)])
                self.assert_fail(result, needle)

    def test_valid_policy_and_log_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            policy = Path(tmp) / "policy.md"
            log = Path(tmp) / "log.md"
            policy.write_text(GOOD_POLICY, encoding="utf-8")
            log.write_text(good_log(), encoding="utf-8")
            ok = run_check(["--policy-file", str(policy), "--log-file", str(log)])
            short = log.with_name("short.md")
            short.write_text("# 研究日志\n\n- batch_id:\n", encoding="utf-8")
            bad = run_check(["--policy-file", str(policy), "--log-file", str(short)])
        self.assert_contract_ok(ok)
        self.assert_fail(bad, "cost_limit")

    def test_gate_baseline_and_counterexamples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "setup-research-os"
            skill.mkdir()
            (skill / "SKILL.md").write_text(GOOD_GATES, encoding="utf-8")
            ok = run_check(["--gates-dir", str(skill), "--skill-name", "setup-research-os"])
            self.assert_contract_ok(ok)

            mutations = {
                "删一条": GOOD_GATES.replace(
                    "Gate: write-confirm | before=workspace-write | approval=explicit-user | source=SKILL.md#确认写入\n",
                    "",
                ),
                "全部none": "Gates: none\n",
                "改ID": GOOD_GATES.replace("model-confirm", "model-ok"),
                "重复": GOOD_GATES.replace(
                    "Gate: model-confirm | before=role-table-write | approval=explicit-user | source=SKILL.md#确认模型\n",
                    "Gate: model-confirm | before=role-table-write | approval=explicit-user | source=SKILL.md#确认模型\n"
                    "Gate: model-confirm | before=role-table-write | approval=explicit-user | source=SKILL.md#确认模型\n",
                    1,
                ),
                "坏source": GOOD_GATES.replace("SKILL.md#确认模型", "SKILL.md#不存在"),
                "整节删": "# Setup\n\n没有门。\n",
            }
            for needle, text in mutations.items():
                with self.subTest(needle=needle):
                    (skill / "SKILL.md").write_text(text, encoding="utf-8")
                    result = run_check(
                        ["--gates-dir", str(skill), "--skill-name", "setup-research-os"]
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shipped_templates_and_full_checker(self) -> None:
        policy = SETUP / "templates" / "compute-policy.md"
        roles = SETUP / "templates" / "research-os-models.md"
        log = SETUP / "templates" / "research-log.md"
        targeted = run_check(
            [
                "--policy-file",
                str(policy),
                "--role-template",
                str(roles),
                "--log-file",
                str(log),
                "--gates-dir",
                str(SETUP),
                "--skill-name",
                "setup-research-os",
            ]
        )
        full = run_check([])
        self.assert_contract_ok(targeted)
        self.assert_contract_ok(full)
        self.assertIn("不是运行授权", policy.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
