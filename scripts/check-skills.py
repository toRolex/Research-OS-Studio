#!/usr/bin/env python3
"""Research OS Studio Skills 静态完整性检查。

纯标准库；报告全部问题并以非零退出码结束。检查项：
1. skills/ 下 SKILL.md 数量与 frontmatter 基本规范（name/description）
2. name 与目录名一致、name 全局唯一
3. 调用策略：除 setup-research-os 外必须显式调用，且 openai.yaml 的 allow_implicit_invocation 值为 false
3b. 叶 skill 门声明与经审阅基线一致（缺、多、重复、格式、来源、none）
4. 全部 markdown 相对链接指向 git 追踪内存在的文件（豁免占位符与已知 brace 行文）
5. README.md 与 skills/README.md 的 Skill 清单与目录树一致
6. 角色表、算力政策、研究日志字段与门声明基线
"""
import argparse
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
EXPECTED_COUNT = 39
ROLES = (
    "orchestrator",
    "literature",
    "ideator",
    "implementer",
    "analyst",
    "prover",
    "writer",
    "reviewer",
)
THINKING = {"off", "minimal", "low", "medium", "high", "xhigh", "max"}
COMPUTE_UNITS = {"cpu-core-hour", "gpu-device-hour"}
RUN_BASES = {"planned-run", "attempt"}
POLICY_KEYS = (
    "scope",
    "cost_limit",
    "currency",
    "compute_limit",
    "compute_unit",
    "run_limit",
    "run_count_basis",
    "per_attempt_cost_limit",
    "per_attempt_compute_limit",
    "concurrency_limit",
    "retry_limit",
    "valid_for_hours",
    "valid_until",
)
LOG_EXTRAS = (
    "batch_id",
    "plan",
    "mode",
    "user_confirmation",
    "confirmed_at",
    "confirmation_basis",
    "authorization_status",
    "run_id",
    "attempt_id",
    "worst_case_estimate",
    "started_at",
    "finished_at",
    "actual_consumption",
    "result_status",
    "artifact_paths",
)
# 本票只登记 setup。其他 skill 尚未写出门声明时不要求；写出后必须落在此处。
GATE_BASELINE = {
    "setup-research-os": {"model-confirm", "write-confirm"},
}
GATE_RE = re.compile(
    r"^Gate:\s*([A-Za-z0-9-]+)\s*\|\s*before=([A-Za-z0-9-]+)\s*\|\s*"
    r"approval=([A-Za-z0-9-]+)\s*\|\s*source=(\S+)\s*$"
)
GATES_NONE_RE = re.compile(r"^Gates:\s*none\s*$")
ROLE_LINE_RE = re.compile(r"^([a-z]+):\s*(\S+)\s*\|\s*([A-Za-z0-9]+)\s*$")
ROLE_REF_RE = re.compile(r"Role:\s*([A-Za-z0-9_-]+)")
FIELD_RE = re.compile(r"^-\s*([a-z_]+):\s*(.*?)\s*$")
ANCHOR_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")

# 已知豁免：上游路径描述的 brace 展开行文（systems-paper-writing 来源段），
# 行内已注明"上游仓库路径"，本仓不持有这些文件。
LINK_EXEMPT_SNIPPETS = ("references/{", "writing-systems-papers")

problems: list[str] = []


def err(msg: str) -> None:
    problems.append(msg)


def git_tracked() -> set[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True
    ).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


tracked: set[str] = set()
skill_files: list[Path] = []
names: dict[str, str] = {}
classifications: dict[str, str] = {}
SETUP_NAME = "setup-research-os"
EXPLICIT_EXCEPTIONS = {SETUP_NAME}


def frontmatter_body(fm: str) -> str:
    return "\n".join(line for line in fm.splitlines() if not line.lstrip().startswith("#"))


def yaml_implicit_value(yaml_path: Path) -> str | None:
    if not yaml_path.exists():
        return None
    match = re.search(
        r"^\s*allow_implicit_invocation\s*:\s*(\S+)\s*$",
        yaml_path.read_text(encoding="utf-8"),
        re.M,
    )
    return match.group(1).strip().strip("'\"") if match else None


