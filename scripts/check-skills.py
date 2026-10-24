#!/usr/bin/env python3
"""Research OS Studio Skills 静态完整性检查。

纯标准库；报告全部问题并以非零退出码结束。检查项：
1. skills/ 下 SKILL.md 数量与 frontmatter 基本规范（name/description）
2. name 与目录名一致、name 全局唯一
3. 调用策略：除 setup-research-os 外必须显式调用，且 openai.yaml 的 allow_implicit_invocation 值为 false
3b. 叶 skill 门声明与经审阅基线一致；入口 research-os 用 Gates: none；setup 门由同一脚本的角色/政策合同核对
4. 全部 markdown 相对链接指向 git 追踪内存在的文件（豁免占位符与已知 brace 行文）
5. README.md 与 skills/README.md 的 Skill 清单与目录树一致
6. 角色表、算力政策、研究日志字段；--skip-suite 只查显式给出的合同文件

范围：静态结构、可解析声明与少量明确肯定的违约指令。任意自然语言中的隐式依赖、
阶段顺序和额度语义仍须人工核验；结构通过不等于模型行为或全部语义已经认证。
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
SETUP_NAME = "setup-research-os"
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
# setup、入口、叶基线分别登记；全部复用 gate_problems。
GATE_BASELINE = {
    "setup-research-os": {"model-confirm", "write-confirm"},
}
GATES_NONE_RE = re.compile(r"^Gates:\s*none\s*$")
ROLE_LINE_RE = re.compile(r"^([a-z]+):\s*(\S+)\s*\|\s*([A-Za-z0-9]+)\s*$")
ROLE_REF_RE = re.compile(r"Role:\s*([A-Za-z0-9_-]+)")
FIELD_RE = re.compile(r"^-\s*([a-z_]+):\s*(.*?)\s*$")

# 已知豁免：上游路径描述的 brace 展开行文（systems-paper-writing 来源段），
# 行内已注明"上游仓库路径"，本仓不持有这些文件。

LINK_EXEMPT_SNIPPETS = ("references/{", "writing-systems-papers")

problems: list[str] = []


def err(msg: str) -> None:
    problems.append(msg)


def declaration_values(text: str, key: str) -> list[str]:
    """读取整行 YAML 声明，而不是值、注释或其他键内的子串。"""
    return [value.strip().strip("'\"") for value in re.findall(
        rf"^\s*{re.escape(key)}\s*:\s*([^\n#]*)(?:#[^\n]*)?$", text, re.M
    )]


def duplicate_yaml_problems(text: str) -> list[str]:
    """限定发行 YAML 的映射键检查；同层/同父键重复即拒绝。"""
    found: list[str] = []
    parents: list[tuple[int, str]] = []
    seen: set[tuple[tuple[str, ...], str]] = set()
    critical = {"name", "description", "disable-model-invocation", "allow_implicit_invocation"}
    critical_seen: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^( *)([A-Za-z_][\w-]*):(?:\s|$)", line)
        if not match:
            continue
        indent, key = len(match.group(1)), match.group(2)
        while parents and parents[-1][0] >= indent:
            parents.pop()
        identity = (tuple(parent[1] for parent in parents), key)
        if identity in seen or (key in critical and key in critical_seen):
            found.append(f"YAML 重复声明 {key}")
        seen.add(identity)
        if key in critical:
            critical_seen.add(key)
        parents.append((indent, key))
    return found


def yaml_allow_implicit(yaml_text: str | None) -> str | None:
    values = declaration_values(yaml_text or "", "allow_implicit_invocation")
    return values[0] if len(values) == 1 else None


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
# 不写死总数：实际发现的目录必须与两份 README 清单一致（第 5 节），且每个 skill 目录
# 都要有正文。新增或迁移 Skill 只同步清单与门基线，不需要改常数。
skill_files = sorted(SKILLS.glob("*/*/SKILL.md"))
for skill_dir in sorted(SKILLS.glob("*/*")):
    if skill_dir.is_dir() and not (skill_dir / "SKILL.md").is_file():
        err(f"{skill_dir.relative_to(ROOT)}: skill 目录缺 SKILL.md")

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

    for problem in duplicate_yaml_problems(fm_body):
        err(f"{rel}: {problem}")
    invocation_values = declaration_values(fm_body, "disable-model-invocation")
    explicit = invocation_values == ["true"]
    openai_yaml = sf.parent / "agents" / "openai.yaml"
    has_openai_yaml = openai_yaml.exists()
    yaml_text = openai_yaml.read_text(encoding="utf-8") if has_openai_yaml else None
    implicit = yaml_allow_implicit(yaml_text)
    for problem in duplicate_yaml_problems(yaml_text or ""):
        err(f"{openai_yaml.relative_to(ROOT)}: {problem}")
    if name == SETUP_NAME:
        # #40：唯一允许模型建议。不得保留 disable-model-invocation，yaml 必须为 true。
        if explicit:
            err(f"{rel}: setup-research-os 必须允许模型建议，不能禁用 model invocation")
        if not has_openai_yaml:
            err(f"{rel}: setup-research-os 缺 agents/openai.yaml")
        elif implicit != "true":
            err(f"{rel}: setup-research-os 的 allow_implicit_invocation 必须为 true，实际 {implicit!r}")
    else:
        if not explicit:
            err(f"{rel}: 调用策略缺失或值错误，除 setup 外必须 disable-model-invocation: true")
        if not has_openai_yaml:
            err(f"{rel}: User-invoked 但缺 agents/openai.yaml")
        elif implicit != "false":
            err(f"{rel}: allow_implicit_invocation 必须为 false，实际 {implicit!r}")
    classifications[rel] = "U" if explicit else "M"
    skill_text = text.split("---", 2)[-1] if text.startswith("---") else text
    skill_bodies.append((name, rel, sf.parent, skill_text, explicit, yaml_text))

# --- 4: markdown 相对链接 -------------------------------------------------
def tracked_markdown_files() -> list[Path]:
    """只访问 tracked Markdown 的祖先目录，保留目录枚举与栈遍历顺序。"""
    candidates = {ROOT / rel for rel in tracked
                  if rel.endswith(".md") and ".git" not in Path(rel).parts}
    parents = {ROOT / parent for path in candidates
               for parent in path.relative_to(ROOT).parents}
    found: list[Path] = []
    pending = [ROOT]
    while pending:
        directory = pending.pop()
        try:
            entries = list(directory.iterdir())
        except OSError:
            continue  # 与 rglob 一样跳过不可读／已消失的目录。
        found.extend(path for path in entries if path in candidates)
        pending.extend(path for path in entries
                       if path in parents and path.is_dir() and not path.is_symlink())
    return found


md_files = tracked_markdown_files()
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
    if yaml_allow_implicit(yaml_text) != "false":
        return [f"{name}: allow_implicit_invocation 必须唯一且为 false"]
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


PAPER_WRITING_VARIANTS = ("general", "ml", "systems")
PAPER_WRITING_REQUIRED = (
    "skills/writing-cycle/paper-writing/SKILL.md",
    "skills/writing-cycle/paper-writing/references/composition-map.md",
    "skills/writing-cycle/paper-writing/references/standards.md",
)
PAPER_WRITING_DOMAIN_RESOURCES = {
    "ml": (
        "ml-ai-standards.md",
        "ml-experiment-reporting.md",
        "ml-reviewer-expectations.md",
        "ml-venue-checklists.md",
        "../templates/ml-writing-report.md",
    ),
    "systems": (
        "systems-standards.md",
        "systems-writing-methods.md",
        "systems-evaluation-methods.md",
        "systems-checklist.md",
        "systems-venue-and-reviewer.md",
        "../templates/systems-paper-writing-report.md",
    ),
}
PAPER_WRITING_SOURCE_LICENSES = {
    "ml": ("LICENSE-ML.txt",),
    "systems": ("LICENSE-ARIS.txt", "LICENSE-Orchestra.txt"),
}


def paper_writing_domain_standard_problems(variant: str, root: Path) -> list[str]:
    """专业标准必须从统一 Skill 的安装包内真实可达。"""
    resources = PAPER_WRITING_DOMAIN_RESOURCES.get(variant)
    if resources is None:
        return []
    standards = root / "skills/writing-cycle/paper-writing/references/standards.md"
    if not standards.is_file():
        return []

    text = standards.read_text(encoding="utf-8")
    links = {
        target.split("#", 1)[0]
        for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)", text)
        if not target.startswith(("http:", "https:", "mailto:"))
    }
    found: list[str] = []
    for resource in resources:
        if resource not in links:
            found.append(f"paper-writing/{variant} standards.md 缺专业资源链接：{resource}")
            continue
        target = (standards.parent / resource).resolve()
        package = (root / "skills/writing-cycle/paper-writing").resolve()
        if package not in target.parents or not target.is_file():
            found.append(f"paper-writing/{variant} 专业资源不可达：{resource}")

    sources = standards.parent / "sources.md"
    source_text = sources.read_text(encoding="utf-8") if sources.is_file() else ""
    if "sources.md" not in links:
        found.append(f"paper-writing/{variant} standards.md 缺来源许可记录链接：sources.md")
    for license_name in PAPER_WRITING_SOURCE_LICENSES[variant]:
        license_path = standards.parent.parent / license_name
        if not license_path.is_file():
            found.append(f"paper-writing/{variant} 缺共置来源许可：{license_name}")
        if f"../{license_name}" not in source_text:
            found.append(f"paper-writing/{variant} sources.md 未指向共置许可：{license_name}")
    return found


def paper_writing_variant_problems(variant: str, text: str, root: Path) -> list[str]:
    """写作变体必须到达唯一总控；专业差异在总控的按需资源中表达。"""
    if variant not in PAPER_WRITING_VARIANTS:
        return [f"paper-writing 变体未知：{variant}"]
    found: list[str] = []
    for path in PAPER_WRITING_REQUIRED:
        if f"`{path}`" not in text:
            found.append(f"paper-writing/{variant} 缺统一入口 {path}")
        elif not (root / path).is_file():
            found.append(f"paper-writing/{variant} 统一入口目标不存在：{path}")
    found.extend(paper_writing_domain_standard_problems(variant, root))
    return found


def paper_writing_route_problems(rows: list[dict[str, str]], root: Path) -> list[str]:
    """仓库路由表里的 paper-writing 三变体必须成套，并指向真实 playbook。"""
    found: list[str] = []
    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        if row["路线"] != "paper-writing":
            continue
        variant = row["变体"]
        if variant in seen:
            found.append(f"paper-writing 变体重复：{variant}")
        seen[variant] = row
    for variant in PAPER_WRITING_VARIANTS:
        row = seen.get(variant)
        if row is None:
            found.append(f"缺 paper-writing/{variant} 路由行")
            continue
        if row["只读约束"] != "no":
            found.append(f"paper-writing/{variant} 的只读约束必须是 no")
        expected = f"playbooks/paper-writing-{variant}.md"
        if expected not in row["playbook"]:
            found.append(f"paper-writing/{variant} 的 playbook 必须是 {expected}")
            continue
        playbook = root / "skills/general/research-os" / expected
        if not playbook.is_file():
            found.append(f"paper-writing/{variant} 的 playbook 文件不存在")
            continue
        found.extend(
            paper_writing_variant_problems(
                variant, playbook.read_text(encoding="utf-8"), root
            )
        )
    return found


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
            clean = token.split("#", 1)[0]
            # .agents 等是研究项目配置示例；./ 与 ../ 才是真实相对级联。
            if (clean.startswith(("~", "/"))
                    or (clean.startswith(".") and not clean.startswith(("./", "../")))
                    or "/" not in clean or not clean.endswith(".md")):
                continue
            clean = clean.split()[0]
            if clean.startswith(("http://", "https://")):
                continue
            raw_candidates = [source.parent]
            if clean.startswith("skills/"):
                raw_candidates.append(root)
            elif not clean.startswith(("./", "../")):
                # 显式 dot 路径只相对引用文件；同名 skill-root 文件不能掩盖坏基准。
                raw_candidates.append(skill_root)
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


def gate_problems(
    name: str, skill_dir: Path, text: str, expected: frozenset[str],
    tracked_paths: set[str] | None = None,
) -> list[str]:
    """共同门校验；仓库扫描额外要求来源追踪，外部合同不依赖本仓索引。"""
    found: list[str] = []
    ids: list[str] = []
    none_count = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if GATES_NONE_RE.fullmatch(line):
            none_count += 1
            continue
        if not line.startswith(("Gate:", "Gates:")):
            continue
        match = GATE_RE.fullmatch(line)
        if not match:
            found.append(f"{name}:{lineno}: 门声明格式错误")
            continue
        gate_id, before, approval, source = match.groups()
        ids.append(gate_id)
        if not re.fullmatch(r"[a-z0-9-]+", before) or approval != "explicit-user":
            found.append(f"{name}:{lineno}: 门声明格式错误，approval 必须是 explicit-user")
        source_path, separator, anchor = source.partition("#")
        if not separator or not anchor:
            found.append(f"{name}: 门 {gate_id} 的 source 缺锚点")
            continue
        if source_path != "SKILL.md" and not source_path.startswith("references/"):
            found.append(f"{name}: 门 {gate_id} 的 source 越出当前 skill：{source_path}")
            continue
        target = (skill_dir / source_path).resolve()
        try:
            inside = target.relative_to(skill_dir.resolve())
            if inside.as_posix() != "SKILL.md" and (not inside.parts or inside.parts[0] != "references"):
                raise ValueError
        except ValueError:
            found.append(f"{name}: 门 {gate_id} 的 source 越出当前 skill：{source_path}")
            continue
        if not target.is_file():
            found.append(f"{name}: 门 {gate_id} 的 source 不存在：{source_path}")
            continue
        if tracked_paths is not None:
            try:
                rel_target = target.relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                rel_target = ""
            if rel_target not in tracked_paths:
                found.append(f"{name}: 门声明来源未追踪：{source_path}")
        if anchor not in heading_anchors(target.read_text(encoding="utf-8")):
            found.append(f"{name}: 门 {gate_id} 的锚点不存在：{anchor}")
    if none_count > 1:
        found.append(f"{name}: Gates: none 重复")
    if none_count and ids:
        found.append(f"{name}: none 与具体门不能并存")
    if not none_count and not ids:
        found.append(f"{name}: 整节删，缺 Gates: none 或 Gate 声明")
    if none_count and expected:
        found.append(f"{name}: 全部→none，基线要求 {sorted(expected)}")
    for gate_id in sorted(set(ids)):
        if ids.count(gate_id) > 1:
            found.append(f"{name}: 重复门 {gate_id}")
    actual = set(ids)
    for gate_id in sorted(expected - actual):
        found.append(f"{name}: 缺失门 {gate_id}")
    for gate_id in sorted(actual - expected):
        found.append(f"{name}: 多余门 {gate_id}")
    return found


def legacy_router_problems(files: dict[str, str]) -> list[str]:
    found: list[str] = []
    for rel, text in files.items():
        for lineno, line in enumerate(text.splitlines(), 1):
            # 逐引用所在句判断，其他段的 breaking/migration 不授予全文豁免。
            for sentence in re.split(r"[。！？!?]|(?<=\.)\s+", line):
                if LEGACY_ROUTER not in sentence:
                    continue
                migration = any(token in sentence.lower() for token in LEGACY_ALLOW_MIGRATION)
                active = bool(re.search(
                    r"请使用|请调用|推荐使用|继续使用|(?:use|invoke|run)\s+[`$ /]*ask-research-os", sentence, re.I
                ))
                if not migration or active:
                    found.append(f"{rel}:{lineno}: 产品正文残留旧 router {LEGACY_ROUTER}")
    return found


REQUIRED_RELEASE_ROUTES = (
    ("route-only", "—", "yes"),
    ("literature", "—", "no"),
    ("discovery", "—", "no"),
    ("experiment-plan", "—", "no"),
    ("experiment-bridge", "—", "no"),
    ("paper-writing", "general", "no"),
    ("paper-writing", "ml", "no"),
    ("paper-writing", "systems", "no"),
    ("proof", "—", "no"),
    ("rebuttal", "—", "no"),
    ("resubmit", "—", "no"),
    ("paper-talk", "—", "no"),
    ("improvement", "—", "no"),
    ("pickup", "—", "no"),
    ("custom", "—", "no"),
    ("swarm", "—", "no"),
)
STALE_PROMISE_SNIPPETS = (
    "完成后立即停止，绝不自动跳转",
    "No Automatic Chaining",
    "顶层工作流交付产物后立即结束，不会自动触发后续流程",
    "Top-level workflows stop upon completion and never transition to subsequent stages without explicit instruction",
)
HOST_PREREQUISITE_MARKERS = ("子代理", "blocked", "独立调用")
HOST_SERIAL_SUBSTITUTES = (
    "无该工具时由编排者串行执行",
    "编排者按 playbook 顺序自己执行",
    "由编排者串行完成",
    "编排者串行完成同一合同",
)


INTERROGATE_BUCKETS = ("Act on", "Consider", "Noted", "Dismissed")
INTERROGATE_FIXED_MODEL_MARKERS = ("claude-opus", "grok-4", "composer-", "cursor")


def interrogate_dispatch_contract(text: str) -> dict:
    """Read this Skill's local dispatch declaration, not a research runtime protocol."""
    match = re.search(r"(?ms)^### Reviewer dispatch contract\s*\n```json\n(.*?)\n```", text)
    if not match:
        raise ValueError("interrogate 缺本次 reviewer 集合/隔离声明")
    try:
        contract = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ValueError(f"interrogate 派发声明不是合法JSON: {error}") from error
    if not isinstance(contract, dict):
        raise ValueError("interrogate 派发声明必须是对象")
    return contract


