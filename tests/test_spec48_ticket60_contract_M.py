"""#60 proof-controller retirement seam: preserve resources, remove callers.

This slice verifies the installed Skill boundary and declared routing contract;
it does not claim mathematical correctness or host runtime behavior.
"""
from __future__ import annotations

import difflib
import hashlib
import os
import re
import subprocess
import tempfile
import unittest
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_PROOF = "skills/validation-cycle/proof-orchestrator"
PROOF_REVIEW = ROOT / "skills/validation-cycle/proof-review"
FIXTURE_ROOT = ROOT / "tests/fixtures/spec48-ticket60-contract-M"


def baseline_files(prefix: str) -> list[str]:
    fixture = FIXTURE_ROOT / "baseline"
    return [
        f"{prefix}/{path.relative_to(fixture).as_posix()}"
        for path in sorted(fixture.rglob("*"))
        if path.is_file()
    ]


@lru_cache(maxsize=None)
def baseline_bytes(path: str) -> bytes:
    relative = Path(path).relative_to(OLD_PROOF)
    if relative.suffix == ".md":
        relative = relative.with_suffix(".fixture")
    return (FIXTURE_ROOT / "baseline" / relative).read_bytes()


@lru_cache(maxsize=None)
def approved_bytes(relative: str) -> bytes:
    fixture_relative = Path(relative)
    if fixture_relative.suffix == ".md":
        fixture_relative = fixture_relative.with_suffix(".fixture")
    approved = FIXTURE_ROOT / "approved" / fixture_relative
    if approved.is_file():
        return approved.read_bytes()
    return baseline_bytes(f"{OLD_PROOF}/{relative}")


def resource_preservation_problems(relative: str, actual: bytes) -> list[str]:
    """Original bytes outside reviewed control deltas; approved controls cannot regress.

    Equal spans come from the checked-in public baseline fixture. Only lines
    changed by the reviewed adaptation use its exact fixture bytes, including
    whitespace. No local Git history is needed.
    No file is exempted; method/attribution/license edits fail.
    """
    original = baseline_bytes(f"{OLD_PROOF}/{relative}")
    approved = approved_bytes(relative)
    if approved == original:
        return [] if actual == original else ["未适配资源的方法/来源/许可字节发生变化"]
    old_lines = original.decode("utf-8").splitlines(keepends=True)
    expected = approved.decode("utf-8").splitlines(keepends=True)
    current = actual.decode("utf-8").splitlines(keepends=True)
    if len(current) != len(expected):
        return ["资源结构/方法或控制块发生未经批准的增删"]
    problems = []
    for kind, old_start, old_end, new_start, new_end in difflib.SequenceMatcher(
        None, old_lines, expected, autojunk=False
    ).get_opcodes():
        if kind == "equal":
            if current[new_start:new_end] != old_lines[old_start:old_end]:
                problems.append(f"原始受保护方法/来源/许可发生变化（行{new_start + 1}–{new_end}）")
        else:
            # Do not skip adapted files/blocks: constrain their approved role,
            # permission and retry rules too. Reinstating old gates must fail.
            if current[new_start:new_end] != expected[new_start:new_end]:
                problems.append(f"批准的角色/发送控制适配被改变或回退（行{new_start + 1}–{new_end}）")
    return problems


