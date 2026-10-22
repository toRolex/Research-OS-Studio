"""Spec #48 ticket #52：迁入 interrogate，交付独立挑战与主审判断。

只测结构合同与文本合同；不宣称数学审查质量或全宿主行为已被验证。
"""
from __future__ import annotations

import importlib.util
import sys
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

    def test_entry_pointer(self):
        text = (ROOT / "skills/general/research-os/SKILL.md").read_text(encoding="utf-8")
        assert "interrogate" in text
        assert "../interrogate/SKILL.md" in text

    def test_checker_function_registered_and_clean(self):
        text = read("SKILL.md")
        problems = check_skills.interrogate_contract_problems(text)
        assert problems == [], problems


class NoNewRegression(unittest.TestCase):
    def test_checker_clean_on_new_skill(self):
        skill_text = read("SKILL.md")
        assert check_skills.interrogate_contract_problems(skill_text) == []
