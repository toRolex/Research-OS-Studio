"""#60 proof-controller retirement seam: preserve resources, remove callers.

This slice verifies the installed Skill boundary and declared routing contract;
it does not claim mathematical correctness or host runtime behavior.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "14d9c6ef6ca7411dad1ac779647ba1a7cfb7603e"
OLD_PROOF = "skills/validation-cycle/proof-orchestrator"
PROOF_REVIEW = ROOT / "skills/validation-cycle/proof-review"


def baseline_files(prefix: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", BASELINE, "--", prefix],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return [item.decode() for item in result.stdout.splitlines()]


def baseline_bytes(path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{BASELINE}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return result.stdout


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
                    expected_hash = hashlib.sha256(baseline_bytes(source)).hexdigest()
                    actual_hash = hashlib.sha256(target.read_bytes()).hexdigest()
                    self.assertEqual(actual_hash, expected_hash, source)

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
            r"(?i)(?:--skill\s+proof-orchestrator|/proof-orchestrator\b|"
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


if __name__ == "__main__":
    unittest.main()
