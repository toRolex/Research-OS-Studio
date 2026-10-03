"""Seam B mechanical packaging check: leaf resources survive flat installation."""
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IdeaSourceRelocation(unittest.TestCase):
    def test_source_verification_is_available_in_flat_leaf_copies(self):
        for name in ("research-lit", "novelty-check"):
            with self.subTest(skill=name), tempfile.TemporaryDirectory() as tmp:
                leaf = Path(tmp) / name
                shutil.copytree(ROOT / "skills" / "idea-cycle" / name, leaf)
                body = (leaf / "SKILL.md").read_text()
                targets = re.findall(r"\[source verification\]\(([^)]+)\)", body)
                self.assertEqual(len(targets), 1)
                target = (leaf / targets[0].split("#")[0]).resolve()
                self.assertTrue(target.is_file(), f"Installed {name}: missing {targets[0]}")
                self.assertTrue(target.is_relative_to(leaf), "Resource must be self-contained")


if __name__ == "__main__":
    unittest.main()
