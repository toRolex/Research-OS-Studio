"""Real installed-wheel driver. Candidate/review/acceptance text is fixture input.

No product implementation is imported into the checkout test process. Helper API
calls run in the wheel environment only to author user-owned documents / stage
Publication; every user workflow is a separate canonical CLI subprocess.
"""
from __future__ import annotations

import atexit
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-09-06T00:00:00Z"
AXES = (
    "structural_conformance", "empirical_reproducibility", "mathematical_argument_review",
    "formal_verification", "independent_review", "human_acceptance",
)
_workspace = None
_environment = None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_env():
    env = dict(os.environ)
    for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"):
        env.pop(key, None)
    env.update(PYTHONDONTWRITEBYTECODE="1", RESEARCH_OS_OFFLINE="1")
    return env


def execute(args, cwd, *, check=True):
    result = subprocess.run(args, cwd=cwd, env=clean_env(), capture_output=True,
                            text=True, timeout=180)
    if check and result.returncode:
        raise AssertionError(f"{args}\nexit={result.returncode}\n{result.stdout}\n{result.stderr}")
    return result


def wheel_environment():
    global _workspace, _environment
    if _environment is None:
        _workspace = tempfile.TemporaryDirectory(prefix="research-os-release-wheel-")
        atexit.register(_workspace.cleanup)
        root = Path(_workspace.name).resolve()
        execute(["uv", "build", "--wheel", "--out-dir", str(root / "dist"), str(ROOT)], root)
        _environment = root / "venv"
        execute(["uv", "venv", "--python", sys.executable, str(_environment)], root)
        wheel = next((root / "dist").glob("*.whl"))
        execute(["uv", "pip", "install", "--no-deps", "--python",
                 str(_environment / "bin/python"), str(wheel)], root)
    return _environment


def artifact(path, kind, spec, **extra):
    return dict(contract={"name": "research-os/artifact", "version": "1.1.0"},
                target={"kind": "git", "path": path},
                type={"name": kind, "version": "1.0.0"}, spec=spec, **extra)


