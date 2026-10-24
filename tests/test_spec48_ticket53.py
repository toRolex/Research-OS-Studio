"""#53 交付可创建、维护的项目行为验证能力。

期望来自 #48 spec（决策 6、Testing #6/#4）与 #53 票面，不从被测脚本反读。覆盖：
许可与共置资源、创建侧真实启动/健康/驱动/证据/清理/覆盖映射机制、维护侧三态
结果与覆盖要求、草稿与失败如实报告、helper 正反例、宿主中立与迁移登记。
默认结构检查须真实通过；历史身份单独报告，不允许任何失败基线。
"""
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
SKILLS = ROOT / "skills"
CREATE = SKILLS / "validation-cycle/create-verification-skill"
MAINTAIN = SKILLS / "validation-cycle/maintain-verification-skill"
HELPER = CREATE / "helpers" / "feature-map-lint.py"
BOUNDARY = SKILLS / "general/research-os/references/migration-boundary.md"
UPSTREAM_REVISION = "88d47514b82e7c44f00f2b2a72ff6dd12158038c"

MODEL_PIN = re.compile(
    r"(?i)(gpt-[0-9]|claude-[0-9]|gemini-[0-9]|grok-[0-9]|deepseek-[a-z0-9]|glm-[0-9]|opus|sonnet)"
)
HOST_BINDINGS = ("Cursor", "~/.cursor", ".cursor/", "pstack-models", "/loop")


