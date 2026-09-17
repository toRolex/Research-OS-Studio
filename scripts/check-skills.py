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
    fm_body = "\n".join(l for l in fm_lines if not l.lstrip().startswith("#"))

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
    has_openai_yaml = (sf.parent / "agents" / "openai.yaml").exists()
    if user_invoked and not has_openai_yaml:
        err(f"{rel}: User-invoked 但缺 agents/openai.yaml")
    if not user_invoked and has_openai_yaml:
        err(f"{rel}: model-invoked 但存在 agents/openai.yaml")
    classifications[rel] = "U" if user_invoked else "M"

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

# --- 结果 -------------------------------------------------------------------
if problems:
    print(f"FAIL: {len(problems)} 个问题")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)

u_count = sum(1 for v in classifications.values() if v == "U")
m_count = sum(1 for v in classifications.values() if v == "M")
print(f"OK: {len(skill_files)} 个 Skill（U {u_count} / M {m_count}），全部检查通过")
