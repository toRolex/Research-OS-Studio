"""Targeted public skill-contract regressions; real behavior is Seam B evidence."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AcceptRemediationContract(unittest.TestCase):
    def test_ml_build_attempts_share_one_budget(self):
        text = (ROOT / 'skills/writing-cycle/ml-paper-writing/SKILL.md').read_text()
        for clause in ('失败构建也计一次', '同一累计编译次数', '已用次数、上限、剩余次数', '旧 PDF'):
            self.assertIn(clause, text)

    def test_idea_dispatch_and_canonical_keep_original_feedback(self):
        review = (ROOT / 'skills/idea-cycle/idea-review/SKILL.md').read_text()
        composition = (ROOT / 'skills/idea-cycle/idea-discovery/references/composition-notes.md').read_text()
        self.assertIn('派发前逐字段核对', review)
        self.assertIn('移除排名', review)
        self.assertIn('逐字完整内联', composition)
        self.assertIn('链接或摘要不替代', composition)

    def test_talk_severe_gate_build_bucket_and_review_version(self):
        text = (ROOT / 'skills/writing-cycle/paper-talk/SKILL.md').read_text()
        for clause in ('严重发现逐项确认', '一般 unattended', '失败编译也计一次', '最新实际渲染', '先前审查不能继承'):
            self.assertIn(clause, text)

    def test_playbook_copy_is_verbatim_not_summary(self):
        text = (ROOT / 'skills/general/research-os/SKILL.md').read_text()
        self.assertIn('保留编号、原句及子列表', text)
        self.assertIn('逐项直接对照 playbook', text)


if __name__ == '__main__':
    unittest.main()
