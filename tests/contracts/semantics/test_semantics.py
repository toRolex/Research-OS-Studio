from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from research_os.validation.semantics import (
    SemanticsSchemaValidator,
    find_assurance_conflicts,
    parse_json_pointer,
    scopes_overlap,
    select_migration_rule,
    validate_assessment,
    validate_claim,
    validate_evidence,
    validate_fixed_ref,
    validate_migration_receipt,
    validate_migration_rule,
    validate_project,
    validate_provenance,
    validate_revision_isolation,
    validate_scope,
    validate_workstream,
    version_in_range,
)

C1 = "1" * 40
C2 = "2" * 40
C3 = "3" * 40
D1 = "a" * 64
D2 = "b" * 64
D3 = "c" * 64
ROOT = Path(__file__).resolve().parents[3]
CONTRACTS = ROOT / "core" / "contracts"


def target(path: str, commit: str | None = C1) -> dict[str, str]:
    value = {"kind": "git", "path": path}
    if commit is not None:
        value["commit"] = commit
    return value


def ref(path: str, commit: str = C1, digest: str = D1) -> dict[str, object]:
    return {"target": target(path, commit), "sha256": digest}


def fixed_artifact(value: dict[str, object], commit: str) -> dict[str, object]:
    fixed = copy.deepcopy(value)
    fixed["target"]["commit"] = commit
    return fixed


def component(name: str) -> dict[str, str]:
    return {"name": name, "version": "1.0.0", "sha256": D3}


def artifact(type_name: str, path: str, spec: dict[str, object], **extra: object) -> dict[str, object]:
    value: dict[str, object] = {
        "contract": {"name": "research-os/artifact", "version": "1.1.0"},
        "target": target(path, None),
        "type": {"name": type_name, "version": "1.0.0"},
        "spec": spec,
    }
    value.update(extra)
    return value


def project() -> dict[str, object]:
    return artifact(
        "project",
        "project.json",
        {
            "name": "Sparse bounds",
            "question": "Can the bound be reproduced?",
            "boundaries": ["small models", "fixed compute"],
            "principals": [
                {"identity": "alice", "roles": ["user", "researcher"]},
                {"identity": "bob", "roles": ["reviewer"]},
                {"identity": "agent:runner", "roles": ["agent"]},
            ],
        },
    )


def fixed_project() -> dict[str, object]:
    value = project()
    value["target"]["commit"] = C1
    return value


def assessment(
    *,
    dimension: str = "structural_conformance",
    verdict: str = "pass",
    scope: object = "whole_subject",
    subject: dict[str, object] | None = None,
    assessor: str = "agent:runner",
) -> dict[str, object]:
    return artifact(
        "assessment",
        "assessments/a.json",
        {
            "project": ref("project.json"),
            "subject": subject or ref("claims/c.json", C2, D2),
            "dimension": dimension,
            "scope": scope,
            "verdict": verdict,
            "method": "deterministic check",
            "evidence": [ref("reports/check.json", C3, D3)],
            "assessor": assessor,
            "assessed_at": "2026-09-06T12:00:00Z",
            "validity": "active",
        },
    )


class ProjectWorkstreamTests(unittest.TestCase):
    def test_project_binds_roles_without_global_phase(self) -> None:
        self.assertEqual(validate_project(project()), [])
        broken = copy.deepcopy(project())
        broken["spec"]["current_phase"] = "experiment"
        broken["spec"]["principals"][0]["roles"] = ["researcher"]
        codes = {item.code for item in validate_project(broken)}
        self.assertIn("field.unknown", codes)
        self.assertIn("principal.user_required", codes)

    def test_project_rejects_duplicate_identity_and_unknown_role(self) -> None:
        broken = copy.deepcopy(project())
        broken["spec"]["principals"].append({"identity": "alice", "roles": ["owner"]})
        codes = {item.code for item in validate_project(broken)}
        self.assertIn("principal.duplicate", codes)
        self.assertIn("principal.role", codes)

    def test_workstream_has_fixed_project_and_local_state_only(self) -> None:
        value = artifact("workstream", "workstreams/proof.json", {"project": ref("project.json"), "name": "Proof", "intent": "Review theorem", "state": "paused"})
        self.assertEqual(validate_workstream(value), [])
        value["spec"]["project"]["target"].pop("commit")
        value["spec"]["state"] = "completed"
        codes = {item.code for item in validate_workstream(value)}
        self.assertIn("target.not_fixed", codes)
        self.assertIn("workstream.state", codes)


