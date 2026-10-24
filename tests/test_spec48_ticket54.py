"""#54 交付形式化验证资产及对应审计能力。

期望来自 #48 spec（ID7、Testing #6）与 #54 票面，不从被测脚本反读。
默认结构 scope 不允许任何失败；历史身份严格 scope 另报未验证。
"""
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree
from spec48_checker_result import parse_checker_result

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-skills.py"
SKILLS = ROOT / "skills"
CREATE = SKILLS / "validation-cycle/create-formal-verification-skill"
MAINTAIN = SKILLS / "validation-cycle/maintain-formal-verification-skill"
BOUNDARY = SKILLS / "general/research-os/references/migration-boundary.md"
ENTRY = SKILLS / "general/research-os/SKILL.md"
UPSTREAM = "docs/upstream-sources-and-licenses.md"
REVISION = "88d47514b82e7c44f00f2b2a72ff6dd12158038c"

README_LIST = re.compile(r"\]\((?:skills/)?([a-z-]+/[a-z0-9-]+)/SKILL\.md\)")
KINDS = ("代码性质", "形式模型", "数学定理", "普通测试")
MODEL_PIN = re.compile(
    r"(?i)(gpt-[0-9]|claude-[0-9]|gemini-[0-9]|grok-[0-9]|deepseek-[a-z0-9]|glm-[0-9]|opus|sonnet)"
)
HOST_BINDINGS = ("Cursor", "~/.cursor", ".cursor/", "pstack-models", "/loop")


def load():
    spec = importlib.util.spec_from_file_location("check_skills_t54", CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load check-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discovered() -> set[str]:
    return {f"{p.parent.parent.name}/{p.parent.name}" for p in SKILLS.glob("*/*/SKILL.md")}


def problem_lines(root: Path) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check-skills.py")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return parse_checker_result(result)


def fresh_problems(root: Path) -> list[str]:
    return problem_lines(root)


def heading_set(text: str) -> set[str]:
    return {match.group(1).strip() for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, re.M)}


SKILL_TEMPLATE = (
    "---\nname: new-capability\ndescription: \"临时能力。\"\n"
    "disable-model-invocation: true\n---\n\n# New\n\nGates: none\n"
)


class WorkCopy:
    """可损坏副本：git 初始化后即等价于已追踪工作区。"""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "repo"
        copy_tracked_tree(ROOT, self.path)
        for command in (
            ["git", "init"],
            ["git", "add", "-f", "."],
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base"],
        ):
            subprocess.run(command, cwd=self.path, check=True, capture_output=True)

    def __enter__(self) -> "WorkCopy":
        return self

    def __exit__(self, *_exc) -> None:
        self._tmp.cleanup()

    def stage(self) -> None:
        subprocess.run(["git", "add", "-A"], cwd=self.path, check=True, capture_output=True)


class FormalSkillContract(unittest.TestCase):
    def test_both_skills_exist_with_license_notice_and_host_metadata(self):
        for skill_dir in (CREATE, MAINTAIN):
            name = skill_dir.name
            self.assertTrue((skill_dir / "SKILL.md").is_file(), name)
            license_text = (skill_dir / "LICENSE").read_text(encoding="utf-8")
            self.assertIn("MIT License", license_text, name)
            self.assertIn("Copyright (c) 2026 Lauren Tan", license_text, name)
            notice = (skill_dir / "NOTICE.md").read_text(encoding="utf-8")
            self.assertIn("cursor/plugins", notice, name)
            self.assertIn(REVISION, notice, name)
            self.assertIn("MIT", notice, name)
            yaml_text = (skill_dir / "agents/openai.yaml").read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: false", yaml_text, name)

    def test_frontmatter_is_explicit_invocation_and_migrated_to_mandate(self):
        for skill_dir in (CREATE, MAINTAIN):
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = text.split("---", 2)[1]
            self.assertIn(f"name: {skill_dir.name}", frontmatter)
            self.assertIn("disable-model-invocation: true", frontmatter)
            self.assertTrue(re.search(r"^description:\s*\S", frontmatter, re.M))
            self.assertRegex(text, r"(?m)^Gates: none$")
            self.assertNotRegex(text, r"(?m)^Gate: ")
            self.assertIn("委托继承", heading_set(text))

    def test_resources_are_co_located_and_self_contained(self):
        for rel in (
            "references/tool-selection.md",
            "references/assumption-ledger.md",
            "references/correspondence-audit.md",
            "templates/formal-verification-record.md",
        ):
            self.assertTrue((CREATE / rel).is_file(), rel)
        created = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        for target in ("references/tool-selection.md", "references/assumption-ledger.md",
                       "references/correspondence-audit.md",
                       "templates/formal-verification-record.md"):
            self.assertIn(target, created, target)


