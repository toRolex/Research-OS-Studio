# v2 release doc sweep fix

## Scope / decisions
- Base tip `5efd2da`。完整读 README 中英、ticket46 tests、stale_promise_problems、approved shared contract 与本地 #37 缓存；不 gh/commit/global/main，不编辑 acceptance。
- 仅改两 doc、既有 checker/test46；独立日志 `/tmp/ros-v2-release-doc-sweep`。
- 复用已有 literal sweep，补真实残留措辞，不引入新 validator，不泛匹配叶级停止。
- 安全全测试 agent 已通知；完成后要求重测。

## TDD
- RED：先新增真实两句损坏 README 副本回归（两个 subtest）与合法叶停止正例；`uv run python -m unittest discover -s scripts -p test_check_skills_ticket46.py -v` exit 1，恰好两真实措辞反例失败。日志 `red.log`。
- GREEN：仅向现 stale_promise_problems 使用的 STALE_PROMISE_SNIPPETS 加两条原句，修两 doc 对应单行；同命令 8/8 OK。日志 `green.log`。
- `uv run python scripts/check-skills.py` exit 0：39 Skill（U38 / M1）；日志 `checker.log`。`git diff --check` 通过，两个 Python active LSP 零诊断。
- 四文件编辑结束时已通知 security agent 最终版重测全 tests；未自行声明它的全套结果。

## Risks
- 仍是窄 literal 检测，不声称能发现所有自然语言同义旧承诺；保留叶交付停止，不把合法停止泛判为错误。
- 静态绿不证明运行时三类门或跨阶段行为；全套 security 重测由并行 agent 汇报。

## Deviations
- 无。
