from __future__ import annotations

import unittest

from research_os.validation.foundation import (
    Issue,
    SemVer,
    TypeDescriptor,
    TypeRegistry,
    validate_artifact,
)


class RegistryArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = TypeRegistry()
        self.registry.register("research-charter", "1.0.0", self.validate_charter)

    @staticmethod
    def validate_charter(spec: object) -> list[Issue]:
        if not isinstance(spec, dict) or not isinstance(spec.get("question"), str) or not spec["question"].strip():
            return [Issue("charter.question", "question is required", "/spec/question")]
        return []

    @staticmethod
    def artifact(contract_version: str = "1.0.0") -> dict[str, object]:
        return {
            "contract": {"name": "research-os/artifact", "version": contract_version},
            "target": {"kind": "git", "path": "artifacts/charter.json"},
            "type": {"name": "research-charter", "version": "1.0.0"},
            "spec": {"question": "What is reproducible?"},
        }

    def test_registry_registers_resolves_snapshots_and_delegates(self) -> None:
        self.assertEqual(len(self.registry), 1)
        self.assertIsNotNone(self.registry.resolve("research-charter", "1.0.0"))
        self.assertEqual(self.registry.snapshot()["types"], [{"name": "research-charter", "version": "1.0.0"}])
        self.assertEqual(validate_artifact(self.artifact(), self.registry), [])
        invalid = self.artifact()
        invalid["spec"] = {"question": ""}
        self.assertIn("charter.question", {issue.code for issue in validate_artifact(invalid, self.registry)})

    def test_registry_rejects_duplicates_invalid_names_and_bad_validator_contract(self) -> None:
        with self.assertRaises(ValueError):
            self.registry.register("research-charter", "1.0.0", lambda spec: [])
        with self.assertRaises(ValueError):
            self.registry.register("Research Charter", "1.0.0", lambda spec: [])
        with self.assertRaises(TypeError):
            self.registry.register_descriptor(
                TypeDescriptor("broken", SemVer.parse("1.0.0"), None)  # type: ignore[arg-type]
            )
        broken = TypeRegistry()
        broken.register("broken", "1.0.0", lambda spec: ["not an issue"])
        artifact = self.artifact()
        artifact["type"] = {"name": "broken", "version": "1.0.0"}
        self.assertIn("type.validator_contract", {issue.code for issue in validate_artifact(artifact, broken)})

    def test_registry_snapshot_is_independent_of_registration_order(self) -> None:
        first = TypeRegistry()
        first.register("example", "1.0.0+z", lambda spec: [])
        first.register("example", "1.0.0+a", lambda spec: [])
        second = TypeRegistry()
        second.register("example", "1.0.0+a", lambda spec: [])
        second.register("example", "1.0.0+z", lambda spec: [])
        self.assertEqual(first.snapshot(), second.snapshot())

    def test_envelope_versions_have_identical_runtime_shape(self) -> None:
        for version in ("1.0.0", "1.1.0"):
            with self.subTest(version=version):
                self.assertEqual(validate_artifact(self.artifact(version), self.registry), [])
        invalid = self.artifact("2.0.0")
        self.assertIn("contract.version.unsupported", {issue.code for issue in validate_artifact(invalid, self.registry)})

    def test_unknown_type_exact_versions_unknown_fields_and_non_object_spec_fail(self) -> None:
        fixtures = []
        unknown = self.artifact(); unknown["type"] = {"name": "unknown", "version": "1.0.0"}; fixtures.append((unknown, "type.unsupported"))
        range_version = self.artifact(); range_version["type"] = {"name": "research-charter", "version": "^1.0.0"}; fixtures.append((range_version, "type.version"))
        extra = self.artifact(); extra["status"] = "valid"; fixtures.append((extra, "artifact.field"))
        bad_spec = self.artifact(); bad_spec["spec"] = []; fixtures.append((bad_spec, "spec.object"))
        for value, code in fixtures:
            with self.subTest(code=code):
                self.assertIn(code, {issue.code for issue in validate_artifact(value, self.registry)})

    def test_omitted_and_explicit_empty_optional_arrays_remain_distinct_and_valid(self) -> None:
        omitted = self.artifact()
        explicit = self.artifact(); explicit.update({"provenance": [], "relations": [], "assurance": []})
        self.assertEqual(validate_artifact(omitted, self.registry), [])
        self.assertEqual(validate_artifact(explicit, self.registry), [])
        self.assertNotEqual(omitted, explicit)