def resolve_interrogate_reviewers(contract: dict, role_text: str) -> list[dict[str, str]]:
    """Static shape/source validation only; does not verify live tools or grant authority."""
    inputs = contract.get("reviewer_inputs")
    if (
        contract.get("context") != "fresh" or contract.get("readonly") is not True
        or contract.get("reviewer_reads_peer_findings") is not False
        or not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs)
        or set(inputs) != {"intent", "source_material", "rubric"} or len(inputs) != 3
        or contract.get("lead_reads_after") != "all_reviewers_complete"
    ):
        raise ValueError("interrogate 隔离关系无效：reviewer只读原材料，主审须后置综合")
    roles: dict[str, tuple[str, str]] = {}
    for line in role_text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = ROLE_LINE_RE.fullmatch(line.strip())
        if not match:
            raise ValueError("角色行格式无效")
        role, model, thinking = match.groups()
        if role not in ROLES or role in roles or thinking not in THINKING:
            raise ValueError("角色未知/重复或thinking无效；不允许扩展重复reviewer行")
        roles[role] = (model, thinking)
    reviewers = contract.get("reviewers")
    if not isinstance(reviewers, list) or len(reviewers) < 2:
        raise ValueError("blocked: 本次独立reviewer集合至少需要两个实例")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in reviewers:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip() or row["id"] in seen:
            raise ValueError("reviewer实例必须有唯一非空id")
        seen.add(row["id"])
        source = row.get("source")
        if source == "role:reviewer":
            if "reviewer" not in roles:
                raise ValueError("blocked: 缺reviewer绑定，须明示真实session回退来源")
            model, thinking = roles["reviewer"]
        elif source in ("explicit", "session"):
            if source == "session" and "reviewer" in roles:
                raise ValueError("已有显式reviewer绑定，不能借缺行session回退绕过替代授权")
            model, thinking = row.get("model"), row.get("thinking")
            if not isinstance(row.get("authority"), str) or not row["authority"].strip():
                raise ValueError("显式/回退条目缺原授权或能力来源索引，不能自行授予权限")
        else:
            raise ValueError("reviewer来源须为role:reviewer、explicit或session")
        if (
            not isinstance(model, str) or not re.fullmatch(r"[^/\s]+/\S+", model) or model.endswith("/")
            or not isinstance(thinking, str) or thinking not in THINKING
        ):
            raise ValueError("reviewer模型/档位格式无效")
        result.append({
            "id": row["id"], "model": model, "thinking": thinking, "source": source,
            "authority": row.get("authority", "project role:reviewer binding"),
        })
    distinct = contract.get("require_distinct_models", False)
    if not isinstance(distinct, bool):
        raise ValueError("require_distinct_models必须是布尔值")
    if distinct and len({row["model"] for row in result}) < 2:
        raise ValueError("blocked: 已请求多模型但可表达集合不足，不能静默降级")
    return result


def interrogate_contract_problems(text: str) -> list[str]:
    """interrogate 技能的合同检查：只读、独立审查机制与宿主中立。"""
    found: list[str] = []
    for marker in (
        "## 委托继承",
        "Gates: none",
        "只读",
        "不自动",
        "去重",
        "分歧",
        "主审",
        "子代理",
        "blocked",
        ".agents/research-os-models.md",
    ):
        if marker not in text:
            found.append(f"interrogate 正文缺 {marker}")
    for bucket in INTERROGATE_BUCKETS:
        if bucket not in text:
            found.append(f"interrogate 主审四桶缺 {bucket}")
    for banned in INTERROGATE_FIXED_MODEL_MARKERS:
        if banned in text.lower():
            found.append(f"interrogate 残留固定模型/宿主绑定：{banned}")
    try:
        contract = interrogate_dispatch_contract(text)
        # Validate the shipped declaration against the actual standard setup shape.
        template = SKILLS / "general/setup-research-os/templates/research-os-models.md"
        resolve_interrogate_reviewers(contract, template.read_text(encoding="utf-8"))
    except (ValueError, OSError) as error:
        found.append(str(error))
    step3 = text.split("## Step 3", 1)[-1].split("## Step 4", 1)[0]
    # Reject the review's explicit affirmative reversal, not arbitrary uses of 'findings'.
    if re.search(r"(?:^|[；。\n])\s*后续\s*reviewer\s*(?:必须|可以|应当)\s*先(?:读取|读)\s*前序\s*reviewer[^。\n]{0,120}findings[^。\n]{0,80}形成判断", step3, re.I):
        found.append("interrogate reviewer判断前读取前序findings，与隔离声明冲突")
    if not (SKILLS / "general" / "interrogate" / "references" / "research-review.md").exists():
        found.append("interrogate 缺科研审查 lens research-review.md")
    if not (SKILLS / "general" / "interrogate" / "references" / "PROVENANCE.md").exists():
        found.append("interrogate 缺来源登记 PROVENANCE.md")
    return found


def release_route_problems(rows: list[dict[str, str]]) -> list[str]:
    """14 个已交付 playbook 必须成套，只读约束与合同一致。"""
    found: list[str] = []
    actual = {(row["路线"], row["变体"], row["只读约束"]) for row in rows}
    for route, variant, readonly in REQUIRED_RELEASE_ROUTES:
        if (route, variant, readonly) not in actual:
            found.append(f"发布路由缺或只读约束不符：{route}/{variant}/{readonly}")
    return found


def stale_promise_problems(files: dict[str, str]) -> list[str]:
    """产品文档不得把「交付后绝不进入下一阶段」写成现行门语义。"""
    found: list[str] = []
    for rel, text in files.items():
        for snippet in STALE_PROMISE_SNIPPETS:
            if snippet in text:
                found.append(f"{rel}: 残留旧停止承诺：{snippet}")
    return found


def swarm_aggregate_contract_problems(text: str) -> list[str]:
    """Aggregate 需在局部保留重派上限、额度门槛与最终缺口状态。"""
    aggregate = re.search(r"(?ms)^## Phase C: Aggregate\s*\n(.*?)(?=^## Phase D: Report\s*$)", text)
    if aggregate is None:
        return ["swarm Aggregate 缺失或无法定位"]

    contract = aggregate.group(1)
    found: list[str] = []
    if not re.search(r"剩余额度允许时最多重派一次", contract):
        found.append("swarm Aggregate 缺剩余额度允许时的重派上限")
    if not re.search(r"否则直接记为缺口", contract):
        found.append("swarm Aggregate 缺额度不足时直接记最终缺口")
    if not re.search(r"第二次仍缺，记为缺口", contract):
        found.append("swarm Aggregate 缺二次缺证后的最终缺口")
    return found