class QuestionChoosesTool(unittest.TestCase):
    def test_four_kinds_are_distinguished(self):
        texts = [
            (CREATE / "SKILL.md").read_text(encoding="utf-8"),
            (CREATE / "references/tool-selection.md").read_text(encoding="utf-8"),
        ]
        for text in texts:
            for kind in KINDS:
                self.assertIn(kind, text, kind)

    def test_question_not_toolchain_chooses_and_no_forced_full_chain(self):
        text = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        tools = (CREATE / "references/tool-selection.md").read_text(encoding="utf-8")
        self.assertIn("按问题选工具", text)
        self.assertIn("不强制全链", tools)
        self.assertIn("代码级", text + tools)
        self.assertIn("模型检查", text + tools)
        self.assertIn("没有可用验证器", tools)
        self.assertIn("测试", tools)

    def test_ordinary_tests_are_allowed_to_be_enough(self):
        text = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("普通测试", text)
        self.assertIn("够用", text)


class AssumptionVersionSync(unittest.TestCase):
    def test_ledger_records_assumptions_materials_versions_coverage_sync(self):
        ledger = (CREATE / "references/assumption-ledger.md").read_text(encoding="utf-8")
        for field in ("外部假设", "材料", "版本", "覆盖", "同步状态", "重验"):
            self.assertIn(field, ledger, field)
        record = (CREATE / "templates/formal-verification-record.md").read_text(encoding="utf-8")
        for field in ("外部假设与材料", "同步状态", "commit", "重验触发条件"):
            self.assertIn(field, record, field)

    def test_sync_status_markers_are_documented(self):
        create = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        maintain = (MAINTAIN / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("同步", create)
        self.assertIn("commit", create)
        self.assertIn("失效", create)
        self.assertIn("同步", maintain)
        self.assertIn("stale", maintain)
        self.assertIn("blocked", maintain)


class CorrespondenceAudit(unittest.TestCase):
    def test_original_problem_definition_and_statement_are_audited(self):
        text = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        audit = (CREATE / "references/correspondence-audit.md").read_text(encoding="utf-8")
        for part in ("原问题", "编码定义", "定理"):
            self.assertIn(part, text, part)
            self.assertIn(part, audit, part)
        for item in ("量词", "假设", "边界", "对象"):
            self.assertIn(item, audit, item)

    def test_placeholders_compile_and_finite_numbers_cannot_stand_for_theorem(self):
        text = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        audit = (CREATE / "references/correspondence-audit.md").read_text(encoding="utf-8")
        for phrase in ("占位符", "编译成功", "有限数值"):
            self.assertIn(phrase, text, phrase)
            self.assertIn(phrase, audit, phrase)
        self.assertIn("不得记为", text)
        self.assertIn("不得冒充", audit)

    def test_maintenance_repeats_the_correspondence_audit(self):
        text = (MAINTAIN / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("对应审计", text)
        self.assertIn("原问题", text)
        self.assertIn("占位符", text)


class FaultExposureAndDraft(unittest.TestCase):
    def test_checks_must_be_seen_to_fail(self):
        create = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        maintain = (MAINTAIN / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("故障暴露", create)
        self.assertIn("能够失败", create)
        self.assertIn("破坏", maintain)
        self.assertIn("抓住", maintain)

    def test_unexecuted_assets_are_drafts(self):
        create = (CREATE / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("草稿", create)
        self.assertIn("从未被执行", create)
        self.assertIn("草稿", (CREATE / "templates/formal-verification-record.md").read_text(encoding="utf-8"))


class HostNeutrality(unittest.TestCase):
    def test_no_cursor_personal_directory_or_fixed_model_binding(self):
        # NOTICE.md 是来源归属，必须点名上游；宿主绑定检查只看产品指令与宿主元数据。
        for skill_dir in (CREATE, MAINTAIN):
            for rel in ("SKILL.md", "agents/openai.yaml"):
                text = (skill_dir / rel).read_text(encoding="utf-8")
                for binding in HOST_BINDINGS:
                    self.assertNotIn(binding, text, f"{skill_dir.name}/{rel}: {binding}")
                self.assertIsNone(MODEL_PIN.search(text), f"{skill_dir.name}/{rel} 绑定固定模型")

    def test_subagent_is_a_prerequisite_and_missing_capability_blocks(self):
        for skill_dir in (CREATE, MAINTAIN):
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("子代理", text)
            self.assertIn("blocked", text)
            self.assertIn("宿主", text)

    def test_proof_family_is_not_rewritten(self):
        for skill_dir in (CREATE, MAINTAIN):
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("proof 族", text)


class Registration(unittest.TestCase):
    def test_migrated_and_readme_and_entry_pointer(self):
        module = load()
        for skill_dir in (CREATE, MAINTAIN):
            rel = f"skills/validation-cycle/{skill_dir.name}/SKILL.md"
            self.assertEqual(module.MIGRATED_CONTRACT.get(rel), "委托继承", rel)
            self.assertNotIn(rel, module.LEGACY_LEAF_GATES, rel)
        boundary = BOUNDARY.read_text(encoding="utf-8")
        for skill_dir in (CREATE, MAINTAIN):
            self.assertIn(skill_dir.name, boundary)
        for name in ("README.md", "skills/README.md"):
            listed = set(README_LIST.findall((ROOT / name).read_text(encoding="utf-8")))
            self.assertTrue(listed <= discovered(), name)
            for skill_dir in (CREATE, MAINTAIN):
                self.assertIn(f"validation-cycle/{skill_dir.name}", listed, name)
        self.assertIn("create-formal-verification-skill", ENTRY.read_text(encoding="utf-8"))
        upstream = (ROOT / UPSTREAM).read_text(encoding="utf-8")
        self.assertIn(REVISION, upstream)
        self.assertIn("create-formal-verification-skill", upstream)

    def test_current_tree_has_no_new_breakage(self):
        self.assertEqual(fresh_problems(ROOT), [])

    def test_checker_has_independent_formal_contract_function(self):
        module = load()
        self.assertTrue(callable(getattr(module, "formal_verification_problems", None)))
        text = CHECK.read_text(encoding="utf-8")
        self.assertIn("formal_verification_problems(ROOT", text)


class CheckerCounterexamples(unittest.TestCase):
    def test_dropped_kind_distinction_is_red(self):
        with WorkCopy() as work:
            path = work.path / (CREATE / "references/tool-selection.md").relative_to(ROOT)
            path.write_text(
                path.read_text(encoding="utf-8").replace("形式模型", "模型", 1), encoding="utf-8"
            )
            work.stage()
            self.assertIn("形式模型", "\n".join(problem_lines(work.path)))

    def test_fixed_model_binding_is_red(self):
        with WorkCopy() as work:
            path = work.path / (MAINTAIN / "SKILL.md").relative_to(ROOT)
            path.write_text(
                path.read_text(encoding="utf-8") + "\n本步固定使用 claude-4-opus。\n",
                encoding="utf-8",
            )
            work.stage()
            self.assertIn("固定模型", "\n".join(problem_lines(work.path)))

    def test_dropped_draft_marking_is_red(self):
        with WorkCopy() as work:
            path = work.path / (CREATE / "SKILL.md").relative_to(ROOT)
            path.write_text(
                path.read_text(encoding="utf-8").replace("草稿", "结果"), encoding="utf-8"
            )
            work.stage()
            self.assertIn("草稿", "\n".join(problem_lines(work.path)))

    def test_dropped_license_is_red(self):
        with WorkCopy() as work:
            (work.path / (MAINTAIN / "LICENSE").relative_to(ROOT)).unlink()
            work.stage()
            self.assertIn("LICENSE", "\n".join(problem_lines(work.path)))

    def test_unregistered_formal_skill_is_red(self):
        with WorkCopy() as work:
            path = work.path / "scripts/check-skills.py"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                '    "skills/validation-cycle/create-formal-verification-skill/SKILL.md": "委托继承",\n',
                "",
                1,
            )
            path.write_text(text, encoding="utf-8")
            work.stage()
            self.assertIn("缺少门声明基线", "\n".join(problem_lines(work.path)))


class FlatInstall(unittest.TestCase):
    def test_both_skills_install_flat_with_reachable_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for skill_dir in (CREATE, MAINTAIN):
                shutil.copytree(skill_dir, root / skill_dir.name)
            for skill_dir in (root / CREATE.name, root / MAINTAIN.name):
                self.assertTrue((skill_dir / "LICENSE").is_file())
                self.assertTrue((skill_dir / "SKILL.md").is_file())
                for md in skill_dir.rglob("*.md"):
                    body = md.read_text(encoding="utf-8")
                    for target in re.findall(r"\]\(([^)\s]+)\)", body):
                        if target.startswith(("http://", "https://", "#", "mailto:")):
                            continue
                        clean = target.split("#")[0]
                        resolved = (md.parent / clean).resolve()
                        self.assertTrue(resolved.is_file(), f"{md.name}: {target}")
            self.assertTrue((root / CREATE.name / "templates/formal-verification-record.md").is_file())


if __name__ == "__main__":
    unittest.main()
