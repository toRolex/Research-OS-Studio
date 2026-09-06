from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from research_os.workflows.computational import (  # noqa: E402
    BudgetCounter,
    BudgetExceeded,
    BudgetLimits,
    BudgetUsage,
    ExecutionReceipt,
    analyze_experiment,
    assess_result_to_claim,
    design_experiment,
    execute_local_command,
    prepare_experiment,
    run_experiment,
)
from research_os.workflows.computational.execution import (  # noqa: E402
    AttemptContext,
    write_outputs_exclusive,
)


def write_json(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return digest(path)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_bytes())


class ComputationalWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(self.project),
                "config",
                "user.email",
                "test@example.invalid",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.project), "config", "user.name", "Test"],
            check=True,
        )
        write_json(
            self.project / "question.json",
            {
                "contract": {"name": "research-os/artifact", "version": "1.1.0"},
                "target": {"kind": "git", "path": "question.json"},
                "type": {"name": "research-question", "version": "1.0.0"},
                "spec": {
                    "question": "Does the CPU baseline reproduce?",
                    "boundaries": ["CPU fixture"],
                },
            },
        )
        self.commit_all("question")
        write_json(
            self.project / "project.json",
            {
                "contract": {"name": "research-os/artifact", "version": "1.1.0"},
                "target": {"kind": "git", "path": "project.json"},
                "type": {"name": "project", "version": "1.0.0"},
                "spec": {
                    "name": "CPU reference",
                    "question": "Does the baseline reproduce?",
                    "boundaries": ["four-value CPU fixture"],
                    "principals": [
                        {"identity": "test-user", "roles": ["user", "researcher"]}
                    ],
                },
            },
        )
        revision = self.commit_all("project boundary")
        self.project_ref = {
            "target": {"kind": "git", "path": "project.json", "commit": revision},
            "sha256": digest(self.project / "project.json"),
        }
        write_json(
            self.project / "workstream.json",
            {
                "contract": {"name": "research-os/artifact", "version": "1.1.0"},
                "target": {"kind": "git", "path": "workstream.json"},
                "type": {"name": "workstream", "version": "1.0.0"},
                "spec": {
                    "project": self.project_ref,
                    "name": "CPU baseline",
                    "intent": "Compare the fixed criterion",
                    "state": "active",
                },
            },
        )
        revision = self.commit_all("workstream boundary")
        self.workstream_ref = {
            "target": {"kind": "git", "path": "workstream.json", "commit": revision},
            "sha256": digest(self.project / "workstream.json"),
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def commit_all(self, message: str) -> str:
        subprocess.run(["git", "-C", str(self.project), "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", str(self.project), "commit", "-q", "-m", message],
            check=True,
        )
        return subprocess.check_output(
            ["git", "-C", str(self.project), "rev-parse", "HEAD"], text=True
        ).strip()

    def pin(self, relative: str) -> tuple[str, str, str]:
        return (
            relative,
            digest(self.project / relative),
            self.commit_all(f"pin {relative}"),
        )

    def make_design(self, **budget: object) -> tuple[str, str, str]:
        limits = {
            "seconds": 30.0,
            "cost_usd": 0.0,
            "tokens": 0,
            "gpu_hours": 0.0,
            "attempts": 6,
            "rounds": 6,
        }
        limits.update(budget)
        source = (
            "question.json",
            digest(self.project / "question.json"),
            subprocess.check_output(
                ["git", "-C", str(self.project), "rev-parse", "HEAD"], text=True
            ).strip(),
        )
        outcome = design_experiment(
            self.project,
            source=source[0],
            source_sha256=source[1],
            source_commit=source[2],
            project_ref=self.project_ref,
            workstream_ref=self.workstream_ref,
            output="artifacts/design.json",
            report="reports/design.json",
            hypothesis="The fixed CPU baseline has MSE 1.25.",
            dataset={"target": {"kind": "git", "path": "data.json"}},
            controls=["constant mean"],
            metrics=[
                {"name": "mean_squared_error", "direction": "equal", "target": 1.25}
            ],
            run_matrix=[{"name": "cpu", "parameters": {}}],
            success_criteria=["mean_squared_error equals 1.25"],
            failure_criteria=["result missing or metric differs"],
            stop_criteria=["any hard budget is exhausted"],
            budget=limits,
        )
        self.assertEqual(outcome.stop_reason, "candidate_created")
        commit = self.commit_all("design")
        return (
            "artifacts/design.json",
            digest(self.project / "artifacts/design.json"),
            commit,
        )

    def make_preparation(self, design: tuple[str, str, str]) -> tuple[str, str, str]:
        outcome = prepare_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            output="artifacts/preparation.json",
            report="reports/preparation.json",
            ledger_directory="runs/preparation",
            commands=[
                (
                    sys.executable,
                    "-c",
                    "import pathlib; assert pathlib.Path('experiment.py').is_file()",
                )
            ],
            environment={},
        )
        self.assertEqual(outcome.stop_reason, "preparation_complete")
        commit = self.commit_all("preparation")
        return (
            "artifacts/preparation.json",
            digest(self.project / "artifacts/preparation.json"),
            commit,
        )

    def install_reference(self) -> None:
        source = ROOT / "reference-projects/computational"
        for name in ("experiment.py", "data.json"):
            shutil.copy2(source / name, self.project / name)
        self.commit_all("install reference")

    def successful_run(self) -> tuple[str, str, str]:
        self.install_reference()
        design = self.make_design()
        preparation = self.make_preparation(design)
        outcome = run_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            preparation=preparation[0],
            preparation_sha256=preparation[1],
            preparation_commit=preparation[2],
            output="artifacts/run.json",
            report="reports/run.json",
            ledger_directory="runs/experiment",
            commands=[(sys.executable, "experiment.py")],
            expected_result="result.json",
        )
        self.assertEqual(outcome.stop_reason, "run_complete")
        commit = self.commit_all("run")
        return "artifacts/run.json", digest(self.project / "artifacts/run.json"), commit

    def make_analysis(self) -> tuple[str, str, str]:
        run = self.successful_run()
        analyze_experiment(
            self.project,
            run=run[0],
            run_sha256=run[1],
            run_commit=run[2],
            output="artifacts/analysis.json",
            report="reports/analysis.json",
            analyzer=lambda data, spec: {
                "method": "fixed criterion comparison",
                "findings": [
                    {"mean_squared_error": json.loads(data)["mean_squared_error"]}
                ],
                "uncertainties": ["reference fixture only"],
                "criterion_results": [
                    {"criterion": "MSE equals 1.25", "verdict": "pass"}
                ],
            },
        )
        commit = self.commit_all("analysis")
        return (
            "artifacts/analysis.json",
            digest(self.project / "artifacts/analysis.json"),
            commit,
        )

    def make_claim(self) -> tuple[str, str, str]:
        name = "artifacts/claim.json"
        write_json(
            self.project / name,
            {
                "contract": {"name": "research-os/artifact", "version": "1.1.0"},
                "target": {"kind": "git", "path": name},
                "type": {"name": "claim", "version": "1.0.0"},
                "spec": {
                    "statement": "The fixed CPU baseline MSE is 1.25.",
                    "project": self.project_ref,
                    "workstream": self.workstream_ref,
                    "scope": ["/spec/statement"],
                    "conditions": [],
                    "limitations": ["CPU fixture only"],
                },
            },
        )
        commit = self.commit_all("claim")
        return name, digest(self.project / name), commit

    def test_design_handoff_passes_shared_contract_and_real_context(self) -> None:
        from research_os.contracts import validate_artifact
        from research_os.validation.semantics import (
            validate_fixed_ref,
            validate_provenance,
        )

        design = self.make_design()
        value = read_json(self.project / design[0])
        self.assertEqual(validate_artifact(value), [])
        self.assertEqual(validate_provenance(value["provenance"]), [])
        self.assertEqual(value["spec"]["project"], self.project_ref)
        self.assertEqual(value["spec"]["workstream"], self.workstream_ref)
        for record in value["provenance"]:
            for reference in record["inputs"]:
                self.assertEqual(
                    validate_fixed_ref(
                        reference, repository=self.project, structural_only=False
                    ),
                    [],
                )

    def test_design_is_commit_pinned_complete_and_stops_without_preparing(self) -> None:
        design = self.make_design()
        artifact = read_json(self.project / design[0])
        self.assertEqual(
            sorted(artifact["spec"]["budget"]),
            ["attempts", "cost_usd", "gpu_hours", "rounds", "seconds", "tokens"],
        )
        source_target = artifact["provenance"][0]["inputs"][0]["target"]
        self.assertEqual(len(source_target["commit"]), 40)
        report = read_json(self.project / "reports/design.json")
        self.assertFalse(report["automatic_next_workflow"])
        self.assertFalse((self.project / "artifacts/preparation.json").exists())
        self.assertFalse((self.project / "runs").exists())

    def test_digest_only_pin_is_not_accepted(self) -> None:
        with self.assertRaises(TypeError):
            design_experiment(
                self.project,
                source="question.json",
                source_sha256=digest(self.project / "question.json"),
                output="artifacts/design.json",
                report="reports/design.json",
                hypothesis="x",
                dataset={"x": 1},
                controls=["c"],
                metrics=[{"m": 1}],
                run_matrix=[{"r": 1}],
                success_criteria=["s"],
                failure_criteria=["f"],
                stop_criteria=["stop"],
                budget={
                    "seconds": 1,
                    "cost_usd": 0,
                    "tokens": 0,
                    "gpu_hours": 0,
                    "attempts": 1,
                    "rounds": 1,
                },
            )

    def test_commit_pin_rejects_same_digest_outside_selected_revision(self) -> None:
        commit = subprocess.check_output(
            ["git", "-C", str(self.project), "rev-parse", "HEAD"], text=True
        ).strip()
        write_json(self.project / "other.json", {"question": "different path"})
        with self.assertRaises(ValueError):
            design_experiment(
                self.project,
                source="other.json",
                source_sha256=digest(self.project / "other.json"),
                source_commit=commit,
                output="artifacts/design.json",
                report="reports/design.json",
                hypothesis="x",
                dataset={"x": 1},
                controls=["c"],
                metrics=[{"m": 1}],
                run_matrix=[{"r": 1}],
                success_criteria=["s"],
                failure_criteria=["f"],
                stop_criteria=["stop"],
                budget={
                    "seconds": 1,
                    "cost_usd": 0,
                    "tokens": 0,
                    "gpu_hours": 0,
                    "attempts": 1,
                    "rounds": 1,
                },
            )

    def test_all_six_budget_counters_are_hard_and_programmatic(self) -> None:
        limits = BudgetLimits(1.0, 2.0, 3, 4.0, 5, 6)
        deltas = {
            "seconds": BudgetUsage(seconds=1.1),
            "cost_usd": BudgetUsage(cost_usd=2.1),
            "tokens": BudgetUsage(tokens=4),
            "gpu_hours": BudgetUsage(gpu_hours=4.1),
            "attempts": BudgetUsage(attempts=6),
            "rounds": BudgetUsage(rounds=7),
        }
        for dimension, delta in deltas.items():
            with self.subTest(dimension=dimension):
                with self.assertRaises(BudgetExceeded) as caught:
                    BudgetCounter(limits).consume(delta)
                self.assertEqual(caught.exception.dimension, dimension)

    def test_elapsed_wall_time_reduces_executor_allowance(self) -> None:
        with patch(
            "research_os.workflows.computational.budget.monotonic_ns",
            side_effect=[0, 250_000_000],
        ):
            counter = BudgetCounter(BudgetLimits(1.0, 0.0, 0, 0.0, 1, 1))
            remaining = counter.remaining()
        self.assertEqual(remaining.seconds, 0.75)

    def test_ordinary_mode_stops_on_first_failure_and_preserves_it(self) -> None:
        self.install_reference()
        design = self.make_design()
        calls: list[int] = []

        def executor(project, context, remaining):
            calls.append(context.attempt)
            return ExecutionReceipt(
                "failed",
                7,
                BudgetUsage(seconds=0.1),
                b"first output\n",
                b"first failure\n",
            )

        outcome = prepare_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            output="artifacts/preparation.json",
            report="reports/preparation.json",
            ledger_directory="runs/preparation",
            commands=[("first",), ("must-not-run",)],
            mode="ordinary",
            executor=executor,
        )
        self.assertEqual(outcome.stop_reason, "execution_failed")
        self.assertEqual(calls, [1])
        record = read_json(self.project / "runs/preparation/attempt-0001.json")
        self.assertEqual(record["execution_outcome"], "failed")
        self.assertEqual(
            (self.project / record["stderr"]["path"]).read_bytes(), b"first failure\n"
        )

    def test_bounded_mode_uses_cumulative_preparation_and_run_budget(self) -> None:
        self.install_reference()
        design = self.make_design(attempts=2, rounds=2)

        def failed(project, context, remaining):
            return ExecutionReceipt("failed", 1, BudgetUsage(seconds=0.01), b"", b"no")

        prepare_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            output="artifacts/preparation.json",
            report="reports/preparation.json",
            ledger_directory="runs/preparation",
            commands=[("one",), ("two",)],
            mode="bounded_autonomy",
            executor=failed,
        )
        preparation_commit = self.commit_all("failed preparation")
        preparation = (
            "artifacts/preparation.json",
            digest(self.project / "artifacts/preparation.json"),
            preparation_commit,
        )
        value = read_json(self.project / preparation[0])
        value["spec"]["status"] = "prepared"
        value["spec"]["design"] = {
            "target": {"kind": "git", "path": design[0], "commit": design[2]},
            "sha256": design[1],
        }
        write_json(self.project / preparation[0], value)
        preparation_commit = self.commit_all("user accepted prepared fixture")
        preparation = (
            preparation[0],
            digest(self.project / preparation[0]),
            preparation_commit,
        )
        outcome = run_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            preparation=preparation[0],
            preparation_sha256=preparation[1],
            preparation_commit=preparation[2],
            output="artifacts/run.json",
            report="reports/run.json",
            ledger_directory="runs/experiment",
            commands=[("must-not-run",)],
            expected_result="result.json",
            executor=lambda *args: self.fail("budget must hard-stop before executor"),
        )
        self.assertEqual(outcome.stop_reason, "budget_exhausted")

    def test_execution_receipt_rejects_false_success_and_false_failure(self) -> None:
        with self.assertRaises(ValueError):
            ExecutionReceipt("succeeded", 7, BudgetUsage(), b"", b"")
        with self.assertRaises(ValueError):
            ExecutionReceipt("failed", 0, BudgetUsage(), b"", b"")

    def test_blocked_is_preserved_and_never_reported_as_support(self) -> None:
        self.install_reference()
        design = self.make_design()
        outcome = prepare_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            output="artifacts/preparation.json",
            report="reports/preparation.json",
            ledger_directory="runs/preparation",
            commands=[("missing",)],
            executor=lambda *args: ExecutionReceipt(
                "blocked", None, BudgetUsage(), b"", b"missing", "tool unavailable"
            ),
        )
        self.assertEqual(outcome.stop_reason, "external_prerequisite_unavailable")
        artifact = read_json(self.project / "artifacts/preparation.json")
        self.assertEqual(artifact["spec"]["status"], "not_prepared")
        self.assertNotIn("relations", artifact)

    def test_failed_run_snapshots_partial_result_before_later_changes(self) -> None:
        self.install_reference()
        design = self.make_design()
        preparation = self.make_preparation(design)

        def executor(project, context, remaining):
            (project / "result.json").write_bytes(b"partial\n")
            return ExecutionReceipt(
                "failed", 9, BudgetUsage(seconds=0.01), b"", b"boom"
            )

        run_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            preparation=preparation[0],
            preparation_sha256=preparation[1],
            preparation_commit=preparation[2],
            output="artifacts/run.json",
            report="reports/run.json",
            ledger_directory="runs/experiment",
            commands=[("bad",)],
            expected_result="result.json",
            executor=executor,
        )
        record = read_json(self.project / "runs/experiment/attempt-0001.json")
        snapshot = self.project / record["artifacts"][0]["snapshot"]["path"]
        self.assertEqual(snapshot.read_bytes(), b"partial\n")
        (self.project / "result.json").write_bytes(b"changed\n")
        self.assertEqual(snapshot.read_bytes(), b"partial\n")

    def test_preexisting_result_cannot_make_failed_command_look_successful(
        self,
    ) -> None:
        self.install_reference()
        design = self.make_design()
        preparation = self.make_preparation(design)
        (self.project / "result.json").write_text('{"stale": true}\n', encoding="utf-8")
        with self.assertRaises(FileExistsError):
            run_experiment(
                self.project,
                design=design[0],
                design_sha256=design[1],
                design_commit=design[2],
                preparation=preparation[0],
                preparation_sha256=preparation[1],
                preparation_commit=preparation[2],
                output="artifacts/run.json",
                report="reports/run.json",
                ledger_directory="runs/experiment",
                commands=[("bad",)],
                expected_result="result.json",
                executor=lambda *args: ExecutionReceipt(
                    "failed", 1, BudgetUsage(), b"", b"bad"
                ),
            )

    def test_real_local_cpu_reference_run_is_deterministic_and_not_a_claim(
        self,
    ) -> None:
        run = self.successful_run()
        self.assertEqual(
            read_json(self.project / "result.json"),
            {
                "algorithm": "constant-mean-baseline",
                "count": 4,
                "mean": 2.5,
                "mean_squared_error": 1.25,
            },
        )
        artifact = read_json(self.project / run[0])
        self.assertEqual(artifact["spec"]["claim_assessment"], "not_performed")
        self.assertNotIn("relations", artifact)
        record = read_json(self.project / "runs/experiment/attempt-0001.json")
        self.assertEqual(len(record["revision"]), 40)
        self.assertTrue(record["artifacts"])

    def test_analysis_reads_result_from_run_commit_and_has_no_rerun_seam(self) -> None:
        run = self.successful_run()
        data_at_pin = (self.project / "result.json").read_bytes()
        calls: list[bytes] = []

        def analyzer(data, run_spec):
            calls.append(data)
            result = json.loads(data)
            return {
                "method": "compare fixed MSE criterion",
                "findings": [
                    {
                        "metric": "mean_squared_error",
                        "value": result["mean_squared_error"],
                    }
                ],
                "uncertainties": ["single tiny deterministic fixture"],
                "criterion_results": [
                    {"criterion": "MSE equals 1.25", "verdict": "pass"}
                ],
            }

        analyze_experiment(
            self.project,
            run=run[0],
            run_sha256=run[1],
            run_commit=run[2],
            output="artifacts/analysis.json",
            report="reports/analysis.json",
            analyzer=analyzer,
        )
        self.assertEqual(calls, [data_at_pin])
        self.assertFalse(
            read_json(self.project / "artifacts/analysis.json")["spec"][
                "additional_runs_performed"
            ]
        )

    def test_analysis_rejects_preexisting_symlink_sandbox(self) -> None:
        run = self.successful_run()
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (self.project / "analysis").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            analyze_experiment(
                self.project,
                run=run[0],
                run_sha256=run[1],
                run_commit=run[2],
                output="artifacts/analysis.json",
                report="reports/analysis.json",
                analyzer=lambda data, spec: {
                    "method": "x",
                    "findings": [],
                    "uncertainties": [],
                    "criterion_results": [],
                },
            )
        self.assertEqual(list(outside.iterdir()), [])

    def test_output_parent_symlink_is_rejected_without_outside_write(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (self.project / "escape").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OSError):
            write_outputs_exclusive(self.project, {"escape/pwned.json": b"{}\n"})
        self.assertFalse((outside / "pwned.json").exists())

    def test_output_parent_swap_during_open_cannot_escape_project(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        parent = self.project / "safe"
        parent.mkdir()
        original_open = os.open
        swapped = False

        def swapping_open(path, flags, mode=0o777, *, dir_fd=None):
            nonlocal swapped
            if path == "target.json" and dir_fd is not None and not swapped:
                swapped = True
                parent.rename(self.project / "safe-old")
                (self.project / "safe").symlink_to(outside, target_is_directory=True)
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with patch(
            "research_os.workflows.computational.execution.os.open",
            side_effect=swapping_open,
        ):
            write_outputs_exclusive(self.project, {"safe/target.json": b"secure\n"})
        self.assertFalse((outside / "target.json").exists())
        self.assertEqual(
            (self.project / "safe-old/target.json").read_bytes(), b"secure\n"
        )

    def test_local_executor_does_not_leak_provider_environment(self) -> None:
        secret = "host-secret-value"
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": secret}, clear=False):
            receipt = execute_local_command(
                self.project,
                AttemptContext(
                    attempt=1,
                    round=1,
                    command=(
                        sys.executable,
                        "-c",
                        "import os; print(os.environ.get('ANTHROPIC_API_KEY', 'absent'))",
                    ),
                ),
                BudgetUsage(seconds=5, attempts=1, rounds=1),
            )
        self.assertEqual(receipt.outcome, "succeeded")
        self.assertEqual(receipt.stdout.strip(), b"absent")

    def test_local_executor_records_explicit_non_time_usage_receipt(self) -> None:
        receipt = execute_local_command(
            self.project,
            AttemptContext(
                attempt=1,
                round=1,
                command=(sys.executable, "-c", "print('ok')"),
                environment={
                    "RESEARCH_OS_USAGE_COST_USD": "1.25",
                    "RESEARCH_OS_USAGE_TOKENS": "42",
                    "RESEARCH_OS_USAGE_GPU_HOURS": "0.5",
                },
            ),
            BudgetUsage(
                seconds=5,
                cost_usd=2,
                tokens=100,
                gpu_hours=1,
                attempts=1,
                rounds=1,
            ),
        )
        self.assertEqual(receipt.usage.cost_usd, 1.25)
        self.assertEqual(receipt.usage.tokens, 42)
        self.assertEqual(receipt.usage.gpu_hours, 0.5)

    def test_local_executor_rejects_partial_usage_receipt(self) -> None:
        with self.assertRaises(ValueError):
            execute_local_command(
                self.project,
                AttemptContext(
                    attempt=1,
                    round=1,
                    command=(sys.executable, "-c", "print('ok')"),
                    environment={"RESEARCH_OS_USAGE_TOKENS": "42"},
                ),
                BudgetUsage(seconds=5, tokens=100, attempts=1, rounds=1),
            )

    def test_contract_rejects_wrong_artifact_version_and_unknown_fields(self) -> None:
        self.install_reference()
        design = self.make_design()
        value = read_json(self.project / design[0])
        value["type"]["version"] = "999.0.0"
        value["provider"] = "claude"
        write_json(self.project / design[0], value)
        bad_commit = self.commit_all("bad design")
        with self.assertRaises(ValueError):
            prepare_experiment(
                self.project,
                design=design[0],
                design_sha256=digest(self.project / design[0]),
                design_commit=bad_commit,
                output="artifacts/preparation.json",
                report="reports/preparation.json",
                ledger_directory="runs/preparation",
                commands=[("unused",)],
                executor=lambda *args: self.fail(
                    "invalid contract must fail before execution"
                ),
            )

    def test_analysis_contract_rejects_empty_object_findings(self) -> None:
        run = self.successful_run()
        with self.assertRaises(ValueError):
            analyze_experiment(
                self.project,
                run=run[0],
                run_sha256=run[1],
                run_commit=run[2],
                output="artifacts/analysis.json",
                report="reports/analysis.json",
                analyzer=lambda data, spec: {
                    "method": "x",
                    "findings": [{}],
                    "uncertainties": [],
                    "criterion_results": [],
                },
            )

    def test_result_to_claim_creates_only_finite_fixed_support(self) -> None:
        analysis = self.make_analysis()
        claim = self.make_claim()
        outcome = assess_result_to_claim(
            self.project,
            analysis=analysis[0],
            analysis_sha256=analysis[1],
            analysis_commit=analysis[2],
            claim=claim[0],
            claim_sha256=claim[1],
            claim_commit=claim[2],
            evidence_output="artifacts/evidence.json",
            assessment_output="artifacts/result-to-claim.json",
            report="reports/result-to-claim.json",
            method="fixed metric comparison",
            conditions=["the checked-in four-value fixture is unchanged"],
            scope=["/spec/statement"],
            verdict="supports",
            limitations=["does not generalize beyond the fixture"],
        )
        self.assertEqual(outcome.stop_reason, "assessment_complete")
        evidence = read_json(self.project / "artifacts/evidence.json")
        self.assertEqual(len(evidence["relations"]), 1)
        relation = evidence["relations"][0]
        self.assertEqual(relation["relation"], "supports")
        self.assertEqual(relation["claim"]["target"]["commit"], claim[2])
        self.assertEqual(relation["claim"]["sha256"], claim[1])
        self.assertEqual(relation["scope"], ["/spec/statement"])
        assessment = read_json(self.project / "artifacts/result-to-claim.json")
        self.assertFalse(assessment["spec"]["claim_truth_determined"])
        self.assertEqual(assessment["spec"]["human_acceptance"], "not_performed")
        from research_os.contracts import validate_artifact
        from research_os.validation.semantics import (
            SemanticsSchemaValidator,
            validate_fixed_ref,
            validate_provenance,
        )

        self.commit_all("user pins result-to-claim outputs")
        self.assertEqual(SemanticsSchemaValidator().validate("evidence", evidence), [])
        self.assertEqual(
            SemanticsSchemaValidator().validate(
                "claim", read_json(self.project / claim[0])
            ),
            [],
        )
        for path in (
            "design",
            "preparation",
            "run",
            "analysis",
            "claim",
            "evidence",
            "result-to-claim",
        ):
            value = read_json(self.project / f"artifacts/{path}.json")
            with self.subTest(handoff=path):
                self.assertEqual(validate_artifact(value), [])
                self.assertEqual(value["spec"]["project"], self.project_ref)
                self.assertEqual(value["spec"]["workstream"], self.workstream_ref)
                self.assertEqual(validate_provenance(value.get("provenance", [])), [])
                for record in value.get("provenance", []):
                    for reference in record["inputs"]:
                        self.assertEqual(
                            validate_fixed_ref(
                                reference,
                                repository=self.project,
                                structural_only=False,
                            ),
                            [],
                        )
        self.assertNotIn(
            "evidence",
            assessment["spec"],
            "same-invocation live output is not a fixed handoff",
        )
        self.assertEqual(
            assessment["type"], {"name": "experiment-analysis", "version": "1.0.0"}
        )

    def test_inconclusive_assessment_has_no_support_relation(self) -> None:
        analysis = self.make_analysis()
        claim = self.make_claim()
        assess_result_to_claim(
            self.project,
            analysis=analysis[0],
            analysis_sha256=analysis[1],
            analysis_commit=analysis[2],
            claim=claim[0],
            claim_sha256=claim[1],
            claim_commit=claim[2],
            evidence_output="artifacts/evidence.json",
            assessment_output="artifacts/result-to-claim.json",
            report="reports/result-to-claim.json",
            method="fixed metric comparison",
            conditions=["fixture only"],
            scope=["/spec/statement"],
            verdict="inconclusive",
            limitations=["insufficient repetitions"],
        )
        self.assertFalse((self.project / "artifacts/evidence.json").exists())
        assessment = read_json(self.project / "artifacts/result-to-claim.json")
        self.assertEqual(assessment["type"]["name"], "experiment-analysis")
        self.assertEqual(assessment["spec"]["verdict"], "inconclusive")
        self.assertNotIn("relations", assessment)
        from research_os.contracts import validate_artifact

        self.assertEqual(validate_artifact(assessment), [])

    def assess(self, analysis, claim, **overrides):
        arguments = dict(
            analysis=analysis[0],
            analysis_sha256=analysis[1],
            analysis_commit=analysis[2],
            claim=claim[0],
            claim_sha256=claim[1],
            claim_commit=claim[2],
            evidence_output="artifacts/evidence.json",
            assessment_output="artifacts/result-to-claim.json",
            report="reports/result-to-claim.json",
            method="fixed criterion comparison",
            conditions=[],
            scope=["/spec/statement"],
            verdict="supports",
            limitations=[],
        )
        arguments.update(overrides)
        return assess_result_to_claim(self.project, **arguments)

    def test_does_not_support_is_analysis_not_evidence(self) -> None:
        analysis, claim = self.make_analysis(), self.make_claim()
        outcome = self.assess(analysis, claim, verdict="does_not_support")
        self.assertNotIn("artifacts/evidence.json", outcome.outputs)
        self.assertFalse((self.project / "artifacts/evidence.json").exists())
        value = read_json(self.project / "artifacts/result-to-claim.json")
        from research_os.contracts import validate_artifact

        self.assertEqual(validate_artifact(value), [])
        self.assertEqual(value["spec"]["verdict"], "does_not_support")

    def test_shared_scope_accepts_root_and_rejects_redundant_pointers(self) -> None:
        analysis, claim = self.make_analysis(), self.make_claim()
        for scope in (["/spec", "/spec/statement"], ["/spec", "/spec"], ["/bad~2"]):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                self.assess(analysis, claim, scope=scope)
        self.assess(analysis, claim, scope=[""])
        value = read_json(self.project / "artifacts/evidence.json")
        self.assertEqual(value["relations"][0]["conditions"], [])
        self.assertEqual(value["relations"][0]["scope"], [""])

    def test_claim_wrong_workstream_or_project_is_rejected_before_outputs(self) -> None:
        analysis, claim = self.make_analysis(), self.make_claim()
        original = read_json(self.project / claim[0])
        import copy

        for field in ("project", "workstream"):
            value = copy.deepcopy(original)
            value["spec"][field]["sha256"] = "0" * 64
            sha = write_json(self.project / claim[0], value)
            commit = self.commit_all("invalid boundary digest")
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.assess(analysis, (claim[0], sha, commit))
        self.assertFalse((self.project / "artifacts/evidence.json").exists())
        self.assertFalse((self.project / "artifacts/result-to-claim.json").exists())

    def test_status_only_analysis_cannot_be_used_as_support(self) -> None:
        analysis, claim = self.make_analysis(), self.make_claim()
        value = read_json(self.project / analysis[0])
        value["spec"] = {
            "status": "candidate",
            "project": self.project_ref,
            "workstream": self.workstream_ref,
        }
        sha = write_json(self.project / analysis[0], value)
        commit = self.commit_all("empty analysis")
        with self.assertRaises(ValueError):
            self.assess((analysis[0], sha, commit), claim)
        self.assertFalse((self.project / "artifacts/evidence.json").exists())

    def test_user_stop_preserves_failed_attempt_and_does_not_retry(self) -> None:
        design = self.make_design()
        calls = []

        def failed(project, context, remaining):
            calls.append(context.attempt)
            return ExecutionReceipt(
                "failed", 1, BudgetUsage(), b"", b"preserved failure"
            )

        outcome = prepare_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            output="artifacts/preparation.json",
            report="reports/preparation.json",
            ledger_directory="runs/preparation",
            commands=[("first",), ("never",)],
            mode="bounded_autonomy",
            executor=failed,
            stop_requested=lambda: bool(calls),
        )
        self.assertEqual(outcome.stop_reason, "user_stopped")
        self.assertEqual(calls, [1])
        self.assertEqual(
            (self.project / "runs/preparation/attempt-0001.stderr").read_bytes(),
            b"preserved failure",
        )
        self.assertFalse((self.project / "runs/preparation/attempt-0002.json").exists())

    def test_analysis_cannot_substitute_an_unrelated_fixed_run(self) -> None:
        analysis, claim = self.make_analysis(), self.make_claim()
        value = read_json(self.project / analysis[0])
        value["spec"]["run"] = self.project_ref
        sha = write_json(self.project / analysis[0], value)
        commit = self.commit_all("unrelated fixed run")
        with self.assertRaises(ValueError):
            self.assess((analysis[0], sha, commit), claim)
        self.assertFalse((self.project / "artifacts/evidence.json").exists())

    def test_failed_partial_result_cannot_satisfy_later_successful_noop(self) -> None:
        self.install_reference()
        design = self.make_design(cost_usd=1, tokens=100, gpu_hours=1)
        preparation = self.make_preparation(design)
        calls = []

        def executor(project, context, remaining):
            calls.append(context.attempt)
            if len(calls) == 1:
                (project / "result.json").write_bytes(b"partial")
                return ExecutionReceipt("failed", 1, BudgetUsage(), b"", b"failure")
            return ExecutionReceipt("succeeded", 0, BudgetUsage(), b"", b"")

        outcome = run_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            preparation=preparation[0],
            preparation_sha256=preparation[1],
            preparation_commit=preparation[2],
            output="artifacts/run.json",
            report="reports/run.json",
            ledger_directory="runs/experiment",
            commands=[("partial",), ("noop",)],
            expected_result="result.json",
            mode="bounded_autonomy",
            executor=executor,
        )
        self.assertEqual(outcome.stop_reason, "partial_result_requires_user_action")
        self.assertEqual(calls, [1])
        self.assertEqual((self.project / "result.json").read_bytes(), b"partial")
        self.assertEqual(
            list((self.project / "runs/experiment").glob("attempt-0002.*")), []
        )
        self.assertEqual(
            read_json(self.project / "artifacts/run.json")["spec"]["status"], "failed"
        )
        record = read_json(self.project / "runs/experiment/attempt-0001.json")
        self.assertEqual(
            (self.project / record["artifacts"][0]["snapshot"]["path"]).read_bytes(),
            b"partial",
        )

    def test_valid_different_workstream_cannot_be_substituted_for_claim(self) -> None:
        analysis, claim = self.make_analysis(), self.make_claim()
        workstream = read_json(self.project / "workstream.json")
        workstream["target"]["path"] = "other-workstream.json"
        workstream["spec"]["name"] = "Separate experiment"
        sha = write_json(self.project / "other-workstream.json", workstream)
        commit = self.commit_all("separate real workstream")
        value = read_json(self.project / claim[0])
        value["spec"]["workstream"] = {
            "target": {
                "kind": "git",
                "path": "other-workstream.json",
                "commit": commit,
            },
            "sha256": sha,
        }
        sha = write_json(self.project / claim[0], value)
        commit = self.commit_all("Claim in different workstream")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.assess(analysis, (claim[0], sha, commit))
        self.assertFalse((self.project / "artifacts/evidence.json").exists())

    def test_analysis_cannot_substitute_another_committed_result(self) -> None:
        analysis, claim = self.make_analysis(), self.make_claim()
        value = read_json(self.project / analysis[0])
        value["spec"]["result"] = self.project_ref
        sha = write_json(self.project / analysis[0], value)
        commit = self.commit_all("unrelated result bytes")
        with self.assertRaisesRegex(ValueError, "result does not match"):
            self.assess((analysis[0], sha, commit), claim)
        self.assertFalse((self.project / "artifacts/evidence.json").exists())

    def test_fixed_provenance_digest_is_verified_before_support(self) -> None:
        analysis, claim = self.make_analysis(), self.make_claim()
        value = read_json(self.project / analysis[0])
        value["provenance"][0]["inputs"][0]["sha256"] = "0" * 64
        sha = write_json(self.project / analysis[0], value)
        commit = self.commit_all("forged analysis provenance")
        with self.assertRaises(ValueError):
            self.assess((analysis[0], sha, commit), claim)
        self.assertFalse((self.project / "artifacts/evidence.json").exists())

    def test_support_rejects_invalid_pointer_and_claim_target_mismatch(self) -> None:
        analysis = self.make_analysis()
        claim = self.make_claim()
        value = read_json(self.project / claim[0])
        value["target"]["path"] = "artifacts/other-claim.json"
        write_json(self.project / claim[0], value)
        bad_sha = digest(self.project / claim[0])
        bad_commit = self.commit_all("mismatched claim target")
        subprocess.run(
            [
                "git",
                "-C",
                str(self.project),
                "checkout",
                "-q",
                claim[2],
                "--",
                claim[0],
            ],
            check=True,
        )
        for commit, sha, scope in (
            (bad_commit, bad_sha, ["/spec/statement"]),
            (claim[2], claim[1], ["spec/not-a-pointer"]),
        ):
            with self.subTest(commit=commit, scope=scope):
                with self.assertRaises(ValueError):
                    assess_result_to_claim(
                        self.project,
                        analysis=analysis[0],
                        analysis_sha256=analysis[1],
                        analysis_commit=analysis[2],
                        claim=claim[0],
                        claim_sha256=sha,
                        claim_commit=commit,
                        evidence_output="artifacts/evidence.json",
                        assessment_output="artifacts/result-to-claim.json",
                        report="reports/result-to-claim.json",
                        method="fixed comparison",
                        conditions=["fixture only"],
                        scope=scope,
                        verdict="supports",
                        limitations=[],
                    )
        self.assertFalse((self.project / "artifacts/evidence.json").exists())

    def test_second_invocation_appends_new_attempt_without_overwriting_failure(
        self,
    ) -> None:
        self.install_reference()
        design = self.make_design()

        def failed(project, context, remaining):
            return ExecutionReceipt(
                "failed",
                1,
                BudgetUsage(seconds=0.01),
                f"attempt {context.attempt}".encode(),
                b"failure",
            )

        first = prepare_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            output="artifacts/preparation-1.json",
            report="reports/preparation-1.json",
            ledger_directory="runs/preparation",
            commands=[("bad",)],
            executor=failed,
        )
        self.assertEqual(first.stop_reason, "execution_failed")
        original = (self.project / "runs/preparation/attempt-0001.stdout").read_bytes()
        second = prepare_experiment(
            self.project,
            design=design[0],
            design_sha256=design[1],
            design_commit=design[2],
            output="artifacts/preparation-2.json",
            report="reports/preparation-2.json",
            ledger_directory="runs/preparation",
            commands=[("bad",)],
            executor=failed,
        )
        self.assertEqual(second.stop_reason, "execution_failed")
        self.assertEqual(
            (self.project / "runs/preparation/attempt-0001.stdout").read_bytes(),
            original,
        )
        self.assertEqual(
            (self.project / "runs/preparation/attempt-0002.stdout").read_bytes(),
            b"attempt 2",
        )

    def test_output_and_ledger_paths_reject_dot_segments(self) -> None:
        design = self.make_design()
        with self.assertRaises(ValueError):
            prepare_experiment(
                self.project,
                design=design[0],
                design_sha256=design[1],
                design_commit=design[2],
                output="artifacts/preparation.json",
                report="reports/preparation.json",
                ledger_directory="runs/./preparation",
                commands=[("unused",)],
                executor=lambda *args: ExecutionReceipt(
                    "succeeded", 0, BudgetUsage(), b"", b""
                ),
            )

    def test_pinned_input_drift_and_output_collision_fail_before_write(self) -> None:
        commit = subprocess.check_output(
            ["git", "-C", str(self.project), "rev-parse", "HEAD"], text=True
        ).strip()
        old_digest = digest(self.project / "question.json")
        write_json(self.project / "question.json", {"question": "changed"})
        with self.assertRaises(ValueError):
            design_experiment(
                self.project,
                source="question.json",
                source_sha256=old_digest,
                source_commit=commit,
                output="same.json",
                report="same.json",
                hypothesis="x",
                dataset={"x": 1},
                controls=["c"],
                metrics=[{"m": 1}],
                run_matrix=[{"r": 1}],
                success_criteria=["s"],
                failure_criteria=["f"],
                stop_criteria=["stop"],
                budget={
                    "seconds": 1,
                    "cost_usd": 0,
                    "tokens": 0,
                    "gpu_hours": 0,
                    "attempts": 1,
                    "rounds": 1,
                },
            )
        self.assertFalse((self.project / "same.json").exists())


if __name__ == "__main__":
    unittest.main()