class ClaimEvidenceTests(unittest.TestCase):
    def test_claim_is_versioned_statement_with_exact_scope(self) -> None:
        value = artifact("claim", "claims/c.json", {"project": ref("project.json"), "workstream": ref("workstreams/w.json"), "statement": "Accuracy is retained", "scope": ["/spec/metrics/accuracy"], "conditions": [], "limitations": ["CPU fixture"]})
        self.assertEqual(validate_claim(value), [])

    def test_evidence_embeds_only_supports_with_fixed_claim(self) -> None:
        value = artifact(
            "evidence",
            "evidence/e.json",
            {"project": ref("project.json"), "workstream": ref("workstreams/w.json"), "description": "Frozen run output"},
            relations=[{"relation": "supports", "claim": ref("claims/c.json", C2, D2), "scope": ["/spec/metrics"], "method": "pre-registered comparison", "conditions": []}],
        )
        self.assertEqual(validate_evidence(value), [])
        value["relations"][0]["relation"] = "proves"
        value["relations"][0]["claim"]["target"].pop("commit")
        codes = {item.code for item in validate_evidence(value)}
        self.assertIn("supports.relation", codes)
        self.assertIn("target.not_fixed", codes)

    def test_evidence_requires_conditions_even_when_empty(self) -> None:
        value = artifact("evidence", "evidence/e.json", {"project": ref("project.json"), "workstream": ref("workstreams/w.json"), "description": "run"}, relations=[{"relation": "supports", "claim": ref("claims/c.json"), "scope": "whole_subject", "method": "comparison"}])
        self.assertIn("supports.conditions", {item.code for item in validate_evidence(value)})

    def test_provenance_fixes_inputs_and_generator(self) -> None:
        value = [{"activity": "derived", "inputs": [ref("inputs/x.json")], "generator": component("analyzer")}]
        self.assertEqual(validate_provenance(value), [])
        value[0]["inputs"][0]["target"].pop("commit")
        self.assertIn("target.not_fixed", {item.code for item in validate_provenance(value)})

    def test_uri_fixed_ref_digest_must_agree(self) -> None:
        value = {"target": {"kind": "uri", "uri": "https://example.test/data", "sha256": D1}, "sha256": D2}
        self.assertIn("fixed_ref.digest_mismatch", {item.code for item in validate_fixed_ref(value)})


class ScopeTests(unittest.TestCase):
    def test_json_pointer_decoding_and_token_prefix_overlap(self) -> None:
        self.assertEqual(parse_json_pointer("/a~1b/~0x"), ("a/b", "~x"))
        self.assertTrue(scopes_overlap(["/spec/a"], ["/spec/a/b"]))
        self.assertFalse(scopes_overlap(["/spec/a"], ["/spec/ab"]))
        self.assertTrue(scopes_overlap("whole_subject", ["/spec/a"]))

    def test_scope_rejects_bad_escapes_duplicates_and_redundancy(self) -> None:
        codes = {item.code for item in validate_scope(["/a", "/a/b", "/bad~2", "/a"])}
        self.assertIn("scope.pointer", codes)
        self.assertIn("scope.duplicate", codes)
        self.assertIn("scope.redundant", codes)

    def test_empty_json_pointer_represents_root(self) -> None:
        self.assertEqual(validate_scope([""]), [])
        self.assertTrue(scopes_overlap([""], ["/anything"]))