def run_suite() -> None:
    global tracked, skill_files
    tracked = git_tracked()
    skill_files = sorted(SKILLS.glob("*/*/SKILL.md"))
    if len(skill_files) != EXPECTED_COUNT:
        err(f"skills/ 下 SKILL.md 数量为 {len(skill_files)}，期望 {EXPECTED_COUNT}")
    collect_frontmatter()
    check_links()
    check_readmes()


def collect_frontmatter() -> None:
    for sf in skill_files:
        rel = sf.relative_to(ROOT).as_posix()
        dir_name = sf.parent.name
        text = sf.read_text(encoding="utf-8")
        if not text.startswith("---"):
            err(f"{rel}: 缺少 YAML frontmatter")
            continue
        try:
            fm = text.split("---", 2)[1]
        except IndexError:
            err(f"{rel}: frontmatter 未闭合")
            continue
        fm_lines = fm.splitlines()
        fm_body = "\n".join(
            line for line in fm_lines if not line.lstrip().startswith("#")
        )

        m = re.search(r"^name:\s*(.+?)\s*$", fm_body, re.M)
        if not m:
            err(f"{rel}: frontmatter 缺 name")
            continue
        name = m.group(1).strip().strip('"').strip("'")
        if name != dir_name:
            err(f"{rel}: name '{name}' 与目录名 '{dir_name}' 不一致")
        if name in names:
            err(f"{rel}: name '{name}' 重复（另见 {names[name]}）")
        names[name] = rel

        if not re.search(r"^description:\s*\S", fm_body, re.M):
            err(f"{rel}: frontmatter 缺 description 或为空")

        user_invoked = "disable-model-invocation: true" in fm_body
        yaml_path = sf.parent / "agents" / "openai.yaml"
        has_openai_yaml = yaml_path.exists()
        if name == "setup-research-os":
            if user_invoked:
                err(f"{rel}: setup-research-os 必须允许模型建议，不能禁用 model invocation")
            if not has_openai_yaml:
                err(f"{rel}: setup-research-os 缺 agents/openai.yaml")
            elif "allow_implicit_invocation: true" not in yaml_path.read_text(encoding="utf-8"):
                err(f"{rel}: setup-research-os 的 allow_implicit_invocation 必须为 true")
        else:
            implicit = yaml_implicit_value(yaml_path)
            if not user_invoked:
                err(f"{rel}: 除 setup 外必须 disable-model-invocation: true")
            if implicit != "false":
                err(f"{rel}: allow_implicit_invocation 必须为 false，实际 {implicit!r}")
        classifications[rel] = "U" if user_invoked else "M"


def check_links() -> None:
    md_files = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]
    link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


    def is_exempt(target: str, line: str) -> bool:
        if re.fullmatch(r"\{[^}]*\}", target):
            return True
        for snip in LINK_EXEMPT_SNIPPETS:
            if snip in line and ("上游" in line or "upstream" in line.lower()):
                return True
        return False


    for md in md_files:
        rel_md = md.relative_to(ROOT).as_posix()
        if rel_md not in tracked:
            continue
        for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for target in link_re.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if re.fullmatch(r"\{[^}]*\}|<[^>]*>", target):
                    continue
                if is_exempt(target, line):
                    continue
                clean = target.split("#")[0]
                if not clean:
                    continue
                resolved = (md.parent / clean).resolve()
                try:
                    rel_resolved = resolved.relative_to(ROOT.resolve()).as_posix()
                except ValueError:
                    err(f"{rel_md}:{i}: 链接越出仓库: {target}")
                    continue
                if not (ROOT / rel_resolved).is_file():
                    err(f"{rel_md}:{i}: 链接目标不存在: {target}")