def swarm_contract_problems(text: str) -> list[str]:
    """swarm 能力合同：分片/竞赛/混合、预声明规则、输出隔离、有界重派与缺口；无宿主/固定模型绑定。"""
    found: list[str] = []
    for marker in (
        "Frame", "Fan out", "Aggregate", "Report",
        "分片", "竞赛", "混合", "first pass", "rank all", "best-of",
        "完成条件", "独立 brief", "输出隔离", "重派",
        "缺口不算通过", "blocked", "子代理", "Role: implementer",
        ".agents/research-os-models.md", "88d47514b82e7c44f00f2b2a72ff6dd12158038c",
    ):
        if marker not in text:
            found.append(f"swarm 正文缺 {marker}")
    found.extend(swarm_aggregate_contract_problems(text))
    lowered = text.lower()
    for banned in ("~/.cursor", "pstack-models", "grok-4.7", 'environment: "cloud"', "cloud_base_branch"):
        if banned in lowered:
            found.append(f"swarm 正文残留固定绑定：{banned}")
    return found


def host_capability_problems(text: str) -> list[str]:
    """宿主映射按会话真实能力判定：子代理是前提，缺它时如实 blocked，不以串行代跑冒充已执行。"""
    found: list[str] = []
    for marker in HOST_PREREQUISITE_MARKERS:
        if marker not in text:
            found.append(f"宿主映射缺 {marker}")
    for snippet in HOST_SERIAL_SUBSTITUTES:
        if snippet in text:
            found.append(f"宿主映射把缺子代理写成串行代跑：{snippet}")
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


# --- 4b: 历史归档索引 ------------------------------------------------------
ARCHIVE_INDEX_REL = "docs/acceptance/evidence/README.md"
ARCHIVE_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.tar\.gz")
ARCHIVE_SHA_RE = re.compile(r"[0-9a-f]{64}")


