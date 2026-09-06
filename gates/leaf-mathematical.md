# Gates: Mathematical and Lean slice
Scope: 普通证明、独立审查、可选 Lean 与固定 reference project。

P0 Lean 支持边界：能力为 `isolated-rebuild`，仅无外部依赖、可信执行环境、封闭 Nat/Eq 等 builtin 常量命题。非空依赖、path dependency、自定义类型环境、编译产物/cache 输入均 fail-closed；不声称完整 trusted-base 固定、恶意并发安全或 principal 身份认证。receipt 显式记录 `principal_attestation=caller-declared`、`toolchain_scope=direct-executables-only`、`toctou_model=non-adversarial`。每阶段 digest 检查用于发现正常执行漂移；新鲜树不复制 `.git` 或 build cache。单元/mock 全绿不能签发真实 Lean E2E。最终顾问条件复核要求已以支持范围收紧及负例闭环；未声明 closure 失败也保留实际源码，预算先于 candidate snapshot。
- [x] G1: mathematical tests pass
  CHECK: uv --project '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' run python -m unittest discover -s '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/tests/mathematical' -t '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' -v
  EXPECT: OK
  EVIDENCE: 2026-09-06，最终 uv discover：Ran 52 tests in 0.540s | OK。起始指定树为 26 tests OK，`_make_result` 已存在，未复现旧 7 errors；新增 hostile 回归真实 RED→GREEN。
- [x] G2: math-proof 实现 examples/counterexamples、statement candidate/确认/revision 重确认、lemma map、有界 attempts、proof gaps、准确停止原因
  CHECK: uv --project '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' run python -m unittest discover -s '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/tests/mathematical' -t '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' -p 'test_math_proof.py' -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 hostile regression RED→GREEN；Ran 11 tests in 0.002s | OK。lemma open/gap、candidate 自带 gap、历史未闭合 gap/反例均阻断 candidate；重算 digest 仍不能绕过结果/历史一致性；bool revision/budget 拒绝。全量 mathematical：Ran 50 tests in 0.507s | OK。
- [x] G3: independent proof review 固定 subject、独立 principal、隔离输入 receipt；不得自我确认或继承旧 revision
  CHECK: uv --project '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' run python -m unittest discover -s '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/tests/mathematical' -t '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' -p 'test_math_review.py' -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 hostile regression RED→GREEN；Ran 11 tests in 0.017s | OK。必填 project_root；精确两份真实 statement/proof，安全相对常规文件、SHA-256 实际 bytes、typed target/revision；拒绝路径逃逸/symlink/重复/额外/缺失输入、重签伪造 receipt、自审/user 审、history access、bool revision 与旧 revision 继承。顾问复核发现的反例 attempt 和 bool revision 漏洞已补回归修复。
- [x] G4: lean-formalize 仅在显式授权且 statement 已确认、普通证明存在、独立 review 已执行时运行；statement 不得替换或弱化
  CHECK: uv --project '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' run python -m unittest discover -s '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/tests/mathematical' -t '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' -p 'test_lean_formalize.py' -v
  EXPECT: OK
  EVIDENCE: 2026-09-06，Lean/audit/security/blocked/reference 专项 30 tests in 0.629s | OK；review fail/inconclusive 在 tooling 前阻断；实际 review 文件 bytes 重验；bool revision/exit 拒绝；statement lexical mismatch 与 kernel elaborated type mismatch 均独立失败。
- [x] G5: Lean toolchain lock、lake build、placeholder/sorry、axiom/import audit、statement comparator、metadata validation 与 kernel replay 已实现
  CHECK: uv --project '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' run python -m unittest discover -s '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/tests/mathematical' -t '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' -p 'test_lean_audit.py' -v
  EXPECT: OK
  EVIDENCE: 2026-09-06，专项 30 tests OK。全项目 Lean sources 保守覆盖 imports closure/build targets、嵌套 Lake config/toolchain/manifest 锁定；原树与隔离树均执行固定目标 type/axiom probe；每阶段 source/tool executable digest 检查；不同 principal 标签与新鲜无 cache 文件树；request/candidate/实际源码/失败 command/report 以独占创建留存。mock 只验证协议逻辑，不是 Lean kernel E2E PASS。
- [x] G6: Lean 不可用时准确返回结构化 BLOCKED/退出码 3；普通 math-proof 不强制 Lean
  CHECK: uv --project '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' run python -m unittest discover -s '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/tests/mathematical' -t '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' -p 'test_blocked_semantics.py' -v
  EXPECT: OK
  EVIDENCE: Ran 3 tests in 0.228s | OK
- [x] G7: 固定 Lean reference fixture 在可用固定工具链中真实 build/audit/comparator/kernel replay；独立 replay receipt 可复核，BLOCKED 不冒充发布 PASS
  CHECK: cd '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' && env ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin RESEARCH_OS_REQUIRE_LEAN=1 uv run --frozen python -m unittest tests.mathematical.test_reference_fixture -v
  EXPECT: OK
  EVIDENCE: 2026-09-06 真实官方 elan 隔离工具链 PASS：Lean 4.19.0 commit 6caaee842e94；Lake 5.0.0-6caaee8。reference 3 tests / OK；真实 `lake build` 输出目标 axiom-free；release 流程 result=verified、audit=pass、kernel replay=pass，且至少记录 8 条真实命令。精确账本见 `gates/leaf-lean419-reference.md`。
- [x] G8: owned files 无 TODO/placeholder，且四遍（实现、专家复读、缺陷猎杀、打磨）记录完整
  CHECK: ! rg -n 'NotImplementedError|^\s*pass\s*(#.*)?$' '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/core/skills/math-proof' '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/core/skills/lean-formalize' '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/src/research_os/workflows/mathematical' '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/templates/mathematical' '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/reference-projects/mathematical' '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/tests/mathematical'
  EXPECT: exit 0
  EVIDENCE: `rg` returned 1 (no matches); four passes recorded in `/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/src/research_os/workflows/mathematical/mathematical-implementation-notes.md`.
