# Gates: Lean 4.19 real reference gate

Scope: 在隔离临时 elan 环境安装官方工具链，执行固定数学 reference 的真实 Lean/Lake 正向 gate；必要时仅修复数学/Lean相关文件。

- [x] G1: 官方 elan 安装在项目外临时 ELAN_HOME/CARGO_HOME，且未修改用户全局默认或 PATH 配置
  CHECK: test -x /tmp/research-os-lean419/elan/bin/elan && test "$(shasum -a 256 "$HOME/.elan/settings.toml" | cut -d ' ' -f 1)" = "1b5185e66f865f3af295cb217fdcf86fb3ad8ac3d6886e3c565fb618949c34c3" && test "$(shasum -a 256 "$HOME/.profile" | cut -d ' ' -f 1)" = "1ad600935ee24f2dc8254c80e0e9ec064a5c5d7040f47d97d97742fa263ccf46" && test "$(shasum -a 256 "$HOME/.zprofile" | cut -d ' ' -f 1)" = "bbcf385e4691d979df3c1167dc106cbad239ab9c299bcec46602fa08e7477df5" && test "$(shasum -a 256 "$HOME/.zshrc" | cut -d ' ' -f 1)" = "785a97a2665581a28d019f889b79a293f0f4c154b1e63f4ca75eebdb8e063bff" && env ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 /tmp/research-os-lean419/elan/bin/elan show
  EXPECT: environment override by ELAN_TOOLCHAIN
  EVIDENCE: leanprover/lean4:v4.19.0 (environment override by ELAN_TOOLCHAIN) | Lean (version 4.19.0, arm64-apple-darwin23.6.0, commit 6caaee842e94, Release)

- [x] G2: 隔离环境固定并实际运行 leanprover/lean4:v4.19.0 的 Lean 与 Lake
  CHECK: env ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin /tmp/research-os-lean419/elan/bin/lean --version && env ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin /tmp/research-os-lean419/elan/bin/lake --version
  EXPECT: Lean (version 4.19.0
  EVIDENCE: Lean (version 4.19.0, arm64-apple-darwin23.6.0, commit 6caaee842e94, Release) | Lake version 5.0.0-6caaee8 (Lean version 4.19.0)

- [x] G3: 固定 reference 项目真实 lake build 成功
  CHECK: cd '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/reference-projects/mathematical' && env ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin /tmp/research-os-lean419/elan/bin/lake build
  EXPECT: Build completed successfully
  EVIDENCE: info: ././././ResearchOSMath/Solution.lean:5:0: 'research_os_add_zero' does not depend on any axioms | Build completed successfully.

- [x] G4: release 模式 reference 测试执行真实 build、kernel axiom audit、statement comparator 与独立 replay 并 PASS
  CHECK: cd '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' && env ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin RESEARCH_OS_REQUIRE_LEAN=1 uv run --frozen python -m unittest tests.mathematical.test_reference_fixture -v
  EXPECT: OK
  EVIDENCE: Ran 3 tests in 4.840s | OK

- [x] G5: 完整数学测试在相同隔离工具链可用时通过，普通测试仍不依赖 release 环境变量
  CHECK: cd '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system' && unset RESEARCH_OS_REQUIRE_LEAN; ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin uv run --frozen python -m unittest discover -s tests/mathematical -t . -v
  EXPECT: OK
  EVIDENCE: Ran 55 tests in 2.647s | OK

- [x] G6: 精确安装/验收命令、版本、结果和 retained run 证据写入数学 gate 与实施笔记
  EVIDENCE: `planning/research-os-wayfinder/lean419-reference-implementation-notes.md` 记录官方安装器 SHA-256、隔离安装/固定 toolchain/版本核验/真实 build/release 与全量测试命令。`gates/leaf-mathematical.md` G7 已更新为真实 PASS。release 测试成功报告断言 audit=pass、kernel_replay=pass、commands_recorded>=8；TemporaryDirectory 退出后 retained 路径按设计清理，此生命周期限制已明确记录。
