# Gates: Domain semantics
Scope: Project/Workstream/Claim/Evidence/relation/Assessment/Assurance/migration。
- [x] G1: semantics tests pass
  CHECK: uv run python -m unittest discover -s tests/contracts/semantics -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 hostile review 后实跑 34 tests；`Ran 34 tests in 0.073s`，最终 `OK`。
- [x] G2: relation、scope conflict、revision isolation、identity、pinning 与 migration negative paths 被机械拒绝
  EVIDENCE: hostile 复现确认并修复 5 类真实缺陷：原 suite 自身 2 个空绿/过时正例；semantics JSON schemas 无可执行入口；target profile 接受非 canonical URI/带空白路径；fixed ref 仅校验自报 commit/digest 且未拒绝 symlink blob；Assessment evidence 与 migration receipt 可仅靠自报。每类均有独立测试，位于 `tests/contracts/semantics/test_semantics.py` 的 `HostileContractTests` 或对应原测试。
- [x] G3: schemas and Python modules are mechanically loadable
  CHECK: uv run python -m compileall -q src/research_os/validation/semantics tests/contracts/semantics
  EXPECT: exit 0
  EVIDENCE: 2026-09-06 实跑 exit 0；新增 `SemanticsSchemaValidator` 离线执行 7 类 semantics schema/type dispatcher，hostile 正例矩阵通过；`git diff --check` 对允许范围 exit 0。
- [x] G4: hostile security and control review complete
  EVIDENCE: fixed Git ref 的 trust-validation 模式无 repository context 即 fail closed；有 context 时使用 `git ls-tree` + `git cat-file blob` 读取指定 commit 字节，不信任工作树，拒绝 symlink/tree 并核对 SHA-256；canonical target 复用 foundation profile；Assessment 默认要求 Project/digest 与 Evidence context；migration receipt 无 rule/input/output context 必 fail。语义 leaf 无 workflow 推进实现，扫描未发现 provider 配置或自动 next-workflow 声明。未执行任何外部环境，因此未记录外部 PASS；本 leaf 不声明外部能力支持。
- [x] G5: expert reread / defect hunt / polish complete
  EVIDENCE: 复读 PLAN.md、Issue #24、全部 leaf 源码/schema/tests 与实际 worktree diff；修复保持在允许目录；未 commit/push。
