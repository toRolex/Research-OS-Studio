"""Spec #48 ticket #52：迁入 interrogate，交付独立挑战与主审判断。

只测结构合同与文本合同；不宣称数学审查质量或全宿主行为已被验证。
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "general" / "interrogate"
sys.path.insert(0, str(ROOT / "scripts"))

_spec = importlib.util.spec_from_file_location(
    "check_skills", ROOT / "scripts" / "check-skills.py"
)
assert _spec is not None and _spec.loader is not None
check_skills = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_skills)


def read(rel: str) -> str:
    return (SKILL_DIR / rel).read_text(encoding="utf-8")


class Structure(unittest.TestCase):
    def test_skill_files_exist(self):
        required = [
            "SKILL.md",
            "agents/openai.yaml",
            "LICENSE",
            "references/reviewer-prompt.md",
            "references/rubric.md",
            "references/code-quality-review.md",
            "references/lead-judgment.md",
            "references/research-review.md",
            "references/PROVENANCE.md",
        ]
        for rel in required:
            assert (SKILL_DIR / rel).is_file(), rel

    def test_openai_yaml_disallows_implicit_invocation(self):
        text = read("agents/openai.yaml")
        assert "interrogate" in text
        assert "false" in text


class DelegationContract(unittest.TestCase):
    def test_mandate_inheritance_section(self):
        text = read("SKILL.md")
        assert "## 委托继承" in text
        assert "Gates: none" in text
        assert "mandate" in text or "委托" in text

    def test_readonly_no_auto_apply(self):
        text = read("SKILL.md")
        assert "只读" in text
        assert "不自动" in text  # 不自动修订/不自动应用
        # 修复归属：由编排者按授权组织，不在本调用内
        assert "编排" in text
        assert "授权" in text

    def test_host_neutral_no_fixed_models(self):
        text = read("SKILL.md")
        for banned in ("cursor", "claude-opus", "grok-4", "composer-"):
            assert banned not in text.lower(), banned
        assert ".agents/research-os-models.md" in text  # 项目角色表解析 reviewer 模型
        assert "子代理" in text
        assert "blocked" in text

    def test_registered_in_migrated_contract(self):
        assert (
            check_skills.MIGRATED_CONTRACT.get("skills/general/interrogate/SKILL.md")
            == "委托继承"
        )


class FindingsContract(unittest.TestCase):
    def test_dedup_and_attribution(self):
        text = read("SKILL.md")
        assert "去重" in text or "合并" in text  # 同一问题不同表述合并
        assert "模型" in text and ("哪个" in text or "哪些" in text)  # 记录谁提出

    def test_disagreements_retained(self):
        text = read("SKILL.md")
        assert "分歧" in text
        assert "相反" in text or "不一致" in text

    def test_lead_judgment_four_buckets(self):
        text = read("SKILL.md")
        for bucket in ("Act on", "Consider", "Noted", "Dismissed"):
            assert bucket in text, bucket
        assert "主审" in text
        # 每条判断带理由
        assert "理由" in text or "rationale" in read("references/lead-judgment.md")

    def test_reviewer_prompt_template(self):
        text = read("references/reviewer-prompt.md")
        assert "{INTENT}" in text or "Intent" in text
        assert "readonly" in text.lower() or "只读" in text
        assert "no findings" in text.lower() or "无发现" in text  # 空审查合法


class ResearchLens(unittest.TestCase):
    def test_research_reference_covers_materials_and_obligations(self):
        text = read("references/research-review.md")
        assert "证明义务" in text
        assert "材料" in text
        # finding 必须引用具体命题/步骤
        assert "具体" in text

    def test_renamed_lemma_not_progress(self):
        text = read("references/research-review.md")
        assert "等强" in text or "换名" in text or "改写" in text

    def test_consensus_is_not_mathematical_evidence(self):
        text = read("references/research-review.md")
        assert "共识" in text or "重合" in text
        assert "证据" in text

    def test_numerical_results_stay_candidates(self):
        text = read("references/research-review.md")
        assert "数值" in text or "计算" in text
        assert "候选" in text


class ProvenanceAndLicense(unittest.TestCase):
    def test_provenance_records_upstream_revision(self):
        text = read("references/PROVENANCE.md")
        assert "88d47514b82e7c44f00f2b2a72ff6dd12158038c" in text
        assert "MIT" in text
        assert "Lauren Tan" in text

    def test_license_coloated(self):
        text = read("LICENSE")
        assert "MIT License" in text
        assert "Lauren Tan" in text

    def test_upstream_mechanisms_retained(self):
        # rubric / code-quality / lead-judgment 是上游正文，不得只剩摘要
        assert len(read("references/rubric.md")) > 3000
        assert "Nitpick Gravity" in read("references/lead-judgment.md")
        assert "code judo" in read("references/code-quality-review.md")


class Registration(unittest.TestCase):
    def test_readmes_list_interrogate(self):
        for readme in ("README.md", "skills/README.md"):
            text = (ROOT / readme).read_text(encoding="utf-8")
            assert "general/interrogate/SKILL.md" in text, readme

    def test_entry_declares_installable_interrogate_slug_without_cross_skill_link(self):
        text = (ROOT / "skills/general/research-os/SKILL.md").read_text(encoding="utf-8")
        assert "interrogate" in text
        assert "`interrogate`" in text
        assert "只阻塞依赖它的分支" in text
        assert "../interrogate/SKILL.md" not in text

    def test_checker_function_registered_and_clean(self):
        text = read("SKILL.md")
        problems = check_skills.interrogate_contract_problems(text)
        assert problems == [], problems


class NoNewRegression(unittest.TestCase):
    def test_checker_clean_on_new_skill(self):
        skill_text = read("SKILL.md")
        assert check_skills.interrogate_contract_problems(skill_text) == []


class ReviewerSetAndIsolation(unittest.TestCase):
    def roles(self):
        template = (ROOT / "skills/general/setup-research-os/templates/research-os-models.md").read_text(encoding="utf-8")
        return template.replace("example/replace-with-live-model", "test-provider/model-a")

    def contract(self):
        text = read("SKILL.md")
        match = re.search(r"(?ms)^### Reviewer dispatch contract\s*\n```json\n(.*?)\n```", text)
        self.assertIsNotNone(match, "interrogate needs an explicit call-local reviewer set")
        return json.loads(match.group(1))

    def test_standard_unique_setup_role_resolves_two_fresh_reviewers(self):
        roles = self.roles()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roles.md"
            path.write_text(roles, encoding="utf-8")
            prior = list(check_skills.problems)
            check_skills.check_role_file(path, "fixture roles")
            self.assertEqual(check_skills.problems, prior)
        self.assertEqual(sum(line.startswith("reviewer:") for line in roles.splitlines()), 1)
        rows = check_skills.resolve_interrogate_reviewers(self.contract(), roles)
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["model"] for row in rows}, {"test-provider/model-a"})
        self.assertEqual(len({row["id"] for row in rows}), 2)

    def test_explicit_multimodel_set_does_not_add_global_role_rows(self):
        contract = self.contract()
        contract["require_distinct_models"] = True
        contract["reviewers"][1] = {
            "id": "B", "source": "explicit", "model": "test-provider/model-b",
            "thinking": "high", "authority": "original mandate explicitly permits B",
        }
        rows = check_skills.resolve_interrogate_reviewers(contract, self.roles())
        self.assertEqual({row["model"] for row in rows}, {"test-provider/model-a", "test-provider/model-b"})
        contract["reviewers"][1]["authority"] = ""
        with self.assertRaises(ValueError):
            check_skills.resolve_interrogate_reviewers(contract, self.roles())

    def test_duplicate_global_roles_and_insufficient_multimodel_set_rejected(self):
        with self.assertRaises(ValueError):
            check_skills.resolve_interrogate_reviewers(self.contract(), self.roles() + "\nreviewer: test-provider/model-b | high\n")
        contract = self.contract()
        contract["require_distinct_models"] = True
        with self.assertRaises(ValueError):
            check_skills.resolve_interrogate_reviewers(contract, self.roles())

    def test_missing_role_and_incomplete_set_are_blocked_not_implicit_fallback(self):
        with self.assertRaisesRegex(ValueError, "blocked"):
            check_skills.resolve_interrogate_reviewers(self.contract(), "")
        contract = self.contract()
        contract["reviewers"] = contract["reviewers"][:1]
        with self.assertRaisesRegex(ValueError, "blocked"):
            check_skills.resolve_interrogate_reviewers(contract, self.roles())

    def test_transparent_session_sources_cannot_override_selected_role(self):
        contract = self.contract()
        contract["reviewers"] = [
            {"id": label, "source": "session", "model": "test-provider/model-a",
             "thinking": "medium", "authority": "missing role; verified session catalog"}
            for label in ("A", "B")
        ]
        self.assertEqual(len(check_skills.resolve_interrogate_reviewers(contract, "")), 2)
        with self.assertRaises(ValueError):
            check_skills.resolve_interrogate_reviewers(contract, self.roles())

    def test_negated_peer_read_rule_and_later_lead_synthesis_are_valid(self):
        source = read("SKILL.md")
        valid = source.replace(
            "reviewer 各自给出 findings，互相不可见。",
            "reviewer 各自给出 findings；后续 reviewer 不得先读前序 reviewer 的 findings 再形成判断。",
        )
        self.assertEqual(check_skills.interrogate_contract_problems(valid), [])
        contract = self.contract()
        contract["reviewer_inputs"] = ["rubric", "intent", "source_material"]
        self.assertEqual(len(check_skills.resolve_interrogate_reviewers(contract, self.roles())), 2)

    def test_malformed_explicit_thinking_is_rejected_without_crashing(self):
        contract = self.contract()
        contract["reviewers"][1] = {
            "id": "B", "source": "explicit", "model": "test-provider/model-b",
            "thinking": [], "authority": "original mandate",
        }
        with self.assertRaises(ValueError):
            check_skills.resolve_interrogate_reviewers(contract, self.roles())

    def test_original_report_peer_read_mutant_is_rejected(self):
        source = read("SKILL.md")
        before = "reviewer 各自给出 findings，互相不可见。"
        after = "reviewer 各自给出 findings；后续 reviewer 必须先读前序 reviewer 的 findings 再形成判断。"
        self.assertEqual(source.count(before), 1)
        self.assertTrue(check_skills.interrogate_contract_problems(source.replace(before, after)))

    def test_structural_peer_input_and_shared_context_mutants_rejected(self):
        for key, value in (
            ("reviewer_reads_peer_findings", True), ("context", "shared"),
            ("reviewer_inputs", ["intent", "source_material", "rubric", "peer_findings"]),
            ("lead_reads_after", "each_reviewer"),
        ):
            contract = self.contract()
            contract[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                check_skills.resolve_interrogate_reviewers(contract, self.roles())
