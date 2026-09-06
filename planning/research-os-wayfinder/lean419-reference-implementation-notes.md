# Lean 4.19 reference gate 实施记录

## 目标

在不修改用户全局默认的前提下，以项目外临时 `ELAN_HOME`/`CARGO_HOME` 安装官方 elan，固定 `leanprover/lean4:v4.19.0`，执行 `reference-projects/mathematical` 的真实 Lean/Lake 正向验收。

## 基线

- 目标工作树：`/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system`。
- reference 锁定 `leanprover/lean4:v4.19.0`、`Lake version 5.0.0`，无外部依赖。
- `tests/mathematical/test_reference_fixture.py` 在 `RESEARCH_OS_REQUIRE_LEAN=1` 时要求真实 `verified`、audit pass、kernel replay pass。
- 安全边界：不执行四个上游社区仓库代码；本任务不访问或运行它们。

## 计划

1. 使用 `/tmp/research-os-lean419` 隔离 elan/cargo 下载与配置。
2. 安装官方 elan，禁用默认 toolchain 与 PATH 修改。
3. 仅在隔离环境安装固定 Lean 4.19.0，核验 Lean/Lake 版本。
4. 先直接执行 reference `lake build`，再以 release 模式运行 reference gate 和完整数学测试。
5. 若出现项目缺陷，先增加回归测试，再做最小修复。
6. 更新 gate/notes，运行 gate checker，并复核未触碰非数学/Lean文件。

## 决策

- 采用 `/tmp/research-os-lean419/elan` 与 `/tmp/research-os-lean419/cargo`；所有命令显式传入环境变量和绝对 executable 路径。
- 安装使用官方 `elan-init.sh`，参数 `--default-toolchain none --no-modify-path -y`；不调用 `elan default`。
- 工具链选择依赖 `ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0` 与 reference 自带 `lean-toolchain`，不修改用户全局设置。
- `Lake version 5.0.0-6caaee8 (Lean version 4.19.0)` 是官方固定工具链真实输出；metadata 保持 base 版本 `Lake version 5.0.0`，运行时仅接受受限的 7–40 位小写十六进制 commit suffix，避免锁定平台展示文本。
- Lake 首次 build 会生成 `lake-manifest.json`。为保持执行期间输入不可变，不放宽 drift 检测；将稳定的零依赖 manifest 作为 reference source 锁定，SHA-256 为 `272ad6c843fd55149d8ec3b9ee23a0e770ff90f6b31516a84db9a107eb09dc1d`。

## 执行记录

### 安装

```bash
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o /tmp/research-os-lean419/downloads/elan-init.sh
ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo sh /tmp/research-os-lean419/downloads/elan-init.sh -y --default-toolchain none --no-modify-path
ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo /tmp/research-os-lean419/elan/bin/elan toolchain install leanprover/lean4:v4.19.0
```

结果：官方 elan 安装成功；固定 toolchain 安装为 `Lean (version 4.19.0, arm64-apple-darwin23.6.0, commit 6caaee842e94, Release)`。安装器 SHA-256：`a620ff1641616222c8d37c54845492004bb84d6877cdbc944dd65c1aa685bf53`。

### 版本核验

```bash
ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin /tmp/research-os-lean419/elan/bin/lean --version
ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin /tmp/research-os-lean419/elan/bin/lake --version
```

结果：Lean 4.19.0；Lake 5.0.0-6caaee8，绑定 Lean 4.19.0。

### 正向 gate

```bash
cd '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system/reference-projects/mathematical'
ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin lake build
```

结果：`Build completed successfully.`；`research_os_add_zero` 不依赖任何 axioms。

```bash
cd '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system'
ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin RESEARCH_OS_REQUIRE_LEAN=1 uv run --frozen python -m unittest tests.mathematical.test_reference_fixture -v
```

结果：3 tests / OK；真实 build、kernel type/axiom probe、statement comparator、隔离 replay 全通过；成功报告断言 `commands_recorded >= 8`。

```bash
cd '/Users/rolex/Documents/Codes/githubProject/MyProject/Research OS.research-skills-system'
unset RESEARCH_OS_REQUIRE_LEAN
ELAN_HOME=/tmp/research-os-lean419/elan CARGO_HOME=/tmp/research-os-lean419/cargo ELAN_TOOLCHAIN=leanprover/lean4:v4.19.0 PATH=/tmp/research-os-lean419/elan/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin uv run --frozen python -m unittest discover -s tests/mathematical -t . -v
```

结果：最终 55 tests / OK（新增真实 Lake 输出正例及 hostile suffix 负例后复验）。

## 修复

- 测试先行：新增真实 Lake commit suffix 正例，原实现 RED/BLOCKED；限制性版本匹配修复后 GREEN。
- 测试先行：新增 reference manifest 必须锁定及字节篡改 fail-closed；将 `lake-manifest.json` 纳入 source lock，避免首次 build 合法生成文件被误判 drift。
- 增加 hostile Lake suffix/关联版本负例：错误 Lake 版本、过短、大写、非十六进制、Lake 声称 Lean 4.18.0、任意括号 metadata、尾随垃圾均保持 `tooling-blocked`，不会启动 build。

## Deviations

- 首次直接 `lake build` 在 reference 中生成未锁定 `lake-manifest.json`，导致静态 audit 和后续 drift gate 失败。保守选择锁定稳定零依赖 manifest，不放宽 runtime drift 规则。
- 原计划仅运行 release reference gate；为确认改动不破坏 BLOCKED/普通数学语义，额外执行完整数学 suite。
- release test 在 `TemporaryDirectory` 中运行，函数返回后目录按设计清理，因此 retained run 路径不能跨测试保存。改为在测试作用域内由流程写入并以 `commands_recorded >= 8`、成功 report 字段及独立 replay receipt 验证真实链；精确命令/结果长期记录在本 notes 与 gate ledger。

## 安全复核

- 未执行四个上游社区仓库代码；未访问其工作目录。
- 用户全局 `~/.elan/settings.toml`、`~/.profile`、`~/.zprofile`、`~/.zshrc` 摘要在安装后保持记录值不变；无 `elan default`。
- 项目内 `.lake` build cache 已通过 `lake clean` 清理；仅保留审计所需的锁定 `lake-manifest.json`。
