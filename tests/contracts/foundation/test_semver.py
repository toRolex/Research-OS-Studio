from __future__ import annotations

import unittest

from research_os.validation.foundation import SemVer, is_exact_semver


class SemVerTests(unittest.TestCase):
    def test_accepts_semver_examples(self) -> None:
        for value in (
            "0.0.0", "1.2.3", "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-0.3.7",
            "1.0.0-x.7.z.92", "1.0.0+20130313144700", "1.0.0-beta+exp.sha.5114f85",
        ):
            with self.subTest(value=value):
                self.assertTrue(is_exact_semver(value))
                self.assertEqual(str(SemVer.parse(value)), value)

    def test_rejects_non_exact_or_invalid_versions(self) -> None:
        for value in ("1", "1.2", "v1.2.3", "01.2.3", "1.02.3", "1.2.03", "1.0.0-01", "1.0.0-", "1.0.0+", " 1.0.0", 1, None):
            with self.subTest(value=value):
                self.assertFalse(is_exact_semver(value))

    def test_precedence_follows_semver_and_ignores_build(self) -> None:
        ordered = [SemVer.parse(value) for value in (
            "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta",
            "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0",
        )]
        self.assertEqual(sorted(reversed(ordered)), ordered)
        self.assertEqual(SemVer.parse("1.0.0+one"), SemVer.parse("1.0.0+two"))
        self.assertEqual(
            hash(SemVer.parse("1.0.0+one")),
            hash(SemVer.parse("1.0.0+two")),
        )
        self.assertEqual(
            len({SemVer.parse("1.0.0+one"), SemVer.parse("1.0.0+two")}),
            1,
        )
