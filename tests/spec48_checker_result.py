"""Parse the structure CLI's report, never treating a crashed check as success."""
import re
from subprocess import CompletedProcess

HISTORY_STATUS = re.compile(
    r"HISTORY (UNVERIFIED|MISMATCH|BYTE_MATCH): [A-Za-z0-9][A-Za-z0-9._-]*\.tar\.gz "
    r"\((UNAVAILABLE|AVAILABLE); 摘要不认证来源/安全\)"
)
SUCCESS = re.compile(r"OK: (\d+) 个 Skill（U (\d+) / M (\d+)），调用策略与门声明通过")
FAILURE = re.compile(r"FAIL: (\d+) 个问题")


def parse_checker_result(result: CompletedProcess[str]) -> list[str]:
    if result.stderr:
        raise AssertionError(f"checker wrote to stderr (exit={result.returncode}): {result.stderr!r}")
    output = [line for line in result.stdout.splitlines() if not HISTORY_STATUS.fullmatch(line)]
    if result.returncode == 0:
        summary = SUCCESS.fullmatch(output[0]) if len(output) == 1 else None
        if summary is None or int(summary[1]) != int(summary[2]) + int(summary[3]):
            raise AssertionError(f"checker returned success without a valid OK summary: {result.stdout!r}")
        return []
    if result.returncode == 1:
        summary = FAILURE.fullmatch(output[0]) if output else None
        problems = output[1:]
        if (
            summary is None or int(summary[1]) < 1
            or int(summary[1]) != len(problems)
            or not all(line.startswith("  - ") and line[4:].strip() for line in problems)
        ):
            raise AssertionError(f"checker did not finish with a valid failure report: {result.stdout!r}")
        return problems
    raise AssertionError(
        f"checker exited unexpectedly (exit={result.returncode}): {result.stdout!r}"
    )
