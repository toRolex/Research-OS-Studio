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
"""
import argparse
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
EXPECTED_COUNT = 39
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


def yaml_allow_implicit(yaml_text: str | None) -> str | None:
    if yaml_text is None:
        return None
    match = re.search(
        r"^\s*allow_implicit_invocation\s*:\s*(\S+)\s*$",
        yaml_text,
        re.M,
    )
    return match.group(1).strip().strip("'\"") if match else None


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

    explicit = "disable-model-invocation: true" in fm_body
    openai_yaml = sf.parent / "agents" / "openai.yaml"
    has_openai_yaml = openai_yaml.exists()
    yaml_text = openai_yaml.read_text(encoding="utf-8") if has_openai_yaml else None
    implicit = yaml_allow_implicit(yaml_text)
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


PAPER_WRITING_SHARED = (
    "skills/writing-cycle/paper-plan/SKILL.md",
    "skills/writing-cycle/academic-plotting/SKILL.md",
    "skills/writing-cycle/paper-drafting/SKILL.md",
    "skills/writing-cycle/paper-compile/SKILL.md",
    "skills/writing-cycle/paper-claim-audit/SKILL.md",
    "skills/writing-cycle/citation-audit/SKILL.md",
    "skills/writing-cycle/claim-stress-test/SKILL.md",
    "skills/validation-cycle/proof-review/SKILL.md",
)
PAPER_WRITING_REQUIRED: dict[str, tuple[str, ...]] = {
    "general": PAPER_WRITING_SHARED
    + (
        "skills/writing-cycle/paper-writing/SKILL.md",
        "skills/writing-cycle/paper-writing/references/composition-map.md",
    ),
    "ml": PAPER_WRITING_SHARED
    + (
        "skills/writing-cycle/ml-paper-writing/SKILL.md",
        "skills/writing-cycle/ml-paper-writing/references/composition-map.md",
        "skills/writing-cycle/ml-paper-writing/references/experiment-reporting.md",
        "skills/writing-cycle/ml-paper-writing/references/reviewer-expectations.md",
        "skills/writing-cycle/ml-paper-writing/references/venue-checklists.md",
    ),
    "systems": PAPER_WRITING_SHARED
    + (
        "skills/writing-cycle/systems-paper-writing/SKILL.md",
        "skills/writing-cycle/systems-paper-writing/references/composition-map.md",
        "skills/writing-cycle/systems-paper-writing/references/systems-writing-methods.md",
        "skills/writing-cycle/systems-paper-writing/references/evaluation-methods.md",
        "skills/writing-cycle/systems-paper-writing/references/checklist.md",
        "skills/writing-cycle/systems-paper-writing/references/venue-and-reviewer.md",
        "skills/writing-cycle/paper-plan/references/systems-blueprints.md",
        "skills/writing-cycle/paper-plan/references/systems-patterns.md",
    ),
}
PAPER_WRITING_FORBIDDEN: dict[str, tuple[str, ...]] = {
    "general": (
        "skills/writing-cycle/ml-paper-writing/SKILL.md",
        "skills/writing-cycle/systems-paper-writing/SKILL.md",
    ),
    "ml": (
        "skills/writing-cycle/paper-writing/SKILL.md",
        "skills/writing-cycle/systems-paper-writing/SKILL.md",
    ),
    "systems": (
        "skills/writing-cycle/paper-writing/SKILL.md",
        "skills/writing-cycle/ml-paper-writing/SKILL.md",
    ),
}
PAPER_WRITING_HARD_STOPS = ("paper-compile-repair", "apply-citation-fixes")


def paper_writing_variant_problems(variant: str, text: str, root: Path) -> list[str]:
    """单个 paper-writing playbook：本变体级联存在，且不经其他写作入口。"""
    found: list[str] = []
    required = PAPER_WRITING_REQUIRED.get(variant)
    if required is None:
        return [f"paper-writing 变体未知：{variant}"]
    for path in required:
        if f"`{path}`" not in text:
            found.append(f"paper-writing/{variant} 缺级联 {path}")
        elif not (root / path).is_file():
            found.append(f"paper-writing/{variant} 级联目标不存在：{path}")
    for path in PAPER_WRITING_FORBIDDEN[variant]:
        if f"`{path}`" in text:
            found.append(f"paper-writing/{variant} 不得级联其他写作入口：{path}")
    for name in PAPER_WRITING_HARD_STOPS:
        if f"`{name}`" not in text:
            found.append(f"paper-writing/{variant} 缺另行点名硬停止：{name}")
    if "授权" not in text:
        found.append(f"paper-writing/{variant} 未保留叶授权门")
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
    for variant in ("general", "ml", "systems"):
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
        if LEGACY_ROUTER not in text:
            continue
        if any(token in text.lower() or token in text for token in LEGACY_ALLOW_MIGRATION):
            continue
        found.append(f"{rel}: 产品正文残留旧 router {LEGACY_ROUTER}")
    return found


REQUIRED_RELEASE_ROUTES = (
    ("route-only", "—", "yes"),
    ("idea-discovery", "—", "no"),
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
)
STALE_PROMISE_SNIPPETS = (
    "完成后立即停止，绝不自动跳转",
    "No Automatic Chaining",
)
HOST_FALLBACK_MARKERS = ("pi", "Claude Code", "Codex", "串行")


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


def host_fallback_problems(text: str) -> list[str]:
    """宿主映射必须点名三宿主，并写明无子代理时串行执行。"""
    found: list[str] = []
    for marker in HOST_FALLBACK_MARKERS:
        if marker not in text:
            found.append(f"宿主映射缺 {marker}")
    if "无该工具时由编排者串行执行" not in text and "没有时，编排者按 playbook 顺序自己执行" not in text:
        found.append("宿主映射未写无子代理时的串行降级")
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
    for problem in host_fallback_problems(research_os.read_text(encoding="utf-8")):
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
for problem in stale_promise_problems(legacy_files):
    err(problem)


# --- 叶 skill 门声明（#39 基线）；入口与 setup 不进这份路径表 ---
LEAF_EXPECTED_GATES: dict[str, set[str]] = {
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
    "skills/general/research-os/SKILL.md",
}




for sf in skill_files:
    rel = sf.relative_to(ROOT).as_posix()
    if rel not in LEAF_EXPECTED_GATES:
        if rel not in GATE_SKIP:
            err(f"{rel}: 缺少门声明基线")
        continue
    body = sf.read_text(encoding="utf-8").split("---", 2)[-1]
    for problem in gate_problems(sf.parent.name, sf.parent, body, frozenset(LEAF_EXPECTED_GATES[rel]), tracked):
        err(f"{rel}: {problem}")


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
    expected = GATE_BASELINE.get(skill_name)
    if expected is None:
        expected = EXPECTED_GATES.get(skill_name)
    if expected is None:
        expected = LEAF_EXPECTED_GATES.get(f"skills/{skill_dir.parent.name}/{skill_name}/SKILL.md")
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