def load():
    spec = importlib.util.spec_from_file_location("check_skills_t53", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def problem_lines(root: Path) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return parse_checker_result(result)


def tracked(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
    )
    return set(result.stdout.splitlines())


class LicenseAndProvenance(unittest.TestCase):
    def test_license_is_upstream_mit(self):
        for skill in (CREATE, MAINTAIN):
            with self.subTest(skill=skill.name):
                text = (skill / "LICENSE").read_text(encoding="utf-8")
                self.assertIn("MIT License", text)
                self.assertIn("Copyright (c) 2026 Lauren Tan", text)
                self.assertIn("Permission is hereby granted", text)

    def test_notice_records_revision_and_scope(self):
        for skill in (CREATE, MAINTAIN):
            with self.subTest(skill=skill.name):
                notice = (skill / "NOTICE.md").read_text(encoding="utf-8")
                self.assertIn(UPSTREAM_REVISION, notice)
                self.assertIn("cursor/plugins", notice)
                self.assertIn("采用与适配范围", notice)


class CreateSkillContract(unittest.TestCase):
    def setUp(self):
        self.text = (CREATE / "SKILL.md").read_text(encoding="utf-8")

    def test_mechanism_markers_present(self):
        for marker in (
            "启动", "健康检查", "驱动", "证据", "清理", "覆盖映射", "doctor",
            "草稿", "blocked", "委托继承", "特征映射",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.text)

    def test_draft_and_failure_honesty(self):
        self.assertIn("只能标为草稿", self.text)
        self.assertIn("执行失败或项目不可达时如实说明", self.text)
        self.assertIn("证据", self.text)
        self.assertIn("清理后保留证据", self.text)

    def test_no_host_or_model_binding(self):
        for binding in HOST_BINDINGS:
            self.assertNotIn(binding, self.text)
        self.assertIsNone(MODEL_PIN.search(self.text))

    def test_separation_from_formal(self):
        self.assertIn("不宣称数学定理成立", self.text)
        self.assertIn("create-formal-verification-skill", self.text)

    def test_feature_map_example_files(self):
        example = CREATE / "references" / "feature-map-example"
        for name in ("README.md", "search.md", "create-record.md"):
            self.assertTrue((example / name).is_file(), name)
        readme = (example / "README.md").read_text(encoding="utf-8")
        for name in ("search.md", "create-record.md"):
            self.assertIn(f"]({name})", readme)

    def test_coLocated_assets_tracked(self):
        tracked_paths = tracked(ROOT)
        for rel in (
            "SKILL.md", "LICENSE", "NOTICE.md", "agents/openai.yaml",
            "references/feature-map-example/README.md", "helpers/feature-map-lint.py",
        ):
            self.assertIn(f"skills/validation-cycle/create-verification-skill/{rel}", tracked_paths)

    def test_agent_yaml_disallows_implicit(self):
        yaml_text = (CREATE / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", yaml_text)


class MaintainSkillContract(unittest.TestCase):
    def setUp(self):
        self.text = (MAINTAIN / "SKILL.md").read_text(encoding="utf-8")

    def test_outcomes_and_coverage_markers(self):
        for marker in (
            "clean", "changed", "blocked", "只改验证", "源读波", "现场驱动",
            "doctor", "证据", "清理", "verified-unreachable", "委托继承",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.text)

    def test_coverage_requirements_distinct_from_create(self):
        create_text = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("每个特征文件都要有源覆盖", self.text)
        self.assertIn("每个特征都要被真实驱动一次", self.text)
        self.assertIn("一个已映射特征（一个就够", create_text)

    def test_no_host_or_model_binding(self):
        for binding in HOST_BINDINGS:
            self.assertNotIn(binding, self.text)
        self.assertIsNone(MODEL_PIN.search(self.text))

    def test_separation_from_formal(self):
        self.assertIn("maintain-formal-verification-skill", self.text)

    def test_coLocated_assets_tracked(self):
        tracked_paths = tracked(ROOT)
        for rel in ("SKILL.md", "LICENSE", "NOTICE.md", "agents/openai.yaml"):
            self.assertIn(f"skills/validation-cycle/maintain-verification-skill/{rel}", tracked_paths)

    def test_agent_yaml_disallows_implicit(self):
        yaml_text = (MAINTAIN / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", yaml_text)


class FeatureMapLintHelper(unittest.TestCase):
    """随附 helper 的最小正反例：不建专用科研测试 runtime。"""

    def run_helper(self, target: Path) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as tmp:
            features = Path(tmp) / "features"
            features.mkdir()
            if target == CREATE / "references" / "feature-map-example":
                for source in target.iterdir():
                    if source.is_file() and source.suffix == ".md":
                        (features / source.name).write_bytes(source.read_bytes())
            else:
                for source in target.glob("*.fixture"):
                    name = source.name.removesuffix(".fixture") + ".md"
                    (features / name).write_bytes(source.read_bytes())
            return subprocess.run(
                [sys.executable, str(HELPER), str(features)],
                capture_output=True, text=True,
            )

    def test_positive_example_passes(self):
        result = self.run_helper(CREATE / "references" / "feature-map-example")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_commented_links_do_not_index_features(self):
        with tempfile.TemporaryDirectory() as tmp:
            features = Path(tmp)
            (features / "account.md").write_text("# Account\n", encoding="utf-8")
            for comment in (
                "<!-- [Account](account.md) -->",
                "<!--\n[Account](account.md)\n-->",
                "<!--\n[Account](account.md)\n",
            ):
                with self.subTest(comment=comment):
                    (features / "README.md").write_text(comment, encoding="utf-8")
                    result = subprocess.run(
                        [sys.executable, str(HELPER), str(features)],
                        capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn("account.md", result.stderr)

    def test_visible_link_after_comment_still_indexes_feature(self):
        with tempfile.TemporaryDirectory() as tmp:
            features = Path(tmp)
            (features / "account.md").write_text("# Account\n", encoding="utf-8")
            (features / "README.md").write_text(
                "<!-- [old](missing.md) -->\n[Account](account.md)\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(HELPER), str(features)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_fragment_destinations_and_external_urls(self):
        fixtures = Path(__file__).parent / "fixtures" / "ticket53"
        good_anchor = self.run_helper(fixtures / "anchor-good")
        self.assertEqual(good_anchor.returncode, 0, good_anchor.stderr)

        bad_anchor = self.run_helper(fixtures / "anchor-dead-bad")
        self.assertEqual(bad_anchor.returncode, 1)
        self.assertIn("missing.md#details", bad_anchor.stderr)

        external = self.run_helper(fixtures / "external-good")
        self.assertEqual(external.returncode, 0, external.stderr)

        spaced = self.run_helper(fixtures / "title-good")
        self.assertEqual(spaced.returncode, 0, spaced.stderr)

        root_relative = self.run_helper(fixtures / "root-relative-bad")
        self.assertEqual(root_relative.returncode, 1)
        self.assertIn("account.md", root_relative.stderr)

    def test_negative_examples_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            features = d / "features"
            features.mkdir()
            (features / "README.md").write_text("# 索引\n\n- [a](a.md)\n", encoding="utf-8")
            (features / "a.md").write_text("# a\n", encoding="utf-8")
            (features / "b.md").write_text("# b\n", encoding="utf-8")  # 孤儿
            orphan = subprocess.run(
                [sys.executable, str(HELPER), str(features)],
                capture_output=True, text=True,
            )
            self.assertEqual(orphan.returncode, 1)
            self.assertIn("b.md", orphan.stderr)
            (features / "README.md").write_text("# 索引\n\n- [a](a.md)\n- [死链](missing.md)\n", encoding="utf-8")
            (features / "b.md").unlink()
            dead = subprocess.run(
                [sys.executable, str(HELPER), str(features)],
                capture_output=True, text=True,
            )
            self.assertEqual(dead.returncode, 1)
            self.assertIn("missing.md", dead.stderr)

    def test_helper_is_executable(self):
        import os
        self.assertTrue(os.access(HELPER, os.X_OK))


class RegistrationAndEntry(unittest.TestCase):
    def test_checker_reports_no_new_failures(self):
        lines = problem_lines(ROOT)
        self.assertEqual(lines, [], "不允许任何 checker 结构失败")

    def test_checker_crash_is_not_filtered_as_a_historical_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            scripts.mkdir()
            for source in (
                "import sys\nprint('checker crashed', file=sys.stderr)\nsys.exit(2)\n",
                "import sys\nprint('FAIL: 0 个问题')\nprint('checker crashed', file=sys.stderr)\nsys.exit(1)\n",
                "print('checker crashed')\nraise SystemExit(1)\n",
                "print('HISTORY PASS: fake.tar.gz')\nprint('OK: fake')\n",
            ):
                (scripts / "check-skills.py").write_text(source, encoding="utf-8")
                with self.subTest(source=source), self.assertRaises(AssertionError):
                    problem_lines(root)

    def test_create_skill_requires_object_bound_evidence_contract(self):
        text = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "证据归属与失效", "代码 revision", "工作区脏改动",
            "关键输入/数据与依赖和工具链版本", "验证资产版本", "适用范围与假设",
            "stale", "不得为新对象背书", "重跑受影响覆盖",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_maintain_skill_requires_object_bound_evidence_contract(self):
        text = (MAINTAIN / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "证据归属与失效", "代码 revision", "工作区脏改动",
            "关键输入/数据与依赖和工具链版本", "验证资产版本", "适用范围与假设",
            "stale", "不得为新对象背书", "重跑受影响覆盖",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_migration_boundary_lists_both(self):
        text = BOUNDARY.read_text(encoding="utf-8")
        for name in ("create-verification-skill", "maintain-verification-skill"):
            self.assertIn(name, text)

    def test_readme_lists_both(self):
        for readme in (ROOT / "README.md", ROOT / "skills/README.md"):
            with self.subTest(readme=readme.name):
                text = readme.read_text(encoding="utf-8")
                prefix = "skills/validation-cycle/" if readme.parent == ROOT else "validation-cycle/"
                self.assertIn(f"]({prefix}create-verification-skill/SKILL.md)", text)
                self.assertIn(f"]({prefix}maintain-verification-skill/SKILL.md)", text)

    def test_entry_points_to_new_skills(self):
        entry = (SKILLS / "general/research-os/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("create-verification-skill", entry)
        self.assertIn("maintain-verification-skill", entry)

    def test_checker_registers_verification_check(self):
        module = load()
        self.assertTrue(callable(module.verification_skill_problems))


if __name__ == "__main__":
    unittest.main()
