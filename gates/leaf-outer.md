# Gates: Outer workflows
Scope: 六个外循环 workflow 完整契约与显式停止。
- [x] G1: outer workflow tests pass
  CHECK: uv run python -m unittest discover -s tests/workflows/outer -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 hostile review 后在仓库根运行；20 tests，Ran 20 tests in 0.039s，OK。`uv run ruff check src/research_os/workflows/outer tests/workflows/outer` 为 `All checks passed!`；`git diff --check` 无输出。
- [x] G2: 每个 workflow 只读 pinned input，输出 candidate/report/options 后停止且不推进下一 workflow
  EVIDENCE: `tests/workflows/outer/test_outer_workflows.py` 20 个 public-seam 测试覆盖六 workflow 的 candidate/report/next_steps/显式停止；输入 SHA-256、type、顺序、唯一性、Artifact envelope 与 target/path 一致性；Charter 用户拥有 question/boundaries/success criteria/budget/invariants；gap evidence 只能逐项匹配 pinned citations；idea/novelty 多候选必须显式选择；candidate 未知字段和 nested provider 字段拒绝；预算超限、空边界、pin 错误、错误 type、未固定材料、覆盖、late collision、input symlink swap、publish 前 symlink swap、路径逃逸均失败且不冒充支持。报告固定 `status=stopped`、`automatic_next_workflow=false`、`human_acceptance=null`。未运行任何外部环境，因此无外部环境 PASS 声明。
- [x] G3: hostile review 无遗留 blocker/high
  EVIDENCE: 初次实际运行 16 tests 有 6 failures，证明旧 gate 的 9-test PASS 已过时。独立复现并修复：Artifact envelope/target 接受集过宽；gap 可引用未固定 evidence；idea/novelty 隐式首项推进；candidate 数量被静默截断；reflection 忽略 candidate 且预算计数失真；Charter 可改用户边界/成功标准/预算/invariants；candidate/provider 未知字段泄漏；输入读取及输出 publish 的 symlink/TOCTOU。修复后 20/20 通过。外部能力未参与，不使用 BLOCKED 冒充 PASS。