def check_archive_index(strict: bool = False) -> None:
    """Validate structure; only strict scope requires historical byte identity.

    BYTE_MATCH proves digest/size equality only, not provenance or safe contents.
    Local-only records never cause reads of unapproved local archive bytes.
    """
    index = ROOT / ARCHIVE_INDEX_REL
    if ARCHIVE_INDEX_REL not in tracked or not index.is_file():
        err(f"历史归档索引不存在或未追踪: {ARCHIVE_INDEX_REL}")
        return

    index_text = index.read_text(encoding="utf-8")
    index_anchors = heading_anchors(index_text)
    rows: dict[str, tuple[str, str, str, str]] = {}
    for line_number, line in enumerate(index_text.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            continue
        if not line.lstrip().startswith("| `") and not ARCHIVE_NAME_RE.search(line.split("|")[1]):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            err(f"{ARCHIVE_INDEX_REL}:{line_number}: 归档索引行必须恰有 6 列")
            continue
        name = cells[0].strip("`")
        size = cells[1].replace(",", "")
        historical_sha = cells[2].strip("`")
        candidate_sha = cells[3].strip("`")
        status = cells[4]
        if not ARCHIVE_NAME_RE.fullmatch(name):
            err(f"{ARCHIVE_INDEX_REL}:{line_number}: 无效归档名")
            continue
        if name in rows:
            err(f"{ARCHIVE_INDEX_REL}:{line_number}: 重复归档记录 {name}")
            continue
        if not size.isdigit() or int(size) <= 0:
            err(f"{ARCHIVE_INDEX_REL}:{line_number}: 无效候选字节数 {name}")
            continue
        if not ARCHIVE_SHA_RE.fullmatch(historical_sha) or not ARCHIVE_SHA_RE.fullmatch(candidate_sha):
            err(f"{ARCHIVE_INDEX_REL}:{line_number}: SHA-256 字段无效 {name}")
            continue
        if status not in {"仅本地保留、未入库", "已入库、待核验", "已入库、已核验"}:
            err(f"{ARCHIVE_INDEX_REL}:{line_number}: 未知归档可用状态 {name}")
            continue
        rows[name] = (size, historical_sha, candidate_sha, status)

    if not rows:
        err(f"{ARCHIVE_INDEX_REL}: 没有有效历史归档记录")
        return

    for name, (size, historical_sha, candidate_sha, status) in rows.items():
        archive_rel = f"docs/acceptance/evidence/{name}"
        archive = ROOT / archive_rel
        available = archive_rel in tracked and archive.is_file()
        if status == "仅本地保留、未入库":
            if archive_rel in tracked or archive.exists():
                err(f"归档索引状态与仓库文件矛盾: {name}")
        elif not available:
            err(f"归档索引状态要求已追踪的真实字节: {name}")

        identity = "MISMATCH" if historical_sha != candidate_sha else "UNVERIFIED"
        availability = "UNAVAILABLE"
        if available and status != "仅本地保留、未入库":
            actual_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
            availability = "AVAILABLE"
            if actual_sha != candidate_sha or archive.stat().st_size != int(size):
                err(f"归档候选字节与索引 SHA/size 不符: {name}")
            elif actual_sha == historical_sha:
                identity = "BYTE_MATCH"
            if actual_sha != historical_sha:
                identity = "MISMATCH"
        if status == "已入库、已核验" and identity != "BYTE_MATCH":
            err(f"归档核验状态与历史 SHA 不符: {name}")
        print(f"HISTORY {identity}: {name} ({availability}; 摘要不认证来源/安全)")
        if strict and identity != "BYTE_MATCH":
            err(f"历史身份未通过: {name}: {identity}/{availability}")

    def is_index_target(markdown: Path, target: str) -> bool:
        path, separator, fragment = target.partition("#")
        return (
            lexical_relative(markdown.parent, path) == index.as_posix()
            and (not separator or unquote(fragment) in index_anchors)
        )

    linked_names: set[str] = set()
    for markdown in md_files:
        rel_markdown = markdown.relative_to(ROOT).as_posix()
        if rel_markdown == ARCHIVE_INDEX_REL or rel_markdown not in tracked:
            continue
        for line_number, line in enumerate(markdown.read_text(encoding="utf-8").splitlines(), 1):
            names = set(ARCHIVE_NAME_RE.findall(line))
            links = list(link_re.finditer(line))
            if not names or not links:
                continue
            explicit_names: set[str] = set()
            referenced_names: set[str] = set()
            links_index = False
            for link in links:
                target = link.group(1)
                valid_target = is_index_target(markdown, target)
                links_index |= valid_target
                link_names = set(ARCHIVE_NAME_RE.findall(link.group(0)))
                explicit_names.update(link_names)
                if valid_target:
                    referenced_names.update(link_names)
                else:
                    for name in sorted(link_names):
                        err(f"{rel_markdown}:{line_number}: 归档引用必须链接真实索引: {name} -> {target}")
            # A nearby index link may support a plain-text archive mention,
            # but never override an explicit archive link's own destination.
            if links_index:
                referenced_names.update(names - explicit_names)
            for name in names:
                # An invalid explicit target must not bypass registration.
                if name not in rows and (name in explicit_names or name in referenced_names):
                    err(f"归档索引缺少被引用记录: {name}")
                if name in referenced_names:
                    linked_names.add(name)
                elif name not in explicit_names and name in rows and rel_markdown.startswith("docs/acceptance/"):
                    err(f"{rel_markdown}:{line_number}: 归档引用必须链接真实索引: {name}")

    for name in sorted(rows.keys() - linked_names):
        err(f"历史归档记录没有验收文档索引入口: {name}")


# --- 5: README 清单与目录树一致 -------------------------------------------
actual = {f"{sf.parent.parent.name}/{sf.parent.name}" for sf in skill_files}
for readme_name in ("README.md", "skills/README.md"):
    rp = ROOT / readme_name
    if not rp.exists():
        err(f"{readme_name}: 不存在")
        continue
    readme_text = rp.read_text(encoding="utf-8")
    listed = set(re.findall(r"\]\((?:skills/)?([a-z-]+/[a-z0-9-]+)/SKILL\.md\)", readme_text))
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
    for problem in gate_problems(skill_name, skill_dir, skill_text, EXPECTED_GATES[skill_name], tracked):
        err(f"{rel}: {problem}")

research_os = SKILLS / "general" / "research-os" / "SKILL.md"
if research_os.exists():
    route_rows, route_errors = parse_route_table(research_os.read_text(encoding="utf-8"))
    for problem in route_errors:
        err(f"skills/general/research-os/SKILL.md: {problem}")
    route_problems, route_hints = route_table_problems(route_rows, research_os.parent)
    for problem in route_problems:
        err(f"skills/general/research-os/SKILL.md: {problem}")
    for problem in paper_writing_route_problems(route_rows, ROOT):
        err(f"skills/general/research-os/SKILL.md: {problem}")
    for problem in release_route_problems(route_rows):
        err(f"skills/general/research-os/SKILL.md: {problem}")
    for problem in host_capability_problems(research_os.read_text(encoding="utf-8")):
        err(f"skills/general/research-os/SKILL.md: {problem}")
    swarm_skill = SKILLS / "general" / "swarm" / "SKILL.md"
    if swarm_skill.is_file():
        for problem in swarm_contract_problems(swarm_skill.read_text(encoding="utf-8")):
            err(f"skills/general/swarm/SKILL.md: {problem}")
    else:
        err("skills/general/swarm/SKILL.md: swarm 能力缺失")
    HINTS.extend(route_hints)

interrogate_skill = SKILLS / "general" / "interrogate" / "SKILL.md"
if interrogate_skill.exists():
    for problem in interrogate_contract_problems(interrogate_skill.read_text(encoding="utf-8")):
        err(f"skills/general/interrogate/SKILL.md: {problem}")

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
for problem in stale_promise_problems(legacy_files):
    err(problem)


def expected_gates(skill_dir: Path, skill_name: str) -> frozenset[str] | None:
    """按迁移状态解析门基线：已迁移为空，未迁移为旧基线，未登记为 None。"""
    rel = f"skills/{skill_dir.parent.name}/{skill_name}/SKILL.md"
    if skill_name in GATE_BASELINE:
        return frozenset(GATE_BASELINE[skill_name])
    if skill_name in EXPECTED_GATES:
        return EXPECTED_GATES[skill_name]
    if rel in MIGRATED_CONTRACT:
        return frozenset()
    if rel in LEGACY_LEAF_GATES:
        return frozenset(LEGACY_LEAF_GATES[rel])
    return None


def migration_contract_problems(root: Path, tracked_paths: set[str]) -> list[str]:
    """委托合同与 expand 边界：合同单一权威，迁移集与文档记录一致。"""
    found: list[str] = []
    mandate = root / MANDATE_DOC
    if not mandate.is_file():
        found.append(f"{MANDATE_DOC}: 研究委托合同不存在")
    elif MANDATE_DOC not in tracked_paths:
        found.append(f"{MANDATE_DOC}: 研究委托合同未追踪")
    else:
        anchors = heading_anchors(mandate.read_text(encoding="utf-8"))
        for section in MANDATE_SECTIONS:
            if section not in anchors:
                found.append(f"{MANDATE_DOC}: 缺「{section}」小节")
    entry = root / "skills/general/research-os/SKILL.md"
    if entry.is_file() and "references/mandate.md" not in entry.read_text(encoding="utf-8"):
        found.append("skills/general/research-os/SKILL.md: 入口未指向 references/mandate.md")
    for rel, marker in MIGRATED_CONTRACT.items():
        path = root / rel
        if not path.is_file():
            found.append(f"{rel}: 已登记迁移但文件不存在")
        elif marker not in heading_anchors(path.read_text(encoding="utf-8")):
            found.append(f"{rel}: 已迁移技能缺「{marker}」小节")
    boundary = root / MIGRATION_DOC
    if not boundary.is_file() or MIGRATION_DOC not in tracked_paths:
        found.append(f"{MIGRATION_DOC}: 迁移边界文档缺失或未追踪")
        return found
    text = boundary.read_text(encoding="utf-8")
    if "未迁移" not in heading_anchors(text):
        found.append(f"{MIGRATION_DOC}: 缺「未迁移」小节")
    if "LEGACY_LEAF_GATES" not in text:
        found.append(f"{MIGRATION_DOC}: 未指明未迁移门基线的权威位置")
    for rel in MIGRATED_CONTRACT:
        if Path(rel).parent.name not in text:
            found.append(f"{MIGRATION_DOC}: 未列出已迁移技能 {Path(rel).parent.name}")
    return found


def contract_directive_lines(text: str) -> list[str]:
    """Read ordinary directive/declaration lines, not code examples or block quotes."""
    result = []
    in_code = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.lstrip().startswith(">"):
            continue
        line = re.sub(r"[*`]", "", line).strip()
        result.append(re.sub(r"^(?:[-+]\s+|\d+\.\s+)", "", line))
    return result


def discovery_order_problems(text: str) -> list[str]:
    """Only explicit affirmative universal mandates; ambiguous prose is manual review."""
    for line in contract_directive_lines(text):
        for clause in re.split(r"[；。，]", line):
            clause = clause.strip()
            if re.match(r"^(?:必须|务必|应当)(?:按)?固定顺序执行(?:全部|所有|五项|五个)", clause):
                return ["固定顺序强制所有职责"]
            if re.match(r"^(?:必须|务必|应当)(?:在)?(?:每个|每一|各个)阶段.*(?:批准|确认)", clause):
                return ["明确要求每阶段重复批准"]
            if re.match(r"^本(?:配方|流程)(?:必须)?(?:是|作为)(?:独立的)?第二总控", clause):
                return ["明确声明第二总控"]
    return []


def arena_required_dependencies(text: str) -> set[str]:
    """Parse named Required skills/Dependencies declarations, not arbitrary mentions."""
    dependencies: set[str] = set()
    for line in contract_directive_lines(text):
        match = re.fullmatch(r"(?:Required skills|Dependencies|必需依赖):\s*([a-z0-9-]+(?:\s*,\s*[a-z0-9-]+)*)", line, re.I)
        if match:
            dependencies.update(item.strip().lower() for item in match[1].split(","))
        if re.match(r"^(?:必须|务必|应当)先(?:运行|调用)\s+swarm\b", line, re.I):
            dependencies.add("swarm")
    sections = re.findall(r"(?ms)^## (?:Required skills|Dependencies|必需依赖)\s*\n(.*?)(?=^## |\Z)", text)
    for section in sections:
        for line in contract_directive_lines(section):
            if re.fullmatch(r"[a-z][a-z0-9-]*", line):
                dependencies.add(line)
            link = re.fullmatch(r"\[[^]]+\]\(([^)]+)\)", line)
            if link and Path(link[1]).name == "SKILL.md":
                dependencies.add(Path(link[1]).parent.name)
    return dependencies


def shared_quota_contract_problems(text: str) -> list[str]:
    """Check the canonical mandate link and explicit resets; prose coverage is manual."""
    found = []
    lines = contract_directive_lines(text)
    if not re.search(r"\[[^]]+\]\(\.\./references/mandate\.md(?:#[^)]*)?\)", text):
        found.append("缺共享额度权威mandate的可解析引用；完整事件覆盖语义须人工核验")
    for line in lines:
        for clause in re.split(r"[；。，]", line):
            if re.match(r"^\s*(?:每次|每个)?(?:并行|换线程|重试|恢复|子代理)(?:时|后)?(?:都)?(?:从零|重新)?(?:重置|清零)", clause):
                found.append("明确指令重置共享额度，与累计委托冲突")
    return found


CONTINUATION_PLAYBOOK = "skills/general/research-os/playbooks/continuation.md"
CONTINUATION_MARKERS = (
    "references/mandate.md",
    "references/batch-authorization.md",
    "可核验收束条件",
    "wall-clock",
    "暂停保存",
    "停滞",
    "真正死路",
    "恢复前完整走",
    "不把 Skill 文本当后台服务",
    "blocked",
)
CONTINUATION_HOST_BINDINGS = ("~/.cursor", "/loop", "agent-transcripts")
CONTINUATION_NOTICE = "skills/writing-cycle/research-improvement/NOTICE.md"
CONTINUATION_LICENSE = "skills/writing-cycle/research-improvement/UPSTREAM-LICENSE.md"
CONTINUATION_ENTRY_NOTICE = "skills/general/research-os/NOTICE-PSTACK.md"
CONTINUATION_ENTRY_LICENSE = "skills/general/research-os/LICENSE-PSTACK"
CONTINUATION_PSTACK_LICENSE_SHA256 = (
    "bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e"
)
CONTINUATION_DEPENDENCIES = "skills/writing-cycle/research-improvement/references/dependencies.md"


def continuation_contract_problems(root: Path, tracked_paths: set[str]) -> list[str]:
    """#59 持续/暂停/恢复：委托额度、真实恢复和宿主/权限边界不漂移。"""
    found: list[str] = []
    path = root / CONTINUATION_PLAYBOOK
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not path.is_file():
        found.append(f"{CONTINUATION_PLAYBOOK}: 持续执行配方不存在")
    elif CONTINUATION_PLAYBOOK not in tracked_paths:
        found.append(f"{CONTINUATION_PLAYBOOK}: 持续执行配方未追踪")
    for marker in CONTINUATION_MARKERS:
        if marker not in text:
            found.append(f"{CONTINUATION_PLAYBOOK}: 缺「{marker}」")
    for binding in CONTINUATION_HOST_BINDINGS:
        if binding in text:
            found.append(f"{CONTINUATION_PLAYBOOK}: 宿主绑定残留 {binding}")
    required_assets = (
        (CONTINUATION_NOTICE, "来源说明", ("cursor/plugins", FORMAL_UPSTREAM_REVISION, "MIT", "Lauren Tan"), "缺来源记录"),
        (CONTINUATION_LICENSE, "许可证", ("MIT License", "Copyright (c) 2026 Lauren Tan"), "缺 MIT 版权文本"),
        (
            CONTINUATION_ENTRY_NOTICE,
            "来源说明",
            (
                "cursor/plugins",
                FORMAL_UPSTREAM_REVISION,
                "pstack/skills/poteto-mode/playbooks/",
                "pstack/LICENSE",
                "continuation.md",
                "适配范围",
                "MIT",
                "Lauren Tan",
                "LICENSE-PSTACK",
            ),
            "缺入口包来源记录",
        ),
        (
            CONTINUATION_ENTRY_LICENSE,
            "许可证",
            ("MIT License", "Copyright (c) 2026 Lauren Tan"),
            "缺完整 MIT 版权文本",
        ),
        (CONTINUATION_DEPENDENCIES, "安装依赖映射", ("research-os/references/mandate.md", "research-os/references/batch-authorization.md", "<skills-root>/research-os/", "实际存在且可读", "composition-map.md"), "缺依赖声明"),
    )
    for rel, label, markers, detail in required_assets:
        asset = root / rel
        if not asset.is_file():
            found.append(f"{rel}: {label}不存在")
            continue
        if rel not in tracked_paths:
            found.append(f"{rel}: {label}未追踪")
        body = asset.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in body:
                found.append(f"{rel}: {detail} {marker}")
    entry_license = root / CONTINUATION_ENTRY_LICENSE
    if entry_license.is_file():
        entry_license_bytes = entry_license.read_bytes()
        if hashlib.sha256(entry_license_bytes).hexdigest() != CONTINUATION_PSTACK_LICENSE_SHA256:
            found.append(f"{CONTINUATION_ENTRY_LICENSE}: 与固定 revision 的完整 pstack MIT 字节不一致")
        source_license = root / CONTINUATION_LICENSE
        if source_license.is_file() and entry_license_bytes != source_license.read_bytes():
            found.append(f"{CONTINUATION_ENTRY_LICENSE}: 与 research-improvement 上游 MIT 字节不一致")
    return found


TICKET59_CONTRACTS: dict[str, tuple[str, ...]] = {
    CONTINUATION_PLAYBOOK: (
        "未知消耗保留预留，不按 0 释放",
    ),
    "skills/general/research-os/playbooks/pickup.md": (
        "必须回到**原始产物**和原始命令核对",
        "旧总结的成功标签不能直接当事实",
        "普通研究恢复不要求 setup-research-os",
        "原委托来源",
        "剩余额度",
        "不要求恢复会话另有本轮批准清单",
    ),
    "skills/writing-cycle/research-improvement/SKILL.md": (
        "独立显式调用本能力时",
        "由已授权的 research-os 委托级联时",
        "只核对原委托的最大轮数、当前轮次、剩余额度与写域",
        "先展示拟改内容并等用户确认",
        "不自动向公共仓库或 tracker 写入",
        "不计为 fresh 独立审查",
        "reviewer 不可用",
    ),
    "skills/writing-cycle/research-improvement/references/composition-map.md": (
        "已迁移能力不要求另行点名",
        "未迁移叶仍执行其自身门",
        "review/repair/re-review 轮统一标 `blocked`",
    ),
    "skills/writing-cycle/research-improvement/references/loop-methods.md": (
        "reviewer 不可用",
        "只读自查建议",
        "不计为 fresh 独立审查",
        "不得降级为单执行者评估",
    ),
    CONTINUATION_DEPENDENCIES: (
        "仅作业/费用批次分支依赖",
        "普通研究恢复不需要 `setup-research-os`",
        "独立 reviewer 是 review/repair/re-review 的必要条件",
        "不计为 fresh 独立审查",
    ),
}
TICKET59_FORBIDDEN_CONTRACTS: dict[str, tuple[str, ...]] = {
    "skills/writing-cycle/research-improvement/SKILL.md": (
        "没有任何未经再次确认的新轮次",
    ),
    "skills/general/research-os/playbooks/pickup.md": (
        "文件不存在就停",
    ),
    "skills/writing-cycle/research-improvement/references/loop-methods.md": (
        "审查者不可用或独立性无法建立时，标 `independent review not performed` 并降级为单执行者评估",
    ),
    "skills/writing-cycle/research-improvement/references/composition-map.md": (
        "以下均为 user-invoked，只能由用户另行显式调用",
    ),
}
TICKET59_DEPENDENCY_REPO_PATHS = {
    "skills/general/research-os/references/mandate.md",
    "skills/general/research-os/references/batch-authorization.md",
    "skills/general/setup-research-os/templates/compute-policy.md",
    "skills/general/setup-research-os/templates/research-log.md",
    "skills/writing-cycle/paper-compile/SKILL.md",
}
TICKET59_LICENSE_SHA256 = "bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e"


def ticket59_dependency_rows(text: str) -> list[tuple[str, str, str]]:
    """Return (name, source repository path, flattened install path) table rows."""
    rows: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        source = cells[1].strip("`")
        installed = cells[2].strip("`")
        if source.startswith("skills/"):
            rows.append((cells[0].strip("`"), source, installed))
    return rows


def ticket59_contract_problems(root: Path, tracked_paths: set[str]) -> list[str]:
    """Check #59's specific recovery/review contract and installable file map.

    This is a narrow set of explicit contract clauses and path relationships, not
    a claim that static text analysis understands arbitrary natural language.
    """
    found: list[str] = []
    for rel, markers in TICKET59_CONTRACTS.items():
        path = root / rel
        if not path.is_file():
            found.append(f"{rel}: #59 合同文件不存在")
            continue
        if rel not in tracked_paths:
            found.append(f"{rel}: #59 合同文件未追踪")
        body = path.read_text(encoding="utf-8")
        if rel == CONTINUATION_PLAYBOOK:
            found.extend(f"{rel}: {problem}" for problem in shared_quota_contract_problems(body))
        for marker in markers:
            if marker not in body:
                found.append(f"{rel}: 缺少 #59 合同条款「{marker}」")
        for obsolete in TICKET59_FORBIDDEN_CONTRACTS.get(rel, ()):
            if obsolete in body:
                found.append(f"{rel}: 残留与迁移合同冲突的旧条款「{obsolete}」")

    dependency_path = root / CONTINUATION_DEPENDENCIES
    if not dependency_path.is_file():
        return found
    dependency_text = dependency_path.read_text(encoding="utf-8")
    rows = ticket59_dependency_rows(dependency_text)
    mapped_sources: set[str] = set()
    mapped_targets: set[str] = set()
    for name, source_rel, install_cell in rows:
        mapped_sources.add(source_rel)
        source = root / source_rel
        if not source.is_file():
            found.append(f"{CONTINUATION_DEPENDENCIES}: 依赖仓库目标不存在 {source_rel}")
        elif source_rel not in tracked_paths:
            found.append(f"{CONTINUATION_DEPENDENCIES}: 依赖仓库目标未追踪 {source_rel}")
        expected = "/".join(source_rel.split("/")[2:])
        prefix = "<skills-root>/"
        actual = install_cell.removeprefix(prefix)
        if not install_cell.startswith(prefix) or actual != expected:
            found.append(
                f"{CONTINUATION_DEPENDENCIES}: {name} 扁平映射应为 {prefix}{expected}，实际为 {install_cell}"
            )
        mapped_targets.add(actual)

    for source_rel in sorted(TICKET59_DEPENDENCY_REPO_PATHS - mapped_sources):
        found.append(f"{CONTINUATION_DEPENDENCIES}: 缺少依赖映射 {source_rel}")

    composition_path = root / "skills/writing-cycle/research-improvement/references/composition-map.md"
    if composition_path.is_file():
        composition = composition_path.read_text(encoding="utf-8")
        for skill_name in re.findall(r"\|[^|]+\|\s*`([a-z0-9-]+)`\s*\|", composition):
            if f"{skill_name}/SKILL.md" not in mapped_targets:
                found.append(
                    f"{CONTINUATION_DEPENDENCIES}: composition-map 分支 {skill_name} 无对应安装映射"
                )

    pickup_path = root / "skills/general/research-os/playbooks/pickup.md"
    if pickup_path.is_file():
        pickup = pickup_path.read_text(encoding="utf-8")
        for source_rel in re.findall(r"`(skills/[^`]+)`", pickup):
            if not source_rel.endswith((".md", ".py", ".sh", ".json")):
                continue
            if not (root / source_rel).is_file():
                found.append(f"pickup.md: 反引号必读资源不存在 {source_rel}")
                continue
            target = "/".join(source_rel.split("/")[2:])
            package = target.split("/", 1)[0]
            if not any(mapped.startswith(f"{package}/") for mapped in mapped_targets):
                found.append(f"{CONTINUATION_DEPENDENCIES}: pickup.md 必读包 {package} 未声明映射")

    license_path = root / CONTINUATION_LICENSE
    if license_path.is_file():
        digest = hashlib.sha256(license_path.read_bytes()).hexdigest()
        if digest != TICKET59_LICENSE_SHA256:
            found.append(f"{CONTINUATION_LICENSE}: MIT 许可证全文校验失败（SHA256 {digest}）")
    else:
        found.append(f"{CONTINUATION_LICENSE}: MIT 许可证全文不存在")
    return found


# --- expand 迁移边界 -------------------------------------------------------
# 已迁移能力遵循委托合同（references/mandate.md）：正文无旧门，并带指定的合同小节。
# 未迁移能力保留 #39 旧门基线，照旧单独可用；某能力迁移完成后，把它的条目从这里
# 移入 MIGRATED_CONTRACT，并在 references/migration-boundary.md 记录同一事实。
MIGRATED_CONTRACT: dict[str, str] = {
    "skills/general/research-os/SKILL.md": "研究委托",
    "skills/idea-cycle/creative-thinking-for-research/SKILL.md": "委托继承",
    "skills/idea-cycle/idea-generation/SKILL.md": "委托继承",
    "skills/idea-cycle/idea-refinement/SKILL.md": "委托继承",
    "skills/idea-cycle/idea-review/SKILL.md": "委托继承",
    "skills/idea-cycle/novelty-check/SKILL.md": "委托继承",
    "skills/idea-cycle/research-lit/SKILL.md": "委托继承",
    "skills/organization/arena/SKILL.md": "委托继承",
    "skills/validation-cycle/create-verification-skill/SKILL.md": "委托继承",
    "skills/validation-cycle/maintain-verification-skill/SKILL.md": "委托继承",
    "skills/general/swarm/SKILL.md": "委托继承",
    "skills/general/interrogate/SKILL.md": "委托继承",
    "skills/writing-cycle/academic-plotting/SKILL.md": "委托继承",
    "skills/validation-cycle/create-formal-verification-skill/SKILL.md": "委托继承",
    "skills/validation-cycle/maintain-formal-verification-skill/SKILL.md": "委托继承",
    "skills/writing-cycle/research-improvement/SKILL.md": "委托继承",
    "skills/validation-cycle/experiment-plan/SKILL.md": "委托继承",
    "skills/validation-cycle/run-experiment/SKILL.md": "委托继承",
    "skills/validation-cycle/experiment-queue/SKILL.md": "委托继承",
    "skills/validation-cycle/monitor-experiment/SKILL.md": "委托继承",
    "skills/validation-cycle/training-health-check/SKILL.md": "委托继承",
    "skills/validation-cycle/analyze-results/SKILL.md": "委托继承",
    "skills/validation-cycle/experiment-audit/SKILL.md": "委托继承",
    "skills/validation-cycle/result-to-claim/SKILL.md": "委托继承",
    "skills/validation-cycle/formula-derivation/SKILL.md": "委托继承",
    "skills/validation-cycle/proof-writer/SKILL.md": "委托继承",
    "skills/validation-cycle/proof-repair/SKILL.md": "委托继承",
    "skills/writing-cycle/paper-writing/SKILL.md": "委托继承",
    "skills/writing-cycle/paper-plan/SKILL.md": "委托继承",
    "skills/writing-cycle/paper-drafting/SKILL.md": "委托继承",
    "skills/writing-cycle/paper-compile/SKILL.md": "委托继承",
    "skills/writing-cycle/paper-compile-repair/SKILL.md": "委托继承",
    "skills/writing-cycle/citation-audit/SKILL.md": "委托继承",
    "skills/writing-cycle/apply-citation-fixes/SKILL.md": "委托继承",
    "skills/writing-cycle/paper-claim-audit/SKILL.md": "委托继承",
    "skills/writing-cycle/claim-stress-test/SKILL.md": "委托继承",
    "skills/writing-cycle/rebuttal/SKILL.md": "委托继承",
    "skills/writing-cycle/resubmit-pipeline/SKILL.md": "委托继承",
    "skills/writing-cycle/paper-talk/SKILL.md": "委托继承",
}
MANDATE_DOC = "skills/general/research-os/references/mandate.md"
MIGRATION_DOC = "skills/general/research-os/references/migration-boundary.md"
MANDATE_SECTIONS = ("目标", "权限", "研究额度", "完成与停止")

# --- 未迁移叶 skill 门声明（#39 基线）；入口、setup 与已迁移能力不进这份路径表 ---
LEGACY_LEAF_GATES: dict[str, set[str]] = {
    "skills/validation-cycle/proof-review/SKILL.md": set(),
}


# --- #54 形式化验证资产与对应审计 -----------------------------------------
# 来源与许可随 Skill 共置（LICENSE/NOTICE.md），正文必须区分四类对象、记录外部假设与
# 版本／同步、审计编码与原问题对应、保留故障暴露证据，并且不绑定宿主或个人目录。
FORMAL_UPSTREAM_REVISION = "88d47514b82e7c44f00f2b2a72ff6dd12158038c"
FORMAL_SKILLS: dict[str, tuple[str, ...]] = {
    "create-formal-verification-skill": (
        "代码性质", "形式模型", "数学定理", "普通测试", "按问题选工具",
        "外部假设", "同步", "对应审计", "故障暴露", "草稿", "子代理", "blocked",
        "宿主", "proof 族",
    ),
    "maintain-formal-verification-skill": (
        "in sync", "updated", "bug", "blocked", "同步 commit", "对应审计",
        "占位符", "子代理", "宿主", "proof 族",
    ),
}
FORMAL_REQUIRED_FILES = {
    "create-formal-verification-skill": (
        "LICENSE",
        "NOTICE.md",
        "agents/openai.yaml",
        "references/tool-selection.md",
        "references/assumption-ledger.md",
        "references/correspondence-audit.md",
        "templates/formal-verification-record.md",
    ),
    "maintain-formal-verification-skill": (
        "LICENSE",
        "NOTICE.md",
        "agents/openai.yaml",
    ),
}
FORMAL_REFERENCE_MARKERS = {
    "references/tool-selection.md": (
        "代码性质", "形式模型", "数学定理", "普通测试", "不强制全链", "没有可用验证器",
    ),
    "references/assumption-ledger.md": (
        "外部假设", "材料", "版本", "覆盖", "同步状态", "重验", "草稿",
    ),
    "references/correspondence-audit.md": (
        "原问题", "编码定义", "定理", "量词", "假设", "边界", "对象", "占位符",
        "编译成功", "有限数值", "不得冒充",
    ),
    "templates/formal-verification-record.md": (
        "外部假设与材料", "同步状态", "commit", "重验触发条件", "对应审计", "草稿",
    ),
}
FORMAL_HOST_BINDINGS = ("Cursor", "~/.cursor", ".cursor/", "pstack-models", "/loop")
FORMAL_MODEL_PIN = re.compile(
    r"(?i)(gpt-[0-9]|claude-[0-9]|gemini-[0-9]|grok-[0-9]|deepseek-[a-z0-9]|glm-[0-9]|opus|sonnet)"
)


def formal_verification_problems(root: Path, tracked_paths: set[str]) -> list[str]:
    """#54 形式化验证：许可、工具选择、假设与同步、对应审计、故障暴露、宿主中立。"""
    found: list[str] = []
    base = root / "skills/validation-cycle"
    for name, markers in FORMAL_SKILLS.items():
        skill_dir = base / name
        rel_dir = f"skills/validation-cycle/{name}"
        if not skill_dir.is_dir():
            found.append(f"{rel_dir}: 形式化验证 Skill 不存在")
            continue
        for rel in ("SKILL.md", *FORMAL_REQUIRED_FILES[name]):
            path = skill_dir / rel
            rel_path = f"{rel_dir}/{rel}"
            if not path.is_file():
                found.append(f"{rel_path}: 缺少形式化验证资产")
            elif rel_path not in tracked_paths:
                found.append(f"{rel_path}: 未追踪")
        license_path = skill_dir / "LICENSE"
        if license_path.is_file():
            license_text = license_path.read_text(encoding="utf-8")
            for marker in ("MIT License", "Copyright (c) 2026 Lauren Tan"):
                if marker not in license_text:
                    found.append(f"{rel_dir}/LICENSE: 缺 MIT 版权文本 {marker}")
        notice_path = skill_dir / "NOTICE.md"
        if notice_path.is_file():
            notice = notice_path.read_text(encoding="utf-8")
            for marker in ("cursor/plugins", FORMAL_UPSTREAM_REVISION, "MIT"):
                if marker not in notice:
                    found.append(f"{rel_dir}/NOTICE.md: 缺来源记录 {marker}")
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.is_file():
            continue
        text = skill_path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                found.append(f"{rel_dir}/SKILL.md: 缺「{marker}」")
        if "委托继承" not in heading_anchors(text):
            found.append(f"{rel_dir}/SKILL.md: 缺「委托继承」小节")
        for binding in FORMAL_HOST_BINDINGS:
            if binding in text:
                found.append(f"{rel_dir}/SKILL.md: 宿主绑定残留 {binding}")
        if FORMAL_MODEL_PIN.search(text):
            found.append(f"{rel_dir}/SKILL.md: 固定模型绑定")
        yaml_path = skill_dir / "agents" / "openai.yaml"
        if yaml_path.is_file():
            if yaml_allow_implicit(yaml_path.read_text(encoding="utf-8")) != "false":
                found.append(f"{rel_dir}/agents/openai.yaml: allow_implicit_invocation 必须为 false")
        for rel, required in FORMAL_REFERENCE_MARKERS.items():
            path = skill_dir / rel
            if not path.is_file():
                continue
            body = path.read_text(encoding="utf-8")
            for marker in required:
                if marker not in body:
                    found.append(f"{rel_dir}/{rel}: 缺「{marker}」")
        if f"{rel_dir}/SKILL.md" not in MIGRATED_CONTRACT:
            found.append(f"{rel_dir}/SKILL.md: 未登记迁移状态")
    boundary = root / MIGRATION_DOC
    if boundary.is_file():
        boundary_text = boundary.read_text(encoding="utf-8")
        for name in FORMAL_SKILLS:
            if name not in boundary_text:
                found.append(f"{MIGRATION_DOC}: 未列出形式化验证能力 {name}")
    return found


# --- #53 项目行为验证资产 ---------------------------------------------------
# 来源与许可随 Skill 共置（LICENSE/NOTICE.md）。创建侧必须保留真实启动、健康检查、
# 驱动、证据、清理与特征覆盖映射的机制并带 helper；维护侧必须带三态结果、只改
# 验证、源读波与现场驱动。未执行的生成资产只能标草稿；证据须绑定被测对象且在
# 相关材料变化后失效；不绑定宿主或固定模型，与形式化能力分工明确。
VERIFICATION_UPSTREAM_REVISION = "88d47514b82e7c44f00f2b2a72ff6dd12158038c"
VERIFICATION_SKILLS: dict[str, tuple[str, ...]] = {
    "create-verification-skill": (
        "启动", "健康检查", "驱动", "证据", "清理", "覆盖映射", "doctor",
        "草稿", "blocked", "子代理", "宿主", "证据归属与失效", "stale",
        "不得为新对象背书", "重跑受影响覆盖",
        "create-formal-verification-skill", "不宣称数学定理成立",
    ),
    "maintain-verification-skill": (
        "clean", "changed", "blocked", "只改验证", "源读波", "现场驱动",
        "doctor", "证据", "清理", "verified-unreachable", "子代理", "宿主",
        "证据归属与失效", "stale", "不得为新对象背书", "重跑受影响覆盖",
        "maintain-formal-verification-skill",
    ),
}
VERIFICATION_REQUIRED_FILES = {
    "create-verification-skill": (
        "LICENSE", "NOTICE.md", "agents/openai.yaml",
        "references/feature-map-example/README.md",
        "helpers/feature-map-lint.py",
    ),
    "maintain-verification-skill": (
        "LICENSE", "NOTICE.md", "agents/openai.yaml",
    ),
}


def verification_skill_problems(root: Path, tracked_paths: set[str]) -> list[str]:
    """#53 行为验证：许可、共置资源、机制保留、草稿/分工语义、宿主中立。"""
    found: list[str] = []
    base = root / "skills/validation-cycle"
    for name, markers in VERIFICATION_SKILLS.items():
        skill_dir = base / name
        rel_dir = f"skills/validation-cycle/{name}"
        if not skill_dir.is_dir():
            found.append(f"{rel_dir}: 行为验证 Skill 不存在")
            continue
        for rel in VERIFICATION_REQUIRED_FILES[name]:
            path = skill_dir / rel
            rel_path = f"{rel_dir}/{rel}"
            if not path.is_file():
                found.append(f"{rel_path}: 缺少行为验证资产")
            elif rel_path not in tracked_paths:
                found.append(f"{rel_path}: 未追踪")
        license_path = skill_dir / "LICENSE"
        if license_path.is_file():
            license_text = license_path.read_text(encoding="utf-8")
            for marker in ("MIT License", "Copyright (c) 2026 Lauren Tan"):
                if marker not in license_text:
                    found.append(f"{rel_dir}/LICENSE: 缺 MIT 版权文本 {marker}")
        notice_path = skill_dir / "NOTICE.md"
        if notice_path.is_file():
            notice = notice_path.read_text(encoding="utf-8")
            for marker in ("cursor/plugins", VERIFICATION_UPSTREAM_REVISION, "MIT"):
                if marker not in notice:
                    found.append(f"{rel_dir}/NOTICE.md: 缺来源记录 {marker}")
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.is_file():
            continue
        text = skill_path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                found.append(f"{rel_dir}/SKILL.md: 缺「{marker}」")
        if "委托继承" not in heading_anchors(text):
            found.append(f"{rel_dir}/SKILL.md: 缺「委托继承」小节")
        for binding in FORMAL_HOST_BINDINGS:
            if binding in text:
                found.append(f"{rel_dir}/SKILL.md: 宿主绑定残留 {binding}")
        if FORMAL_MODEL_PIN.search(text):
            found.append(f"{rel_dir}/SKILL.md: 固定模型绑定")
        yaml_path = skill_dir / "agents" / "openai.yaml"
        if yaml_path.is_file() and yaml_allow_implicit(yaml_path.read_text(encoding="utf-8")) != "false":
            found.append(f"{rel_dir}/agents/openai.yaml: allow_implicit_invocation 必须为 false")
        if f"{rel_dir}/SKILL.md" not in MIGRATED_CONTRACT:
            found.append(f"{rel_dir}/SKILL.md: 未登记迁移状态")
    boundary = root / MIGRATION_DOC
    if boundary.is_file():
        boundary_text = boundary.read_text(encoding="utf-8")
        for name in VERIFICATION_SKILLS:
            if name not in boundary_text:
                found.append(f"{MIGRATION_DOC}: 未列出行为验证能力 {name}")
    return found

RESEARCH_ASSETS = {
    "skills/idea-cycle/research-lit": (
        "LICENSE",
        "references/source-methods.md",
        "references/file-capability-audit.md",
        "references/source-verification.md",
        "templates/literature-report.md",
    ),
    "skills/idea-cycle/novelty-check": (
        "LICENSE",
        "references/source-verification.md",
    ),
    "skills/idea-cycle/creative-thinking-for-research": (
        "LICENSE-Orchestra.txt",
        "references/creative-frameworks.md",
    ),
    "skills/writing-cycle/academic-plotting": (
        "LICENSE-ARIS.txt",
        "LICENSE-Orchestra.txt",
        "references/data-visualization.md",
        "references/diagram-generation.md",
        "references/diagram-styles.md",
        "references/style-guide.md",
        "references/table-and-review.md",
        "templates/figure-note.md",
    ),
}
DISCOVERY_PHASE_LEAVES = (
    "research-lit",
    "idea-generation",
    "novelty-check",
    "idea-review",
    "idea-refinement",
)
DISCOVERY_LIVE_CALLERS = (
    "README.md",
    "docs/README-en.md",
    "skills/README.md",
    "skills/general/research-os/SKILL.md",
    "skills/general/research-os/playbooks/discovery.md",
    "skills/general/research-os/playbooks/literature-review.md",
    "skills/general/research-os/references/PRODUCT-MAP.md",
    "skills/general/research-os/references/idea-cycle.md",
    "skills/general/research-os/references/migration-boundary.md",
    "docs/assets/README.md",
    "docs/assets/demo-script.sh",
    "docs/assets/workflow-diagrams.md",
    "docs/user-acceptance-guide.md",
)
DISCOVERY_LICENSE_SHA256 = "e30cf5dd5f49b4f9b656590e23d782b4756c924a9f0ff0162b3e7b5d87006bf5"


def research_asset_problems(root: Path, tracked_paths: set[str]) -> list[str]:
    """#58 检索/绘图与 #60 Discovery 资源：检查既有能力归属及随包可达。"""
    found: list[str] = []
    for rel_dir, rels in RESEARCH_ASSETS.items():
        for rel in rels:
            rel_path = f"{rel_dir}/{rel}"
            path = root / rel_path
            if not path.is_file():
                found.append(f"{rel_path}: 缺少随包研究资产")
            elif rel_path not in tracked_paths:
                found.append(f"{rel_path}: 未追踪")
    discovery_root = root / "skills/idea-cycle/idea-discovery"
    if (discovery_root / "SKILL.md").exists() or (discovery_root / "agents/openai.yaml").exists():
        found.append("skills/idea-cycle/idea-discovery: 旧发现控制器未退役")

    composition_rel = "skills/general/research-os/references/discovery-composition.md"
    composition = root / composition_rel
    if not composition.is_file():
        found.append(f"{composition_rel}: 缺少组合说明")
    elif composition_rel not in tracked_paths:
        found.append(f"{composition_rel}: 未追踪")
    else:
        text = composition.read_text(encoding="utf-8")
        for marker in (
            "Required skills", "DEPENDENCY MISSING / BLOCKED", "子集", "重排", "回访",
            "目标替换", "fresh 独立评审", "原始回复", "缺少依赖只阻塞受影响职责",
            *DISCOVERY_PHASE_LEAVES,
        ):
            if marker not in text:
                found.append(f"{composition_rel}: 缺「{marker}」")
        found.extend(f"{composition_rel}: {problem}" for problem in discovery_order_problems(text))
        install_line = next((line for line in text.splitlines() if "--skill research-os" in line), "")
        missing = [name for name in DISCOVERY_PHASE_LEAVES if name not in install_line]
        if missing:
            found.append(f"{composition_rel}: 成组安装命令缺 Required skills " + ", ".join(missing))
        if "creative-thinking-for-research" in install_line:
            found.append(f"{composition_rel}: 可选 creative-thinking-for-research 被误列为 Required")

    playbook_rel = "skills/general/research-os/playbooks/discovery.md"
    playbook = root / playbook_rel
    if not playbook.is_file():
        found.append(f"{playbook_rel}: 缺 Discovery 配方")
    else:
        text = playbook.read_text(encoding="utf-8")
        if "skills/idea-cycle/" in text:
            found.append(f"{playbook_rel}: 使用仓库源码路径，无法解析安装后的 Skill 资源")
        if "按安装后的 Skill 名称定位其目录" not in text:
            found.append(f"{playbook_rel}: 缺安装后 Skill 目录解析规则")
        for marker in ("方向到 Proposal", "目标缺口", "子集", "重排", "回访", "fresh 独立评审"):
            if marker not in text:
                found.append(f"{playbook_rel}: 缺组合行为 {marker}")
        for rel in DISCOVERY_PHASE_LEAVES:
            if rel not in text:
                found.append(f"{playbook_rel}: 缺组合叶 {rel}")
        found.extend(f"{playbook_rel}: {problem}" for problem in discovery_order_problems(text))

    required_discovery_assets = (
        "skills/general/research-os/templates/research-brief.md",
        "skills/general/research-os/templates/discovery-report.md",
        "skills/general/research-os/licenses/idea-cycle/LICENSE",
    )
    for rel in required_discovery_assets:
        path = root / rel
        if not path.is_file():
            found.append(f"{rel}: 缺 Discovery 随包资源")
        elif rel not in tracked_paths:
            found.append(f"{rel}: 未追踪")
    license_path = root / required_discovery_assets[-1]
    if license_path.is_file() and hashlib.sha256(license_path.read_bytes()).hexdigest() != DISCOVERY_LICENSE_SHA256:
        found.append(f"{required_discovery_assets[-1]}: 上游 MIT 许可与原文不一致")

    for rel in DISCOVERY_LIVE_CALLERS:
        path = root / rel
        if path.is_file() and "idea-discovery" in path.read_text(encoding="utf-8"):
            found.append(f"{rel}: 仍调用已退役的 idea-discovery slug")

    plotting = root / "skills/writing-cycle/academic-plotting/SKILL.md"
    if plotting.is_file():
        text = plotting.read_text(encoding="utf-8")
        if "没有计划时" in text and ("确认选择" in text or "确认候选" in text):
            found.append("skills/writing-cycle/academic-plotting/SKILL.md: 无条件要求确认普通选图")
        if "已授权目录内" not in text or "新文件路径" not in text:
            found.append("skills/writing-cycle/academic-plotting/SKILL.md: 缺授权目录内自主选择新路径")
    audit = root / "skills/idea-cycle/research-lit/references/file-capability-audit.md"
    if not audit.is_file():
        found.append("skills/idea-cycle/research-lit/references/file-capability-audit.md: 缺文件能力缺口审计")
    else:
        audit_text = audit.read_text(encoding="utf-8")
        for marker in ("plain text", "PDF", "OCR", "connector", "plotting", "export", "host prerequisite", "not bundled", "No additional external asset is selected in this ticket", "license", "dependencies"):
            if marker not in audit_text:
                found.append(f"skills/idea-cycle/research-lit/references/file-capability-audit.md: 缺「{marker}」")
        audit_rows = (
            "Search plain text / Markdown",
            "Read and extract born-digital PDF text",
            "Read scanned PDFs / image-only documents",
            "Reference-manager and notes connectors",
            "Plotting and diagram production",
            "Figure export and visual inspection",
        )
        for topic in audit_rows:
            prefix = f"| {topic} |"
            row = next((line for line in audit_text.splitlines() if line.startswith(prefix)), None)
            cells = row.strip().strip("|").split("|") if row else []
            if len(cells) != 4 or any(not cell.strip() for cell in cells):
                found.append(f"skills/idea-cycle/research-lit/references/file-capability-audit.md: 缺文件能力审计条目或覆盖信息 {topic}")
    return found


EXPERIMENT_SKILLS: tuple[str, ...] = (
    "experiment-plan",
    "run-experiment",
    "experiment-queue",
    "monitor-experiment",
    "training-health-check",
    "analyze-results",
    "experiment-audit",
    "result-to-claim",
)
EXPERIMENT_JOB_CONTRACT = (
    "输入版本", "工具链", "独立目录", "作业身份", "退出码", "原始日志", "产物",
)
EXPERIMENT_RECOVERY = (
    "原作业", "不盲重跑", "旧文件", "作业退出", "产物有效", "科学结论",
)
EXPERIMENT_REMOTE = (
    "远程只是执行位置", "SSH", "已有调度", "不新造执行引擎", "不锁定供应商",
    "凭据", "独立目录", "作业身份", "原作业",
)
EXPERIMENT_REQUIRED_FILES = {
    "experiment-plan": (
        "references/mandate.md", "references/block-checks.md", "templates/experiment-plan.md",
    ),
    "run-experiment": (
        "references/mandate.md",
        "references/execution-contract.md",
        "references/remote-execution.md",
        "references/batch-authorization.md",
        "references/composition-map.md",
        "templates/run-report.md",
    ),
    "experiment-queue": ("references/mandate.md", "templates/batch-manifest.md"),
    "monitor-experiment": (
        "references/mandate.md", "references/observation-sources.md", "templates/run-status-report.md",
    ),
    "training-health-check": (
        "references/mandate.md", "references/health-signals.md", "templates/health-report.md",
    ),
    "analyze-results": (
        "references/mandate.md", "references/statistical-checks.md", "templates/analysis-report.md",
    ),
    "experiment-audit": (
        "references/mandate.md", "references/integrity-checks.md", "templates/audit-report.md",
    ),
    "result-to-claim": (
        "references/mandate.md", "references/claim-judgment.md", "templates/claim-report.md",
    ),
}
EXPERIMENT_TEXT_MARKERS = {
    "run-experiment": (
        "唯一实验执行控制", "小批量或队列", "委托继承", *EXPERIMENT_JOB_CONTRACT,
        "作业退出", "产物有效", "科学结论", "旧文件",
        "远程只是执行位置", "SSH", "已有调度",
    ),
    "experiment-queue": (
        "委托继承", *EXPERIMENT_JOB_CONTRACT, *EXPERIMENT_RECOVERY,
        "不因进入队列或新波次重复索权", "研究日志",
    ),
    "experiment-plan": (
        "委托继承", "数学计算", "不硬套训练 baseline", "计划声明的对照",
        "不逐 milestone 再索权",
    ),
    "monitor-experiment": ("委托继承",),
    "training-health-check": ("委托继承",),
    "analyze-results": ("委托继承",),
    "experiment-audit": ("委托继承", "作业退出", "产物有效", "科学结论", "unknown"),
    "result-to-claim": ("委托继承", "作业退出", "产物有效", "科学结论", "旧文件"),
}
EXPERIMENT_MANDATE_MARKERS = (
    "references/mandate.md",
    "完整规范的唯一权威仍是 `skills/general/research-os/references/mandate.md`",
    "分发摘录缺失",
    "本次动作超出摘录",
)
EXPERIMENT_MANDATE_PACKAGE_MARKERS = (
    "叶能力、下一阶段或一次审查完成都不重置授权",
    "用户明确只要推荐、只审查、只规划或不要执行时，保持该范围",
    "未授权的破坏性动作",
    "项目内的依赖、工具与缓存可在授权内自动准备",
    "有界首轮",
    "并行、换线程、重试与恢复都消耗同一份额度，不重置",
    "用户叫停是停止，不是完成",
    "委托的验收看实际产物，不看执行者的自述",
    "额度、权限与目标互不推导",
)
EXPERIMENT_COMPANION_DEPENDENCIES = {
    "experiment-queue": ("run-experiment",),
    "result-to-claim": ("analyze-results",),
}
EXPERIMENT_FILE_MARKERS = {
    "run-experiment/references/composition-map.md": (
        "是唯一执行控制", "experiment-plan", "experiment-queue", "monitor-experiment",
        "training-health-check", "analyze-results", "experiment-audit", "result-to-claim",
        "blocked",
    ),
    "run-experiment/references/execution-contract.md": EXPERIMENT_JOB_CONTRACT,
    "run-experiment/references/remote-execution.md": EXPERIMENT_REMOTE,
    "run-experiment/references/batch-authorization.md": (
        "research-log.md", "valid_until", "scope", "cost_limit", "compute_limit", "run_limit",
        "run_count_basis: planned-run", "concurrency_limit", "retry_limit", "worst_case_estimate",
    ),
    "run-experiment/templates/run-report.md": (
        *EXPERIMENT_JOB_CONTRACT, "Artifact validity", "Scientific conclusion",
        "Monitoring and Health", "Analysis and Independent Audit", "Tracker Update",
        "Optional Ablation Suggestions",
    ),
    "experiment-queue/templates/batch-manifest.md": EXPERIMENT_JOB_CONTRACT,
}
EXPERIMENT_HOST_BINDINGS = FORMAL_HOST_BINDINGS
EXPERIMENT_MODEL_PIN = FORMAL_MODEL_PIN
EXPERIMENT_AUTHORIZATION_MARKERS = (
    "research-log.md", "valid_until", "scope", "累计额度", "run_count_basis=planned-run",
    "concurrency_limit", "retry_limit", "worst_case_estimate", "不按 milestone 重复索取",
    "batch-authorization.md",
)
EXPERIMENT_BRIDGE_PLAYBOOK = "skills/general/research-os/playbooks/experiment-bridge.md"


def experiment_execution_problems(root: Path, tracked_paths: set[str]) -> list[str]:
    """#56 实验执行：委托继承、桥接合流、运行/恢复/远程合同与宿主中立。"""
    found: list[str] = []
    base = root / "skills" / "validation-cycle"
    legacy_bridge = base / "experiment-bridge"
    if (legacy_bridge / "SKILL.md").exists() or any(
        path.is_file() for path in legacy_bridge.rglob("*")
    ):
        found.append("skills/validation-cycle/experiment-bridge: 旧 Skill 仍可发现或安装")
    packaged_mandate_text: str | None = None
    for name in EXPERIMENT_SKILLS:
        rel_dir = f"skills/validation-cycle/{name}"
        skill_dir = base / name
        if not skill_dir.is_dir():
            found.append(f"{rel_dir}: 实验 Skill 不存在")
            continue
        for rel in ("SKILL.md", "LICENSE", "agents/openai.yaml", *EXPERIMENT_REQUIRED_FILES.get(name, ())):
            path = skill_dir / rel
            rel_path = f"{rel_dir}/{rel}"
            if not path.is_file():
                found.append(f"{rel_path}: 缺少实验执行资产")
            elif rel_path not in tracked_paths:
                found.append(f"{rel_path}: 未追踪")
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.is_file():
            continue
        text = skill_path.read_text(encoding="utf-8")
        for marker in EXPERIMENT_TEXT_MARKERS.get(name, ()):
            if marker not in text:
                found.append(f"{rel_dir}/SKILL.md: 缺「{marker}」")
        for marker in EXPERIMENT_MANDATE_MARKERS:
            if marker not in text:
                found.append(f"{rel_dir}/SKILL.md: 缺单装委托合同引用/失效处理「{marker}」")
        mandate_copy = skill_dir / "references" / "mandate.md"
        canonical_mandate = root / "skills/general/research-os/references/mandate.md"
        if mandate_copy.is_file() and canonical_mandate.is_file():
            copy_text = mandate_copy.read_text(encoding="utf-8")
            canonical_text = canonical_mandate.read_text(encoding="utf-8")
            if packaged_mandate_text is None:
                packaged_mandate_text = copy_text
            elif copy_text != packaged_mandate_text:
                found.append(f"{rel_dir}/references/mandate.md: 分发副本与其他实验叶不一致")
            for marker in EXPERIMENT_MANDATE_PACKAGE_MARKERS:
                if marker not in canonical_text:
                    found.append(f"skills/general/research-os/references/mandate.md: 权威合同缺「{marker}」")
                if marker not in copy_text:
                    found.append(f"{rel_dir}/references/mandate.md: 单装合同缺「{marker}」")
            if "本文件摘录自唯一规范源 `skills/general/research-os/references/mandate.md`" not in copy_text:
                found.append(f"{rel_dir}/references/mandate.md: 缺规范源与分发副本关系")
        elif not mandate_copy.is_file():
            found.append(f"{rel_dir}/references/mandate.md: 缺单装委托合同资源")
        elif not canonical_mandate.is_file():
            found.append("skills/general/research-os/references/mandate.md: 委托唯一权威缺失或未追踪")
        companions = EXPERIMENT_COMPANION_DEPENDENCIES.get(name, ())
        if companions:
            dependency_header = "## 联装能力依赖"
            if dependency_header not in text:
                found.append(f"{rel_dir}/SKILL.md: 缺联装能力依赖声明")
            else:
                dependency_body = text.split(dependency_header, 1)[1].split("\n## ", 1)[0]
                for companion in companions:
                    if f"`{companion}`" not in dependency_body:
                        found.append(f"{rel_dir}/SKILL.md: 未声明联装依赖 {companion}")
                if "缺失时标为 `blocked`" not in dependency_body:
                    found.append(f"{rel_dir}/SKILL.md: 缺联装能力缺失时的 blocked 行为")
                if "npx skills add <repo>" not in dependency_body:
                    found.append(f"{rel_dir}/SKILL.md: 缺联装能力补装命令")
        if "委托继承" not in heading_anchors(text):
            found.append(f"{rel_dir}/SKILL.md: 缺「委托继承」小节")
        if re.search(r"(?m)^Gate:", text):
            found.append(f"{rel_dir}/SKILL.md: 已迁移实验能力残留旧门")
        for binding in EXPERIMENT_HOST_BINDINGS:
            if binding in text:
                found.append(f"{rel_dir}/SKILL.md: 宿主绑定残留 {binding}")
        if EXPERIMENT_MODEL_PIN.search(text):
            found.append(f"{rel_dir}/SKILL.md: 固定模型绑定")
        yaml_path = skill_dir / "agents" / "openai.yaml"
        if yaml_path.is_file() and yaml_allow_implicit(yaml_path.read_text(encoding="utf-8")) != "false":
            found.append(f"{rel_dir}/agents/openai.yaml: allow_implicit_invocation 必须为 false")
        if f"{rel_dir}/SKILL.md" not in MIGRATED_CONTRACT:
            found.append(f"{rel_dir}/SKILL.md: 未登记迁移状态")
        for rel, markers in EXPERIMENT_FILE_MARKERS.items():
            if not rel.startswith(f"{name}/"):
                continue
            path = base / rel
            if not path.is_file():
                asset_path = f"skills/validation-cycle/{rel}"
                message = f"{asset_path}: 缺少实验执行资产"
                if message not in found:
                    found.append(message)
                continue
            body = path.read_text(encoding="utf-8")
            for marker in markers:
                if marker not in body:
                    found.append(f"skills/validation-cycle/{rel}: 缺「{marker}」")
    mandate = root / "skills/general/research-os/references/mandate.md"
    if not mandate.is_file() or "skills/general/research-os/references/mandate.md" not in tracked_paths:
        found.append("skills/general/research-os/references/mandate.md: 委托唯一权威缺失或未追踪")

    # The repository-wide link check validates files; validate fragments as well
    # for all nine shipped experiment skills, including same-file anchors.
    for name in EXPERIMENT_SKILLS:
        skill_dir = base / name
        if not skill_dir.is_dir():
            continue
        for markdown in skill_dir.rglob("*.md"):
            rel_markdown = markdown.relative_to(root).as_posix()
            lines = markdown.read_text(encoding="utf-8").splitlines()
            for line_number, line in enumerate(lines, 1):
                for target in link_re.findall(line):
                    if target.startswith(("http://", "https://", "mailto:")):
                        continue
                    file_part, separator, fragment = target.partition("#")
                    if not separator or not fragment:
                        fragment = ""
                    if not file_part:
                        target_markdown = markdown
                    else:
                        resolved = lexical_relative(markdown.parent, unquote(file_part))
                        if resolved is None:
                            continue
                        target_markdown = Path(resolved)
                    try:
                        target_markdown.relative_to(skill_dir)
                    except ValueError:
                        found.append(
                            f"{rel_markdown}:{line_number}: 单装时不可解析的跨叶 Markdown 引用 {target}"
                        )
                    if not target_markdown.is_file():
                        continue  # Missing paths are reported by the repository-wide link check.
                    if not fragment:
                        continue
                    anchor = unquote(fragment)
                    if anchor not in heading_anchors(target_markdown.read_text(encoding="utf-8")):
                        found.append(
                            f"{rel_markdown}:{line_number}: 无效 Markdown fragment #{anchor}"
                        )
    run_text = base / "run-experiment" / "SKILL.md"
    if run_text.is_file():
        run_body = run_text.read_text(encoding="utf-8")
        if "../experiment-bridge/SKILL.md" in run_body:
            found.append("skills/validation-cycle/run-experiment/SKILL.md: 仍依赖旧桥接控制器")
        if "唯一实验执行控制" not in run_body:
            found.append("skills/validation-cycle/run-experiment/SKILL.md: 未声明唯一执行控制")
        if "仓库中的 `experiment-queue`" not in run_body or "单装 `run-experiment` 时" not in run_body:
            found.append("skills/validation-cycle/run-experiment/SKILL.md: 缺批量队列可用性边界")
        for marker in EXPERIMENT_AUTHORIZATION_MARKERS:
            if marker not in run_body:
                found.append(f"skills/validation-cycle/run-experiment/SKILL.md: 缺批次授权合同「{marker}」")
    bridge_playbook = root / EXPERIMENT_BRIDGE_PLAYBOOK
    if bridge_playbook.is_file():
        playbook = bridge_playbook.read_text(encoding="utf-8")
        for marker in (
            "skills/validation-cycle/run-experiment/SKILL.md", "唯一执行控制",
            "monitor-experiment", "training-health-check", "analyze-results",
            "experiment-audit", "result-to-claim",
        ):
            if marker not in playbook:
                found.append(f"{EXPERIMENT_BRIDGE_PLAYBOOK}: 缺能力路由 {marker}")
        for marker in (
            "skills/validation-cycle/experiment-bridge/SKILL.md", "-s experiment-bridge",
            "/experiment-bridge",
        ):
            if marker in playbook:
                found.append(f"{EXPERIMENT_BRIDGE_PLAYBOOK}: 残留旧 Skill 调用或安装 slug {marker}")
        for marker in ("run_count_basis=planned-run", "每个 attempt 先记最坏预留"):
            if marker in playbook:
                found.append(f"{EXPERIMENT_BRIDGE_PLAYBOOK}: 桥接 playbook 重复执行控制合同 {marker}")
    else:
        found.append(f"{EXPERIMENT_BRIDGE_PLAYBOOK}: playbook 不存在")
    active_route_docs = (
        "README.md", "docs/README-en.md", "docs/user-acceptance-guide.md", "skills/README.md",
        "skills/general/research-os/SKILL.md",
        "skills/general/research-os/references/PRODUCT-MAP.md",
        "skills/general/research-os/references/validation.md",
        "skills/general/research-os/references/migration-boundary.md",
        "skills/general/research-os/references/batch-authorization.md",
        EXPERIMENT_BRIDGE_PLAYBOOK,
    )
    for relative in active_route_docs:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in (
            "skills/validation-cycle/experiment-bridge/SKILL.md", "-s experiment-bridge",
        ):
            if marker in text:
                found.append(f"{relative}: 残留旧 Skill 路径或安装 slug {marker}")
        if re.search(r"(?m)^\s*/experiment-bridge\b", text):
            found.append(f"{relative}: 残留旧 /experiment-bridge 可调用入口")
    boundary = root / MIGRATION_DOC
    if boundary.is_file():
        boundary_text = boundary.read_text(encoding="utf-8")
        for name in EXPERIMENT_SKILLS:
            if name not in boundary_text:
                found.append(f"{MIGRATION_DOC}: 未列出实验能力 {name}")
    return found


for sf in skill_files:
    rel = sf.relative_to(ROOT).as_posix()
    expected = expected_gates(sf.parent, sf.parent.name)
    if expected is None:
        err(f"{rel}: 缺少门声明基线")
        continue
    body = sf.read_text(encoding="utf-8").split("---", 2)[-1]
    for problem in gate_problems(sf.parent.name, sf.parent, body, expected, tracked):
        err(f"{rel}: {problem}")

# --- arena 阶段保真（#51）：六阶段机制不得静默丢失 ---
ARENA_REL = "skills/organization/arena/SKILL.md"
ARENA_PHASES = ("Frame", "Fan-out", "Cross-judge", "Pick", "Graft", "Verify")
ARENA_UPSTREAM_REMNANTS = ("~/.cursor", "pstack-models.mdc")


def arena_contract_problems(root: Path) -> list[str]:
    found: list[str] = []
    path = root / ARENA_REL
    if not path.is_file():
        return [f"{ARENA_REL}: arena 技能不存在"]
    text = path.read_text(encoding="utf-8")
    for phase in ARENA_PHASES:
        if phase not in text:
            found.append(f"{ARENA_REL}: arena 缺阶段 {phase}")
    for token in ARENA_UPSTREAM_REMNANTS:
        if token in text:
            found.append(f"{ARENA_REL}: arena 残留上游宿主绑定 {token}")
    if "swarm" in arena_required_dependencies(text):
        found.append(f"{ARENA_REL}: arena 声明必需依赖 swarm，不独立")
    return found


for problem in migration_contract_problems(ROOT, tracked):
    err(problem)
for problem in continuation_contract_problems(ROOT, tracked):
    err(problem)
for problem in ticket59_contract_problems(ROOT, tracked):
    err(problem)
for problem in formal_verification_problems(ROOT, tracked):
    err(problem)
for problem in verification_skill_problems(ROOT, tracked):
    err(problem)
for problem in experiment_execution_problems(ROOT, tracked):
    err(problem)

for problem in arena_contract_problems(ROOT):
    err(problem)

for problem in research_asset_problems(ROOT, tracked):
    err(problem)


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
    repeatable = {"compute_limit", "compute_unit", "per_attempt_compute_limit"}
    for key, values in fields.items():
        if key not in POLICY_KEYS:
            err(f"{path}: 政策含未知字段 {key}")
        if key not in repeatable and len(values) != 1:
            err(f"{path}: 政策字段必须唯一 {key}")
        if any(not raw for raw in values):
            err(f"{path}: 政策字段不能为空 {key}")
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
    numeric_keys = {"cost_limit", "compute_limit", "run_limit", "per_attempt_cost_limit",
                    "per_attempt_compute_limit", "concurrency_limit", "retry_limit", "valid_for_hours"}
    zero_default = all(finite_number(raw) == 0 for key in numeric_keys for raw in fields.get(key, []))
    inactive_policy = all(finite_number(raw) == 0 for key in ("run_limit", "valid_for_hours")
                          for raw in fields.get(key, []))
    explained = "因为" in text or "because" in text.lower()
    for key in ("currency", "scope", "valid_until"):
        for raw in fields.get(key, []):
            if raw == "未指定":
                if not inactive_policy:
                    err(f"{path}: {key} 未指定只适用于不可执行默认政策，不是运行许可")
                continue
            if raw == "not-applicable":
                if not explained:
                    err(f"{path}: {key}=not-applicable 必须解释")
                if key == "currency" and any(value != 0 for value in numbers.get("cost_limit", [])):
                    err(f"{path}: currency=not-applicable 只适用于零费用")
                if key == "valid_until" and not zero_default:
                    err(f"{path}: 可执行批次不能以 not-applicable 省略 valid_until")
                continue
            if key == "scope" and (finite_number(raw) is not None or raw.lower() in {"true", "false", "null", "none"}):
                err(f"{path}: scope 必须是说明计划、写域和环境的非空文字")
            if key == "currency" and not re.fullmatch(r"[A-Z]{3}", raw):
                err(f"{path}: currency 必须是三字母大写币种或解释过的 not-applicable")
            if key == "valid_until":
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", raw):
                        raise ValueError
                    if raw[-1] != "Z" and (int(raw[-5:-3]) > 23 or int(raw[-2:]) > 59):
                        raise ValueError
                    value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                    if value.utcoffset() is None:
                        raise ValueError
                except ValueError:
                    err(f"{path}: valid_until 必须是合法且带时区的 ISO8601 时间")
    runs = [finite_number(raw) for raw in fields.get("run_limit", [])]
    concurrency = [finite_number(raw) for raw in fields.get("concurrency_limit", [])]
    if any(value is not None and value > 0 for value in runs) and not all(
        value is not None and value >= 1 for value in concurrency
    ):
        err(f"{path}: 可执行批次 concurrency_limit 至少为 1")
    costs = numbers.get("cost_limit", [])
    per_costs = numbers.get("per_attempt_cost_limit", [])
    if costs and per_costs and max(per_costs) > min(costs):
        err(f"{path}: 单次超过累计上限")
    units = fields.get("compute_unit", [])
    if len(units) != len(set(units)):
        err(f"{path}: compute_unit 重复，异构额度必须按不同单位分行")
    if len(fields.get("compute_limit", [])) != len(fields.get("per_attempt_compute_limit", [])):
        err(f"{path}: compute_limit 与 per_attempt_compute_limit 必须按单位逐行配对")
    # 使用原字段位置，非法数值不能让后续单位错位；CPU/GPU 从不求和。
    for index, (raw_limit, raw_per) in enumerate(zip(
        fields.get("compute_limit", []), fields.get("per_attempt_compute_limit", []), strict=False
    )):
        limit, per_attempt = finite_number(raw_limit), finite_number(raw_per)
        if limit is not None and per_attempt is not None and per_attempt > limit:
            unit = units[index] if index < len(units) else "无单位"
            err(f"{path}: 第 {index + 1} 行 {unit} 单次超过累计上限")
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


def check_gates(skill_dir: Path, skill_name: str) -> None:
    expected = expected_gates(skill_dir, skill_name)
    if expected is None:
        err(f"{skill_name}: 门声明不在已审阅基线")
        return
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        err(f"{skill_name}: SKILL.md 不存在")
        return
    body = skill_file.read_text(encoding="utf-8").split("---", 2)[-1]
    for problem in gate_problems(skill_name, skill_dir, body, frozenset(expected)):
        err(problem)


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
    parser = argparse.ArgumentParser(
        description="Research OS skill 与配置合同检查",
        epilog="静态检查只核结构/可解析声明及有限明确违约；自然语言的隐式依赖、阶段顺序、共享额度完整语义仍须人工核验。结构通过不证明模型遵从或科研正确性。",
    )
    parser.add_argument(
        "--archive-scope", choices=("structure", "history"), default="structure",
        help="默认检查归档索引结构；history 另要求每包历史 SHA/字节完整（不认证来源/安全）",
    )
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




def run_builtin_contract() -> None:
    setup_dir = SKILLS / "general" / "setup-research-os"
    roles = check_role_file(
        setup_dir / "templates" / "research-os-models.md", "research-os-models.md"
    )
    check_role_refs([path for path in md_files if path.relative_to(ROOT).as_posix() in tracked
                     and path.is_relative_to(SKILLS)], roles)
    check_policy(setup_dir / "templates" / "compute-policy.md")
    check_log(setup_dir / "templates" / "research-log.md", {})
    check_gates(SKILLS / "general" / "setup-research-os", "setup-research-os")



def main() -> int:
    args = parse_args()
    check_archive_index(strict=args.archive_scope == "history")
    if args.skip_suite:
        run_contract(args)
    else:
        run_builtin_contract()
        run_contract(args)
    if problems:
        print(f"FAIL: {len(problems)} 个问题")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    u_count = sum(1 for value in classifications.values() if value == "U")
    m_count = sum(1 for value in classifications.values() if value == "M")
    print(
        f"OK: {len(skill_files)} 个 Skill（U {u_count} / M {m_count}），调用策略与门声明通过"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
