"""Installed public contracts for the two #60 residual findings."""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILLS_VERSION = "1.7.4"
PAPER_COMPILE_REPAIR = ROOT / "skills/writing-cycle/paper-compile-repair"
PAPER_COMPILE = ROOT / "skills/writing-cycle/paper-compile"
PAPER_CLAIM_AUDIT = ROOT / "skills/writing-cycle/paper-claim-audit"
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def external_compile_links(package: Path) -> list[tuple[str, str, Path]]:
    links: list[tuple[str, str, Path]] = []
    for document in sorted(package.rglob("*.md")):
        for target in MARKDOWN_LINK.findall(document.read_text(encoding="utf-8")):
            if "paper-compile/" in target:
                links.append(
                    (document.relative_to(package).as_posix(), target, document.parent / target)
                )
    return links


def canonical_compile_resource(target: str) -> Path:
    prefix = (
        "../paper-compile"
        if target.startswith("../paper-compile/")
        else "../../paper-compile"
    )
    return PAPER_COMPILE / Path(target).relative_to(prefix)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class InstalledResidualContracts(unittest.TestCase):
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
        cls.evidence_root = Path("/tmp/spec48-residual-contract-install/cli")
        cls.evidence_root.mkdir(parents=True, exist_ok=True)

    def new_install_root(self, name: str) -> tuple[Path, Path]:
        run = Path(tempfile.mkdtemp(prefix=f"{name}-", dir=self.evidence_root))
        project, home = run / "cwd", run / "home"
        project.mkdir()
        home.mkdir()
        return project, home

    def install(self, project: Path, home: Path, slug: str) -> Path:
        command = [
            "npx", "--offline", "--yes", f"skills@{SKILLS_VERSION}", "add",
            str(ROOT), "--skill", slug, "--agent", "claude-code", "--copy", "--yes",
        ]
        result = subprocess.run(
            command,
            cwd=project,
            env={
                **os.environ,
                "HOME": str(home),
                "TMPDIR": str(project.parent),
                "npm_config_cache": self.npm_cache,
            },
            capture_output=True,
            text=True,
            timeout=175,
        )
        print(f"CLI slug={slug} rc={result.returncode} cwd={project} home={home}")
        print(result.stdout, end="")
        print(result.stderr, end="")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        package = project / ".claude/skills" / slug
        self.assertTrue((package / "SKILL.md").is_file(), slug)
        return package

    def install_all(self) -> Path:
        run = Path(tempfile.mkdtemp(prefix="all-skills-", dir=self.evidence_root))
        project, home = run / "cwd", run / "home"
        project.mkdir()
        home.mkdir()
        result = subprocess.run(
            [
                "npx", "--offline", "--yes", f"skills@{SKILLS_VERSION}", "add",
                str(ROOT), "--skill", "*", "--agent", "claude-code", "--copy", "--yes",
            ],
            cwd=project,
            env={
                **os.environ,
                "HOME": str(home),
                "TMPDIR": str(run),
                "npm_config_cache": self.npm_cache,
            },
            capture_output=True,
            text=True,
            timeout=175,
        )
        print(f"CLI all rc={result.returncode} cwd={project} home={home}")
        print(result.stdout, end="")
        print(result.stderr, end="")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return project

    def test_repair_single_install_declares_dependency_and_scoped_blocks(self):
        project, home = self.new_install_root("repair-alone")
        package = self.install(project, home, "paper-compile-repair")
        links = external_compile_links(package)

        self.assertEqual(len(links), 7)
        self.assertEqual(sum(not target.resolve().is_file() for _, _, target in links), 7)

        skill = (package / "SKILL.md").read_text(encoding="utf-8")
        dependencies = (package / "references/external-resources.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("必需 sibling Skill `paper-compile`", skill)
        self.assertIn("并非单包自包含", skill)
        self.assertIn("缺失时只阻塞对应分支", dependencies)
        self.assertIn("只读盘点", dependencies)
        self.assertIn("TeX 输入闭合性", dependencies)
        self.assertIn("可验证 sandbox", dependencies)
        self.assertTrue((PAPER_COMPILE / "LICENSE").is_file())

    def test_source_and_flat_required_sibling_install_resolve_all_seven_edges(self):
        source_links = external_compile_links(PAPER_COMPILE_REPAIR)
        self.assertEqual(len(source_links), 7)
        self.assertTrue(all(target.resolve().is_file() for _, _, target in source_links))

        project, home = self.new_install_root("repair-with-required-sibling")
        repair = self.install(project, home, "paper-compile-repair")
        compile_skill = self.install(project, home, "paper-compile")
        self.assertEqual(compile_skill.parent, repair.parent)

        links = external_compile_links(repair)
        self.assertEqual(len(links), 7)
        self.assertTrue(all(target.resolve().is_file() for _, _, target in links))
        for document, target, installed in links:
            canonical = canonical_compile_resource(target)
            self.assertEqual(sha256(installed), sha256(canonical), f"{document}: {target}")
            print(
                f"EDGE {document} -> {target} sha256={sha256(installed)} "
                f"license={sha256(compile_skill / 'LICENSE')}"
            )

        build_pointer = repair / "references/build.md"
        build_target = MARKDOWN_LINK.findall(build_pointer.read_text(encoding="utf-8"))[0]
        build_path = (build_pointer.parent / build_target).resolve()
        self.assertTrue(build_path.is_file())
        build = build_path.read_text(encoding="utf-8")
        self.assertIn("有效父委托", build)
        self.assertIn("当轮完整 diff", build)
        self.assertIn("调用者先核实该委托覆盖当前 dirty 源", build)
        self.assertIn("拟 diff 所属的问题/目标/写域", build)
        self.assertIn("无需逐轮重新索权", build)
        self.assertIn("临时写域", build)
        self.assertIn("可落实", build)
        self.assertNotIn("修复模式仅在用户明确确认当前 dirty 文件及拟 diff 后写入", build)
        self.assertNotIn("用户明确批准临时写域和具体预算后", build)
        self.assertNotIn("在运行前让用户确认本次具体时间及资源预算", build)
        self.assertNotIn("获得临时写域与具体预算批准", build)
        self.assertIn("临时写域及具体资源预算同样须经独立调用明确批准", build)
        self.assertIn("由有效父委托明确覆盖", build)
        self.assertIn("预算是否由独立调用用户明确批准，或被仍有效的父委托覆盖", build)
        self.assertIn("临时写域和具体预算已由独立调用明确获批或被有效父委托覆盖", build)
        self.assertIn("输入闭合性", build)
        self.assertIn("构建前后检测并发变化", build)
        self.assertIn("TeX `openout`", build)
        self.assertIn("sandbox", build)
        self.assertIn("no-shell-escape", build)

        self.assertEqual(sha256(compile_skill / "LICENSE"), sha256(PAPER_COMPILE / "LICENSE"))

    def test_full_cli_install_resolves_the_same_flat_sibling_edges(self):
        project = self.install_all()
        repairs = sorted(
            path.parent for path in project.rglob("paper-compile-repair/SKILL.md")
        )
        self.assertEqual(repairs, [project / ".claude/skills/paper-compile-repair"])
        self.assertEqual(
            {path.name for path in project.iterdir() if path.is_dir()}, {".claude"}
        )
        self.assertEqual(
            {path.relative_to(project).as_posix() for path in project.rglob("skills") if path.is_dir()},
            {".claude/skills"},
        )
        self.assertFalse(any((project.parent / "home").rglob("SKILL.md")))

        checked_edges = 0
        for repair in repairs:
            compile_skill = repair.parent / "paper-compile"
            self.assertTrue((compile_skill / "SKILL.md").is_file(), str(repair))
            self.assertEqual(
                sha256(compile_skill / "LICENSE"), sha256(PAPER_COMPILE / "LICENSE")
            )
            links = external_compile_links(repair)
            self.assertEqual(len(links), 7, str(repair))
            for document, target, installed in links:
                self.assertTrue(installed.resolve().is_file(), f"{repair}: {target}")
                self.assertEqual(
                    sha256(installed), sha256(canonical_compile_resource(target)),
                    f"{repair}/{document}: {target}",
                )
                checked_edges += 1
        print(f"FULL INSTALL repair packages={len(repairs)} edges={checked_edges} all resolved")

    def test_full_install_argv_selects_all_skills_but_only_claude_code(self):
        # Inspect the process boundary without executing the unsafe all-agent alias.
        with patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            self.install_all()
        command = run.call_args.args[0]
        self.assertNotIn("--all", command)
        self.assertEqual(command[command.index("--skill") + 1], "*")
        self.assertEqual(command.count("--agent"), 1)
        self.assertEqual(command[command.index("--agent") + 1], "claude-code")
        self.assertIn("--copy", command)

    def test_claim_audit_returns_readonly_result_to_caller_within_existing_delegation(self):
        project, home = self.new_install_root("paper-claim-audit")
        package = self.install(project, home, "paper-claim-audit")
        skill = (package / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("论文与原始结果只读", skill)
        self.assertIn("额外费用、材料外发或外部能力须在用户授权内", skill)
        self.assertIn("不安装环境，不运行实验或编译，不自动改稿", skill)
        self.assertIn("本叶只读完成本职责", skill)
        self.assertIn("返回调用者", skill)
        self.assertIn("有效委托", skill)
        self.assertIn("不代做其他专项审计", skill)
        self.assertIn(
            "调用者可在仍有效的委托范围与额度内转交对应审计能力", skill
        )
        self.assertIn("无有效委托或新增范围须先取得用户授权", skill)
        self.assertNotIn("其他专项审计由用户另行点名", skill)
