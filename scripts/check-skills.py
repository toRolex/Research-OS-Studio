#!/usr/bin/env python3
"""Research OS Studio Skills 静态完整性检查（spec Testing 5）。

纯标准库；报告全部问题并以非零退出码结束。检查项：
1. skills/ 下 SKILL.md 数量与 frontmatter 基本规范（name/description）
2. name 与目录名一致、name 全局唯一
3. user/model 分类与 disable-model-invocation / agents/openai.yaml 自洽
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


def lexical_relative(base_dir: Path, target: str) -> str | None:
    """从 base_dir 按 URL 段拼接。base_dir 必须是目录，不是文件。"""
    parts = [part for part in base_dir.as_posix().split("/") if part not in ("", ".")]
    absolute = base_dir.as_posix().startswith("/")
    for part in target.replace("\\", "/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    joined = "/".join(parts)
    return f"/{joined}" if absolute else joined


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
skill_bodies: list[tuple[str, str, Path, str, bool, str | None]] = []

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
    fm_body = "\n".join(line for line in fm_lines if not line.lstrip().startswith("#"))

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
    openai_yaml = sf.parent / "agents" / "openai.yaml"
    has_openai_yaml = openai_yaml.exists()
    if user_invoked and not has_openai_yaml:
        err(f"{rel}: User-invoked 但缺 agents/openai.yaml")
    if not user_invoked and has_openai_yaml:
        err(f"{rel}: model-invoked 但存在 agents/openai.yaml")
    classifications[rel] = "U" if user_invoked else "M"
    yaml_text = openai_yaml.read_text(encoding="utf-8") if has_openai_yaml else None
    skill_text = text.split("---", 2)[-1] if text.startswith("---") else text
    skill_bodies.append((name, rel, sf.parent, skill_text, user_invoked, yaml_text))

# --- 4: markdown 相对链接 -------------------------------------------------
md_files = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]
link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


ROUTE_COLUMNS = ("路线", "变体", "触发词", "适用条件", "只读约束", "playbook")
EXPECTED_GATES: dict[str, frozenset[str]] = {"research-os": frozenset()}
LEGACY_ROUTER = "ask-research-os"
LEGACY_ALLOW_MIGRATION = (
    "breaking",
    "已删除",
    "已删",
    "迁移",
    "replaced",
    "removed",
    "deleted",
    "migration",
)
CASCADE_PREFIX = "skills/general/research-os/"
CASCADE_RE = re.compile(r"`([^`\n]+)`")
GATE_RE = re.compile(
    r"^Gate:\s*([a-z0-9-]+)\s*\|\s*before=(\S+)\s*\|\s*approval=(\S+)\s*\|\s*source=(\S+)\s*$",
    re.M,
)
HINTS: list[str] = []


def invocation_value_problems(name: str, user_invoked: bool, yaml_text: str) -> list[str]:
    if not user_invoked:
        return []
    match = re.search(r"allow_implicit_invocation:\s*(\S+)", yaml_text)
    if match is None:
        return [f"{name}: agents/openai.yaml 缺 allow_implicit_invocation: false"]
    if match.group(1).strip().strip("'\"") != "false":
        return [f"{name}: allow_implicit_invocation 必须为 false"]
    return []


def parse_route_table(text: str) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    rows: list[dict[str, str]] = []
    tables: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("|"):
            current.append(line.strip())
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    chosen: list[str] | None = None
    for table in tables:
        cells = [cell.strip() for cell in table[0].strip("|").split("|")]
        if "路线" in cells and "playbook" in cells:
            chosen = table
            break
    if chosen is None:
        return [], ["路由表缺少固定列：" + " | ".join(ROUTE_COLUMNS)]
    header = [cell.strip() for cell in chosen[0].strip("|").split("|")]
    missing = [column for column in ROUTE_COLUMNS if column not in header]
    if missing:
        errors.append("路由表缺列：" + "、".join(missing))
        return [], errors
    indexes = {column: header.index(column) for column in ROUTE_COLUMNS}
    for raw in chosen[2:]:
        cells = [cell.strip() for cell in raw.strip("|").split("|")]
        if len(cells) <= max(indexes.values()):
            errors.append(f"路由行列数不足：{raw}")
            continue
        row = {column: cells[indexes[column]] for column in ROUTE_COLUMNS}
        if not row["路线"] or set(row["路线"]) <= {"-", ":"}:
            continue
        rows.append(row)
    return rows, errors


def route_table_problems(rows: list[dict[str, str]], skill_dir: Path) -> tuple[list[str], list[str]]:
    problems_out: list[str] = []
    hints: list[str] = []
    seen: dict[tuple[str, str], int] = {}
    triggers: dict[str, str] = {}
    link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
    for index, row in enumerate(rows, 1):
        key = (row["路线"], row["变体"])
        if key in seen:
            problems_out.append(f"路由唯一键重复：{key[0]} / {key[1]}（第 {seen[key]} 与 {index} 行）")
        else:
            seen[key] = index
        for column in ("触发词", "适用条件", "只读约束", "playbook"):
            if not row[column]:
                problems_out.append(f"路由行 {key[0]}/{key[1]} 缺 {column}")
        if row["只读约束"].lower() not in {"yes", "no"}:
            problems_out.append(f"路由行 {key[0]}/{key[1]} 的只读约束必须是 yes 或 no")
        targets = link_re.findall(row["playbook"])
        if len(targets) != 1:
            problems_out.append(f"路由行 {key[0]}/{key[1]} 的 playbook 必须是一个 Markdown 链接")
            continue
        target = targets[0].split("#")[0]
        resolved = lexical_relative(skill_dir, target)
        if resolved is None or not Path(resolved).is_file():
            problems_out.append(f"路由目标不存在：{target}")
        for trigger in re.split(r"[、,，]", row["触发词"]):
            trigger = trigger.strip()
            if not trigger:
                continue
            owner = f"{key[0]}/{key[1]}"
            if trigger in triggers and triggers[trigger] != owner:
                hints.append(f"触发词重复（提示，不失败）：{trigger} 同时出现于 {triggers[trigger]} 与 {owner}")
            else:
                triggers[trigger] = owner
    return problems_out, hints


def cascade_scope(rel: str) -> bool:
    return rel.startswith(CASCADE_PREFIX)


def backtick_cascade_problems(rel: str, text: str, root: Path, tracked: set[str]) -> list[str]:
    if not cascade_scope(rel):
        return []
    found: list[str] = []
    skill_root = root / "skills/general/research-os"
    source = root / rel
    for line_no, line in enumerate(text.splitlines(), 1):
        if "上游" in line or "upstream" in line.lower() or "{" in line:
            continue
        for token in CASCADE_RE.findall(line):
            token = token.strip()
            if token.startswith((".", "~", "/")) or "/" not in token or not token.endswith(".md"):
                continue
            clean = token.split("#", 1)[0].split()[0]
            if clean.startswith(("http://", "https://")):
                continue
            raw_candidates = [source.parent]
            if not clean.startswith("skills/"):
                raw_candidates.append(skill_root)
            else:
                raw_candidates.append(root)
            resolved = None
            rel_resolved = ""
            for base in raw_candidates:
                candidate = lexical_relative(base, clean)
                root_text = root.as_posix().rstrip("/")
                if candidate is None or not candidate.startswith(root_text + "/"):
                    continue
                rel_candidate = candidate[len(root_text) + 1 :]
                if rel_candidate in tracked or Path(candidate).is_file():
                    resolved = candidate
                    rel_resolved = rel_candidate
                    break
            if resolved is None:
                found.append(f"{rel}:{line_no}: 反引号级联目标不存在或未追踪: {clean}")
            elif rel_resolved not in tracked:
                found.append(f"{rel}:{line_no}: 反引号级联目标未追踪: {clean}")
    return found


def gate_problems(name: str, skill_dir: Path, text: str, expected: frozenset[str]) -> list[str]:
    found: list[str] = []
    if re.search(r"^Gates:\s*none\s*$", text, re.M):
        if expected:
            found.append(f"{name}: 写成 Gates: none，但基线要求 {sorted(expected)}")
        return found
    matches = GATE_RE.findall(text)
    if not matches:
        found.append(f"{name}: 缺 Gates: none 或 Gate 声明")
        return found
    ids = [item[0] for item in matches]
    for gate_id in ids:
        if ids.count(gate_id) > 1:
            found.append(f"{name}: 门 ID 重复：{gate_id}")
            break
    actual = set(ids)
    for gate_id in sorted(expected - actual):
        found.append(f"{name}: 缺门声明 {gate_id}")
    for gate_id in sorted(actual - expected):
        found.append(f"{name}: 多余门声明 {gate_id}")
    for gate_id, _before, _approval, source in matches:
        if "#" not in source:
            found.append(f"{name}: 门 {gate_id} 的 source 缺锚点")
            continue
        path_part, anchor = source.split("#", 1)
        if path_part.startswith(("/", "http://", "https://")) or ".." in Path(path_part).parts:
            found.append(f"{name}: 门 {gate_id} 的 source 越出 skill：{path_part}")
            continue
        target = (skill_dir / path_part).resolve()
        try:
            target.relative_to(skill_dir.resolve())
        except ValueError:
            found.append(f"{name}: 门 {gate_id} 的 source 越出 skill：{path_part}")
            continue
        if not target.is_file():
            found.append(f"{name}: 门 {gate_id} 的 source 不存在：{path_part}")
            continue
        body = target.read_text(encoding="utf-8")
        if path_part == "SKILL.md":
            parts = body.split("---", 2)
            if body.startswith("---") and len(parts) == 3:
                body = parts[2]
        headings = re.findall(r"^#+\s+(.+?)\s*$", body, re.M)
        if anchor not in headings:
            found.append(f"{name}: 门 {gate_id} 的锚点不存在：{anchor}")
    return found


def legacy_router_problems(files: dict[str, str]) -> list[str]:
    found: list[str] = []
    for rel, text in files.items():
        if LEGACY_ROUTER not in text:
            continue
        if any(token in text.lower() or token in text for token in LEGACY_ALLOW_MIGRATION):
            continue
        found.append(f"{rel}: 产品正文残留旧 router {LEGACY_ROUTER}")
    return found


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
            resolved = lexical_relative(md.parent, clean)
            root_text = ROOT.as_posix().rstrip("/")
            if resolved is None or not resolved.startswith(root_text + "/"):
                err(f"{rel_md}:{i}: 链接越出仓库: {target}")
                continue
            rel_resolved = resolved[len(root_text) + 1 :]
            inside_skill = rel_md.startswith("skills/") and rel_md.count("/") >= 3
            if inside_skill and not rel_resolved.startswith("skills/"):
                err(f"{rel_md}:{i}: 链接越出 skills/: {target}")
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

# --- 6–9: 入口合同（路由、级联、门、旧 router） ---------------------------
for skill_name, rel, skill_dir, skill_text, user_invoked, yaml_text in skill_bodies:
    if yaml_text is not None:
        for problem in invocation_value_problems(skill_name, user_invoked, yaml_text):
            err(f"{rel}: {problem}")
    if skill_name not in EXPECTED_GATES:
        continue
    for problem in gate_problems(skill_name, skill_dir, skill_text, EXPECTED_GATES[skill_name]):
        err(f"{rel}: {problem}")

research_os = SKILLS / "general" / "research-os" / "SKILL.md"
if research_os.exists():
    route_rows, route_errors = parse_route_table(research_os.read_text(encoding="utf-8"))
    for problem in route_errors:
        err(f"skills/general/research-os/SKILL.md: {problem}")
    route_problems, route_hints = route_table_problems(route_rows, research_os.parent)
    for problem in route_problems:
        err(f"skills/general/research-os/SKILL.md: {problem}")
    HINTS.extend(route_hints)

for md in md_files:
    rel_md = md.relative_to(ROOT).as_posix()
    if rel_md not in tracked or not cascade_scope(rel_md):
        continue
    for problem in backtick_cascade_problems(rel_md, md.read_text(encoding="utf-8"), ROOT, tracked):
        err(problem)

legacy_files = {
    rel: (ROOT / rel).read_text(encoding="utf-8")
    for rel in (
        "README.md",
        "docs/README-en.md",
        "skills/README.md",
        "docs/user-acceptance-guide.md",
        "docs/assets/workflow-diagrams.md",
    )
    if (ROOT / rel).exists()
}
for problem in legacy_router_problems(legacy_files):
    err(problem)


def main() -> None:
    if problems:
        print(f"FAIL: {len(problems)} 个问题")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    u_count = sum(1 for v in classifications.values() if v == "U")
    m_count = sum(1 for v in classifications.values() if v == "M")
    print(f"OK: {len(skill_files)} 个 Skill（U {u_count} / M {m_count}），全部检查通过")


if __name__ == "__main__":
    main()
