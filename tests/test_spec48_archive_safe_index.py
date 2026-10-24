"""Structure and byte-identity are separate; fixtures are NOT historical evidence."""
import contextlib
import hashlib
import io
import re
import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path

from spec48_workcopy import copy_tracked_tree

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts/check-skills.py"
INDEX_REL = "docs/acceptance/evidence/README.md"
INDEX = ROOT / INDEX_REL
HISTORICAL_IDENTITIES = ROOT / "tests/fixtures/spec48-archive-history.tsv"


class HistoricalArchiveIndexTests(unittest.TestCase):
    def test_real_local_only_structure_and_strict_history(self):
        names = re.findall(r"^\| `([^`]+\.tar\.gz)`", INDEX.read_text(), re.M)
        self.assertEqual(len(names), 8)
        for scope, rc in (("structure", 0), ("history", 1)):
            with self.subTest(scope=scope):
                result = subprocess.run(
                    ["uv", "run", "--offline", "--no-project", "python", str(CHECK),
                     "--archive-scope", scope], cwd=ROOT, capture_output=True,
                    text=True, timeout=35,
                )
                self.assertEqual(result.returncode, rc, result.stdout + result.stderr)
                for name in names:
                    self.assertRegex(result.stdout, rf"HISTORY (UNVERIFIED|MISMATCH): {re.escape(name)}.*UNAVAILABLE")
                self.assertNotIn("HISTORY PASS", result.stdout)
                self.assertNotIn("链接目标不存在或未追踪: evidence/", result.stdout)

    def setUp(self):
        self.ns = runpy.run_path(str(CHECK))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.index = self.root / INDEX_REL
        self.index.parent.mkdir(parents=True)
        self.doc = self.root / "docs/acceptance/fixture.md"
        self.doc.write_text("[synthetic-fixture.tar.gz](evidence/README.md)\n")
        self.payload = b"artificial mechanism fixture, NOT a recovered historical archive\n"
        self.sha = hashlib.sha256(self.payload).hexdigest()
        self.name = "synthetic-fixture.tar.gz"
        self.archive = self.index.parent / self.name
        self.archive_rel = self.archive.relative_to(self.root).as_posix()
        self.tracked = {INDEX_REL, self.doc.relative_to(self.root).as_posix()}

    def row(self, status="仅本地保留、未入库", historical=None, candidate=None, size=None):
        return (f"| `{self.name}` | {size if size is not None else len(self.payload)} | "
                f"`{historical or self.sha}` | `{candidate or self.sha}` | {status} | "
                "人工机制 fixture，不证明历史身份 |\n")

    def check(self, strict=False):
        env = self.ns["check_archive_index"].__globals__
        env.update(ROOT=self.root, tracked=self.tracked, md_files=[self.doc, self.index])
        env["problems"].clear()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            env["check_archive_index"](strict=strict)
        return list(env["problems"]), output.getvalue()

    def test_local_only_and_mismatch_are_not_structure_errors(self):
        for historical, expected in ((self.sha, "UNVERIFIED"), ("a" * 64, "MISMATCH")):
            self.index.write_text(self.row(historical=historical))
            errors, output = self.check()
            self.assertEqual(errors, [])
            self.assertIn(f"HISTORY {expected}", output)
            self.assertIn("UNAVAILABLE", output)
            self.assertTrue(self.check(strict=True)[0])

    def test_isolated_bytes_can_pass_and_damage_cannot(self):
        self.archive.write_bytes(self.payload)
        self.tracked.add(self.archive_rel)
        self.index.write_text(self.row(status="已入库、已核验"))
        for strict in (False, True):
            self.assertEqual(self.check(strict)[0], [])
        self.assertIn("BYTE_MATCH", self.check(True)[1])
        self.index.write_text(self.row(status="已入库、已核验", size=len(self.payload) + 1))
        for strict in (False, True):
            self.assertIn("候选字节", "\n".join(self.check(strict)[0]))
        self.index.write_text(self.row(status="已入库、已核验"))
        self.archive.write_bytes(self.payload.replace(b"fixture", b"mutated"))
        for strict in (False, True):
            self.assertIn("候选字节", "\n".join(self.check(strict)[0]))
        self.archive.unlink()
        for strict in (False, True):
            self.assertIn("状态", "\n".join(self.check(strict)[0]))

    def test_tracked_candidate_mismatch_is_honest_but_not_verified(self):
        self.archive.write_bytes(self.payload)
        self.tracked.add(self.archive_rel)
        self.index.write_text(self.row(status="已入库、待核验", historical="a" * 64))
        self.assertEqual(self.check()[0], [])
        self.assertIn("MISMATCH", self.check()[1])
        self.assertTrue(self.check(True)[0])
        self.index.write_text(self.row(status="已入库、已核验", historical="a" * 64))
        self.assertIn("核验状态", "\n".join(self.check()[0]))

    def test_bad_fields_duplicate_unknown_and_contradictory_status(self):
        bad = {
            "bad-sha": self.row(candidate="bad"),
            "zero": self.row(size=0), "negative": self.row(size=-1),
            "duplicate": self.row() * 2,
            "unknown": self.row(status="covered"),
            "verified-without-bytes": self.row(status="已入库、已核验"),
            "bad-name": self.row().replace(self.name, "../escape.tar.gz"),
            "extra-invalid-name": self.row() + self.row().replace(self.name, "not-an-archive"),
            "bad-columns": self.row().replace(" | 人工", " | extra | 人工"),
        }
        for label, text in bad.items():
            with self.subTest(label=label):
                self.index.write_text(text)
                for strict in (False, True):
                    self.assertTrue(self.check(strict)[0])
        self.index.write_text(self.row())
        self.archive.write_bytes(self.payload)
        for tracked in (False, True):
            if tracked:
                self.tracked.add(self.archive_rel)
            self.assertIn("状态", "\n".join(self.check()[0]))

    def test_missing_rows_index_and_bad_real_href(self):
        self.index.write_text("# Fixture\n" + self.row())
        self.doc.write_text(f"[{self.name}](evidence/README.md#fixture)\n")
        self.assertEqual(self.check()[0], [])
        valid = f"[{self.name}](evidence/README.md)\n"
        self.doc.write_text(valid + f"[{self.name}](fixture.md)\n")
        self.assertTrue(self.check()[0], "另一正确入口不能遮蔽错误 href")
        for href in ("evidence/missing.md", "evidence/README.md.evil", "evidence/README.md#missing"):
            self.doc.write_text(f"[{self.name}]({href})\n")
            self.assertTrue(self.check()[0], href)
        self.doc.write_text(f"[{self.name}](evidence/README.md)\n")
        self.index.write_text("")
        self.assertTrue(self.check()[0])
        self.index.write_text(self.row())
        self.tracked.remove(INDEX_REL)
        self.assertTrue(self.check()[0])
        self.tracked.add(INDEX_REL)
        self.index.unlink()
        self.assertTrue(self.check()[0])

    def test_each_explicit_archive_link_owns_its_href_and_fragment(self):
        self.index.write_text("# Fixture\n" + self.row())
        good = "[历史归档索引](evidence/README.md)"
        cases = (
            (f"`{self.name}`，见 {good}", True),
            (f"[{self.name}](evidence/README.md) {good}", True),
            (f"[{self.name}](evidence/README.md#fixture) {good}", True),
            (f"[{self.name}](fixture.md) {good}", False),
            (f"[{self.name}](evidence/README.md#missing) {good}", False),
            (f"[{self.name}](fixture.md) [{self.name}](evidence/README.md)", False),
            (f"{good} [{self.name}](evidence/README.md#missing)", False),
        )
        for line, valid in cases:
            with self.subTest(line=line):
                self.doc.write_text(line + "\n")
                errors, _ = self.check()
                self.assertEqual(not errors, valid, errors)
                if not valid:
                    self.assertIn("归档引用必须链接真实索引", "\n".join(errors))

    def test_full_cli_rejects_same_line_masked_archive_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            copy_tracked_tree(ROOT, work)
            for command in (["git", "init", "-q"], ["git", "add", "-A"]):
                subprocess.run(command, cwd=work, check=True, capture_output=True, timeout=30)
            doc = work / "docs/acceptance/v2-release-host-regression.md"
            original = doc.read_text()
            name = "v2-release-host-regression.tar.gz"
            good = "[历史归档索引](evidence/README.md)"
            cases = (
                ("baseline", "", 0),
                ("body-name-index", f"`{name}`，见 {good}", 0),
                ("explicit-valid", f"[{name}](evidence/README.md) {good}", 0),
                ("explicit-valid-fragment", f"[{name}](evidence/README.md#安全与可验证性限制) {good}", 0),
                ("wrong-alone", f"[{name}](../../README.md)", 1),
                ("masked-href", f"[{name}](../../README.md) {good}", 1),
                ("masked-fragment", f"[{name}](evidence/README.md#missing) {good}", 1),
                ("masked-by-same-archive", f"[{name}](../../README.md) [{name}](evidence/README.md)", 1),
            )
            for label, line, rc in cases:
                with self.subTest(case=label):
                    doc.write_text(original + (f"\n- {line}\n" if line else ""))
                    command = ["uv", "run", "--offline", "--no-project", "python", "scripts/check-skills.py"]
                    result = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=35)
                    diff = subprocess.check_output(["git", "diff", "--", str(doc)], cwd=work, text=True, timeout=30)
                    print(f"CLI F3 {label}: command={command!r}, rc={result.returncode}\n{result.stdout}{result.stderr}{diff}")
                    self.assertEqual(result.returncode, rc, result.stdout + result.stderr)
                    if rc:
                        self.assertIn("归档引用必须链接真实索引", result.stdout)
                        self.assertIn(name, result.stdout)
                        self.assertNotIn("链接目标不存在或未追踪", result.stdout)

    def test_full_cli_archive_name_target_registration_matrix(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            copy_tracked_tree(ROOT, work)
            for command in (["git", "init", "-q"], ["git", "add", "-A"]):
                subprocess.run(command, cwd=work, check=True, capture_output=True, timeout=30)
            doc = work / "docs/acceptance/v2-release-host-regression.md"
            original = doc.read_text()
            command = ["uv", "run", "--offline", "--no-project", "python", "scripts/check-skills.py"]
            baseline = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=35)
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            names = ((True, "v2-release-host-regression.tar.gz"), (False, "review-unknown.tar.gz"))
            targets = (("valid", "evidence/README.md"), ("bad-href", "../../README.md"),
                       ("bad-fragment", "evidence/README.md#missing"))
            for known, name in names:
                for kind, target in targets:
                    for with_good_link in (False, True):
                        with self.subTest(known=known, target=kind, good_link=with_good_link):
                            line = f"- [{name}]({target})"
                            if with_good_link:
                                line += " [历史归档索引](evidence/README.md)"
                            doc.write_text(original + "\n" + line + "\n")
                            result = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=35)
                            diff = subprocess.check_output(["git", "diff", "--", str(doc)], cwd=work, text=True, timeout=30)
                            print(f"CLI MATRIX known={known} target={kind} good_link={with_good_link}: "
                                  f"command={command!r}, rc={result.returncode}\n{result.stdout}{result.stderr}{diff}")
                            output = result.stdout + result.stderr
                            self.assertEqual(result.returncode, 0 if known and kind == "valid" else 1, output)
                            self.assertEqual(f"归档索引缺少被引用记录: {name}" in output, not known, output)
                            self.assertEqual(f"归档引用必须链接真实索引: {name} -> {target}" in output,
                                             kind != "valid", output)
                            self.assertNotIn("链接目标不存在或未追踪", output)

    def assert_evidence_contract(self, text):
        for needle in ("v2-accept-deliverables.tar.gz", "历史原包字节未找到", "清单自引用",
                       "不能证明来源", "未纳入本仓库", "不能充当原包", "不得将下面的摘要当成原包恢复"):
            self.assertIn(needle, text)
        # Pin only historical identities, NOT status/candidate/availability.
        # This tiny public fixture avoids depending on a local historical Git object
        # or copying archive payloads into the repository.
        historical = re.compile(r"^\| `([^`]+\.tar\.gz)` \| [^|]+ \| `([0-9a-f]{64})`", re.M)
        expected = [tuple(line.split("\t")) for line in HISTORICAL_IDENTITIES.read_text().splitlines()[1:]]
        self.assertEqual(len(expected), 8)
        self.assertEqual(historical.findall(text), expected)

    def test_limitations_and_historical_sha_are_retained(self):
        self.assert_evidence_contract(INDEX.read_text())

    def test_evidence_contract_rejects_erased_limits_and_historical_identity(self):
        text = INDEX.read_text()
        for needle in ("v2-accept-deliverables.tar.gz", "历史原包字节未找到", "清单自引用", "不能证明来源"):
            with self.subTest(removed=needle), self.assertRaises(AssertionError):
                self.assert_evidence_contract(text.replace(needle, ""))
        with self.assertRaises(AssertionError):
            self.assert_evidence_contract(re.sub(r"`[0-9a-f]{64}`", "`" + "0" * 64 + "`", text, count=1))
