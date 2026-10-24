#!/usr/bin/env python3
"""特征映射一致性检查 helper（#53 随附，MIT，随 create-verification-skill 发行）。

用法::

    python3 feature-map-lint.py <features 目录>

检查两条合同：

1. 特征目录里除索引 README.md 外的每个 ``*.md`` 都被索引（README.md）的非注释链接引用；
2. 索引里的每个相对链接都指向存在的特征文件。

发现孤儿特征文件或死链时以退出码 1 报告；一致时退出码 0。只做结构一致性
检查，不执行应用、不证明特征行为成立。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

MD_LINK = re.compile(r"\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")


def local_markdown_path(destination: str) -> str | None:
    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc or not parsed.path.lower().endswith(".md"):
        return None
    path = unquote(parsed.path)
    if not path or Path(path).is_absolute():
        return None
    return path


def lint(features_dir: Path) -> list[str]:
    index = features_dir / "README.md"
    if not index.is_file():
        return [f"{features_dir}: 缺索引 README.md"]
    text = re.sub(r"<!--.*?(?:-->|\Z)", "", index.read_text(encoding="utf-8"), flags=re.S)
    linked = set[str]()
    problems: list[str] = []
    for match in MD_LINK.finditer(text):
        destination = match.group(1) or match.group(2)
        target = local_markdown_path(destination)
        if target is None:
            continue
        resolved = (features_dir / target).resolve()
        if not resolved.is_file():
            problems.append(f"索引链接不存在: {destination}")
            continue
        linked.add(Path(target).as_posix())
    for feature in sorted(features_dir.glob("*.md")):
        if feature.name == "README.md":
            continue
        if feature.name not in linked:
            problems.append(f"特征文件未被索引链接: {feature.name}")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    problems = lint(Path(argv[1]))
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
