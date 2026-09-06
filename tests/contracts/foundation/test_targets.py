from __future__ import annotations

import unittest

from research_os.validation.foundation import is_canonical_https_uri, is_safe_git_path, validate_target

HEX40 = "a" * 40
HEX64 = "b" * 64


class TargetTests(unittest.TestCase):
    def assertValid(self, target: object) -> None:
        self.assertEqual(validate_target(target), [])

    def test_accepts_live_fixed_cross_repository_and_uri_targets(self) -> None:
        self.assertValid({"kind": "git", "path": "artifacts/result.json"})
        self.assertValid({"kind": "git", "path": "artifacts/result.json", "commit": HEX40})
        self.assertValid({"kind": "git", "path": "artifacts/result.json", "commit": HEX40, "repository": "https://example.org/research/repo.git"})
        self.assertValid({"kind": "uri", "uri": "https://example.org/data/file.csv", "sha256": HEX64})

    def test_rejects_unsafe_git_paths(self) -> None:
        for path in ("", ".", "..", "/tmp/file", "a/../b", "a//b", "a/./b", "dir/", "a\\b", ".git/config", "a/.GIT/config", " file"):
            with self.subTest(path=path):
                self.assertFalse(is_safe_git_path(path))
                self.assertTrue(validate_target({"kind": "git", "path": path}))

    def test_rejects_floating_or_malformed_git_revisions(self) -> None:
        for commit in ("main", "latest", "a" * 7, "A" * 40, "g" * 40):
            with self.subTest(commit=commit):
                codes = {issue.code for issue in validate_target({"kind": "git", "path": "a.json", "commit": commit})}
                self.assertIn("target.commit", codes)

    def test_cross_repository_is_fixed_https_and_credential_free(self) -> None:
        fixtures = (
            {"kind": "git", "path": "a.json", "repository": "https://example.org/repo.git"},
            {"kind": "git", "path": "a.json", "commit": HEX40, "repository": "http://example.org/repo.git"},
            {"kind": "git", "path": "a.json", "commit": HEX40, "repository": "https://user@example.org/repo.git"},
            {"kind": "git", "path": "a.json", "commit": HEX40, "repository": "https://example.org/repo.git?ref=main"},
        )
        for target in fixtures:
            with self.subTest(target=target):
                self.assertTrue(validate_target(target))

    def test_uri_profile_is_canonical_https_without_query_or_fragment(self) -> None:
        self.assertTrue(is_canonical_https_uri("https://example.org/a%20b"))
        self.assertTrue(is_canonical_https_uri("https://example.org/~user"))
        for uri in (
            "http://example.org/a", "https://user:pass@example.org/a", "https://example.org/a?x=1",
            "https://example.org/a#part", "https://EXAMPLE.org/a", "https://example.org:443/a",
            "https://example.org/a/../b", "https://example.org/%2E%2E/a", "https://example.org/%7euser",
            "https://example.org/%zz", "https://example.org/a b", "https://example.org/路径",
        ):
            with self.subTest(uri=uri):
                self.assertFalse(is_canonical_https_uri(uri))
                self.assertTrue(validate_target({"kind": "uri", "uri": uri, "sha256": HEX64}))

    def test_uri_rejects_encoded_path_escape_and_noncanonical_hosts(self) -> None:
        for uri in (
            "https://example.org/%2E./secret",
            "https://example.org/a/%2E%2E/b",
            "https://example.org/%2Fetc/passwd",
            "https://example.org/%5Cserver",
            "https://example.org/%7Euser",
            "https://%65xample.org/a",
            "https://exa_mple.org/a",
            "https://例子.测试/a",
        ):
            with self.subTest(uri=uri):
                self.assertFalse(is_canonical_https_uri(uri))
                self.assertTrue(
                    validate_target(
                        {"kind": "uri", "uri": uri, "sha256": HEX64}
                    )
                )

    def test_uri_requires_lowercase_sha256_and_rejects_unknown_fields(self) -> None:
        self.assertTrue(validate_target({"kind": "uri", "uri": "https://example.org/a", "sha256": "A" * 64}))
        self.assertTrue(validate_target({"kind": "uri", "uri": "https://example.org/a", "sha256": HEX64, "label": "x"}))