class AssuranceTests(unittest.TestCase):
    def test_human_acceptance_requires_bound_user(self) -> None:
        value = assessment(dimension="human_acceptance", assessor="alice")
        evidence = {D3: {"target": target("reports/check.json", C3)}}
        self.assertEqual(
            validate_assessment(
                value,
                project=fixed_project(),
                project_digest=D1,
                evidence_by_digest=evidence,
            ),
            [],
        )
        value["spec"]["assessor"] = "bob"
        self.assertIn(
            "assessment.human_role",
            {
                item.code
                for item in validate_assessment(
                    value,
                    project=fixed_project(),
                    project_digest=D1,
                    evidence_by_digest=evidence,
                )
            },
        )

    def test_assessment_project_binding_must_match_role_source(self) -> None:
        value = assessment(dimension="human_acceptance", assessor="alice")
        value["spec"]["project"] = ref("other-project.json", C1, D1)
        self.assertIn(
            "assessment.project_mismatch",
            {item.code for item in validate_assessment(value, project=fixed_project(), project_digest=D1)},
        )

    def test_human_acceptance_cannot_be_failed_or_agent_authored(self) -> None:
        value = assessment(dimension="human_acceptance", verdict="fail", assessor="agent:runner")
        codes = {item.code for item in validate_assessment(value, project=fixed_project(), project_digest=D1)}
        self.assertIn("assessment.human_role", codes)
        self.assertIn("assessment.human_verdict", codes)

    def test_identity_checks_fail_closed_without_project_digest(self) -> None:
        value = assessment(dimension="human_acceptance", assessor="alice")
        self.assertIn(
            "assessment.project_digest_required",
            {item.code for item in validate_assessment(value, project=fixed_project())},
        )

    def test_independent_review_requires_different_principal_fixed_inputs_and_isolation(self) -> None:
        value = assessment(dimension="independent_review", assessor="bob")
        value["spec"]["isolation_receipt"] = {
            "reviewer": "bob",
            "authors": ["alice"],
            "inputs": [value["spec"]["subject"]],
            "fresh_context": True,
            "conversation_history_access": False,
            "issued_at": "2026-09-06T11:00:00Z",
        }
        evidence = {D3: {"target": target("reports/check.json", C3)}}
        self.assertEqual(
            validate_assessment(
                value,
                project=fixed_project(),
                project_digest=D1,
                evidence_by_digest=evidence,
            ),
            [],
        )
        value["spec"]["isolation_receipt"]["authors"] = ["bob"]
        value["spec"]["isolation_receipt"]["fresh_context"] = False
        codes = {
            item.code
            for item in validate_assessment(
                value,
                project=fixed_project(),
                project_digest=D1,
                evidence_by_digest=evidence,
            )
        }
        self.assertIn("isolation.same_principal", codes)
        self.assertIn("isolation.fresh_context", codes)

    def test_assurance_conflict_requires_same_fixed_subject_dimension_and_overlap(self) -> None:
        left = assessment(scope=["/spec/results"], verdict="pass")
        right = assessment(scope=["/spec/results/accuracy"], verdict="fail")
        self.assertEqual([item.code for item in find_assurance_conflicts([left, right])], ["assurance.conflict"])
        right["spec"]["subject"] = ref("claims/c.json", C3, D2)
        self.assertEqual(find_assurance_conflicts([left, right]), [])

    def test_not_applicable_conflicts_with_pass_on_overlapping_scope(self) -> None:
        left = assessment(verdict="not_applicable")
        right = assessment(verdict="pass")
        self.assertEqual(
            [item.code for item in find_assurance_conflicts([left, right])],
            ["assurance.conflict"],
        )

    def test_inactive_assessment_does_not_conflict(self) -> None:
        left = assessment(verdict="pass")
        right = assessment(verdict="fail")
        right["spec"]["validity"] = "revoked"
        right["spec"]["validity_reason"] = "withdrawn"
        self.assertEqual(find_assurance_conflicts([left, right]), [])

    def test_revision_isolation_checks_commit_and_digest(self) -> None:
        subject = ref("claims/c.json", C2, D2)
        old = assessment(subject=ref("claims/c.json", C1, D2))
        changed_bytes = assessment(subject=ref("claims/c.json", C2, D1))
        current = assessment(subject=subject)
        self.assertEqual(len(validate_revision_isolation(subject, [old, changed_bytes, current])), 2)

    def test_assurance_slots_are_fixed_references(self) -> None:
        value = project()
        value["assurance"] = [ref("assessments/a.json")]
        self.assertEqual(validate_project(value), [])
        value["assurance"][0]["target"].pop("commit")
        self.assertIn("target.not_fixed", {item.code for item in validate_project(value)})