class ProofControllerRetirement(unittest.TestCase):
    def test_every_proof_resource_and_license_has_a_complete_replacement(self):
        resources = [
            path
            for path in baseline_files(OLD_PROOF)
            if path.startswith(f"{OLD_PROOF}/references/")
            or path in {f"{OLD_PROOF}/LICENSE", f"{OLD_PROOF}/NOTICE.md"}
        ]
        self.assertTrue(resources, "baseline proof-orchestrator resources must be enumerated")

        for source in resources:
            with self.subTest(source=source):
                relative = source.removeprefix(f"{OLD_PROOF}/")
                if relative == "NOTICE.md":
                    target = PROOF_REVIEW / "NOTICE-ETA.md"
                    self.assertTrue(target.is_file(), f"missing replacement for {source}: {target}")
                    notice = target.read_text(encoding="utf-8")
                    self.assertIn("EtaSkill", notice)
                    self.assertIn("f49ce5dd6b0bfb7565c35063e10aa1ac42a480e9", notice)
                    self.assertIn("MIT", notice)
                    self.assertIn("proof-review/references", notice)
                else:
                    target = PROOF_REVIEW / relative
                self.assertTrue(target.is_file(), f"missing replacement for {source}: {target}")
                self.assertEqual(resource_preservation_problems(relative, target.read_bytes()), [], source)

        self.assertFalse((ROOT / OLD_PROOF / "SKILL.md").exists())
        self.assertFalse((ROOT / OLD_PROOF / "agents/openai.yaml").exists())
        self.assertFalse((ROOT / OLD_PROOF).exists())

    def test_review_role_discloses_migrated_methods_and_closes_local_links(self):
        skill = (PROOF_REVIEW / "SKILL.md").read_text(encoding="utf-8")
        expected = (
            "audit-output-contract.md",
            "proof-audit-rubric.md",
            "independent-review.md",
            "stress-tests.md",
            "notation-audit.md",
            "lean-methods.md",
            "dispatch-prompts.md",
        )
        for resource in expected:
            with self.subTest(resource=resource):
                self.assertIn(resource, skill)

        link = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
        for source in PROOF_REVIEW.rglob("*.md"):
            text = source.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), 1):
                for href in link.findall(line):
                    if href.startswith(("http:", "https:", "mailto:", "#")):
                        continue
                    destination = (source.parent / href.split("#", 1)[0]).resolve()
                    self.assertTrue(destination.is_file(), f"{source}:{line_no}: {href}")
                    self.assertIn(PROOF_REVIEW.resolve(), destination.parents)

    def test_proof_recipe_no_longer_calls_the_compatibility_controller(self):
        playbook = (ROOT / "skills/general/research-os/playbooks/proof.md").read_text(
            encoding="utf-8"
        )
        validation = (ROOT / "skills/general/research-os/references/validation.md").read_text(
            encoding="utf-8"
        )
        catalog = (ROOT / "skills/README.md").read_text(encoding="utf-8")
        self.assertNotIn("proof-orchestrator", playbook)
        self.assertNotIn("proof-orchestrator", validation)
        self.assertNotRegex(catalog, r"\[[^\]]*proof-orchestrator")
        self.assertNotRegex(catalog, r"--skill[^\n]*proof-orchestrator")
        self.assertIn("proof-review", playbook)

        live_docs = [
            *((ROOT / "skills").rglob("*.md")),
            ROOT / "README.md",
            ROOT / "skills/README.md",
            ROOT / "docs/README-en.md",
            ROOT / "docs/user-acceptance-guide.md",
            ROOT / "docs/assets/workflow-diagrams.md",
        ]
        stale_caller = re.compile(
            r"(?i)(?:--skill\s+proof-orchestrator|(?<![a-z0-9_./-])/proof-orchestrator\b|"
            r"\[[^\]]*proof-orchestrator\]\([^)]*proof-orchestrator|"
            r"`proof-orchestrator`[^\n]*(?:调用|安装|入口))"
        )
        for path in live_docs:
            with self.subTest(path=path):
                self.assertIsNone(stale_caller.search(path.read_text(encoding="utf-8")), path)

    def test_cached_skills_cli_installs_each_replacement_package_in_isolation(self):
        cache = subprocess.run(
            ["npm", "config", "get", "cache"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        ).stdout.strip()
        version = subprocess.run(
            ["npx", "--offline", "--yes", "skills@1.7.4", "--version"],
            cwd=ROOT,
            env={**os.environ, "npm_config_cache": cache},
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(version.returncode, 0, version.stdout + version.stderr)
        self.assertEqual(version.stdout.strip(), "1.7.4")

        log_dir = os.environ.get("SPEC48_TICKET60_LOG_DIR")
        for slug, source in (
            ("research-os", ROOT / "skills/general/research-os"),
            ("proof-review", PROOF_REVIEW),
        ):
            with tempfile.TemporaryDirectory(dir="/tmp", prefix=f"ticket60-{slug}-") as tmp:
                project = Path(tmp) / "project"
                home = Path(tmp) / "home"
                project.mkdir()
                home.mkdir()
                result = subprocess.run(
                    [
                        "npx", "--offline", "--yes", "skills@1.7.4", "add", str(ROOT),
                        "--skill", slug, "--agent", "claude-code", "--copy", "--yes",
                    ],
                    cwd=project,
                    env={
                        **os.environ,
                        "HOME": str(home),
                        "TMPDIR": tmp,
                        "npm_config_cache": cache,
                    },
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                if log_dir:
                    output = Path(log_dir)
                    output.mkdir(parents=True, exist_ok=True)
                    (output / f"skills-{slug}-context.txt").write_text(
                        "\n".join(
                            (
                                f"cwd={project}",
                                f"HOME={home}",
                                f"TMPDIR={tmp}",
                                f"npm_cache={cache}",
                                f"source={ROOT}",
                                f"command=npx --offline --yes skills@1.7.4 add {ROOT} --skill {slug} --agent claude-code --copy --yes",
                                f"returncode={result.returncode}",
                            )
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                    (output / f"skills-{slug}-install.log").write_bytes(
                        (result.stdout + result.stderr).encode()
                    )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

                package = project / ".claude/skills" / slug
                self.assertTrue((package / "SKILL.md").is_file(), slug)
                source_files = {
                    path.relative_to(source).as_posix(): path.read_bytes()
                    for path in source.rglob("*")
                    if path.is_file()
                }
                installed_files = {
                    path.relative_to(package).as_posix(): path.read_bytes()
                    for path in package.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(installed_files.keys(), source_files.keys(), slug)
                for relative, expected in source_files.items():
                    expected_hash = hashlib.sha256(expected).hexdigest()
                    actual_hash = hashlib.sha256(installed_files[relative]).hexdigest()
                    self.assertEqual(actual_hash, expected_hash, f"{slug}/{relative}")
                if log_dir:
                    manifest = "".join(
                        f"{hashlib.sha256(installed_files[path]).hexdigest()}  {path}\n"
                        for path in sorted(installed_files)
                    )
                    (Path(log_dir) / f"skills-{slug}-manifest.sha256").write_text(
                        manifest, encoding="utf-8"
                    )

                link = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
                for document in package.rglob("*.md"):
                    for line_no, line in enumerate(
                        document.read_text(encoding="utf-8").splitlines(), 1
                    ):
                        for href in link.findall(line):
                            if href.startswith(("http:", "https:", "mailto:", "#")):
                                continue
                            destination = (document.parent / href.split("#", 1)[0]).resolve()
                            self.assertTrue(destination.is_file(), f"{document}:{line_no}: {href}")
                            self.assertIn(package.resolve(), destination.parents)


class ResourcePreservationCounterexamples(unittest.TestCase):
    def current(self, relative: str) -> bytes:
        target = "NOTICE-ETA.md" if relative == "NOTICE.md" else relative
        return (PROOF_REVIEW / target).read_bytes()

    def test_deleting_substantive_lean_and_notation_methods_is_rejected(self):
        for relative, start, end in (
            ("references/lean-methods.md", "## 2. 搜索前提", "## 3. 编辑反馈"),
            ("references/notation-audit.md", "## 警告阈值", "## 九步核查"),
        ):
            with self.subTest(resource=relative):
                source = self.current(relative).decode()
                first, rest = source.split(start, 1)
                _, last = rest.split(end, 1)
                mutated = (first + end + last).encode()
                self.assertNotEqual(mutated, source.encode())
                self.assertTrue(resource_preservation_problems(relative, mutated))
        relative = "references/lean-methods.md"
        source = self.current(relative)
        self.assertIn("退出码 0 不能单独证明".encode(), source)
        changed = source.replace("退出码 0 不能单独证明".encode(), "退出码 0 可以单独证明".encode(), 1)
        self.assertTrue(any("受保护方法" in problem for problem in resource_preservation_problems(relative, changed)))

    def test_tampered_license_and_attribution_are_rejected(self):
        for relative, before, after in (
            ("LICENSE", b"Copyright (c) 2026 wanshuiyin", b"Copyright (c) 2026 someone-else"),
            ("NOTICE.md", b"EtaSkill", b"Unattributed"),
        ):
            with self.subTest(resource=relative):
                source = self.current(relative)
                self.assertIn(before, source)
                self.assertTrue(resource_preservation_problems(relative, source.replace(before, after, 1)))

    def test_all_seven_old_control_versions_remain_rejected(self):
        for relative in (
            "references/audit-output-contract.md", "references/dispatch-prompts.md",
            "references/lean-methods.md", "references/notation-audit.md",
            "references/prompts/explicit-send.md", "references/prompts/local-proof.md",
            "references/stress-tests.md",
        ):
            with self.subTest(resource=relative):
                old = baseline_bytes(f"{OLD_PROOF}/{relative}")
                self.assertNotEqual(old, self.current(relative))
                self.assertTrue(resource_preservation_problems(relative, old))

    def test_reinstating_reviewer_report_write_is_rejected(self):
        relative = "references/audit-output-contract.md"
        source = self.current(relative).decode()
        current_line = next(line for line in source.splitlines() if line.startswith("reviewer 以自然 Markdown"))
        old_line = next(line for line in baseline_bytes(f"{OLD_PROOF}/{relative}").decode().splitlines() if line.startswith("用于 `<本轮目录>/audit.md`"))
        problems = resource_preservation_problems(relative, source.replace(current_line, old_line, 1).encode())
        self.assertTrue(any("控制适配" in problem for problem in problems), problems)

    def test_reinstating_per_send_reapproval_is_rejected(self):
        relative = "references/prompts/explicit-send.md"
        source = self.current(relative).decode()
        current_line = next(line for line in source.splitlines() if line.startswith("- 若原委托只覆盖一次"))
        stale = "- 不自动重试、追加对话或调用第二个模型；下一次发送须新授权。"
        problems = resource_preservation_problems(relative, source.replace(current_line, stale, 1).encode())
        self.assertTrue(any("控制适配" in problem for problem in problems), problems)

    def test_untouched_resources_keep_strict_original_bytes(self):
        relative = "references/proof-audit-rubric.md"
        old = baseline_bytes(f"{OLD_PROOF}/{relative}")
        self.assertEqual(old, approved_bytes(relative))
        self.assertEqual(resource_preservation_problems(relative, old), [])
        self.assertTrue(resource_preservation_problems(relative, old + b"\n"))

    def test_explicitly_approved_control_content_is_preserved(self):
        relative = "references/dispatch-prompts.md"
        source = self.current(relative)
        original = baseline_bytes(f"{OLD_PROOF}/{relative}")
        self.assertNotEqual(source, original)
        self.assertEqual(source, approved_bytes(relative))
        self.assertEqual(resource_preservation_problems(relative, source), [])
        line = next(line for line in source.decode().splitlines() if line.startswith("先按执行角色使用模板"))
        indented = source.decode().replace(line, "    " + line, 1).encode()
        self.assertTrue(resource_preservation_problems(relative, indented), "must not turn role controls into a code example")

    def test_unapproved_control_whitespace_changes_are_rejected(self):
        relative = "references/independent-review.md"
        source = self.current(relative)
        marker = "3. 核实路线".encode()
        self.assertEqual(source.count(marker), 1)
        for spacing in (b"     ", b"\t", b" \t"):
            with self.subTest(spacing=spacing):
                changed = source.replace(marker, b"3." + spacing + "核实路线".encode(), 1)
                self.assertNotEqual(changed, source)
                self.assertTrue(resource_preservation_problems(relative, changed))


if __name__ == "__main__":
    unittest.main()
