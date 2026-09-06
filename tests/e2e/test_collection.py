"""Release discovery must include every test file, not just importable packages."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class CollectionAcceptanceTests(unittest.TestCase):
    def test_root_discovery_includes_every_test_file_without_import_errors(self):
        loader = unittest.TestLoader()
        suite = loader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
        tests = list(flatten(suite))
        self.assertEqual(loader.errors, [])
        collected = {test.__class__.__module__ for test in tests}
        expected = {
            ".".join(path.relative_to(ROOT).with_suffix("").parts)
            for path in (ROOT / "tests").rglob("test*.py")
        }
        self.assertEqual(expected - collected, set(), "silently omitted test modules")
        self.assertGreaterEqual(len(tests), 371, "integration baseline lost tests")


if __name__ == "__main__":
    unittest.main()
