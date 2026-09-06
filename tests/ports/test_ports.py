from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fixtures import MARKER, fixture, release, save, sign_decision, write_bytes, write_json
from research_os.validation.ports import tree_digest, validate_ports


class PortHelpers:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = fixture(self.root)

    def report(self, **kwargs):
        save(self.root, self.manifest)
        return validate_ports(self.root, mode="admission", **kwargs)

    def signed_report(self, **kwargs):
        try:
            sign_decision(self.root, self.manifest)
        except (KeyError, TypeError, ValueError, UnicodeError):
            pass
        save(self.root, self.manifest)
        return validate_ports(self.root, mode="admission", **kwargs)

    def raw_report(self, **kwargs):
        save(self.root, self.manifest)
        return validate_ports(self.root, mode="admission", **kwargs)

    def assert_status(self, report, status, code=None):
        self.assertEqual(report["status"], status, report["issues"])
        self.assertEqual(report["exit_code"], {"pass": 0, "fail": 1, "blocked": 3}[status])
        if code:
            self.assertIn(code, {item["code"] for item in report["issues"]}, report["issues"])


class PortAdmissionTests(PortHelpers, unittest.TestCase):
    def test_adapt_fixture_acceptance_is_explicitly_nonshippable(self):
        report = self.signed_report()
        self.assert_status(report, "pass")
        self.assertFalse(report["release_authorized"])
        self.assertEqual(report["ports"][0]["admission"], "accepted")
        self.assertEqual(report["ports"][0]["scope"], MARKER)
        self.assertEqual({item["action"] for item in self.manifest["ledger"]}, {"keep", "modify", "delete", "add"})

    def test_preserve_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root, "preserve")
            self.assert_status(validate_ports(root, mode="admission"), "pass")

    def test_reject_is_valid_record_not_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = fixture(root, "reject")
            report = validate_ports(root, mode="admission")
            self.assert_status(report, "pass")
            self.assertEqual(report["ports"][0]["admission"], "rejected")
            self.assertIsNone(manifest["product"])

    def test_deterministic_across_roots_mtimes_and_file_order(self):
        first = self.signed_report()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture(root)
            for path in root.rglob("*"):
                if path.is_file():
                    os.utime(path, (1, 1))
            self.assertEqual(first, validate_ports(root, mode="admission"))
        self.assertEqual(first, self.signed_report())
        self.assertNotIn(str(self.root), json.dumps(first))
        files = self.manifest["baseline"]["files"]
        self.assertEqual(tree_digest(files), tree_digest(list(reversed(files))))

    def test_missing_every_required_top_level_field(self):
        original = copy.deepcopy(self.manifest)
        for key in original:
            with self.subTest(key=key):
                self.manifest = copy.deepcopy(original)
                del self.manifest[key]
                self.assert_status(self.report(), "fail")

    def test_unknown_fields_and_versions_fail_closed(self):
        paths = [(), ("source",), ("licensing",), ("licensing", "notice"), ("snapshot",),
                 ("baseline",), ("adapted",), ("original",), ("evaluation",), ("review",), ("product",)]
        original = copy.deepcopy(self.manifest)
        for path in paths:
            with self.subTest(path=path):
                self.manifest = copy.deepcopy(original)
                value = self.manifest
                for key in path:
                    value = value[key]
                value["unexpected"] = True
                self.assert_status(self.report(), "fail")
        for version in ("1", "1.0", "1.0.1", "2.0.0", "latest", 1, None):
            with self.subTest(version=version):
                self.manifest = copy.deepcopy(original)
                self.manifest["contract"]["version"] = version
                self.assert_status(self.report(), "fail")

    def test_missing_nested_required_fields(self):
        original = copy.deepcopy(self.manifest)
        objects = [("source",), ("licensing",), ("licensing", "license"),
                   ("licensing", "notice"), ("snapshot",), ("snapshot", "files", 0),
                   ("original",), ("ledger", 0), ("evaluation",),
                   ("evaluation", "baseline", 0), ("review",), ("product",)]
        for path in objects:
            target = original
            for key in path:
                target = target[key]
            for field in target:
                with self.subTest(path=path, field=field):
                    self.manifest = copy.deepcopy(original)
                    current = self.manifest
                    for key in path:
                        current = current[key]
                    del current[field]
                    self.assert_status(self.report(), "fail")

    def test_wrong_nested_types(self):
        original = copy.deepcopy(self.manifest)
        for key, invalid in (("ledger", {}), ("source", None), ("product", []), ("evaluation", False),
                             ("snapshot", []), ("decision", {}), ("id", 7), ("review", "reviewer")):
            with self.subTest(key=key):
                self.manifest = copy.deepcopy(original)
                self.manifest[key] = invalid
                self.assert_status(self.report(), "fail")

    def test_source_formats(self):
        original = copy.deepcopy(self.manifest)
        bad = {"url": ["http://example.org/repo", "file:///tmp/repo", "https://u:p@example.org/repo", "https://example.org/repo#main", "https://x.invalid:bad/", "not-url"],
               "commit": ["abc1234", "main", "A" * 40, "x" * 40, "0" * 39],
               "path": ["../source", "/tmp/source", "a/./b", "a//b", "a\\b", "a/%2e%2e/b"],
               "retrieved_at": ["today", "2026-02-30T00:00:00Z", "2026-09-06", "2026-09-06T00:00:00", "2026-09-06T00:00:00+00:00"]}
        for key, values in bad.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    self.manifest = copy.deepcopy(original)
                    self.manifest["source"][key] = value
                    self.assert_status(self.report(), "fail")

    def test_unavailable_prerequisites_are_blocked(self):
        original = copy.deepcopy(self.manifest)
        for fields in (("source",), ("licensing",), ("source", "licensing")):
            with self.subTest(fields=fields):
                self.manifest = copy.deepcopy(original)
                for field in fields:
                    self.manifest[field] = {"status": "unavailable", "reason": "No external retrieval permitted"}
                self.assert_status(self.signed_report(), "blocked")

    def test_unavailable_requires_reason_and_cannot_hide_drift(self):
        self.manifest["source"] = {"status": "unavailable", "reason": ""}
        self.assert_status(self.signed_report(), "fail")
        self.manifest["source"]["reason"] = "not retrieved"
        write_bytes(self.root, "evidence/baseline/unit.txt", b"drift")
        report = self.signed_report()
        self.assert_status(report, "fail", "hash.drift")
        self.assertIn("source.unavailable", {item["code"] for item in report["issues"]})

    def test_spdx_notice_license_requirements(self):
        original = copy.deepcopy(self.manifest)
        for expression in ("UNKNOWN", "MIT-ish", "MIT OR", "", " ", "MIT AND MIT", "LicenseRef-Arbitrary"):
            with self.subTest(expression=expression):
                self.manifest = copy.deepcopy(original)
                self.manifest["licensing"]["spdx"] = expression
                self.assert_status(self.report(), "fail")
        self.manifest = copy.deepcopy(original)
        self.manifest["licensing"]["notice"] = {"status": "not-required", "reason": "Local fixture explicitly needs no additional notice"}
        self.assert_status(self.signed_report(), "pass")
        self.manifest["licensing"]["notice"] = {"status": "not-required"}
        self.assert_status(self.signed_report(), "fail")
        self.manifest = copy.deepcopy(original)
        (self.root / "evidence/LICENSE").unlink()
        self.assert_status(self.signed_report(), "fail", "file.unreadable")

    def test_every_file_evidence_hash_is_checked(self):
        refs = [self.manifest["source"]["evidence"], self.manifest["licensing"]["license"],
                self.manifest["licensing"]["notice"]["file"], self.manifest["original"]["behavior"],
                self.manifest["evaluation"]["harness"], self.manifest["evaluation"]["environment"]]
        refs += [run["detail"] for side in ("baseline", "adapted") for run in self.manifest["evaluation"][side]]
        refs += [run["evidence"] for side in ("baseline", "adapted") for run in self.manifest["evaluation"][side]]
        for ref in refs:
            with self.subTest(path=ref["path"]):
                path = self.root / ref["path"]
                old = path.read_bytes()
                path.write_bytes(old + b"drift")
                self.assert_status(self.signed_report(), "fail", "hash.drift")
                path.write_bytes(old)

    def test_snapshot_and_baseline_hash_drift(self):
        for name in ("snapshot", "baseline", "adapted"):
            path = self.root / f"evidence/{name}/unit.txt"
            old = path.read_bytes()
            path.write_bytes(old + b"drift")
            self.assert_status(self.signed_report(), "fail", "hash.drift")
            path.write_bytes(old)

    def test_tree_missing_extra_duplicate_and_alias(self):
        extra = self.root / "evidence/snapshot/unlisted.txt"
        extra.write_bytes(b"unlisted")
        self.assert_status(self.signed_report(), "fail", "tree.inventory")
        extra.unlink()
        self.manifest["snapshot"]["files"].append(self.manifest["snapshot"]["files"][0])
        self.assert_status(self.signed_report(), "fail", "tree.duplicate")
        self.manifest["snapshot"]["files"].pop()
        self.manifest["snapshot"]["path"] = self.manifest["baseline"]["path"]
        self.assert_status(self.signed_report(), "fail", "tree.overlap")

    def test_ledger_contradictions(self):
        original = copy.deepcopy(self.manifest["ledger"])
        cases = [original[:-1], original + [original[0]],
                 original + [{"action": "add", "path": "ghost.txt", "reason": "invented"}]]
        for index in range(len(original)):
            case = copy.deepcopy(original)
            case[index]["action"] = "delete" if case[index]["action"] != "delete" else "keep"
            cases.append(case)
        for ledger in cases:
            with self.subTest(ledger=ledger):
                self.manifest["ledger"] = ledger
                self.assert_status(self.signed_report(), "fail", "ledger.contradiction")

    def test_preserve_cannot_claim_adaptation(self):
        self.manifest["decision"] = "preserve"
        self.assert_status(self.signed_report(), "fail", "decision.preserve_changed")

    def test_baseline_cannot_change_even_with_updated_hash(self):
        entry = write_bytes(self.root, "evidence/baseline/unit.txt", b"changed baseline with matching declaration")
        for item in self.manifest["baseline"]["files"]:
            if item["path"] == "unit.txt":
                item["sha256"] = entry["sha256"]
        self.assert_status(self.signed_report(), "fail", "baseline.changed")

    def test_adapt_requires_real_changes_and_reject_forbids_product(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = fixture(root, "preserve")
            manifest["decision"] = "adapt"
            save(root, manifest)
            self.assert_status(validate_ports(root, mode="admission"), "fail", "decision.adapt_unchanged")
        self.manifest["decision"] = "reject"
        self.assert_status(self.signed_report(), "fail", "decision.rejected_product")

    def test_empty_evidence_and_duplicate_port_ids_fail(self):
        self.manifest["licensing"]["license"] = write_bytes(self.root, "evidence/LICENSE", b"")
        self.assert_status(self.signed_report(), "fail", "license.empty")
        write_json(self.root, "SECOND.json", self.manifest)
        write_json(self.root, "inventory.json", {"contract": {"name": "research-os/port-inventory", "version": "1.0.0"}, "manifests": ["SECOND.json", "PORT.json"]})
        self.assert_status(self.signed_report(), "fail", "port.duplicate")

    def test_eval_requires_two_distinct_runs_each_side(self):
        original = copy.deepcopy(self.manifest["evaluation"])
        for side in ("baseline", "adapted"):
            for runs in ([], original[side][:1], [original[side][0], original[side][0]]):
                with self.subTest(side=side, runs=len(runs)):
                    self.manifest["evaluation"] = copy.deepcopy(original)
                    self.manifest["evaluation"][side] = runs
                    self.assert_status(self.report(), "fail")

    def test_eval_detail_is_required_and_bound(self):
        run = self.manifest["evaluation"]["adapted"][0]
        detail_path = self.root / run["detail"]["path"]
        detail = json.loads(detail_path.read_text())
        detail["checks"][0]["pass"] = False
        detail_path.write_text(json.dumps(detail, sort_keys=True, indent=2) + "\n")
        run["detail"] = write_bytes(self.root, run["detail"]["path"], detail_path.read_bytes())
        self.assert_status(self.signed_report(), "fail", "evaluation.detail")

    def test_eval_receipt_subject_result_and_chronology(self):
        original = copy.deepcopy(self.manifest)
        for key, value, code in (("subject_sha256", "0" * 64, "evaluation.subject"),
                                 ("result", "fail", "evaluation.failed"),
                                 ("executed_at", "2026-09-07T00:00:00Z", "review.chronology"),
                                 ("executed_at", "2026-09-05T00:00:00Z", "evaluation.chronology")):
            with self.subTest(key=key, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest["evaluation"]["baseline"][0][key] = value
                self.assert_status(self.signed_report(), "fail", code)
        self.manifest = copy.deepcopy(original)
        self.manifest["evaluation"]["baseline"][0]["evidence"] = write_json(self.root, "evidence/forged.json", {"result": "pass"})
        self.assert_status(self.signed_report(), "fail", "evaluation.receipt")

    def test_review_principal_and_behavior_dependencies(self):
        for principal in ("", "reviewer", "fixture:", "person: ", None):
            self.manifest["review"]["principal"] = principal
            self.assert_status(self.signed_report(), "fail")
        self.manifest["review"]["principal"] = "fixture:local-reviewer"
        dependency = {"name": "local-test-helper", "version": "1.0.0", "purpose": "fixture only"}
        self.manifest["original"]["dependencies"] = [dependency]
        self.assert_status(self.signed_report(), "pass")
        self.manifest["original"]["dependencies"].append(dependency)
        self.assert_status(self.signed_report(), "fail", "dependencies.duplicate")

    def test_human_decision_receipt_is_required_and_exactly_bound(self):
        self.assert_status(self.signed_report(), "pass")
        original = copy.deepcopy(self.manifest)
        for field, value in (
            ("decision_principal", "service:automated-reviewer"),
            ("decision_principal", "fixture:local-reviewer"),
        ):
            with self.subTest(field=field, value=value):
                self.manifest = copy.deepcopy(original)
                self.manifest[field] = value
                self.assert_status(self.report(), "fail")
        self.manifest = copy.deepcopy(original)
        path = self.root / self.manifest["decision_evidence"]["path"]
        receipt = json.loads(path.read_text())
        receipt["decision"] = "reject"
        path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
        self.manifest["decision_evidence"]["sha256"] = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
        self.assert_status(self.raw_report(), "fail", "decision.receipt")
        self.manifest = copy.deepcopy(original)
        self.manifest["source"]["commit"] = "b" * 40
        receipt_path = self.root / self.manifest["decision_evidence"]["path"]
        self.manifest["decision_evidence"]["sha256"] = __import__("hashlib").sha256(receipt_path.read_bytes()).hexdigest()
        self.assert_status(self.raw_report(), "fail", "decision.receipt")

    def test_product_digest_path_and_binding(self):
        original = copy.deepcopy(self.manifest["product"])
        path = self.root / original["path"]
        old = path.read_bytes()
        path.write_bytes(b"tampered")
        self.assert_status(self.signed_report(), "fail", "product.digest_mismatch")
        path.write_bytes(old)
        self.manifest["product"] = write_bytes(self.root, "products/unbound.txt", b"unbound local bytes")
        self.assert_status(self.signed_report(), "fail", "product.unbound")
        self.manifest["product"] = {"path": "evidence/adapted/unit.txt", "sha256": original["sha256"]}
        self.assert_status(self.signed_report(), "fail", "product.path")
        self.manifest["product"] = None
        self.assert_status(self.signed_report(), "fail", "product.required")

    def test_symlinks_traversal_and_special_files_fail(self):
        path = self.root / "evidence/baseline/unit.txt"
        path.unlink()
        path.symlink_to(self.root / "evidence/snapshot/unit.txt")
        self.assert_status(self.signed_report(), "fail", "tree.unsafe")
        path.unlink()
        os.mkfifo(path)
        self.assert_status(self.signed_report(), "fail", "tree.unsafe")
        for path in ("../PORT.json", "/PORT.json", "a//b", "a/../b", "PORT.json\x00", "a\\b"):
            self.assert_status(validate_ports(self.root, inventory=path, mode="admission"), "fail")

    def test_inventory_is_explicit_nonempty_versioned_unique(self):
        cases = [None, {}, [], {"contract": {"name": "research-os/port-inventory", "version": "1.0.0"}, "manifests": []},
                 {"contract": {"name": "research-os/port-inventory", "version": "2.0.0"}, "manifests": ["PORT.json"]},
                 {"contract": {"name": "research-os/port-inventory", "version": "1.0.0"}, "manifests": ["PORT.json", "PORT.json"]}]
        for case in cases:
            with self.subTest(case=case):
                write_json(self.root, "inventory.json", case)
                self.assert_status(validate_ports(self.root, mode="admission"), "fail")

    def test_invalid_json_duplicate_keys_nonfinite_and_nonobject(self):
        for data in (b"{", b'{"manifests":[],"manifests":[]}', b'{"value":NaN}', b"null", b"[]", b"\xff"):
            write_bytes(self.root, "inventory.json", data)
            self.assert_status(validate_ports(self.root, mode="admission"), "fail")

    def test_lone_surrogates_in_values_and_keys_fail_without_traceback(self):
        original = copy.deepcopy(self.manifest)
        for location in ("path", "text", "key"):
            with self.subTest(location=location):
                self.manifest = copy.deepcopy(original)
                if location == "path":
                    self.manifest["snapshot"]["files"][0]["path"] = "\ud800"
                elif location == "text":
                    self.manifest["review"]["rationale"] = "\udfff"
                else:
                    self.manifest["\ud800"] = True
                self.assert_status(self.signed_report(), "fail", "json.invalid")

    def test_reserved_source_hosts_with_dns_trailing_dot(self):
        self.manifest["origin"] = "external"
        self.manifest["source"]["commit"] = "a" * 40
        for host in ("example.org.", "x.invalid.", "test.example.com", "example.net", "x.test."):
            with self.subTest(host=host):
                source = self.manifest["source"]
                source["url"] = f"https://{host}/repo"
                receipt = {key: source[key] for key in ("url", "commit", "path", "retrieved_at")}
                receipt.update(origin="external", snapshot_sha256=tree_digest(self.manifest["snapshot"]["files"]))
                source["evidence"] = write_json(self.root, "evidence/source.json", receipt)
                self.assert_status(self.signed_report(), "fail", "source.synthetic")

    def test_no_network_or_subprocess_evaluation(self):
        with patch("socket.socket", side_effect=AssertionError("network prohibited")), patch("subprocess.run", side_effect=AssertionError("execution prohibited")):
            self.assert_status(self.signed_report(), "pass")

    def test_cli_status_and_usage(self):
        command = [sys.executable, "-m", "research_os.validation.ports", "--root", str(self.root), "--mode", "admission"]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), self.signed_report())
        self.manifest["source"] = {"status": "unavailable", "reason": "intentionally offline"}
        sign_decision(self.root, self.manifest)
        save(self.root, self.manifest)
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 3)
        self.manifest["id"] = ""
        save(self.root, self.manifest)
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        self.assertEqual(subprocess.run([sys.executable, "-m", "research_os.validation.ports"], capture_output=True).returncode, 2)