class InstalledProject:
    def setup_installed_project(self):
        self.environment = wheel_environment()
        self.temporary = tempfile.TemporaryDirectory(prefix="research-os-clean-reference-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.members = []
        self.invocations = []
        self.command_receipts = []
        self.git("init", "-q")
        self.git("config", "user.name", "Release Fixture")
        self.git("config", "user.email", "fixture@example.test")
        location = self.api("import research_os; print(research_os.__file__)").strip()
        self.assertTrue(Path(location).is_relative_to(self.environment), location)
        self.cli("setup-research-os", "--project", str(self.root))
        self.assertFalse((self.root / "publications").exists())
        self.assertFalse((self.root / "runs").exists())
        for adapter in ("claude-code", "codex"):
            self.assertTrue((self.root / f".research-os/projections/{adapter}/manifest.json").is_file())
        self.project_ref = self.add("project.json", artifact("project.json", "project", {
            "name": "Installed reference", "question": "Does the bounded example hold?",
            "boundaries": ["Fixed CPU / mathematical fixture; no scientific novelty claim"],
            "principals": [{"identity": "alice", "roles": ["user", "researcher"]},
                           {"identity": "bob", "roles": ["reviewer"]},
                           {"identity": "validator", "roles": ["agent"]}],
        }))
        self.workstream_ref = self.add("workstream.json", artifact("workstream.json", "workstream", {
            "project": self.project_ref, "name": "Reference", "intent": "Test fixed inputs", "state": "active",
        }))

    def api(self, source):
        return execute(["uv", "run", "--no-project", str(self.environment / "bin/python"),
                        "-I", "-c", source], self.root).stdout

    def cli(self, *args, code=0):
        result = execute(["uv", "run", "--no-project", str(self.environment / "bin/research-os"),
                          *args], self.root, check=False)
        self.command_receipts.append({"arguments": list(args), "exit_code": result.returncode,
                                      "stdout": result.stdout, "stderr": result.stderr})
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def git(self, *args):
        return execute(["git", "-C", str(self.root), *args], self.root).stdout.strip()

    def write(self, path, value):
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, bytes):
            destination.write_bytes(value)
        else:
            destination.write_text(json.dumps(value, indent=2) + "\n")

    def read(self, path):
        return json.loads((self.root / path).read_bytes())

    def pin(self, path):
        self.git("add", "--", path)
        self.git("commit", "--allow-empty", "-qm", "fixture pin " + path)
        return {"target": {"kind": "git", "path": path, "commit": self.git("rev-parse", "HEAD")},
                "sha256": digest(self.root / path)}

    def add(self, path, value=None, role="artifact", dependencies=None):
        if value is not None:
            self.write(path, value)
        ref = self.pin(path)
        self.members.append({"path": path, "ref": ref, "role": role,
                             "purpose": "Fixed reference " + path, "dependencies": dependencies or []})
        return ref

    def input_pin(self, path):
        return {"path": path, "sha256": digest(self.root / path)}

    def invoke(self, workflow, request, *, code=0):
        self.assertFalse((self.root / "publications").exists())
        before = {member["path"]: (self.root / member["path"]).read_bytes() for member in self.members}
        path = f"requests/{len(self.invocations):02}-{workflow}.json"
        self.write(path, request)
        self.invocations.append(workflow)
        result = self.cli("workflow", workflow, "--project", str(self.root), "--request", path, code=code)
        self.assertFalse(result.get("automatic_next_workflow", False), result)
        self.assertIn(result.get("status"), ("stopped", "candidate"), result)
        for name, raw in before.items():
            self.assertEqual((self.root / name).read_bytes(), raw, name)
        self.assertFalse((self.root / "publications").exists())
        return result

    def validate(self, path, *, context=False):
        args = ["validate", "--project", str(self.root), path]
        if context:
            args.extend(["--context", "validation-context.json"])
        report = self.cli(*args)
        self.assertEqual(report["verdict"], "pass", report)
        return report

    def outer_workflows(self):
        question = artifact("question.json", "research-question", {
            "question": "Does the fixed CPU baseline yield MSE 1.25?", "boundaries": ["CPU only"],
            "success_criteria": ["MSE equals 1.25"], "budget": {"hours": 1},
            "invariants": ["Do not change the four-value dataset"],
        })
        self.add("question.json", question)
        calls = [
            ("research-charter", ["question.json"], "charter.json"),
            ("research-literature", ["charter.json"], "literature.json"),
            ("research-gap", ["literature.json"], "gap.json"),
            ("research-idea", ["gap.json"], "idea.json"),
            ("research-novelty", ["idea.json", "literature.json"], "novelty.json"),
            ("research-reflect", ["novelty.json"], "reflection.json"),
        ]
        for index, (workflow, inputs, output) in enumerate(calls):
            request = {"inputs": [self.input_pin(name) for name in inputs],
                       "output_path": output, "report_path": f"reports/{workflow}.json"}
            if workflow == "research-literature":
                request["candidate"] = {"synthesis": "No external literature evaluated; fixed local reference only.",
                                        "citations": [], "limitations": ["No novelty evidence"]}
            self.invoke(workflow, request)
            self.validate(output)
            self.add(output)
            if index + 1 < len(calls):
                self.assertFalse((self.root / calls[index + 1][2]).exists())
        # No fabricated literature, gap evidence, or novelty success.
        self.assertEqual(self.read("literature.json")["spec"]["queries"], [])
        self.assertEqual(self.read("gap.json")["spec"]["gaps"][0]["support"], "unsupported")
        self.assertEqual(self.read("novelty.json")["spec"]["novelty_verdict"], "inconclusive")

    def computational_workflows(self):
        self.api("from pathlib import Path; import research_os; import shutil; "
                 "root=Path(research_os.__file__).parent/'_reference_projects/computational'; "
                 "[shutil.copy2(root/name, name) for name in ('experiment.py','data.json')]")
        self.add("experiment.py", role="material")
        self.add("data.json", role="material")
        source = self.pin("question.json")
        self.invoke("design-experiment", {
            "project_ref": self.project_ref, "workstream_ref": self.workstream_ref,
            "source": "question.json", "source_sha256": source["sha256"],
            "source_commit": source["target"]["commit"], "output": "design.json", "report": "reports/design.json",
            "hypothesis": "MSE equals 1.25", "dataset": {"target": {"kind": "git", "path": "data.json"}},
            "controls": ["constant mean"], "metrics": [{"name": "mean_squared_error", "target": 1.25}],
            "run_matrix": [{"name": "cpu"}], "success_criteria": ["MSE equals 1.25"],
            "failure_criteria": ["missing result"], "stop_criteria": ["budget exhausted"],
            "budget": {"seconds": 60.0, "cost_usd": 0.0, "tokens": 0, "gpu_hours": 0.0, "attempts": 6, "rounds": 6},
        })
        design = self.add("design.json")
        selected = {"design": "design.json", "design_sha256": design["sha256"],
                    "design_commit": design["target"]["commit"]}
        self.assertFalse((self.root / "preparation.json").exists())
        python = str(self.environment / "bin/python")
        self.invoke("prepare-experiment", {**selected, "output": "preparation.json", "report": "reports/prepare.json",
            "ledger_directory": "runs/prepare", "commands": [[python, "-c", "import json; json.load(open('data.json'))"]]})
        preparation = self.add("preparation.json")
        run_request = {**selected, "preparation": "preparation.json", "preparation_sha256": preparation["sha256"],
                       "preparation_commit": preparation["target"]["commit"], "expected_result": "result.json"}
        self.assertFalse((self.root / "run.json").exists())
        # Explicit ordinary failure must stop, not retry or fabricate a result.
        self.invoke("run-experiment", {**run_request, "output": "failed-run.json", "report": "reports/failed-run.json",
            "ledger_directory": "runs/failed", "commands": [[python, "-c", "raise SystemExit(7)"]]}, code=1)
        failed_bytes = (self.root / "failed-run.json").read_bytes()
        self.assertFalse((self.root / "result.json").exists())
        self.add("failed-run.json")
        self.invoke("run-experiment", {**run_request, "output": "run.json", "report": "reports/run.json",
            "ledger_directory": "runs/execute", "commands": [[python, "experiment.py"]]})
        self.assertEqual((self.root / "failed-run.json").read_bytes(), failed_bytes)
        result = self.read("result.json")
        self.assertEqual(result["mean_squared_error"], 1.25, result)
        self.add("result.json", role="material")
        run = self.add("run.json")
        self.assertFalse((self.root / "analysis.json").exists())
        self.invoke("analyze-experiment", {"run": "run.json", "run_sha256": run["sha256"],
            "run_commit": run["target"]["commit"], "output": "analysis.json", "report": "reports/analysis.json",
            "analysis_candidate": {"method": "fixed criterion comparison", "findings": [{"MSE": 1.25}],
                "uncertainties": ["fixed fixture only"], "criterion_results": [{"criterion": "MSE", "verdict": "pass"}]}})
        analysis = self.add("analysis.json")
        self.claim_ref = self.add("claim.json", artifact("claim.json", "claim", {
            "project": self.project_ref, "workstream": self.workstream_ref,
            "statement": "The fixed CPU baseline MSE equals 1.25.", "scope": ["/statement"],
            "conditions": ["Fixed four-value dataset"], "limitations": ["Fixture only, not a scientific contribution"],
        }))
        self.invoke("assess-result-to-claim", {"analysis": "analysis.json", "analysis_sha256": analysis["sha256"],
            "analysis_commit": analysis["target"]["commit"], "claim": "claim.json", "claim_sha256": self.claim_ref["sha256"],
            "claim_commit": self.claim_ref["target"]["commit"], "evidence_output": "evidence.json",
            "assessment_output": "result-to-claim.json", "report": "reports/assess.json",
            "method": "fixed criterion comparison", "conditions": ["Fixed four-value dataset"],
            "scope": ["/statement"], "verdict": "supports", "limitations": ["Fixture only"]})
        self.evidence_ref = self.add("evidence.json")
        self.add("result-to-claim.json")
        self.assertEqual(self.read("evidence.json")["relations"][0]["claim"], self.claim_ref)
        for path in ("design.json", "preparation.json", "run.json", "analysis.json", "claim.json", "evidence.json", "result-to-claim.json"):
            self.validate(path)
        self.add("design-request.json", self.read("requests/06-design-experiment.json"), role="material")
        # A second explicitly authorized design has one attempt; a failing first
        # preparation cannot execute the next command after the hard budget.
        limited = self.read("design-request.json")
        limited.update(output="limited-design.json", report="reports/limited-design.json")
        limited["budget"].update(attempts=1, rounds=1)
        self.invoke("design-experiment", limited)
        limited_ref = self.add("limited-design.json")
        exhausted = self.invoke("prepare-experiment", {
            "design": "limited-design.json", "design_sha256": limited_ref["sha256"],
            "design_commit": limited_ref["target"]["commit"], "output": "exhausted.json",
            "report": "reports/exhausted.json", "ledger_directory": "runs/exhausted", "mode": "bounded_autonomy",
            "commands": [[python, "-c", "raise SystemExit(9)"],
                         [python, "-c", "open('budget-escaped','w').write('bad')"]],
        }, code=1)
        self.assertEqual(exhausted["stop_reason"], "budget_exhausted")
        self.assertFalse((self.root / "budget-escaped").exists())
        self.add("exhausted.json")
        # Retain execution logs and requests in the closed publication as material.
        for directory in ("runs", "reports", "requests"):
            for path in sorted((self.root / directory).rglob("*")):
                if path.is_file():
                    self.add(path.relative_to(self.root).as_posix(), role="material")

    def publish(self, profile, body):
        # Publication retains its explicit admission profile; canonical math
        # projections remain typed, while historical workflow records stay material.
        for member in self.members:
            if member["role"] == "artifact" and self.read(member["path"])["type"]["name"] not in {"project", "workstream", "claim", "evidence", "math-statement-projection", "math-proof-projection", "math-review-projection"}:
                member["role"] = "material"
        materials = [member["ref"] for member in self.members if member["role"] == "material"]
        claim = self.read("claim.json")["spec"]
        conditions = list(claim["conditions"])
        for relation in self.read("evidence.json").get("relations", []):
            for condition in relation["conditions"]:
                if condition not in conditions:
                    conditions.append(condition)
        limitations = [*claim["limitations"], "Fixture principals and supplied review decisions; not academic or release acceptance"]
        self.manuscript_ref = self.add("manuscript.json", artifact("manuscript.json", "manuscript", {
            "profile": profile, "project": self.project_ref, "title": "A bounded installed reference",
            "authors": ["alice"], "body": body, "contributions": ["Reproducible reference example"],
            "claims": [self.claim_ref], "evidence": [self.evidence_ref], "conditions": conditions,
            "limitations": limitations, "materials": materials, "external_references": [],
        }))
        self.validate("manuscript.json")
        self.api("from pathlib import Path; import json; "
                 "from research_os.publication import manuscript_text, render_pdf; "
                 "text=manuscript_text(json.loads(Path('manuscript.json').read_bytes())); "
                 "Path('paper.txt').write_text(text); Path('paper.pdf').write_bytes(render_pdf(text))")
        self.assertTrue((self.root / "paper.pdf").read_bytes().startswith(b"%PDF-"))
        self.assertIn(body, (self.root / "paper.txt").read_text())
        # paper.txt is a local rendering aid; the one public text is paper.pdf.
        primary = self.add("paper.pdf", role="primary-text", dependencies=[self.manuscript_ref])
        assessments = {axis: [] for axis in AXES}
        required = {"structural_conformance", "independent_review", "human_acceptance",
                    "empirical_reproducibility" if profile == "empirical-computational" else "mathematical_argument_review"}
        self.write("validation-context.json", {"project": self.project_ref, "evidence": [self.evidence_ref]})
        for axis in AXES:
            spec = {"project": self.project_ref, "subject": self.manuscript_ref, "dimension": axis,
                    "scope": "whole_subject", "verdict": "pass" if axis in required else "not_applicable",
                    "method": "Explicit fixture decision on fixed reference inputs, not model-inferred acceptance",
                    "evidence": [self.evidence_ref], "assessor": "alice" if axis == "human_acceptance" else "bob",
                    "assessed_at": STAMP, "validity": "active"}
            if axis == "independent_review":
                spec["isolation_receipt"] = {"reviewer": "bob", "authors": ["alice"], "inputs": [self.manuscript_ref],
                    "fresh_context": True, "conversation_history_access": False, "issued_at": STAMP}
            path = f"assessments/{axis}.json"
            assessments[axis].append(self.add(path, artifact(path, "assessment", spec)))
            self.validate(path, context=True)
        request = {"publication": "reference", "profile": profile, "created_at": STAMP,
            "project": self.project_ref, "manuscript": self.manuscript_ref, "primary_text": primary,
            "members": self.members, "contributions": ["Reproducible reference example"],
            "claims": [self.claim_ref], "evidence": [self.evidence_ref], "conditions": conditions,
            "limitations": limitations, "materials": materials, "assessments": assessments,
            "external_references": [], "required_gates": []}
        self.write("publication-request.json", request)
        self.api("from pathlib import Path; import json; "
                 "from research_os.publication import stage_publication, confirmation_text; "
                 "stage=stage_publication(Path.cwd(), json.loads(Path('publication-request.json').read_bytes())); "
                 "Path('stage.json').write_text(json.dumps(stage, indent=2)+'\\n'); "
                 "Path('confirmation.txt').write_text(confirmation_text(stage))")
        self.write("validation-context.json", {"project": self.project_ref, "evidence": [self.evidence_ref],
                                               "records": [member["ref"] for member in self.members]})
        self.validate("stage.json", context=True)
        # A passing independent review never substitutes for the human axis.
        rejected = self.read("stage.json")
        human_refs = rejected["spec"]["assessments"]["human_acceptance"]
        rejected["spec"]["members"] = [m for m in rejected["spec"]["members"] if m["ref"] not in human_refs]
        rejected["spec"]["assessments"]["human_acceptance"] = []
        self.write("missing-human-stage.json", rejected)
        failed = self.cli("validate", "--project", str(self.root), "missing-human-stage.json",
                          "--context", "validation-context.json", code=1)
        self.assertTrue(any("human_acceptance" in i["message"] for i in failed["issues"]), failed)
        for adapter in ("claude-code", "codex"):
            self.cli("adapter", adapter, "validate", "--project", str(self.root), "stage.json",
                     "--context", "validation-context.json")
            self.assertEqual(failed, self.cli("adapter", adapter, "validate", "--project", str(self.root),
                "missing-human-stage.json", "--context", "validation-context.json", code=1))
        confirmation = (self.root / "confirmation.txt").read_text()
        args = ("freeze-publication", "--project", str(self.root), "--manifest", "stage.json", "--principal", "alice", "--confirm")
        self.cli(*args, "FREEZE reference", code=1)
        self.assertFalse((self.root / "publications/reference").exists())
        self.cli(*args, confirmation)
        frozen = self.root / "publications/reference"
        before = {str(path.relative_to(frozen)): path.read_bytes() for path in frozen.rglob("*") if path.is_file()}
        self.assertEqual(self.read("publications/reference/manifest.json"), self.read("stage.json"))
        self.cli(*args, confirmation, code=1)
        self.assertEqual(before, {str(path.relative_to(frozen)): path.read_bytes() for path in frozen.rglob("*") if path.is_file()})
        self.api("from pathlib import Path; from research_os.publication import verify_publication; "
                 "result=verify_publication(Path.cwd(), 'reference'); "
                 "assert result['verdict'] == 'pass', result")
        # Update is explicit and side-by-side; restore selects committed bytes,
        # preserving actual failed runs and the actual frozen Publication.
        self.git("add", ".")
        self.git("commit", "-qm", "fixture frozen reference and installed tools")
        historical = self.git("rev-parse", "HEAD")
        protected = {path.relative_to(self.root).as_posix(): path.read_bytes()
                     for path in self.root.rglob("*") if path.is_file() and ".git" not in path.relative_to(self.root).parts}
        update = self.cli("update-research-os", "--project", str(self.root), "--environment", "explicit-next")
        self.assertEqual(update["stop_reason"], "installed_explicit_activation_required")
        for path, raw in protected.items():
            self.assertEqual((self.root / path).read_bytes(), raw, path)
        recovery = tempfile.TemporaryDirectory(prefix="research-os-release-restored-")
        self.addCleanup(recovery.cleanup)
        restored = Path(recovery.name).resolve() / "old-project"
        exported = self.cli("export-research-os", "--project", str(self.root), "--commit", historical,
                            "--output", str(restored))
        self.assertEqual(exported["commit"], historical)
        self.assertTrue(exported["read_only"])
        for path, raw in protected.items():
            self.assertEqual((restored / path).read_bytes(), raw, path)
        self.write("acceptance-commands.json", self.command_receipts)
        self.write("acceptance-history.json", {"historical_commit": historical,
                   "update": update, "export": exported, "compared_files": len(protected),
                   "fixture_only": True})
        # Optional evidence retention is opt-in and never writes product source.
        destination = os.environ.get("RESEARCH_OS_E2E_OUTPUT")
        if destination:
            shutil.copytree(self.root, Path(destination) / profile, dirs_exist_ok=False)
