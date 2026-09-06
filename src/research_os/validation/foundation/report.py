from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

from .issues import Issue
from .registry import TYPE_NAME_RE
from .semver import SemVer
from .targets import SHA256_RE, validate_target

Verdict = Literal["pass", "fail", "usage_error", "blocked"]
_VERDICTS = frozenset({"pass", "fail", "usage_error", "blocked"})
_EXIT_CODES = {"pass": 0, "fail": 1, "usage_error": 2, "blocked": 3}


def exit_code_for_verdict(verdict: object) -> int:
    try:
        return _EXIT_CODES[verdict]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"unsupported validation verdict: {verdict}") from exc


@dataclass(frozen=True, slots=True)
class ValidatorIdentity:
    name: str
    version: SemVer

    @classmethod
    def create(cls, name: str, version: str) -> "ValidatorIdentity":
        if not isinstance(name, str) or TYPE_NAME_RE.fullmatch(name) is None:
            raise ValueError("validator name must be lowercase kebab-case")
        return cls(name, SemVer.parse(version))


class ValidationReportBuilder:
    """Build a report from the validator that actually ran and its observations."""

    def __init__(
        self,
        validator_name: str,
        validator_version: str,
        subject_target: dict[str, object],
        *,
        subject_sha256: str | None = None,
    ) -> None:
        self._validator = ValidatorIdentity.create(validator_name, validator_version)
        target_issues = validate_target(subject_target, instance_path="/subject/target")
        if target_issues:
            raise ValueError(target_issues[0].message)
        self._subject_target = dict(subject_target)
        target_digest = subject_target.get("sha256") if subject_target.get("kind") == "uri" else None
        if subject_sha256 is not None and SHA256_RE.fullmatch(subject_sha256) is None:
            raise ValueError("subject_sha256 must be 64 lowercase hexadecimal characters")
        if subject_sha256 is not None and target_digest is not None and subject_sha256 != target_digest:
            raise ValueError("subject_sha256 must equal URI target sha256")
        self._subject_sha256 = subject_sha256
        self._evidence: list[Issue] = []
        self._issues: list[Issue] = []

    def add_evidence(self, code: str, message: str, *, instance_path: str = "", data: dict[str, object] | None = None) -> "ValidationReportBuilder":
        self._evidence.append(Issue(code, message, instance_path, data or {}))
        return self

    def add_issue(self, issue: Issue) -> "ValidationReportBuilder":
        if not isinstance(issue, Issue):
            raise TypeError("issue must be an Issue")
        self._issues.append(issue)
        return self

    def extend_issues(self, issues: Iterable[Issue]) -> "ValidationReportBuilder":
        for issue in issues:
            self.add_issue(issue)
        return self

    def build(self, verdict: Verdict | None = None) -> dict[str, object]:
        final_verdict: str = verdict or ("fail" if self._issues else "pass")
        if final_verdict not in _VERDICTS:
            raise ValueError(f"unsupported validation verdict: {final_verdict}")
        if final_verdict == "pass" and self._issues:
            raise ValueError("a passing report cannot contain issues")
        if final_verdict != "pass" and not self._issues:
            raise ValueError("a non-passing report must contain at least one issue")
        subject: dict[str, object] = {"target": dict(self._subject_target)}
        if self._subject_sha256 is not None:
            subject["sha256"] = self._subject_sha256
        return {
            "contract": {"name": "research-os/validation-report", "version": "1.0.0"},
            "validator": {"name": self._validator.name, "version": str(self._validator.version)},
            "subject": subject,
            "verdict": final_verdict,
            "evidence": [item.as_dict() for item in self._evidence],
            "issues": [item.as_dict() for item in self._issues],
        }


def validate_validation_report(value: object) -> list[Issue]:
    if not isinstance(value, dict):
        return [Issue("report.object", "Validation Report must be an object")]
    issues: list[Issue] = []
    allowed = {"contract", "validator", "subject", "verdict", "evidence", "issues"}
    _reject_fields(value, allowed, issues, "", "report.field")
    contract = value.get("contract")
    if contract != {"name": "research-os/validation-report", "version": "1.0.0"}:
        issues.append(Issue("report.contract", "invalid Validation Report contract", "/contract"))
    validator = value.get("validator")
    if not isinstance(validator, dict):
        issues.append(Issue("report.validator", "validator must be an object", "/validator"))
    else:
        _reject_fields(validator, {"name", "version"}, issues, "/validator", "report.validator.field")
        try:
            ValidatorIdentity.create(validator.get("name"), validator.get("version"))
        except (TypeError, ValueError) as exc:
            issues.append(Issue("report.validator", str(exc), "/validator"))
    subject = value.get("subject")
    if not isinstance(subject, dict):
        issues.append(Issue("report.subject", "subject must be an object", "/subject"))
    else:
        _reject_fields(subject, {"target", "sha256"}, issues, "/subject", "report.subject.field")
        issues.extend(validate_target(subject.get("target"), instance_path="/subject/target"))
        digest = subject.get("sha256")
        if digest is not None and (not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None):
            issues.append(Issue("report.subject.sha256", "subject sha256 must be 64 lowercase hexadecimal characters", "/subject/sha256"))
        target = subject.get("target")
        if (
            isinstance(target, dict)
            and target.get("kind") == "uri"
            and digest is not None
            and digest != target.get("sha256")
        ):
            issues.append(Issue("report.subject.digest_mismatch", "subject sha256 must equal URI target sha256", "/subject/sha256"))
    verdict = value.get("verdict")
    if verdict not in _VERDICTS:
        issues.append(Issue("report.verdict", "unsupported Validation Report verdict", "/verdict"))
    for field in ("evidence", "issues"):
        observations = value.get(field)
        if not isinstance(observations, list):
            issues.append(Issue(f"report.{field}", f"{field} must be an array", f"/{field}"))
            continue
        for index, observation in enumerate(observations):
            path = f"/{field}/{index}"
            if not isinstance(observation, dict):
                issues.append(Issue("report.observation", "observation must be an object", path))
                continue
            _reject_fields(observation, {"code", "message", "instance_path", "data"}, issues, path, "report.observation.field")
            if not isinstance(observation.get("code"), str) or not observation["code"]:
                issues.append(Issue("report.observation.code", "observation code is required", f"{path}/code"))
            if not isinstance(observation.get("message"), str) or not observation["message"]:
                issues.append(Issue("report.observation.message", "observation message is required", f"{path}/message"))
            if "instance_path" in observation and not isinstance(observation["instance_path"], str):
                issues.append(Issue("report.observation.instance_path", "instance_path must be a string", f"{path}/instance_path"))
            if "data" in observation and not isinstance(observation["data"], dict):
                issues.append(Issue("report.observation.data", "data must be an object", f"{path}/data"))
    if verdict == "pass" and isinstance(value.get("issues"), list) and value["issues"]:
        issues.append(Issue("report.pass_with_issues", "passing report cannot contain issues", "/issues"))
    if verdict in {"fail", "usage_error", "blocked"} and isinstance(value.get("issues"), list) and not value["issues"]:
        issues.append(Issue("report.non_pass_without_issues", "non-passing report must contain at least one issue", "/issues"))
    return issues


def _reject_fields(value: dict[object, object], allowed: set[str], issues: list[Issue], path: str, code: str) -> None:
    for key in value:
        if not isinstance(key, str) or key not in allowed:
            issues.append(Issue(code, f"unknown field: {key}", f"{path}/{key}"))