class ReleaseTests(PortHelpers, unittest.TestCase):
    def release_report(self):
        save(self.root, self.manifest)
        return validate_ports(self.root, release_inventory="release.json")

    def test_accepted_fixture_never_enters_release(self):
        release(self.root, self.manifest)
        report = self.release_report()
        self.assert_status(report, "fail", "release.fixture")
        self.assertFalse(report["release_authorized"])

    def test_release_defaults_fail_closed(self):
        self.assert_status(validate_ports(self.root), "fail", "release.required")
        self.assert_status(validate_ports(self.root, mode="invalid"), "fail", "input.invalid")
        self.assert_status(validate_ports(self.root, mode="admission", release_inventory="release.json"), "fail", "input.invalid")

    def test_release_allowlist_unknown_digest_omissions_and_duplicates(self):
        original = release(self.root, self.manifest)
        cases = []
        unknown = copy.deepcopy(original)
        unknown["allowlist"][0]["port_id"] = "unknown"
        cases.append((unknown, "release.unknown_port"))
        mismatch = copy.deepcopy(original)
        mismatch["allowlist"][0]["sha256"] = "0" * 64
        cases.append((mismatch, "release.binding"))
        duplicate = copy.deepcopy(original)
        duplicate["allowlist"].append(duplicate["allowlist"][0])
        cases.append((duplicate, "release.duplicate"))
        for value, code in cases:
            write_json(self.root, "release.json", value)
            self.assert_status(self.release_report(), "fail", code)
        write_json(self.root, "release.json", original)
        write_bytes(self.root, "products/unlisted.txt", b"local unlisted bytes")
        self.assert_status(self.release_report(), "fail", "release.inventory")
        original["products"] = []
        original["allowlist"] = []
        write_json(self.root, "release.json", original)
        self.assert_status(self.release_report(), "fail")

    def test_reject_bytes_cannot_hide_renamed_or_wrapped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = fixture(root, "reject")
            rejected = (root / "evidence/snapshot/unit.txt").read_bytes()
            write_bytes(root, "products/renamed.txt", b"wrapper\n" + rejected + b"suffix")
            report = validate_ports(root, mode="admission")
            self.assert_status(report, "fail", "release.rejected_bytes")
            release(root, manifest)
            self.assert_status(validate_ports(root, release_inventory="release.json"), "fail", "release.rejected")

    def test_fixture_cannot_relabel_as_external(self):
        self.manifest["origin"] = "external"
        release(self.root, self.manifest)
        self.assert_status(self.release_report(), "fail", "source.synthetic")

    def test_external_unavailable_release_is_blocked_not_fabricated_acceptance(self):
        # Negative external case: no source/license evidence, never accepted.
        self.manifest["origin"] = "external"
        self.manifest["review"]["principal"] = "person:local-negative-test"
        self.manifest["source"] = {"status": "unavailable", "reason": "external retrieval prohibited"}
        self.manifest["licensing"] = {"status": "unavailable", "reason": "license unavailable"}
        # Remove fixture markers from product bytes only to isolate BLOCKED semantics;
        # all four evaluation receipts are explicitly negative/unavailable test records.
        data = b"Local negative test bytes; no external admission evidence.\n"
        self.manifest["product"] = write_bytes(self.root, "products/local-test.txt", data)
        decision_bundle = {
            key: self.manifest[key]
            for key in (
                "contract", "id", "origin", "source", "licensing", "snapshot", "baseline",
                "adapted", "original", "ledger", "evaluation", "review", "decision",
                "decision_principal", "product",
            )
        }
        admission_digest = __import__("hashlib").sha256(
            json.dumps(decision_bundle, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()
        decision_receipt = {
            "port_id": self.manifest["id"],
            "principal": self.manifest["decision_principal"],
            "decision": self.manifest["decision"],
            "reviewed_at": self.manifest["review"]["reviewed_at"],
            "product": self.manifest["product"],
            "admission_digest": admission_digest,
        }
        self.manifest["decision_evidence"] = write_json(self.root, "evidence/decision.json", decision_receipt)
        adapted = write_bytes(self.root, "evidence/adapted/unit.txt", data)
        for item in self.manifest["adapted"]["files"]:
            if item["path"] == "unit.txt":
                item["sha256"] = adapted["sha256"]
        for side in ("baseline", "adapted"):
            for run in self.manifest["evaluation"][side]:
                run["subject_sha256"] = tree_digest(self.manifest[side]["files"])
                detail = {"contract": {"name": "research-os/port-evaluation-detail", "version": "1.0.0"},
                          "kind": "negative-unavailable", "subject_sha256": run["subject_sha256"],
                          "tree_sha256": run["subject_sha256"], "result": run["result"],
                          "checks": [{"name": "unavailable-fixture", "pass": True}]}
                run["detail"] = write_json(self.root, run["detail"]["path"], detail)
                receipt = {key: run[key] for key in ("run_id", "executed_at", "subject_sha256", "result")}
                receipt.update(side=side, origin="external", harness_sha256=self.manifest["evaluation"]["harness"]["sha256"], environment_sha256=self.manifest["evaluation"]["environment"]["sha256"])
                run["evidence"] = write_json(self.root, run["evidence"]["path"], receipt)
        sign_decision(self.root, self.manifest)
        release(self.root, self.manifest)
        report = self.release_report()
        self.assert_status(report, "blocked")
        self.assertFalse(report["release_authorized"])
        self.assertEqual(report["ports"][0]["admission"], "not-admitted")


if __name__ == "__main__":
    unittest.main()
