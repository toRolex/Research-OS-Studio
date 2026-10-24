"""Historical archive references remain honest when raw packages stay local."""

import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "docs" / "acceptance" / "evidence" / "README.md"
CHECK = ROOT / "scripts" / "check-skills.py"
ARCHIVE_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.tar\.gz")

EXPECTED_ARCHIVES = {
    "v2-release-host-regression.tar.gz": (
        "15807902",
        "d80e120694d7623533e253798550a43d8b61b6eea78592a5df388a2063a4cadc",
        "d80e120694d7623533e253798550a43d8b61b6eea78592a5df388a2063a4cadc",
    ),
    "v2-final-contract-fixes.tar.gz": (
        "2489643",
        "f2657476febf3689258397dc35d924b0e32ba5b4ca505d946374438d056b2df1",
        "f2657476febf3689258397dc35d924b0e32ba5b4ca505d946374438d056b2df1",
    ),
    "v2-release-gate-combinations.tar.gz": (
        "12544022",
        "2291c39cbe506db6fa90c11e684e5047d9300ebd813d35496d5942e6cbb3efc1",
        "2291c39cbe506db6fa90c11e684e5047d9300ebd813d35496d5942e6cbb3efc1",
    ),
    "v2-merged-host-smoke.tar.gz": (
        "1636956",
        "cead0cd3fd83e9ce6c897934e55b30c7fc727b3128830ab141066d8c6ca4db10",
        "cead0cd3fd83e9ce6c897934e55b30c7fc727b3128830ab141066d8c6ca4db10",
    ),
    "v2-accept-validation.tar.gz": (
        "22334163",
        "705edc4c2496713e578a6b18b364ec7ec542e84ebcabc3b8b3505f401d940cd7",
        "dc4ae3ef5f4d012cfefe908abe69f0c4818a8dbc6ad8634c7bd4268a1e065f91",
    ),
    "v2-accept-hosts.tar.gz": (
        "8148719",
        "cab141490a54d13564d27723a6f8cfcff726d555698da26668111d0eb3cefa9e",
        "cab141490a54d13564d27723a6f8cfcff726d555698da26668111d0eb3cefa9e",
    ),
    "v2-final-contract-independent-verify.tar.gz": (
        "31575",
        "e2107183209155532ccec7e95a9f278ec45508b9418a8f62eb4797be52b4d7d4",
        "e2107183209155532ccec7e95a9f278ec45508b9418a8f62eb4797be52b4d7d4",
    ),
    "v2-accept-remediation.tar.gz": (
        "47077162",
        "ffc305f4c1a94bd9ae6ea31f344de3736f47800b5f8593beb6091077b45e329a",
        "ffc305f4c1a94bd9ae6ea31f344de3736f47800b5f8593beb6091077b45e329a",
    ),
}


class HistoricalArchiveIndexTests(unittest.TestCase):
    def test_index_distinguishes_historical_sha_from_local_candidate(self) -> None:
        text = INDEX.read_text(encoding="utf-8")
        rows = {}
        for line in text.splitlines():
            if not line.startswith("| `"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 6:
                continue
            filename = cells[0].strip("`")
            rows[filename] = tuple(
                cell.strip("`").replace(",", "")
                for cell in (cells[1], cells[2], cells[3])
            )

        self.assertEqual(rows, EXPECTED_ARCHIVES)
        self.assertIn("仅本地保留", text)
        self.assertIn("未纳入本仓库", text)
        self.assertIn("不能证明来源", text)
        self.assertIn("不得将下面的摘要当成原包恢复", text)

    def test_acceptance_docs_link_archive_claims_to_the_index_not_missing_tarballs(self) -> None:
        acceptance = ROOT / "docs" / "acceptance"
        archive_refs = 0
        for path in acceptance.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                if "evidence/README.md" not in line:
                    continue
                refs = set(ARCHIVE_NAME_RE.findall(line)) & EXPECTED_ARCHIVES.keys()
                if refs:
                    archive_refs += 1
            self.assertNotRegex(text, r"\]\([^)]*\.tar\.gz")
        self.assertEqual(archive_refs, 9)
        for filename in EXPECTED_ARCHIVES:
            self.assertFalse((acceptance / "evidence" / filename).exists(), filename)

    def test_checker_keeps_archive_absence_failures(self) -> None:
        result = subprocess.run(
            ["uv", "run", "--offline", "--no-project", "python", str(CHECK)],
            cwd=ROOT,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=35,
            check=False,
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertEqual(output.count("链接目标不存在或未追踪: evidence/"), 9, output)
        for filename in EXPECTED_ARCHIVES:
            self.assertIn(filename, output)
        self.assertNotIn("链接目标不存在或未追踪: evidence/README.md", output)


if __name__ == "__main__":
    unittest.main()
