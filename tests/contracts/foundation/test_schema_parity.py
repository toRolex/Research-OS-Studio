from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_os.validation.foundation import Issue, LocalSchemaValidator, TypeRegistry, ValidationReportBuilder, validate_artifact, validate_validation_report

ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "core" / "contracts"


class SchemaParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schemas = LocalSchemaValidator(SCHEMAS)
        self.registry = TypeRegistry()
        self.registry.register("example", "1.0.0", lambda spec: [] if isinstance(spec, dict) else [Issue("example.spec", "object required")])

    @staticmethod
    def artifact(version: str, target: dict[str, object] | None = None) -> dict[str, object]:
        return {
            "contract": {"name": "research-os/artifact", "version": version},
            "target": target or {"kind": "git", "path": "artifacts/example.json"},
            "type": {"name": "example", "version": "1.0.0"},
            "spec": {},
        }

    def test_artifact_schema_and_runtime_agree_on_positive_and_negative_matrix(self) -> None:
        for version in ("1.0.0", "1.1.0"):
            schema = SCHEMAS / f"artifact-{version}.schema.json"
            values = [
                self.artifact(version),
                self.artifact(version, {"kind": "git", "path": "a.json", "commit": "a" * 40, "repository": "https://example.org/repo.git"}),
                self.artifact(version, {"kind": "uri", "uri": "https://example.org/a", "sha256": "b" * 64}),
            ]
            bad_path = self.artifact(version); bad_path["target"] = {"kind": "git", "path": "../a.json"}; values.append(bad_path)
            bad_uri = self.artifact(version); bad_uri["target"] = {"kind": "uri", "uri": "https://example.org/a?q=1", "sha256": "b" * 64}; values.append(bad_uri)
            bad_version = self.artifact(version); bad_version["type"] = {"name": "example", "version": "latest"}; values.append(bad_version)
            extra = self.artifact(version); extra["created_at"] = "now"; values.append(extra)
            bad_spec = self.artifact(version); bad_spec["spec"] = []; values.append(bad_spec)
            for field in ("provenance", "relations", "assurance"):
                bad_item = self.artifact(version)
                bad_item[field] = ["not-an-object"]
                values.append(bad_item)
            fixtures = Path(__file__).with_name("fixtures")
            expected = {
                "artifact-fixed-uri.json": True,
                "artifact-floating-git.json": False,
                "artifact-live-git.json": True,
                "artifact-query-uri.json": False,
            }
            for name, should_pass in expected.items():
                with self.subTest(version=version, fixture=name):
                    value = json.loads((fixtures / name).read_text(encoding="utf-8"))
                    value["contract"]["version"] = version
                    schema_pass = not self.schemas.validate_file(schema, value)
                    runtime_pass = not validate_artifact(value, self.registry)
                    self.assertEqual(schema_pass, should_pass)
                    self.assertEqual(runtime_pass, should_pass)

    def test_schema_evaluator_fails_closed_for_remote_missing_unknown_keyword_and_unknown_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = {
                "remote.json": {"$ref": "https://example.org/schema.json"},
                "remote-case.json": {"$ref": "HTTPS://example.org/schema.json"},
                "network-path.json": {"$ref": "//example.org/schema.json"},
                "missing.json": {"$ref": "absent.json"},
                "keyword.json": {"x-extension": True},
                "format.json": {"type": "string", "format": "mystery-format"},
            }
            evaluator = LocalSchemaValidator(root)
            for name, schema in cases.items():
                path = root / name
                path.write_text(json.dumps(schema), encoding="utf-8")
                with self.subTest(name=name):
                    issues = evaluator.validate_file(path, "value")
                    self.assertTrue(issues)
                    self.assertTrue(any("blocked" in issue.code or "unsupported" in issue.code for issue in issues))

    def test_schema_evaluator_rejects_malformed_schema_keyword_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = {
                "required.json": {"type": "object", "required": "name"},
                "properties.json": {"type": "object", "properties": []},
                "dependent.json": {"type": "object", "dependentRequired": []},
                "one-of.json": {"oneOf": {}},
                "all-of.json": {"allOf": {}},
                "minimum.json": {"type": "array", "minItems": -1},
            }
            evaluator = LocalSchemaValidator(root)
            for name, schema in cases.items():
                path = root / name
                path.write_text(json.dumps(schema), encoding="utf-8")
                with self.subTest(name=name):
                    issues = evaluator.validate_file(path, {})
                    self.assertIn("schema.definition.blocked", {issue.code for issue in issues})

    def test_schema_root_and_references_reject_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "schemas"
            root.mkdir()
            outside = parent / "outside.json"
            outside.write_text(json.dumps({"type": "string"}), encoding="utf-8")

            linked_root_file = root / "linked.json"
            linked_root_file.symlink_to(outside)
            evaluator = LocalSchemaValidator(root)
            with self.assertRaises(ValueError):
                evaluator.validate_file(linked_root_file, "value")

            (root / "entry.json").write_text(
                json.dumps({"$ref": "linked.json"}), encoding="utf-8"
            )
            issues = evaluator.validate_file(root / "entry.json", "value")
            self.assertIn("schema.reference.blocked", {issue.code for issue in issues})

    def test_validation_report_schema_and_runtime_parity(self) -> None:
        report = ValidationReportBuilder("artifact-envelope", "1.2.0", {"kind": "git", "path": "a.json"}).add_evidence("schema.local", "local schema loaded").build()
        schema_issues = self.schemas.validate_file(SCHEMAS / "foundation" / "validation-report-1.0.0.schema.json", report)
        self.assertEqual(schema_issues, [])
        self.assertEqual(validate_validation_report(report), [])
        report["verdict"] = "unknown"
        self.assertTrue(self.schemas.validate_file(SCHEMAS / "foundation" / "validation-report-1.0.0.schema.json", report))
        self.assertTrue(validate_validation_report(report))

        report = ValidationReportBuilder("artifact-envelope", "1.2.0", {"kind": "git", "path": "a.json"}).build()
        report["verdict"] = "blocked"
        self.assertTrue(self.schemas.validate_file(SCHEMAS / "foundation" / "validation-report-1.0.0.schema.json", report))
        self.assertTrue(validate_validation_report(report))

    def test_fixture_inventory_exercises_positive_and_negative_targets(self) -> None:
        fixtures = Path(__file__).with_name("fixtures")
        names = {path.name for path in fixtures.glob("*.json")}
        self.assertEqual(names, {
            "artifact-fixed-uri.json", "artifact-floating-git.json", "artifact-live-git.json", "artifact-query-uri.json"
        })
        expected = {
            "artifact-fixed-uri.json": True,
            "artifact-floating-git.json": False,
            "artifact-live-git.json": True,
            "artifact-query-uri.json": False,
        }
        for name, should_pass in expected.items():
            with self.subTest(name=name):
                value = json.loads((fixtures / name).read_text(encoding="utf-8"))
                version = value["contract"]["version"]
                schema = SCHEMAS / f"artifact-{version}.schema.json"
                self.assertEqual(not self.schemas.validate_file(schema, value), should_pass)
                self.assertEqual(not validate_artifact(value, self.registry), should_pass)
