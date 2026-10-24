# Ticket #50：迁入 swarm，交付宿主中立的并行覆盖能力。
# 验收对象是结构、合同与资源可达，不验证真实数学求解或全宿主行为。
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from spec48_checker_result import parse_checker_result

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
SWARM_SKILL = ROOT / "skills" / "general" / "swarm" / "SKILL.md"
SWARM_LICENSE = ROOT / "skills" / "general" / "swarm" / "LICENSE"
PLAYBOOK = ROOT / "skills" / "general" / "research-os" / "playbooks" / "swarm.md"
ENTRY = ROOT / "skills" / "general" / "research-os" / "SKILL.md"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_skills_50", CHECK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_checker() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECK)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


class UpstreamAttribution(unittest.TestCase):
    """AC1：核查固定上游正文与许可，MIT 版权文本随技能共置。"""

    def test_license_file_present_and_mit_with_upstream_holder(self):
        text = SWARM_LICENSE.read_text(encoding="utf-8")
        assert "MIT License" in text
        assert "Copyright (c) 2026 Lauren Tan" in text
        assert "Permission is hereby granted" in text

    def test_skill_records_upstream_source_and_revision(self):
        text = SWARM_SKILL.read_text(encoding="utf-8")
        assert "cursor/plugins" in text
        assert "88d47514b82e7c44f00f2b2a72ff6dd12158038c" in text
        assert "pstack" in text
        assert "改写" in text  # 记录适配范围，不是零改复制


class SwarmMechanism(unittest.TestCase):
    """AC2/AC4：分片、竞赛、混合组织与证据聚合机制保留。"""

    def setUp(self):
        self.text = SWARM_SKILL.read_text(encoding="utf-8")

    def test_four_phases_present(self):
        for phase in ("Frame", "Fan out", "Aggregate", "Report"):
            assert phase in self.text, f"缺阶段 {phase}"

    def test_shapes_slice_race_mixed(self):
        for marker in ("分片", "竞赛", "混合"):
            assert marker in self.text

    def test_selection_rule_declared_before_spawn(self):
        assert "first pass" in self.text
        assert "rank all" in self.text
        assert "best-of" in self.text
        assert re.search(r"派发前|Fan out 之前", self.text), "选择规则须在派发前声明"

    def test_done_predicate_declared_up_front(self):
        assert "完成条件" in self.text

    def test_independent_briefs(self):
        assert "独立 brief" in self.text

    def test_output_isolation(self):
        assert "输出隔离" in self.text

    def test_evidence_absent_result_not_pass_and_bounded_respawn(self):
        # 缺证据的结果不算通过；一次有界重派；二次缺失记缺口。
        assert "重派" in self.text
        assert "缺口" in self.text
        assert re.search(r"一次|1 次", self.text)
        assert re.search(r"缺口.{0,40}(不算|不作为|不能计)通过", self.text), "缺口不得计为通过"

    def test_aggregate_contract_has_bounded_retry_and_terminal_gap(self):
        checker = _load_checker()
        problems = checker.swarm_aggregate_contract_problems(self.text)
        assert problems == [], "Aggregate 缺少局部重派上限或最终缺口合同：\n" + "\n".join(problems)

    def test_aggregate_contract_rejects_missing_retry_cap_and_terminal_gap(self):
        checker = _load_checker()
        damaged_copies = (
            (
                "unbounded-retry.md",
                self.text.replace(
                    "剩余额度允许时最多重派一次，brief 里补写证据要求；否则直接记为缺口。第二次仍缺，记为缺口。",
                    "剩余额度允许时继续重派，直到证据完整。第二次仍缺，记为缺口。",
                ),
                "重派上限",
                "下一次会话",
            ),
            (
                "missing-terminal-gap.md",
                self.text.replace("第二次仍缺，记为缺口。", "第二次仍缺，保留原结果状态。"),
                "最终缺口",
                "缺口不算通过",
            ),
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            for filename, damaged_text, expected_problem, unrelated_phrase in damaged_copies:
                assert damaged_text != self.text
                assert unrelated_phrase in damaged_text  # 全文其他段落的措辞不得替代局部 Aggregate 合同。
                damaged_copy = Path(tmp_dir) / filename
                damaged_copy.write_text(damaged_text, encoding="utf-8")
                problems = checker.swarm_contract_problems(damaged_copy.read_text(encoding="utf-8"))
                assert any(expected_problem in problem for problem in problems), problems


class HostNeutrality(unittest.TestCase):
    """AC3：移除 Cursor/固定模型/个人目录绑定，用宿主真实子代理与项目角色。"""

    def setUp(self):
        self.text = SWARM_SKILL.read_text(encoding="utf-8")

    def test_no_cursor_or_fixed_model_bindings(self):
        lowered = self.text.lower()
        for banned in ("~/.cursor", "pstack-models", "grok-4.7", "environment: \"cloud\"", "cloud_base_branch"):
            assert banned not in lowered, f"残留固定绑定：{banned}"

    def test_uses_host_real_subagents_and_blocks_without(self):
        assert "子代理" in self.text
        assert "blocked" in self.text

    def test_resolves_model_from_project_role_table(self):
        assert "Role: implementer" in self.text
        assert ".agents/research-os-models.md" in self.text


class EntryDiscovery(unittest.TestCase):
    """AC5：安装后可独立读取并由入口引用；checker 为本票新增登记。"""

    def test_entry_has_swarm_route_and_playbook_exists(self):
        entry = ENTRY.read_text(encoding="utf-8")
        assert re.search(r"\|\s*swarm\s*\|", entry), "入口路由表缺 swarm 行"
        assert "swarm" in entry
        assert PLAYBOOK.is_file()

    def test_checker_registers_swarm_contract_check(self):
        checker = CHECK.read_text(encoding="utf-8")
        assert "swarm_contract_problems" in checker

    def test_swarm_registered_in_migrated_contract(self):
        module = _load_checker()
        assert "skills/general/swarm/SKILL.md" in module.MIGRATED_CONTRACT
        problems = module.swarm_contract_problems(SWARM_SKILL.read_text(encoding="utf-8"))
        assert problems == []

    def test_swarm_contract_check_catches_drift(self):
        module = _load_checker()
        text = SWARM_SKILL.read_text(encoding="utf-8")
        damaged = text.replace("重派", "")
        assert module.swarm_contract_problems(damaged), "损坏文本必须被 checker 报出"

    def test_readme_lists_swarm(self):
        for readme in (ROOT / "README.md", ROOT / "skills" / "README.md"):
            assert "general/swarm/SKILL.md" in readme.read_text(encoding="utf-8"), (
                f"{readme.name} 清单缺 general/swarm"
            )

    def test_migration_boundary_lists_swarm(self):
        text = (ROOT / "skills/general/research-os/references/migration-boundary.md").read_text(encoding="utf-8")
        assert "swarm" in text

    def test_full_checker_green_with_no_new_failures(self):
        result = _run_checker()
        assert not parse_checker_result(result)
        assert result.returncode == 0