def check_readmes() -> None:
    actual = {f"{sf.parent.parent.name}/{sf.parent.name}" for sf in skill_files}
    for readme_name in ("README.md", "skills/README.md"):
        rp = ROOT / readme_name
        if not rp.exists():
            err(f"{readme_name}: 不存在")
            continue
        listed = set(re.findall(r"\]\((?:skills/)?([a-z-]+/[a-z0-9-]+)/SKILL\.md\)", rp.read_text(encoding="utf-8")))
        if listed != actual:
            missing = sorted(actual - listed)
            extra = sorted(listed - actual)
            if missing:
                err(f"{readme_name}: 清单缺 {len(missing)} 个 Skill: {', '.join(missing)}")
            if extra:
                err(f"{readme_name}: 清单含不存在 Skill: {', '.join(extra)}")


def parse_fields(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for line in text.splitlines():
        match = FIELD_RE.match(line.strip())
        if match:
            found.setdefault(match.group(1), []).append(match.group(2).strip())
    return found


def finite_number(raw: str) -> float | None:
    try:
        value = float(raw)
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    return value


def check_role_file(path: Path, label: str) -> set[str]:
    seen: set[str] = set()
    if not path.is_file():
        err(f"{label}: 角色表不存在")
        return seen
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = ROLE_LINE_RE.match(stripped)
        if not match:
            err(f"{label}:{lineno}: 角色行格式必须是 `角色: provider/model-id | thinking`")
            continue
        role, model, thinking = match.groups()
        if role not in ROLES:
            err(f"{label}:{lineno}: 未知角色 {role}")
        if role in seen:
            err(f"{label}:{lineno}: 角色 {role} 重复")
        seen.add(role)
        if "/" not in model or model.startswith("/") or model.endswith("/"):
            err(f"{label}:{lineno}: 模型必须是 provider/model-id")
        if thinking not in THINKING:
            err(f"{label}:{lineno}: thinking `{thinking}` 不在允许档位")
    missing = [role for role in ROLES if role not in seen]
    if missing:
        err(f"{label}: 角色表缺 {', '.join(missing)}")
    return seen


def check_role_refs(paths: list[Path], roles: set[str]) -> None:
    allowed = roles or set(ROLES)
    for path in paths:
        if not path.is_file():
            err(f"{path}: 角色引用文件不存在")
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for role in ROLE_REF_RE.findall(line):
                if role not in allowed:
                    err(f"{path}:{lineno}: 角色引用未闭合: {role}")


def check_policy(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        err(f"{path}: 政策文件不存在")
        return {}
    text = path.read_text(encoding="utf-8")
    fields = parse_fields(text)
    for key in POLICY_KEYS:
        if key not in fields:
            err(f"{path}: 政策缺字段 {key}")
    for key, values in fields.items():
        if key not in POLICY_KEYS:
            err(f"{path}: 政策含未知字段 {key}")
        for raw in values:
            if raw.lower() in {"unlimited", "nan", "inf", "+inf", "-inf"}:
                err(f"{path}: 非法额度值 {key}={raw}")
    numbers: dict[str, list[float]] = {}
    for key in (
        "cost_limit",
        "compute_limit",
        "per_attempt_cost_limit",
        "per_attempt_compute_limit",
        "valid_for_hours",
    ):
        for raw in fields.get(key, []):
            value = finite_number(raw)
            if value is None or value < 0:
                err(f"{path}: {key} 必须是有限非负数，实际 {raw}")
            else:
                numbers.setdefault(key, []).append(value)
    for key in ("run_limit", "concurrency_limit", "retry_limit"):
        for raw in fields.get(key, []):
            value = finite_number(raw)
            if value is None or value < 0 or not value.is_integer():
                err(f"{path}: {key} 必须是非负整数，实际 {raw}")
    for raw in fields.get("compute_unit", []):
        if raw not in COMPUTE_UNITS:
            err(f"{path}: 无单位或未知算力单位 {raw}")
    if len(fields.get("compute_limit", [])) != len(fields.get("compute_unit", [])):
        err(f"{path}: compute_limit 与 compute_unit 必须逐行配对")
    for raw in fields.get("run_count_basis", []):
        if raw not in RUN_BASES:
            err(f"{path}: run_count_basis 只能是 planned-run 或 attempt")
    for key in ("currency", "scope", "valid_until"):
        for raw in fields.get(key, []):
            if raw == "not-applicable" and "因为" not in text and "because" not in text.lower():
                err(f"{path}: {key}=not-applicable 必须解释")
    costs = numbers.get("cost_limit", [])
    per_costs = numbers.get("per_attempt_cost_limit", [])
    if costs and per_costs and max(per_costs) > min(costs):
        err(f"{path}: 单次超过累计上限")
    computes = numbers.get("compute_limit", [])
    per_computes = numbers.get("per_attempt_compute_limit", [])
    if computes and per_computes and sum(per_computes) > sum(computes) and len(computes) == len(per_computes):
        for index, (limit, per_attempt) in enumerate(zip(computes, per_computes, strict=True)):
            if per_attempt > limit:
                err(f"{path}: 第 {index + 1} 行单次超过累计上限")
    return fields


def check_log(path: Path, policy_fields: dict[str, list[str]]) -> None:
    if not path.is_file():
        err(f"{path}: 日志文件不存在")
        return
    fields = parse_fields(path.read_text(encoding="utf-8"))
    for key in POLICY_KEYS + LOG_EXTRAS:
        if key not in fields:
            err(f"{path}: 日志缺字段 {key}")
    if policy_fields:
        for key in POLICY_KEYS:
            if key not in fields:
                err(f"{path}: 日志未复用政策字段 {key}")


def anchors_in(path: Path) -> set[str]:
    found = set()
    if not path.is_file():
        return found
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ANCHOR_RE.match(line.strip())
        if match:
            found.add(match.group(1).replace(" ", "-"))
    return found


def check_gates(skill_dir: Path, skill_name: str) -> None:
    expected = GATE_BASELINE.get(skill_name)
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        err(f"{skill_name}: SKILL.md 不存在")
        return
    found: list[str] = []
    none_lines = 0
    for lineno, line in enumerate(skill_file.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if GATES_NONE_RE.match(stripped):
            none_lines += 1
            continue
        match = GATE_RE.match(stripped)
        if stripped.startswith(("Gate:", "Gates:")) and match is None and none_lines == 0:
            err(f"{skill_name}:{lineno}: 门声明格式错误")
            continue
        if not match:
            continue
        gate_id, _before, approval, source = match.groups()
        if approval != "explicit-user":
            err(f"{skill_name}:{lineno}: approval 必须是 explicit-user")
        if not source.startswith("SKILL.md#") and not source.startswith("references/"):
            err(f"{skill_name}:{lineno}: source 越出当前 skill")
        source_path, _, anchor = source.partition("#")
        target = skill_dir / source_path
        if anchor not in anchors_in(target):
            err(f"{skill_name}:{lineno}: 坏 source {source}")
        found.append(gate_id)
    duplicates = sorted({gate for gate in found if found.count(gate) > 1})
    if duplicates:
        err(f"{skill_name}: 重复门 {', '.join(duplicates)}")
    if none_lines and found:
        err(f"{skill_name}: none 与具体门不能并存")
    if expected is None:
        if found or none_lines:
            err(f"{skill_name}: 门声明不在已审阅基线")
        return
    actual = set(found)
    if none_lines:
        actual = set()
        if expected:
            err(f"{skill_name}: 全部→none，基线要求 {', '.join(sorted(expected))}")
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        err(f"{skill_name}: 缺失门 {', '.join(missing)}")
    if extra:
        err(f"{skill_name}: 多余门 {', '.join(extra)}")
    if not found and not none_lines and expected:
        err(f"{skill_name}: 整节删，基线要求 {', '.join(sorted(expected))}")


def run_contract(args: argparse.Namespace) -> None:
    roles: set[str] = set()
    if args.role_file:
        roles = check_role_file(Path(args.role_file), args.role_file)
    if args.role_template:
        check_role_file(Path(args.role_template), args.role_template)
    if args.role_refs:
        check_role_refs([Path(item) for item in args.role_refs], roles)
    policy_fields: dict[str, list[str]] = {}
    if args.policy_file:
        policy_fields = check_policy(Path(args.policy_file))
    if args.log_file:
        check_log(Path(args.log_file), policy_fields)
    if args.gates_dir:
        if not args.skill_name:
            err("门检查需要 --skill-name")
        else:
            check_gates(Path(args.gates_dir), args.skill_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research OS skill 与配置合同检查")
    parser.add_argument("--role-file")
    parser.add_argument("--role-template")
    parser.add_argument("--role-refs", nargs="*")
    parser.add_argument("--policy-file")
    parser.add_argument("--log-file")
    parser.add_argument("--gates-dir")
    parser.add_argument("--skill-name")
    parser.add_argument(
        "--skip-suite",
        action="store_true",
        help="只检查显式给出的角色、政策、日志或门，不扫描仓库 skills/",
    )
    return parser.parse_args()



def check_leaf_gates() -> None:
    """核对 #39 已审阅叶 skill 的门声明。setup 另由 check_gates 核对。"""
    EXPECTED_GATES: dict[str, set[str]] = {
        "skills/idea-cycle/creative-thinking-for-research/SKILL.md": {"write-path"},
        "skills/idea-cycle/idea-discovery/SKILL.md": {"stage-checkpoint", "output-path"},
        "skills/idea-cycle/idea-generation/SKILL.md": {"write-path"},
        "skills/idea-cycle/idea-refinement/SKILL.md": {"anchor-clarify"},
        "skills/idea-cycle/idea-review/SKILL.md": {"scope-clarify"},
        "skills/idea-cycle/novelty-check/SKILL.md": set(),
        "skills/idea-cycle/research-lit/SKILL.md": {"write-path"},
        "skills/validation-cycle/analyze-results/SKILL.md": {"write-path"},
        "skills/validation-cycle/experiment-audit/SKILL.md": {"write-path"},
        "skills/validation-cycle/experiment-bridge/SKILL.md": {"run-authorization"},
        "skills/validation-cycle/experiment-plan/SKILL.md": {"output-path"},
        "skills/validation-cycle/experiment-queue/SKILL.md": {"batch-authorization", "precondition-block"},
        "skills/validation-cycle/formula-derivation/SKILL.md": {"write-authorization"},
        "skills/validation-cycle/monitor-experiment/SKILL.md": {"write-path"},
        "skills/validation-cycle/proof-orchestrator/SKILL.md": {"round-scope", "external-action"},
        "skills/validation-cycle/proof-repair/SKILL.md": {
            "repair-contract",
            "assumption-or-claim-change",
            "compile-authorization",
        },
        "skills/validation-cycle/proof-review/SKILL.md": set(),
        "skills/validation-cycle/proof-writer/SKILL.md": {"write-authorization"},
        "skills/validation-cycle/result-to-claim/SKILL.md": {"write-path"},
        "skills/validation-cycle/run-experiment/SKILL.md": {"run-authorization", "milestone-start"},
        "skills/validation-cycle/training-health-check/SKILL.md": {"write-path"},
        "skills/writing-cycle/academic-plotting/SKILL.md": {"figure-choice", "external-resource"},
        "skills/writing-cycle/apply-citation-fixes/SKILL.md": {"apply-authorization"},
        "skills/writing-cycle/citation-audit/SKILL.md": {"audit-scope"},
        "skills/writing-cycle/claim-stress-test/SKILL.md": {"report-target"},
        "skills/writing-cycle/ml-paper-writing/SKILL.md": {"workflow-authorization"},
        "skills/writing-cycle/paper-claim-audit/SKILL.md": {"report-target"},
        "skills/writing-cycle/paper-compile-repair/SKILL.md": {"repair-scope", "round-diff"},
        "skills/writing-cycle/paper-compile/SKILL.md": {"build-scope"},
        "skills/writing-cycle/paper-drafting/SKILL.md": {"boundary-confirm", "venue-conflict"},
        "skills/writing-cycle/paper-plan/SKILL.md": {"write-authorization", "framing-confirm"},
        "skills/writing-cycle/paper-talk/SKILL.md": {"talk-authorization", "outline-confirm"},
        "skills/writing-cycle/paper-writing/SKILL.md": {"workflow-authorization"},
        "skills/writing-cycle/rebuttal/SKILL.md": {"strategy-confirm", "wording-confirm"},
        "skills/writing-cycle/research-improvement/SKILL.md": {"loop-authorization", "experiment-topup"},
        "skills/writing-cycle/resubmit-pipeline/SKILL.md": {"adaptation-scope", "change-confirm"},
        "skills/writing-cycle/systems-paper-writing/SKILL.md": {"workflow-authorization"},
    }
    GATE_SKIP = {
        "skills/general/setup-research-os/SKILL.md",
        "skills/general/ask-research-os/SKILL.md",
    }
    GATE_LINE = re.compile(
        r"^Gate: ([a-z0-9-]+) \| before=([a-z0-9-]+) \| approval=explicit-user \| source=((?:SKILL\.md|references/[A-Za-z0-9_./-]+\.md)#(\S+))$"
    )


    def heading_anchors(text: str) -> set[str]:
        found: set[str] = set()
        for line in text.splitlines():
            match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
            if not match:
                continue
            title = match.group(1).strip()
            found.add(title)
            slug = re.sub(r"[^\w\u4e00-\u9fff\- ]+", "", title.lower())
            slug = re.sub(r"\s+", "-", slug).strip("-")
            found.add(slug)
        return found


    for sf in skill_files:
        rel = sf.relative_to(ROOT).as_posix()
        if rel not in EXPECTED_GATES:
            if rel not in GATE_SKIP:
                err(f"{rel}: 缺少门声明基线")
            continue
        body = sf.read_text(encoding="utf-8").split("---", 2)[-1]
        expected = EXPECTED_GATES[rel]
        none_count = 0
        seen: list[str] = []
        for lineno, line in enumerate(body.splitlines(), 1):
            stripped = line.strip()
            if stripped == "Gates: none":
                none_count += 1
                continue
            if not stripped.startswith("Gate:") and not stripped.startswith("Gates:"):
                continue
            match = GATE_LINE.match(stripped)
            if not match:
                err(f"{rel}:{lineno}: 门声明格式错误: {stripped}")
                continue
            gate_id, source_path, fragment = match.group(1), match.group(3).split("#", 1)[0], match.group(4)
            target = (sf.parent / source_path).resolve()
            try:
                rel_target = target.relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                err(f"{rel}:{lineno}: 门声明来源越出仓库: {stripped}")
                continue
            if not target.is_file():
                err(f"{rel}:{lineno}: 门声明来源不存在: {source_path}")
                continue
            if fragment not in heading_anchors(target.read_text(encoding="utf-8")):
                err(f"{rel}:{lineno}: 门声明锚点无效: {stripped}")
                continue
            seen.append(gate_id)
        if none_count > 1:
            err(f"{rel}: Gates: none 重复")
        if none_count and seen:
            err(f"{rel}: Gates: none 与 Gate 行不能并存")
        duplicates = sorted({gate_id for gate_id in seen if seen.count(gate_id) > 1})
        if duplicates:
            err(f"{rel}: 门声明重复: {', '.join(duplicates)}")
        if expected == set():
            if none_count != 1 or seen:
                err(f"{rel}: 基线为 none，实际 Gate={seen} none={none_count}")
        elif set(seen) != expected or none_count:
            err(f"{rel}: 门声明与基线不一致，期望 {sorted(expected)}，实际 {seen}")


def run_builtin_contract() -> None:
    setup_dir = SKILLS / "general" / "setup-research-os"
    check_role_file(
        setup_dir / "templates" / "research-os-models.md", "research-os-models.md"
    )
    check_policy(setup_dir / "templates" / "compute-policy.md")
    check_log(setup_dir / "templates" / "research-log.md", {})
    check_gates(SKILLS / "general" / "setup-research-os", "setup-research-os")
    check_leaf_gates()


def main() -> int:
    args = parse_args()
    if args.skip_suite:
        run_contract(args)
    else:
        run_suite()
        run_builtin_contract()
        run_contract(args)
    if problems:
        print(f"FAIL: {len(problems)} 个问题")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    u_count = sum(1 for value in classifications.values() if value == "U")
    m_count = sum(1 for value in classifications.values() if value == "M")
    print(f"OK: {len(skill_files)} 个 Skill（U {u_count} / M {m_count}），全部检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
