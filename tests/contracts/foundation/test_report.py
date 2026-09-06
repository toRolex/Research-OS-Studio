from __future__ import annotations

import unittest

from research_os.validation.foundation import (
    Issue,
    ValidationReportBuilder,
    exit_code_for_verdict,
    validate_validation_report,
)


class ValidationReportTests(unittest.TestCase):
    def test_builder_records_actual_validator_subject_evidence_and_issue(self) -> None:
        report = (
            ValidationReportBuilder(
                "artifact-envelope", "2.3.4", {"kind": "git", "path": "artifacts/a.json"}, subject_sha256="a" * 64
            )
            .add_evidence("schema.loaded", "loaded local schema", data={"schema": "artifact-1.1.0"})
            .add_issue(Issue("type.unsupported", "unknown type", "/type"))
            .build()
        )
        self.assertEqual(report["validator"], {"name": "artifact-envelope", "version": "2.3.4"})
        self.assertEqual(report["verdict"], "fail")
        self.assertEqual(report["subject"]["sha256"], "a" * 64)
        self.assertEqual(report["evidence"][0]["data"]["schema"], "artifact-1.1.0")
        self.assertEqual(validate_validation_report(report), [])

    def test_passing_report_cannot_hide_issues(self) -> None:
        builder = ValidationReportBuilder("artifact-envelope", "1.0.0", {"kind": "git", "path": "a.json"})
        builder.add_issue(Issue("x", "failed"))
        with self.assertRaises(ValueError):
            builder.build("pass")

    def test_blocked_report_has_dynamic_identity_and_valid_shape(self) -> None:
        report = (
            ValidationReportBuilder("remote-target", "1.9.0", {"kind": "uri", "uri": "https://example.org/a", "sha256": "b" * 64})
            .add_evidence("network.offline", "offline policy is active")
            .add_issue(Issue("external.unavailable", "network prerequisite unavailable"))
            .build("blocked")
        )
        self.assertEqual(report["verdict"], "blocked")
        self.assertEqual(report["validator"]["name"], "remote-target")
        self.assertEqual(validate_validation_report(report), [])

    def test_non_pass_verdicts_require_matching_issues(self) -> None:
        subject = {"kind": "git", "path": "a.json"}
        for verdict in ("fail", "usage_error", "blocked"):
            with self.subTest(verdict=verdict):
                builder = ValidationReportBuilder("artifact", "1.0.0", subject)
                with self.assertRaises(ValueError):
                    builder.build(verdict)

        blocked = (
            ValidationReportBuilder("artifact", "1.0.0", subject)
            .add_issue(Issue("external.unavailable", "required external prerequisite unavailable"))
            .build("blocked")
        )
        self.assertEqual(validate_validation_report(blocked), [])

        malformed = ValidationReportBuilder("artifact", "1.0.0", subject).build()
        malformed["verdict"] = "blocked"
        self.assertIn(
            "report.non_pass_without_issues",
            {issue.code for issue in validate_validation_report(malformed)},
        )

    def test_uri_subject_digest_cannot_disagree_with_target(self) -> None:
        target = {
            "kind": "uri",
            "uri": "https://example.org/a",
            "sha256": "a" * 64,
        }
        with self.assertRaises(ValueError):
            ValidationReportBuilder(
                "artifact", "1.0.0", target, subject_sha256="b" * 64
            )

        report = ValidationReportBuilder("artifact", "1.0.0", target).build()
        report["subject"]["sha256"] = "b" * 64
        self.assertIn(
            "report.subject.digest_mismatch",
            {issue.code for issue in validate_validation_report(report)},
        )

    def test_verdict_exit_code_mapping_is_stable(self) -> None:
        self.assertEqual(
            {verdict: exit_code_for_verdict(verdict) for verdict in ("pass", "fail", "usage_error", "blocked")},
            {"pass": 0, "fail": 1, "usage_error": 2, "blocked": 3},
        )
        with self.assertRaises(ValueError):
            exit_code_for_verdict("unknown")

    def test_runtime_rejects_hardcoded_or_malformed_reports(self) -> None:
        report = ValidationReportBuilder("artifact", "1.0.0", {"kind": "git", "path": "a.json"}).build()
        report["validator"] = {"name": "artifact", "version": "latest"}
        self.assertTrue(validate_validation_report(report))
        report = ValidationReportBuilder("artifact", "1.0.0", {"kind": "git", "path": "a.json"}).build()
        report["issues"] = [{"code": "x", "message": "failure"}]
        self.assertIn("report.pass_with_issues", {issue.code for issue in validate_validation_report(report)})
