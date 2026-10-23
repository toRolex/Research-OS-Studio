"""#60 public-install contracts for the unified writing package."""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_WRITING = ROOT / "skills/writing-cycle/paper-writing"
ROUTER = ROOT / "skills/general/research-os/SKILL.md"
PLAYBOOKS = ROOT / "skills/general/research-os/playbooks"
PROFESSIONAL_ASSETS = (
    "LICENSE",
    "references/composition-map.md",
    "references/standards.md",
    "references/ml-ai-standards.md",
    "references/ml-experiment-reporting.md",
    "references/ml-reviewer-expectations.md",
    "references/ml-venue-checklists.md",
    "references/systems-standards.md",
    "references/systems-checklist.md",
    "references/systems-evaluation-methods.md",
    "references/systems-writing-methods.md",
    "references/systems-venue-and-reviewer.md",
    "references/sources.md",
    "templates/ml-writing-report.md",
    "templates/systems-paper-writing-report.md",
    "LICENSE-ML.txt",
    "LICENSE-ARIS.txt",
    "LICENSE-Orchestra.txt",
)
RELATIVE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)")


class UnifiedWritingPackage(unittest.TestCase):
    def test_professional_routes_keep_user_intent_and_point_into_one_package(self):
        router = ROUTER.read_text(encoding="utf-8")
        self.assertIn("| paper-writing | ml | 机器学习", router)
        self.assertIn("| paper-writing | systems | 系统论文", router)

        expected = {
            "paper-writing-ml.md": (
                "ml-ai-standards.md",
                "ml-experiment-reporting.md",
                "ml-reviewer-expectations.md",
                "ml-venue-checklists.md",
                "ml-writing-report.md",
            ),
            "paper-writing-systems.md": (
                "systems-standards.md",
                "systems-checklist.md",
                "systems-evaluation-methods.md",
                "systems-writing-methods.md",
                "systems-venue-and-reviewer.md",
                "systems-paper-writing-report.md",
            ),
        }
        for playbook, resources in expected.items():
            text = (PLAYBOOKS / playbook).read_text(encoding="utf-8")
            self.assertIn("skills/writing-cycle/paper-writing/SKILL.md", text)
            for resource in resources:
                self.assertIn(resource, text, f"{playbook}: {resource}")

    def test_old_controllers_have_no_live_routes_or_skill_directories(self):
        old_names = ("ml-paper-writing", "systems-paper-writing")
        for name in old_names:
            self.assertFalse((ROOT / "skills/writing-cycle" / name / "SKILL.md").exists(), name)

        active_routes = [
            ROUTER,
            *PLAYBOOKS.glob("paper-writing-*.md"),
            ROOT / "skills/general/research-os/references/PRODUCT-MAP.md",
            ROOT / "skills/general/research-os/references/writing-cycle.md",
            ROOT / "skills/general/research-os/references/migration-boundary.md",
            ROOT / "skills/README.md",
            ROOT / "README.md",
            ROOT / "docs/README-en.md",
            ROOT / "docs/user-acceptance-guide.md",
            ROOT / "docs/assets/workflow-diagrams.md",
            ROOT / "skills/writing-cycle/research-improvement/references/composition-map.md",
        ]
        for path in active_routes:
            text = path.read_text(encoding="utf-8")
            for name in old_names:
                self.assertNotIn(f"`{name}`", text, str(path))
                self.assertNotIn(f"writing-cycle/{name}/", text, str(path))

    def test_paper_writing_installs_alone_with_professional_assets_and_licenses(self):
        if shutil.which("npx") is None:
            self.skipTest("npx is not installed")

        with tempfile.TemporaryDirectory(dir="/tmp") as tmp:
            project = Path(tmp)
            home = project / "home"
            home.mkdir()
            env = {
                **os.environ,
                "HOME": str(home),
                "TMPDIR": "/tmp",
                "npm_config_cache": str(Path.home() / ".npm"),
            }
            version = subprocess.run(
                ["npx", "--offline", "--yes", "skills@1.7.4", "--version"],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
            )
            if version.returncode != 0:
                self.skipTest("skills@1.7.4 is not available in the npm cache")
            self.assertEqual(version.stdout.strip(), "1.7.4")

            result = subprocess.run(
                [
                    "npx", "--offline", "--yes", "skills@1.7.4", "add", str(ROOT),
                    "--skill", "paper-writing", "--agent", "claude-code", "--copy", "--yes",
                ],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            installed_root = project / ".claude/skills"
            installed = installed_root / "paper-writing"
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertEqual(
                sorted(path.name for path in installed_root.iterdir() if path.is_dir()),
                ["paper-writing"],
            )
            for relative in PROFESSIONAL_ASSETS:
                resource = installed / relative
                self.assertTrue(resource.is_file(), relative)
                self.assertTrue(resource.read_bytes(), relative)

            source_files = {
                path.relative_to(PAPER_WRITING).as_posix(): path.read_bytes()
                for path in PAPER_WRITING.rglob("*")
                if path.is_file()
            }
            installed_files = {
                path.relative_to(installed).as_posix(): path.read_bytes()
                for path in installed.rglob("*")
                if path.is_file()
            }
            self.assertEqual(installed_files.keys(), source_files.keys())
            for relative, expected in source_files.items():
                self.assertEqual(installed_files[relative], expected, relative)

            standards = installed / "references/standards.md"
            for target in RELATIVE_LINK.findall(standards.read_text(encoding="utf-8")):
                if target.startswith(("http:", "https:", "mailto:", "#")):
                    continue
                resolved = (standards.parent / target.split("#", 1)[0]).resolve()
                self.assertIn(installed.resolve(), resolved.parents, f"{standards}: {target}")
                self.assertTrue(resolved.is_file(), f"{standards}: {target}")


if __name__ == "__main__":
    unittest.main()