class MigrationTests(unittest.TestCase):
    def rule(self, path: str = "migration/rule.json", lower: str = "1.0.0", upper: str = "1.9.9") -> dict[str, object]:
        return artifact(
            "migration-rule",
            path,
            {
                "artifact_type": "claim",
                "source": {"min": lower, "min_inclusive": True, "max": upper, "max_inclusive": True},
                "target_version": "2.0.0",
                "migrator": component("claim-migrator"),
                "input_validator": component("claim-validator-v1"),
                "output_validator": component("claim-validator-v2"),
            },
        )

    def test_structured_version_range_and_unique_rule(self) -> None:
        rule = self.rule()
        self.assertEqual(validate_migration_rule(rule), [])
        self.assertTrue(version_in_range("1.5.0", rule["spec"]["source"]))
        selected, issues = select_migration_rule([rule], artifact_type="claim", source_version="1.5.0", target_version="2.0.0")
        self.assertIs(selected, rule)
        self.assertEqual(issues, [])

    def test_semver_range_honors_prerelease_precedence(self) -> None:
        version_range = {
            "min": "2.0.0-alpha.1",
            "min_inclusive": True,
            "max": "2.0.0",
            "max_inclusive": False,
        }
        self.assertTrue(version_in_range("2.0.0-beta.1", version_range))
        self.assertFalse(version_in_range("2.0.0", version_range))

    def test_no_rule_and_multiple_rules_fail(self) -> None:
        rule = self.rule()
        _, missing = select_migration_rule([rule], artifact_type="claim", source_version="3.0.0", target_version="4.0.0")
        _, multiple = select_migration_rule([rule, copy.deepcopy(rule)], artifact_type="claim", source_version="1.5.0", target_version="2.0.0")
        self.assertEqual(missing[0].code, "migration.no_rule")
        self.assertEqual(multiple[0].code, "migration.multiple_rules")

    def test_invalid_or_self_targeting_rule_fails(self) -> None:
        rule = self.rule(lower="2.0.0", upper="2.0.0")
        self.assertIn("migration.target_in_source", {item.code for item in validate_migration_rule(rule)})
        rule["spec"]["source"]["min_inclusive"] = False
        self.assertIn("version_range.empty", {item.code for item in validate_migration_rule(rule)})

    def receipt(self) -> dict[str, object]:
        execution = lambda name: {"component": component(name), "verdict": "pass"}
        return artifact(
            "migration-receipt",
            "migration/receipt.json",
            {
                "input": ref("claims/c.json", C1, D1),
                "output": ref("claims/c-v2.json", C2, D2),
                "input_contract": {"artifact_contract": "1.1.0", "type_name": "claim", "type_version": "1.0.0"},
                "output_contract": {"artifact_contract": "1.1.0", "type_name": "claim", "type_version": "2.0.0"},
                "rule": ref("migration/rule.json", C1, D3),
                "migrator": execution("claim-migrator"),
                "input_validator": execution("claim-validator-v1"),
                "output_validator": execution("claim-validator-v2"),
                "created_at": "2026-09-06T13:00:00Z",
            },
        )

    def test_complete_receipt_passes(self) -> None:
        receipt = self.receipt()
        rule = fixed_artifact(self.rule(), C1)
        input_artifact = artifact(
            "claim",
            "claims/c.json",
            {
                "project": ref("project.json"),
                "workstream": ref("workstreams/w.json"),
                "statement": "old statement",
                "scope": "whole_subject",
            },
        )
        input_artifact["target"]["commit"] = C1
        input_artifact["type"]["version"] = "1.0.0"
        output_artifact = copy.deepcopy(input_artifact)
        output_artifact["target"] = target("claims/c-v2.json", C2)
        output_artifact["type"]["version"] = "2.0.0"
        self.assertEqual(
            validate_migration_receipt(
                receipt,
                rule=rule,
                rule_digest=D3,
                input_artifact=input_artifact,
                input_digest=D1,
                output_artifact=output_artifact,
                output_digest=D2,
            ),
            [],
        )

    def test_receipt_rejects_overwrite_same_commit_and_failed_validator(self) -> None:
        value = self.receipt()
        value["spec"]["output"] = copy.deepcopy(value["spec"]["input"])
        value["spec"]["output_validator"]["verdict"] = "fail"
        codes = {item.code for item in validate_migration_receipt(value)}
        self.assertIn("migration.overwrite", codes)
        self.assertIn("migration.new_commit", codes)
        self.assertIn("migration.execution_verdict", codes)


