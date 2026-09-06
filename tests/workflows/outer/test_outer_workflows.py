from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_os.workflows.outer import (
    InputPin,
    OuterWorkflowError,
    WORKFLOWS,
    run_outer_workflow,
)

ROOT = Path(__file__).resolve().parents[3]


def artifact(path: str, type_name: str, spec: dict[str, object]) -> dict[str, object]:
    return {
        "contract": {"name": "research-os/artifact", "version": "1.1.0"},
        "target": {"kind": "git", "path": path},
        "type": {"name": type_name, "version": "1.0.0"},
        "spec": spec,
    }


def write_json(path: Path, value: dict[str, object]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode()
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


class OuterWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def pin(self, path: str, value: dict[str, object]) -> InputPin:
        return InputPin(path, write_json(self.project / path, value))

    def invoke(self, workflow: str, pins: list[InputPin], stem: str):
        return run_outer_workflow(
            workflow,
            project=self.project,
            inputs=pins,
            output_path=f"artifacts/{stem}.json",
            report_path=f"reports/{stem}.json",
        )

    def assert_stopped(self, result, workflow: str) -> None:
        report = result.report
        self.assertEqual(report["workflow"]["name"], workflow)
        self.assertEqual(report["status"], "stopped")
        self.assertEqual(report["stop_reason"], "candidate_complete")
        self.assertFalse(report["automatic_next_workflow"])
        self.assertIsNone(report["human_acceptance"])
        self.assertTrue(report["next_steps"])
        self.assertEqual(set(report["budget"]["limits"]), set(report["budget"]["used"]))
        for counter, used in report["budget"]["used"].items():
            self.assertLessEqual(used, report["budget"]["limits"][counter])
        self.assertEqual(result.artifact["spec"]["status"], "candidate")
        self.assertNotIn("assurance", result.artifact)

    def test_inventory_skill_docs_and_templates_are_complete(self) -> None:
        expected = {
            "research-charter",
            "research-literature",
            "research-gap",
            "research-idea",
            "research-novelty",
            "research-reflect",
        }
        self.assertEqual(set(WORKFLOWS), expected)
        for name in expected:
            skill = (ROOT / "core" / "skills" / name / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn(f"name: {name}\n", skill)
            self.assertIn("Invocation: user only", skill)
            self.assertIn("Fixed budget", skill)
            self.assertIn("then stop", skill.lower())
        templates = ROOT / "templates" / "outer"
        self.assertEqual(
            {path.name for path in templates.glob("*.json")},
            {
                "research-charter.input.json",
                "research-literature.input.json",
                "research-gap.input.json",
                "research-idea.input.json",
                "research-novelty.inputs.json",
                "research-reflect.input.json",
                "workflow-report.json",
            },
        )
        for path in templates.glob("*.json"):
            json.loads(path.read_bytes())

    def test_all_six_build_candidates_reports_options_and_stop(self) -> None:
        charter = self.invoke(
            "research-charter",
            [
                self.pin(
                    "inputs/question.json",
                    artifact(
                        "inputs/question.json",
                        "research-question",
                        {
                            "question": "Can a fixed baseline improve reproducibility?",
                            "boundaries": ["CPU-only", "No private datasets"],
                            "success_criteria": ["Repeatable output"],
                            "budget": {"hours": 8},
                            "invariants": ["Keep the question unchanged"],
                        },
                    ),
                )
            ],
            "charter",
        )
        self.assert_stopped(charter, "research-charter")
        self.assertEqual(
            charter.artifact["spec"]["boundaries"], ["CPU-only", "No private datasets"]
        )

        literature_input = artifact(
            "inputs/charter.json",
            "research-charter",
            {
                **charter.artifact["spec"],
                "citations": [
                    {"title": "Pinned A", "uri": "https://example.invalid/a"}
                ],
                "literature_synthesis": "Pinned synthesis.",
                "literature_limitations": ["One source"],
            },
        )
        literature = self.invoke(
            "research-literature",
            [self.pin("inputs/charter.json", literature_input)],
            "literature",
        )
        self.assert_stopped(literature, "research-literature")
        self.assertEqual(literature.artifact["spec"]["queries"], [])

        gap_input = artifact(
            "inputs/literature.json",
            "literature-review",
            {
                **literature.artifact["spec"],
                "gap_candidates": [
                    {
                        "statement": "No pinned CPU baseline comparison.",
                        "evidence": [
                            {"title": "Pinned A", "uri": "https://example.invalid/a"}
                        ],
                    },
                    {
                        "statement": "Failure reporting is underspecified.",
                        "evidence": [
                            {"title": "Pinned A", "uri": "https://example.invalid/a"}
                        ],
                    },
                    {
                        "statement": "Replay is not measured.",
                        "evidence": [
                            {"title": "Pinned A", "uri": "https://example.invalid/a"}
                        ],
                    },
                    {
                        "statement": "This fourth candidate exceeds the budget.",
                        "evidence": [],
                    },
                ],
            },
        )
        gap = self.invoke(
            "research-gap", [self.pin("inputs/literature.json", gap_input)], "gap"
        )
        self.assert_stopped(gap, "research-gap")
        self.assertEqual(len(gap.artifact["spec"]["gaps"]), 3)
        self.assertIsNone(gap.artifact["spec"]["selection"])

        idea_input = artifact(
            "inputs/gap.json",
            "research-gap",
            {
                **gap.artifact["spec"],
                "selected_gap": gap.artifact["spec"]["gaps"][0],
                "idea_candidates": [
                    {
                        "proposal": "Compare fixed CPU baselines.",
                        "assumptions": ["Comparable hosts"],
                        "tests": ["Replay"],
                    }
                ],
            },
        )
        idea = self.invoke(
            "research-idea", [self.pin("inputs/gap.json", idea_input)], "idea"
        )
        self.assert_stopped(idea, "research-idea")
        self.assertIsNone(idea.artifact["spec"]["novelty_claim"])

        novelty_literature = artifact(
            "inputs/novelty-literature.json",
            "literature-review",
            {
                **literature.artifact["spec"],
                "prior_work": [
                    {
                        "title": "Pinned A",
                        "observed_difference": "No deterministic seam",
                    }
                ],
            },
        )
        novelty = self.invoke(
            "research-novelty",
            [
                self.pin(
                    "inputs/idea.json",
                    artifact(
                        "inputs/idea.json", "research-idea", dict(idea.artifact["spec"])
                    ),
                ),
                self.pin("inputs/novelty-literature.json", novelty_literature),
            ],
            "novelty",
        )
        self.assert_stopped(novelty, "research-novelty")
        self.assertEqual(novelty.artifact["spec"]["novelty_verdict"], "inconclusive")
        self.assertEqual(novelty.artifact["spec"]["coverage"], "pinned-prior-work-only")

        reflection = self.invoke(
            "research-reflect",
            [
                self.pin(
                    "inputs/reflection.json",
                    artifact(
                        "inputs/reflection.json",
                        "reflection-input",
                        {
                            "observations": ["Pinned observation"],
                            "failures": ["Pinned failed attempt"],
                            "uncertainties": ["Pinned uncertainty"],
                        },
                    ),
                ),
                self.pin(
                    "inputs/novelty.json",
                    artifact(
                        "inputs/novelty.json",
                        "novelty-review",
                        {
                            **novelty.artifact["spec"],
                            "observations": ["Novelty remains inconclusive"],
                            "failures": [],
                            "uncertainties": ["Coverage remains bounded"],
                        },
                    ),
                ),
            ],
            "reflection",
        )
        self.assert_stopped(reflection, "research-reflect")
        self.assertEqual(reflection.artifact["spec"]["decisions"], [])
        self.assertIn(
            "Pinned failed attempt",
            [item["value"] for item in reflection.artifact["spec"]["failures"]],
        )

        generated = {path.stem for path in (self.project / "artifacts").glob("*.json")}
        self.assertEqual(
            generated, {"charter", "literature", "gap", "idea", "novelty", "reflection"}
        )

    def test_charter_rejects_empty_or_implicit_boundaries_without_outputs(self) -> None:
        for boundaries in ([], ["  "]):
            with self.subTest(boundaries=boundaries):
                project = Path(self.temporary.name) / (
                    "case-empty" if not boundaries else "case-blank"
                )
                project.mkdir()
                value = artifact(
                    "question.json",
                    "research-question",
                    {
                        "question": "A question with no explicit boundary",
                        "boundaries": boundaries,
                    },
                )
                digest = write_json(project / "question.json", value)
                with self.assertRaisesRegex(
                    OuterWorkflowError, "explicit boundary"
                ) as error:
                    run_outer_workflow(
                        "research-charter",
                        project=project,
                        inputs=[InputPin("question.json", digest)],
                        output_path="candidate.json",
                        report_path="report.json",
                    )
                self.assertEqual(error.exception.code, "charter.boundaries.empty")
                self.assertFalse((project / "candidate.json").exists())
                self.assertFalse((project / "report.json").exists())

    def test_pin_type_count_order_and_duplicate_inputs_are_enforced(self) -> None:
        idea_pin = self.pin(
            "idea.json",
            artifact(
                "idea.json", "research-idea", {"ideas": [{"proposal": "Pinned idea"}]}
            ),
        )
        literature_pin = self.pin(
            "literature.json",
            artifact(
                "literature.json",
                "literature-review",
                {"question": "Q", "citations": []},
            ),
        )
        cases = (
            ("research-charter", [idea_pin], "input.type"),
            ("research-novelty", [idea_pin], "input.count"),
            ("research-novelty", [literature_pin, idea_pin], "input.type"),
            ("research-novelty", [idea_pin, idea_pin], "output.overlap"),
        )
        for index, (workflow, pins, code) in enumerate(cases):
            with self.subTest(workflow=workflow, code=code):
                with self.assertRaises(OuterWorkflowError) as error:
                    run_outer_workflow(
                        workflow,
                        project=self.project,
                        inputs=pins,
                        output_path=f"out-{index}.json",
                        report_path=f"report-{index}.json",
                    )
                self.assertEqual(error.exception.code, code)
        bad_pin = InputPin("idea.json", "0" * 64)
        with self.assertRaises(OuterWorkflowError) as error:
            self.invoke("research-idea", [bad_pin], "bad-pin")
        self.assertEqual(error.exception.code, "input.pin.mismatch")

    def test_outputs_are_safe_non_overwriting_and_inputs_remain_byte_identical(
        self,
    ) -> None:
        source = artifact(
            "question.json",
            "research-question",
            {"question": "Pinned?", "boundaries": ["One boundary"]},
        )
        pin = self.pin("question.json", source)
        before = (self.project / "question.json").read_bytes()
        first = self.invoke("research-charter", [pin], "safe")
        candidate_before = (self.project / "artifacts/safe.json").read_bytes()
        report_before = (self.project / "reports/safe.json").read_bytes()
        with self.assertRaises(OuterWorkflowError) as error:
            self.invoke("research-charter", [pin], "safe")
        self.assertEqual(error.exception.code, "output.exists")
        self.assertEqual(
            (self.project / "artifacts/safe.json").read_bytes(), candidate_before
        )
        self.assertEqual(
            (self.project / "reports/safe.json").read_bytes(), report_before
        )
        self.assertEqual((self.project / "question.json").read_bytes(), before)
        self.assertEqual(
            hashlib.sha256(candidate_before).hexdigest(),
            first.report["outputs"][0]["sha256"],
        )
        for output, report in (
            ("same.json", "same.json"),
            ("question.json", "other.json"),
            ("../escape", "r.json"),
        ):
            with self.subTest(output=output, report=report):
                with self.assertRaises(OuterWorkflowError):
                    run_outer_workflow(
                        "research-charter",
                        project=self.project,
                        inputs=[pin],
                        output_path=output,
                        report_path=report,
                    )

    def test_symlinks_are_rejected_for_inputs_and_output_parents(self) -> None:
        outside = self.project.parent / f"{self.project.name}-outside"
        outside.mkdir(exist_ok=True)
        outside_file = outside / "question.json"
        digest = write_json(
            outside_file,
            artifact(
                "question.json",
                "research-question",
                {"question": "Q", "boundaries": ["B"]},
            ),
        )
        (self.project / "linked.json").symlink_to(outside_file)
        with self.assertRaises(OuterWorkflowError) as error:
            run_outer_workflow(
                "research-charter",
                project=self.project,
                inputs=[InputPin("linked.json", digest)],
                output_path="candidate.json",
                report_path="report.json",
            )
        self.assertEqual(error.exception.code, "path.symlink")

        pin = self.pin(
            "question.json",
            artifact(
                "question.json",
                "research-question",
                {"question": "Q", "boundaries": ["B"]},
            ),
        )
        (self.project / "linked-dir").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OuterWorkflowError) as error:
            run_outer_workflow(
                "research-charter",
                project=self.project,
                inputs=[pin],
                output_path="linked-dir/candidate.json",
                report_path="report.json",
            )
        self.assertEqual(error.exception.code, "path.symlink")

    def test_output_created_during_parent_setup_is_preserved(self) -> None:
        pin = self.pin(
            "question.json",
            artifact(
                "question.json",
                "research-question",
                {"question": "Q", "boundaries": ["B"]},
            ),
        )
        import research_os.workflows.outer.runner as runner

        original = runner._ensure_output_parent

        def racing_parent(project: Path, destination: Path, field: str) -> None:
            original(project, destination, field)
            if (
                field == "report"
                and not (self.project / "artifacts/race.json").exists()
            ):
                (self.project / "artifacts/race.json").write_text(
                    "concurrent owner\n", encoding="utf-8"
                )

        runner._ensure_output_parent = racing_parent
        try:
            with self.assertRaises(OuterWorkflowError) as error:
                run_outer_workflow(
                    "research-charter",
                    project=self.project,
                    inputs=[pin],
                    output_path="artifacts/race.json",
                    report_path="reports/race.json",
                )
        finally:
            runner._ensure_output_parent = original
        self.assertEqual(error.exception.code, "output.exists")
        self.assertEqual(
            (self.project / "artifacts/race.json").read_text(encoding="utf-8"),
            "concurrent owner\n",
        )
        self.assertFalse((self.project / "reports/race.json").exists())

    def test_typed_candidate_payload_is_bounded_and_invariants_are_enforced(
        self,
    ) -> None:
        pin = self.pin(
            "question.json",
            artifact(
                "question.json",
                "research-question",
                {
                    "question": "Pinned question",
                    "boundaries": ["Pinned source boundary"],
                    "success_criteria": [],
                    "budget": {"hours": 2},
                    "invariants": [],
                },
            ),
        )
        result = run_outer_workflow(
            "research-charter",
            project=self.project,
            inputs=[pin],
            output_path="candidate.json",
            report_path="report.json",
                candidate={
                    "question": "Pinned question",
                    "boundaries": ["Pinned source boundary"],
                    "success_criteria": [],
                    "budget": {"hours": 2},
                    "invariants": [],
                },
            )
        self.assertEqual(
            result.artifact["spec"]["boundaries"], ["Pinned source boundary"]
        )
        changed = Path(self.temporary.name) / "changed-question"
        changed.mkdir()
        changed_pin = InputPin(
            "question.json",
            write_json(
                changed / "question.json",
                artifact(
                    "question.json",
                    "research-question",
                    {"question": "Pinned question", "boundaries": ["B"]},
                ),
            ),
        )
        with self.assertRaises(OuterWorkflowError) as error:
            run_outer_workflow(
                "research-charter",
                project=changed,
                inputs=[changed_pin],
                output_path="candidate.json",
                report_path="report.json",
                candidate={
                    "question": "Rewritten question",
                    "boundaries": ["B"],
                },
            )
        self.assertEqual(error.exception.code, "invariant.question")

        literature_project = Path(self.temporary.name) / "literature-candidate"
        literature_project.mkdir()
        literature_pin = InputPin(
            "charter.json",
            write_json(
                literature_project / "charter.json",
                artifact(
                    "charter.json",
                    "research-charter",
                    {
                        "question": "Pinned question",
                        "boundaries": ["B"],
                        "citations": [{"title": "Pinned source"}],
                    },
                ),
            ),
        )
        with self.assertRaises(OuterWorkflowError) as error:
            run_outer_workflow(
                "research-literature",
                project=literature_project,
                inputs=[literature_pin],
                output_path="candidate.json",
                report_path="report.json",
                candidate={
                    "question": "Pinned question",
                    "boundaries": ["B"],
                    "citations": [{"title": "Unpinned source"}],
                    "synthesis": "Candidate synthesis",
                    "limitations": [],
                },
            )
        self.assertEqual(error.exception.code, "invariant.unpinned_source")

    def test_unpinned_material_is_not_read_or_copied(self) -> None:
        secret = self.project / "secret.txt"
        secret.write_text("must not be copied", encoding="utf-8")
        pin = self.pin(
            "literature.json",
            artifact(
                "literature.json",
                "literature-review",
                {"question": "Q", "citations": [], "gap_candidates": []},
            ),
        )
        result = self.invoke("research-gap", [pin], "no-secret")
        combined = json.dumps({"artifact": result.artifact, "report": result.report})
        self.assertNotIn("must not be copied", combined)
        self.assertEqual(result.artifact["spec"]["gaps"][0]["support"], "unsupported")

    def test_artifact_target_and_envelope_are_part_of_the_pin_contract(self) -> None:
        mismatched = artifact(
            "other.json",
            "research-question",
            {"question": "Q", "boundaries": ["B"]},
        )
        for index, (value, code) in enumerate(
            (
                (mismatched, "input.target"),
                ({**mismatched, "provider_options": {"engine": "x"}}, "input.schema"),
            )
        ):
            with self.subTest(code=code):
                path = f"input-{index}.json"
                pin = self.pin(path, value)
                with self.assertRaises(OuterWorkflowError) as error:
                    self.invoke("research-charter", [pin], f"invalid-{index}")
                self.assertEqual(error.exception.code, code)

    def test_gap_evidence_must_be_pinned_and_empty_evidence_is_unsupported(self) -> None:
        citation = {"title": "Pinned source", "uri": "https://example.invalid/a"}
        pin = self.pin(
            "literature.json",
            artifact(
                "literature.json",
                "literature-review",
                {"question": "Q", "citations": [citation]},
            ),
        )
        with self.assertRaises(OuterWorkflowError) as error:
            run_outer_workflow(
                "research-gap",
                project=self.project,
                inputs=[pin],
                output_path="bad-gap.json",
                report_path="bad-gap-report.json",
                candidate={
                    "question": "Q",
                    "gaps": [{"statement": "Invented support", "evidence": ["Elsewhere"]}],
                },
            )
        self.assertEqual(error.exception.code, "invariant.unpinned_source")
        self.assertFalse((self.project / "bad-gap.json").exists())
        self.assertFalse((self.project / "bad-gap-report.json").exists())

        result = run_outer_workflow(
            "research-gap",
            project=self.project,
            inputs=[pin],
            output_path="unsupported-gap.json",
            report_path="unsupported-gap-report.json",
            candidate={
                "question": "Q",
                "gaps": [{"statement": "Needs evidence", "evidence": []}],
            },
        )
        self.assertEqual(result.artifact["spec"]["gaps"][0]["support"], "unsupported")

    def test_idea_and_novelty_require_explicit_pinned_selection(self) -> None:
        gap_pin = self.pin(
            "gap.json",
            artifact(
                "gap.json",
                "research-gap",
                {
                    "gaps": [
                        {"statement": "First", "evidence": [], "support": "unsupported"},
                        {"statement": "Second", "evidence": [], "support": "unsupported"},
                    ],
                    "selected_gap": None,
                },
            ),
        )
        with self.assertRaises(OuterWorkflowError) as error:
            self.invoke("research-idea", [gap_pin], "implicit-gap")
        self.assertEqual(error.exception.code, "idea.gap.selection_required")

        idea_pin = self.pin(
            "idea.json",
            artifact(
                "idea.json",
                "research-idea",
                {
                    "ideas": [
                        {"proposal": "First", "assumptions": [], "tests": []},
                        {"proposal": "Second", "assumptions": [], "tests": []},
                    ],
                    "selected_idea": None,
                },
            ),
        )
        literature_pin = self.pin(
            "novelty-literature.json",
            artifact(
                "novelty-literature.json",
                "literature-review",
                {"question": "Q", "citations": []},
            ),
        )
        with self.assertRaises(OuterWorkflowError) as error:
            self.invoke(
                "research-novelty", [idea_pin, literature_pin], "implicit-idea"
            )
        self.assertEqual(error.exception.code, "novelty.idea.selection_required")

    def test_candidate_budgets_are_hard_and_nested_payloads_are_typed(self) -> None:
        gap_pin = self.pin(
            "selected-gap.json",
            artifact(
                "selected-gap.json",
                "research-gap",
                {"selected_gap": {"statement": "Pinned gap"}, "gaps": []},
            ),
        )
        with self.assertRaises(OuterWorkflowError) as error:
            run_outer_workflow(
                "research-idea",
                project=self.project,
                inputs=[gap_pin],
                output_path="too-many-ideas.json",
                report_path="too-many-ideas-report.json",
                candidate={
                    "gap": "Pinned gap",
                    "ideas": [
                        {"proposal": f"Idea {index}", "assumptions": [], "tests": []}
                        for index in range(4)
                    ],
                },
            )
        self.assertEqual(error.exception.code, "budget.exceeded")

        idea_pin = self.pin(
            "selected-idea.json",
            artifact(
                "selected-idea.json",
                "research-idea",
                {
                    "selected_idea": {"proposal": "Pinned idea"},
                    "ideas": [],
                },
            ),
        )
        literature_pin = self.pin(
            "typed-literature.json",
            artifact(
                "typed-literature.json",
                "literature-review",
                {
                    "question": "Q",
                    "prior_work": [{"title": "Pinned work"}],
                    "citations": [],
                },
            ),
        )
        result = run_outer_workflow(
            "research-novelty",
            project=self.project,
            inputs=[idea_pin, literature_pin],
            output_path="typed-novelty.json",
            report_path="typed-novelty-report.json",
            candidate={
                "idea": "Pinned idea",
                "comparisons": [
                    {
                        "prior_work": "Pinned work",
                        "observed_difference": "Bounded difference",
                    }
                ],
                "limitations": ["Pinned coverage only"],
            },
        )
        self.assertEqual(
            result.artifact["spec"]["comparisons"],
            [
                {
                    "prior_work": "Pinned work",
                    "observed_difference": "Bounded difference",
                }
            ],
        )

    def test_candidate_payload_rejects_unknown_fields_without_outputs(self) -> None:
        pin = self.pin(
            "candidate-schema-question.json",
            artifact(
                "candidate-schema-question.json",
                "research-question",
                {"question": "Q", "boundaries": ["B"]},
            ),
        )
        with self.assertRaises(OuterWorkflowError) as error:
            run_outer_workflow(
                "research-charter",
                project=self.project,
                inputs=[pin],
                output_path="unknown-candidate.json",
                report_path="unknown-candidate-report.json",
                candidate={
                    "question": "Q",
                    "boundaries": ["B"],
                    "provider_options": {"engine": "leak"},
                },
            )
        self.assertEqual(error.exception.code, "candidate.schema")
        self.assertFalse((self.project / "unknown-candidate.json").exists())
        self.assertFalse((self.project / "unknown-candidate-report.json").exists())

    def test_charter_candidate_cannot_change_user_owned_contract_fields(self) -> None:
        base = {
            "question": "Pinned question",
            "boundaries": ["Pinned boundary"],
            "success_criteria": ["Pinned criterion"],
            "budget": {"hours": 2},
            "invariants": ["Pinned invariant"],
        }
        mutations = (
            ({**base, "boundaries": ["Expanded boundary"]}, "invariant.boundaries"),
            ({**base, "success_criteria": ["Easier criterion"]}, "invariant.success_criteria"),
            ({**base, "budget": {"hours": 20}}, "invariant.budget"),
            ({**base, "invariants": []}, "invariant.invariants"),
        )
        for index, (candidate, code) in enumerate(mutations):
            with self.subTest(code=code):
                project = self.project / f"charter-mutation-{index}"
                project.mkdir()
                digest = write_json(
                    project / "question.json",
                    artifact("question.json", "research-question", base),
                )
                with self.assertRaises(OuterWorkflowError) as error:
                    run_outer_workflow(
                        "research-charter",
                        project=project,
                        inputs=[InputPin("question.json", digest)],
                        output_path="candidate.json",
                        report_path="report.json",
                        candidate=candidate,
                    )
                self.assertEqual(error.exception.code, code)
                self.assertFalse((project / "candidate.json").exists())
                self.assertFalse((project / "report.json").exists())

    def test_input_symlink_swap_during_read_is_rejected_without_outputs(self) -> None:
        pin = self.pin(
            "input-swap-question.json",
            artifact(
                "input-swap-question.json",
                "research-question",
                {"question": "Q", "boundaries": ["B"]},
            ),
        )
        outside = self.project.parent / f"{self.project.name}-input-swap-outside"
        outside.mkdir(exist_ok=True)
        outside_file = outside / "replacement.json"
        outside_file.write_bytes((self.project / pin.path).read_bytes())
        import research_os.workflows.outer.runner as runner

        original = runner.hashlib.sha256
        calls = 0

        def swap_after_first_read(data: bytes = b""):
            nonlocal calls
            calls += 1
            digest = original(data)
            if calls == 1:
                source = self.project / pin.path
                source.unlink()
                source.symlink_to(outside_file)
            return digest

        runner.hashlib.sha256 = swap_after_first_read
        try:
            with self.assertRaises(OuterWorkflowError) as error:
                run_outer_workflow(
                    "research-charter",
                    project=self.project,
                    inputs=[pin],
                    output_path="input-swap-candidate.json",
                    report_path="input-swap-report.json",
                )
        finally:
            runner.hashlib.sha256 = original
        self.assertEqual(error.exception.code, "path.symlink")
        self.assertFalse((self.project / "input-swap-candidate.json").exists())
        self.assertFalse((self.project / "input-swap-report.json").exists())

    def test_symlink_swap_before_publish_is_rejected_without_path_escape(self) -> None:
        pin = self.pin(
            "swap-question.json",
            artifact(
                "swap-question.json",
                "research-question",
                {"question": "Q", "boundaries": ["B"]},
            ),
        )
        outside = self.project.parent / f"{self.project.name}-swap-outside"
        outside.mkdir(exist_ok=True)
        import research_os.workflows.outer.runner as runner

        original = runner._publish_exclusive
        calls = 0

        def swap_parent(temp: Path, destination: Path, project: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                holding = destination.parent.with_name("swap-holding")
                destination.parent.rename(holding)
                destination.parent.symlink_to(outside, target_is_directory=True)
            original(temp, destination, project)

        runner._publish_exclusive = swap_parent
        try:
            with self.assertRaises(OuterWorkflowError) as error:
                run_outer_workflow(
                    "research-charter",
                    project=self.project,
                    inputs=[pin],
                    output_path="swap/candidate.json",
                    report_path="reports/swap.json",
                )
        finally:
            runner._publish_exclusive = original
        self.assertEqual(error.exception.code, "path.changed")
        self.assertFalse((outside / "candidate.json").exists())

    def test_reflection_candidate_seam_preserves_negative_results_within_budget(self) -> None:
        pin = self.pin(
            "reflection.json",
            artifact(
                "reflection.json",
                "reflection-input",
                {
                    "observations": ["Pinned observation"],
                    "failures": ["Pinned failure"],
                    "uncertainties": ["Pinned uncertainty"],
                },
            ),
        )
        result = run_outer_workflow(
            "research-reflect",
            project=self.project,
            inputs=[pin],
            output_path="reflection-candidate.json",
            report_path="reflection-candidate-report.json",
            candidate={
                "observations": ["Candidate reflection"],
            },
        )
        spec = result.artifact["spec"]
        self.assertEqual(
            [item["value"] for item in spec["observations"]],
            ["Candidate reflection"],
        )
        self.assertEqual([item["value"] for item in spec["failures"]], ["Pinned failure"])
        self.assertEqual(
            [item["value"] for item in spec["uncertainties"]],
            ["Pinned uncertainty"],
        )
        self.assertEqual(spec["decisions"], [])
        self.assertNotIn("provider_options", json.dumps(result.artifact))
        self.assertEqual(result.report["budget"]["used"]["observation_count"], 3)
        self.assertEqual(
            result.report["budget"]["used"]["option_count"],
            len(result.report["next_steps"]),
        )

        crowded_project = Path(self.temporary.name) / "crowded-reflection"
        crowded_project.mkdir()
        crowded_value = artifact(
            "reflection.json",
            "reflection-input",
            {"failures": [f"failure-{index}" for index in range(13)]},
        )
        crowded_pin = InputPin(
            "reflection.json",
            write_json(crowded_project / "reflection.json", crowded_value),
        )
        with self.assertRaises(OuterWorkflowError) as error:
            run_outer_workflow(
                "research-reflect",
                project=crowded_project,
                inputs=[crowded_pin],
                output_path="candidate.json",
                report_path="report.json",
            )
        self.assertEqual(error.exception.code, "budget.exceeded")
        self.assertFalse((crowded_project / "candidate.json").exists())
        self.assertFalse((crowded_project / "report.json").exists())

    def test_late_report_collision_rolls_back_only_our_candidate(self) -> None:
        pin = self.pin(
            "question.json",
            artifact(
                "question.json",
                "research-question",
                {"question": "Q", "boundaries": ["B"]},
            ),
        )
        import research_os.workflows.outer.runner as runner

        original = runner._publish_exclusive
        calls = 0

        def collide_on_report(temp: Path, destination: Path, project: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                destination.write_text("concurrent report\n", encoding="utf-8")
            original(temp, destination, project)

        runner._publish_exclusive = collide_on_report
        try:
            with self.assertRaises(OuterWorkflowError) as error:
                self.invoke("research-charter", [pin], "late-collision")
        finally:
            runner._publish_exclusive = original
        self.assertEqual(error.exception.code, "output.exists")
        self.assertFalse((self.project / "artifacts/late-collision.json").exists())
        self.assertEqual(
            (self.project / "reports/late-collision.json").read_text(encoding="utf-8"),
            "concurrent report\n",
        )

    def test_owned_core_is_provider_neutral(self) -> None:
        forbidden = ("claude", "codex", "mcp", "hook", "permission", "model:", "tools:")
        roots = [
            *(ROOT / "core" / "skills" / name for name in WORKFLOWS),
            ROOT / "src" / "research_os" / "workflows" / "outer",
            ROOT / "templates" / "outer",
        ]
        for root in roots:
            for path in root.rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    content = path.read_text(encoding="utf-8").lower()
                    self.assertFalse(any(token in content for token in forbidden), path)


if __name__ == "__main__":
    unittest.main()
