from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from research_os.install import (  # noqa: E402
    AdapterDefinition,
    CapabilityProfile,
    CapabilityState,
    ProjectionBlocked,
    SkillDescriptor,
    SkillKind,
    build_projection,
    load_adapter_definition,
)


def skill(name: str, kind: SkillKind) -> SkillDescriptor:
    content = f"---\nname: {name}\ndescription: fixture\n---\n\n# {name}\n".encode()
    return SkillDescriptor(
        name=name,
        version="1.0.0",
        kind=kind,
        sha256=hashlib.sha256(content).hexdigest(),
        content=content,
    )


class AdapterProjectionTests(unittest.TestCase):
    def test_adapter_definitions_are_strict_and_current(self) -> None:
        for name in ("claude-code", "codex"):
            definition, digest = load_adapter_definition(ROOT / "adapters" / f"{name}.json")
            self.assertEqual(definition.adapter, name)
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            self.assertFalse(definition.automatic_next_workflow)
            self.assertEqual(definition.workflow_invocation, "explicit_user_only")

    def test_claude_projection_separates_workflows_and_disciplines_and_pins_sources(self) -> None:
        definition, digest = load_adapter_definition(ROOT / "adapters/claude-code.json")
        plan = build_projection(
            definition,
            digest,
            [skill("research-charter", SkillKind.WORKFLOW), skill("statistical-check", SkillKind.DISCIPLINE)],
        )
        self.assertNotIsInstance(plan, ProjectionBlocked)
        files = {item.path: item.content for item in plan.files}
        workflow = files[".claude/skills/research-charter/SKILL.md"].decode()
        discipline = files[".claude/skills/statistical-check/SKILL.md"].decode()
        self.assertIn("disable-model-invocation: true\n", workflow)
        self.assertIn("user-invocable: true\n", workflow)
        self.assertIn("user-invocable: false\n", discipline)
        self.assertNotIn("disable-model-invocation", discipline)
        manifest = plan.manifest.to_dict()
        self.assertEqual(manifest["adapter"]["sha256"], digest)
        self.assertEqual(manifest["projection_scope"], "complete")
        self.assertEqual(manifest["excluded_canonical_skills"], [])
        self.assertEqual(manifest["blocked_capabilities"], [])
        self.assertEqual(manifest["workflow_entries"], ["research-charter"])
        self.assertEqual(manifest["discipline_entries"], ["statistical-check"])
        self.assertFalse(manifest["automatic_next_workflow"])
        self.assertRegex(manifest["projection_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(json.loads(files[".research-os/projections/claude-code/manifest.json"]), manifest)

    def test_codex_projection_blocks_disciplines_and_workflow_only_projection_is_explicit(self) -> None:
        definition, digest = load_adapter_definition(ROOT / "adapters/codex.json")
        blocked = build_projection(
            definition,
            digest,
            [skill("research-charter", SkillKind.WORKFLOW), skill("proof-review", SkillKind.DISCIPLINE)],
        )
        self.assertIsInstance(blocked, ProjectionBlocked)
        self.assertEqual(blocked.missing_capabilities, ("discipline_private_visibility",))
        plan = build_projection(
            definition,
            digest,
            [skill("research-charter", SkillKind.WORKFLOW)],
        )
        self.assertNotIsInstance(plan, ProjectionBlocked)
        files = {item.path: item.content for item in plan.files}
        self.assertEqual(
            files[".agents/skills/research-charter/agents/openai.yaml"],
            b"policy:\n  allow_implicit_invocation: false\n",
        )
        self.assertEqual(plan.manifest.workflow_entries, ("research-charter",))
        self.assertEqual(plan.manifest.discipline_entries, ())

    def test_empty_configured_requirements_cannot_remove_platform_skill_baselines(self) -> None:
        for platform, kind, capability in (
            ("claude-code", SkillKind.WORKFLOW, "workflow_model_invocation_control"),
            ("claude-code", SkillKind.DISCIPLINE, "discipline_private_visibility"),
            ("codex", SkillKind.WORKFLOW, "workflow_implicit_invocation_control"),
            ("codex", SkillKind.DISCIPLINE, "discipline_private_visibility"),
        ):
            for state in (None, "unsupported", "unverified"):
                with self.subTest(platform=platform, kind=kind, state=state):
                    value = json.loads((ROOT / "adapters" / f"{platform}.json").read_text())
                    value["required_capabilities"] = []
                    capabilities = value["capability_profile"]["capabilities"]
                    if state is None:
                        capabilities.pop(capability)
                    else:
                        capabilities[capability] = state
                    result = build_projection(
                        AdapterDefinition.from_dict(value), "a" * 64, [skill("example", kind)]
                    )
                    self.assertIsInstance(result, ProjectionBlocked)
                    self.assertIn(capability, result.missing_capabilities)
                    self.assertEqual(result.exit_code, 3)
                    self.assertEqual(result.to_dict()["outputs"], [])

    def test_configured_capabilities_only_add_to_the_selected_skill_kind_baseline(self) -> None:
        for platform, kind, capability in (
            ("claude-code", SkillKind.WORKFLOW, "workflow_model_invocation_control"),
            ("claude-code", SkillKind.DISCIPLINE, "discipline_private_visibility"),
            ("codex", SkillKind.WORKFLOW, "workflow_implicit_invocation_control"),
            ("codex", SkillKind.DISCIPLINE, "discipline_private_visibility"),
        ):
            with self.subTest(platform=platform, kind=kind):
                value = json.loads((ROOT / "adapters" / f"{platform}.json").read_text())
                value["required_capabilities"] = []
                value["capability_profile"]["capabilities"] = {capability: "supported"}
                selected = [skill("example", kind)]
                result = build_projection(AdapterDefinition.from_dict(value), "a" * 64, selected)
                self.assertNotIsInstance(result, ProjectionBlocked)
                self.assertTrue(result.files)

                value["required_capabilities"] = ["execution_isolation"]
                result = build_projection(AdapterDefinition.from_dict(value), "a" * 64, selected)
                self.assertIsInstance(result, ProjectionBlocked)
                self.assertEqual(result.missing_capabilities, ("execution_isolation",))

                value["capability_profile"]["capabilities"]["execution_isolation"] = "supported"
                result = build_projection(AdapterDefinition.from_dict(value), "a" * 64, selected)
                self.assertNotIsInstance(result, ProjectionBlocked)

    def test_adapter_capability_claims_match_enforced_policy_shape(self) -> None:
        for platform in ("claude-code", "codex"):
            with self.subTest(platform=platform):
                value = json.loads((ROOT / "adapters" / f"{platform}.json").read_text())
                if platform == "claude-code":
                    value["workflow_policy"]["disable_model_invocation"] = False
                else:
                    value["discipline_policy"].pop("allow_implicit_invocation")
                with self.assertRaises(ValueError):
                    AdapterDefinition.from_dict(value)

    def test_codex_projection_blocks_disciplines_when_private_visibility_is_unsupported(self) -> None:
        definition, digest = load_adapter_definition(ROOT / "adapters/codex.json")
        result = build_projection(
            definition,
            digest,
            [skill("research-charter", SkillKind.WORKFLOW), skill("proof-review", SkillKind.DISCIPLINE)],
        )
        self.assertIsInstance(result, ProjectionBlocked)
        self.assertEqual(result.missing_capabilities, ("discipline_private_visibility",))
        self.assertEqual(result.exit_code, 3)
        self.assertEqual(result.to_dict()["outputs"], [])

    def test_codex_explicit_workflow_only_scope_records_blocked_disciplines(self) -> None:
        definition, digest = load_adapter_definition(ROOT / "adapters/codex.json")
        workflow = skill("research-charter", SkillKind.WORKFLOW)
        discipline = skill("proof-review", SkillKind.DISCIPLINE)
        plan = build_projection(
            definition,
            digest,
            [workflow],
            excluded_skills=[discipline],
            projection_scope="workflow-only",
            blocked_capabilities=("discipline_private_visibility",),
        )
        self.assertNotIsInstance(plan, ProjectionBlocked)
        manifest = plan.manifest.to_dict()
        self.assertEqual(manifest["projection_scope"], "workflow-only")
        self.assertEqual(manifest["workflow_entries"], ["research-charter"])
        self.assertEqual(manifest["discipline_entries"], [])
        self.assertEqual(
            manifest["excluded_canonical_skills"],
            [{"name": "proof-review", "version": "1.0.0", "kind": "discipline", "sha256": discipline.sha256}],
        )
        self.assertEqual(manifest["blocked_capabilities"], ["discipline_private_visibility"])
        self.assertFalse(any("proof-review" in item.path for item in plan.files))

        with self.assertRaises(ValueError):
            build_projection(
                definition,
                digest,
                [workflow],
                excluded_skills=[discipline],
                projection_scope="workflow-only",
            )

        value = json.loads((ROOT / "adapters/codex.json").read_text())
        value["required_capabilities"] = [
            "discipline_private_visibility",
            "workflow_implicit_invocation_control",
        ]
        value["capability_profile"]["capabilities"]["discipline_private_visibility"] = "supported"
        definition = AdapterDefinition.from_dict(value)
        plan = build_projection(
            definition,
            "a" * 64,
            [skill("research-charter", SkillKind.WORKFLOW), skill("proof-review", SkillKind.DISCIPLINE)],
        )
        self.assertNotIsInstance(plan, ProjectionBlocked)
        files = {item.path: item.content.decode() for item in plan.files}
        for name in ("research-charter", "proof-review"):
            policy = files[f".agents/skills/{name}/agents/openai.yaml"]
            self.assertEqual(policy, "policy:\n  allow_implicit_invocation: false\n")
            self.assertNotIn("visibility", policy)

    def test_missing_or_unverified_required_capability_blocks_without_files(self) -> None:
        definition = AdapterDefinition(
            adapter="codex",
            version="1.0.0",
            projection_version="1.0.0",
            workflow_invocation="explicit_user_only",
            automatic_next_workflow=False,
            workflow_policy={"allow_implicit_invocation": False},
            discipline_policy={"allow_implicit_invocation": False},
            required_capabilities=("discipline_private_visibility", "execution_isolation"),
            capability_profile=CapabilityProfile(
                version="1.0.0",
                capabilities={
                    "discipline_private_visibility": CapabilityState.SUPPORTED,
                    "execution_isolation": CapabilityState.UNVERIFIED,
                },
            ),
        )
        result = build_projection(definition, "a" * 64, [skill("research-charter", SkillKind.WORKFLOW)])
        self.assertIsInstance(result, ProjectionBlocked)
        self.assertEqual(result.exit_code, 3)
        self.assertEqual(
            result.missing_capabilities,
            ("execution_isolation", "workflow_implicit_invocation_control"),
        )
        self.assertEqual(result.to_dict()["outputs"], [])
        self.assertEqual(result.to_dict()["next_steps"], [])

    def test_projection_is_deterministic_and_rejects_drifted_skill_digest(self) -> None:
        definition, digest = load_adapter_definition(ROOT / "adapters/claude-code.json")
        skills = [skill("zeta-workflow", SkillKind.WORKFLOW), skill("alpha-discipline", SkillKind.DISCIPLINE)]
        first = build_projection(definition, digest, skills)
        second = build_projection(definition, digest, reversed(skills))
        self.assertEqual(first.manifest.to_dict(), second.manifest.to_dict())
        with self.assertRaises(ValueError):
            SkillDescriptor(
                name="bad-skill",
                version="1.0.0",
                kind=SkillKind.WORKFLOW,
                sha256="0" * 64,
                content=b"---\nname: bad-skill\n---\n",
            )

    def test_adapter_parser_rejects_unknown_fields_and_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "adapter.json"
            value = json.loads((ROOT / "adapters/codex.json").read_text())
            value["provider_semantics"] = "override"
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                load_adapter_definition(path)
            path.unlink()
            path.symlink_to(ROOT / "adapters/codex.json")
            with self.assertRaises(ValueError):
                load_adapter_definition(path)


if __name__ == "__main__":
    unittest.main()