class HostileContractTests(unittest.TestCase):
    def test_semantics_contracts_have_an_executable_validator(self) -> None:
        fixtures = {
            "project": project(),
            "workstream": artifact(
                "workstream",
                "workstreams/w.json",
                {
                    "project": ref("project.json"),
                    "name": "Experiment",
                    "intent": "Run fixed design",
                    "state": "active",
                },
            ),
            "claim": artifact(
                "claim",
                "claims/c.json",
                {
                    "project": ref("project.json"),
                    "workstream": ref("workstreams/w.json"),
                    "statement": "Accuracy is retained",
                    "scope": ["/spec/metrics/accuracy"],
                },
            ),
            "evidence": artifact(
                "evidence",
                "evidence/e.json",
                {
                    "project": ref("project.json"),
                    "workstream": ref("workstreams/w.json"),
                    "description": "Frozen output",
                },
                relations=[
                    {
                        "relation": "supports",
                        "claim": ref("claims/c.json", C2, D2),
                        "scope": "whole_subject",
                        "method": "comparison",
                        "conditions": [],
                    }
                ],
            ),
            "assessment": assessment(),
            "migration-rule": MigrationTests().rule(),
        }
        for type_name, value in fixtures.items():
            with self.subTest(type_name=type_name):
                self.assertEqual(SemanticsSchemaValidator().validate(type_name, value), [])

    def test_semantics_target_profile_rejects_noncanonical_inputs(self) -> None:
        bad_git_paths = (" link.json", "link.json\n", "link.json\t")
        bad_uris = (
            "https://EXAMPLE.test/data",
            "https://example.test:443/data",
            "https://example.test/a/../data",
            "https://example.test/%2E%2E/data",
            "https://example.test/%7edata",
        )
        for path in bad_git_paths:
            with self.subTest(path=path):
                self.assertIn(
                    "target.path",
                    {item.code for item in validate_fixed_ref(ref(path))},
                )
        for uri in bad_uris:
            with self.subTest(uri=uri):
                value = {"target": {"kind": "uri", "uri": uri, "sha256": D1}, "sha256": D1}
                self.assertIn(
                    "target.uri",
                    {item.code for item in validate_fixed_ref(value)},
                )

    def test_fixed_git_ref_requires_verification_context_for_trust_decision(self) -> None:
        self.assertIn(
            "fixed_ref.verification_context_required",
            {
                item.code
                for item in validate_fixed_ref(
                    ref("claims/c.json"), structural_only=False
                )
            },
        )

    def test_fixed_git_ref_is_verified_from_commit_and_rejects_symlink_blob(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.test"], check=True)
            subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
            artifact_path = repository / "artifact.json"
            artifact_path.write_bytes(b"fixed bytes\n")
            os.symlink("artifact.json", repository / "alias.json")
            subprocess.run(["git", "-C", str(repository), "add", "artifact.json", "alias.json"], check=True)
            subprocess.run(["git", "-C", str(repository), "commit", "-qm", "fixture"], check=True)
            commit = subprocess.run(
                ["git", "-C", str(repository), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            digest = hashlib.sha256(b"fixed bytes\n").hexdigest()
            direct = {"target": target("artifact.json", commit), "sha256": digest}
            self.assertEqual(validate_fixed_ref(direct, repository=repository, structural_only=False), [])
            artifact_path.write_bytes(b"changed working tree\n")
            self.assertEqual(validate_fixed_ref(direct, repository=repository, structural_only=False), [])
            wrong = copy.deepcopy(direct)
            wrong["sha256"] = D2
            self.assertIn(
                "fixed_ref.digest_mismatch",
                {item.code for item in validate_fixed_ref(wrong, repository=repository, structural_only=False)},
            )
            symlink_ref = {"target": target("alias.json", commit), "sha256": hashlib.sha256(b"artifact.json").hexdigest()}
            self.assertIn(
                "fixed_ref.symlink",
                {item.code for item in validate_fixed_ref(symlink_ref, repository=repository, structural_only=False)},
            )

    def test_assessment_claims_require_project_context_and_real_evidence(self) -> None:
        value = assessment(dimension="human_acceptance", assessor="alice")
        self.assertIn(
            "assessment.project_context_required",
            {item.code for item in validate_assessment(value)},
        )
        evidence = {D3: ref("different/report.json", C3, D3)}
        self.assertIn(
            "assessment.evidence_mismatch",
            {
                item.code
                for item in validate_assessment(
                    value,
                    project=fixed_project(),
                    project_digest=D1,
                    evidence_by_digest=evidence,
                )
            },
        )

    def test_migration_receipt_cannot_pass_by_self_report(self) -> None:
        self.assertEqual(
            {item.code for item in validate_migration_receipt(MigrationTests().receipt())},
            {"migration.context_required"},
        )

    def test_provider_neutrality_and_no_workflow_or_blocked_claims(self) -> None:
        forbidden = ("claude", "codex", "anthropic", "openai", "mcp", "hook", "permission")
        product_claims = ("automatic_next_workflow", "next_workflow")
        roots = (
            CONTRACTS / "semantics",
            ROOT / "src" / "research_os" / "validation" / "semantics",
        )
        for root in roots:
            for path in root.rglob("*"):
                if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                text = path.read_text(encoding="utf-8").casefold()
                for token in forbidden + product_claims:
                    with self.subTest(path=path, token=token):
                        self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
