#!/usr/bin/env python3
"""Research OS Studio Skills 静态完整性检查（spec Testing 5）。

纯标准库；报告全部问题并以非零退出码结束。检查项：
1. skills/ 下 SKILL.md 数量与 frontmatter 基本规范（name/description）
2. name 与目录名一致、name 全局唯一
3. 调用策略：除 setup-research-os 外必须显式调用，且 openai.yaml 的 allow_implicit_invocation 值为 false
3b. 叶 skill 门声明与经审阅基线一致（缺、多、重复、格式、来源、none）
4. 全部 markdown 相对链接指向 git 追踪内存在的文件（豁免占位符与已知 brace 行文）
5. README.md 与 skills/README.md 的 Skill 清单与目录树一致
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
EXPECTED_COUNT = 39

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


tracked = git_tracked()

# --- 1/2: 收集 skill 目录与 frontmatter -----------------------------------
skill_files = sorted(SKILLS.glob("*/*/SKILL.md"))
if len(skill_files) != EXPECTED_COUNT:
    err(f"skills/ 下 SKILL.md 数量为 {len(skill_files)}，期望 {EXPECTED_COUNT}")

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
    fm_body = frontmatter_body(fm)

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

    explicit = "disable-model-invocation: true" in fm_body
    yaml_path = sf.parent / "agents" / "openai.yaml"
    implicit = yaml_implicit_value(yaml_path)
    if name not in EXPLICIT_EXCEPTIONS:
        if not explicit:
            err(f"{rel}: 调用策略缺失或值错误，除 setup 外必须 disable-model-invocation: true")
        if implicit != "false":
            err(f"{rel}: allow_implicit_invocation 必须为 false，实际 {implicit!r}")
    else:
        if explicit and implicit != "false":
            err(f"{rel}: setup 若已显式调用，allow_implicit_invocation 必须为 false，实际 {implicit!r}")
        if implicit == "false" and not explicit:
            err(f"{rel}: setup 的 openai.yaml 为 false 但 frontmatter 不是显式调用")
    classifications[rel] = "U" if explicit else "M"

# --- 4: markdown 相对链接 -------------------------------------------------
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
            if rel_resolved not in tracked:
                err(f"{rel_md}:{i}: 链接目标不存在或未追踪: {target}")

# --- 5: README 清单与目录树一致 -------------------------------------------
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

# --- 门声明：叶 skill 基线（setup / ask-research-os / 未来入口另票并入） ----
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
        if rel_target not in tracked or not target.is_file():
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

# --- 结果 -------------------------------------------------------------------
if problems:
    print(f"FAIL: {len(problems)} 个问题")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)

u_count = sum(1 for v in classifications.values() if v == "U")
m_count = sum(1 for v in classifications.values() if v == "M")
print(
    f"OK: {len(skill_files)} 个 Skill（U {u_count} / M {m_count}），调用策略与门声明通过"
)
