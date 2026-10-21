# #49 定向验收与整合记录

## 状态与边界

入口判定：这是已有实现与修复的有界验收/整合 work unit，用户禁止继续派发，故直接执行。只写 `/Users/rolex/.t3/worktrees/Research OS Studio/integration-spec-48`；未触碰主目录或源 worktree，未改产品、未调整测试、未 push/PR/关闭 issue/清理 worktree。用户批准使用 Git worktree，不用 jj。

| 单元 | 状态 | 产物/证据 | 下一步 |
|---|---|---|---|
| 亲核合同、修复及 expand 边界 | done | 本记录逐 AC 及源码定位 | 无本票阻断 |
| 候选/基线及红绿验证 | done | `ticket-49-verification-evidence/{targeted-premerge,targeted-red,suite-candidate,suite-baseline,checker-candidate,checker-baseline}.txt` | 历史失败单列 |
| 安装实证与资源可达性 | done | 同目录 `install-{selected,all}.txt`、`install-inspection.txt`、`all-install-links.txt` | 全包遗留另列 |
| no-ff 整合及复验 | done | merge `23d19f752be8fe1f380a548666c4c866acbb19ce`；`targeted-postmerge.txt`、`suite-postmerge.txt`、`checker-postmerge.txt` | 提交本记录后交回 |

输入：`/tmp/research-os-spec48-context/spec/#48.md`、`/tmp/research-os-spec48-context/tickets/#49.md`、源票 notes、实际 Git diff。基线 `bce31c1618c98b5ca4ed12bf3eb2ed091cdd5e02`；原实现 `9b80491`；修复 `045c172633e5c681f58c9d6461e714ee95419425`（源分支 `t3/implement-ticket-49`）。验收对象仅为 #49 安装后的结构与合同，不是全部 #48 功能或真实科研质量。

证据目录均相对本记录所在目录：`.agents/notes/ticket-49-verification-evidence/`（ignored，本地保留，不强行纳入版本库）。只强制追踪本记录。

## 逐项 AC

| #49 AC | 判定 | 亲核依据与限制 |
|---|---|---|
| 统一目标、权限、研究额度和完成/停止语义；保留只读、目标替换确认及底层独立调用 | ACCEPT | `research-os/references/mandate.md` 的目标/权限/研究额度/完成与停止/验收；入口只读优先与授权继承；目标替换只阻塞该分支；叶 `research-lit` 独立调用自带输入/预算/输出边界。额度跨并行、重试、恢复累计；无 setup/额度有界首轮。用户叫停属于停止，不是目标完成。 |
| 从入口到已有底层能力再到结果验收的完整路径 | ACCEPT | 路由 `literature` → `playbooks/literature-review.md` → 读取已有 `research-lit` 与 source-methods/source-verification/报告模板 → 执行 → 第4步实际产物核验 → 交付收束。需要分派而宿主无子代理时 blocked，不伪造执行。此为完整合同路径与安装可达性验收，未开展真实文献科研任务。 |
| expand 边界，已迁移遵新合同、未迁移仍可用，不假称全叶统一 | ACCEPT | `MIGRATED_CONTRACT` 仅 research-os/research-lit；`LEGACY_LEAF_GATES` 保留其余叶；测试核迁移集合互斥且覆盖（setup 单列）。`migration-boundary.md` 明确剩余能力旧门保留；入口级联未迁移叶仍守该叶门。 |
| 调整固定数量/旧审批检查，保留元数据/资源/引用检查 | ACCEPT | 删除 `EXPECTED_COUNT`，改实际目录/两份 README 清单关系及缺 SKILL.md 检查。`expected_gates()` 共用迁移/旧门来源；元数据、调用策略、门格式、来源锚点、追踪状态、共置资源、相对引用检查保留。旧测试只更新迁移后 research-lit 门、literature 路由及禁止串行伪降级的期望，无新增 skip/xfail/削弱历史失败。新增 HISTORICAL 过滤只用于新增回归测试，不改变全套或 checker 失败状态；基线输出另行逐字比较。 |
| 实际安装后入口/代表能力发现、读取、资源可达；记录后续边界 | ACCEPT | 检查旧 `/tmp/spec48-49-install` 及 `-all`，发现它们是修复前副本，不能替最终修复背书。因此在唯一写域内用真实通用 CLI 从最终候选快照重新做限定和全包安装；2/39 个 SKILL.md 可发现。两代表能力所有文件逐字与候选相同，关键资源存在且可读，内部相对文件链接断链为0。边界见源码文档与下节。 |

以上 ACCEPT 仅对 #49 slice；不表示全部叶已迁移，也不将静态合同当真实科研质量证明。

## 原父审查问题复核

1. **Spec #48 ID16：无子代理串行 fallback**：亲读入口模型/宿主映射/级联、mandate 权限、新 literature 步骤3。均明确子代理能力为分派前提；缺能力标 blocked，只给只读建议，不用当前编排者串行执行冒充委托已执行。保留底层单能力直接调用，不是入口降级。`research-lit` 内部可串行提取论文且不冒充独立 review，属于其单项能力边界，不等于入口绕过前提。结论：修复接受。
2. **用户叫停被算完成**：mandate 完成行仅目标达成/严格反例成立；停止行含用户叫停并有专门澄清。literature 停止段也不把叫停宣称为已完成。结论：修复接受。
3. 红例独立重放：在写域内生成 `9b80491` 副本，仅覆盖成最终两测试文件，不改产品；运行得到 **8 failed, 23 passed, 2 subtests passed**，失败正是叫停语义、无子代理前提、串行代跑/host checker 项。最终候选及合并后均 **31 passed, 2 subtests passed**。

## 执行与实证

所有 bash 显式从 integration worktree `cd`。快照由 `git archive` 生成到证据目录，分别初始化局部 Git 追踪，避免在源工作区跑会写缓存的测试；测试用临时目录也指定到该写域。未运行硬编码源 worktree 的 `/tmp/spec48-49-pytest.sh`，只读其离线依赖路径并复用。

离线运行方式（无改测试内容、无网络拉依赖）：

```sh
cd '/Users/rolex/.t3/worktrees/Research OS Studio/integration-spec-48'
export PYTHONPATH='/Users/rolex/.cache/uv/archive-v0/4CHMQJFdnl52qfUb:/Users/rolex/.cache/uv/archive-v0/l3lk9gBWBxH13PVA:/Users/rolex/.cache/uv/archive-v0/uTIJyihQqUEbcRkg:/Users/rolex/.cache/uv/archive-v0/xVxPMSCAiQhZ4JiW:/Users/rolex/.cache/uv/archive-v0/UI1ydHRDBfHz3GRL'
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$PWD/.agents/notes/ticket-49-verification-evidence/tmp/.venv"
uv run --offline --no-project python -m pytest tests/test_spec48_ticket49.py scripts/test_check_skills_ticket46.py -q
uv run --offline --no-project python -m pytest tests scripts/test_check_skills_ticket*.py -q
uv run --offline --no-project python scripts/check-skills.py
```

| 执行对象 | 定向 | 全套 | checker |
|---|---|---|---|
| bce31c1 基线快照 | 不适用 | 7 failed, 67 passed, 44 subtests passed | exit1，9条历史断链 |
| 045c172 候选快照 | 31 passed, 2 subtests passed | 7 failed, 90 passed, 44 subtests passed | exit1，输出与基线逐字一致 |
| integration 合并后 | 31 passed, 2 subtests passed | 7 failed, 90 passed, 44 subtests passed | exit1，输出与基线逐字一致 |

全套同一7个失败，均由历史 evidence tarball 缺失/未追踪导致 checker 非零：

- `tests/test_check_skills_policy_gates.py::PolicyAndGates::test_checker_green_and_leaf_baseline`
- `tests/test_config_contract.py::ConfigContractTests::test_gate_baseline_and_counterexamples`
- `tests/test_config_contract.py::ConfigContractTests::test_shipped_templates_and_full_checker`
- `tests/test_config_contract.py::ConfigContractTests::test_valid_policy_and_log_fields`
- `tests/test_config_contract.py::ConfigContractTests::test_valid_role_table`
- `tests/test_final_contract_fixes.py::FinalContracts::test_full_cli_damaged_declarations_refs_and_readme`
- `tests/test_review_fixes.py::ReviewFixes::test_compute_limits_are_per_unit_not_summed`

checker 的9条断链为 `docs/acceptance/` 下：v2-release-host-regression、v2-final-contract-fixes、v2-release-gate-combinations、v2-merged-host-smoke、v2-accept-validation、v2-accept-hosts、v2-final-contract-independent-verify（两条）、v2-accept-remediation 所引用的 `evidence/*.tar.gz`。原样保留失败，不声称 checker 全绿。

结构检查的红例涵盖未列清单/未分类新增能力、已迁移叶重新长回 Gate、合同额度标题丢失、边界遗漏已迁移能力、host 串行代跑等；正例为实际树与只依能力不绑品牌的 host 文本。另有旧测试继续覆盖元数据、锚点、追踪及损坏声明/引用。

安装执行使用已有缓存 `skills` **1.7.4** 的实际入口 `/Users/rolex/.npm/_npx/5606f1555d02ef53/node_modules/skills/bin/cli.mjs`，不是测试里的 copytree 假安装。分别在证据目录 `install-selected` / `install-all` 中运行：

```text
node <cached-cli> add <candidate-snapshot> -s research-os -s research-lit -a claude-code -y   # exit0
node <cached-cli> add <candidate-snapshot> -s '*' -a claude-code -y                         # exit0
```

`inspect_installs.py` 检查两个旧 /tmp 安装和两个新安装；新副本与候选所有文件逐字一致；SKILL.md、agents/openai.yaml、LICENSE、mandate/migration-boundary/literature-review 以及叶 source-methods/source-verification/report 模板实际存在并可读。新旧两代表能力内相对文件链接均0断链。最终入口 SKILL.md SHA256 `e35f9e06ee3db3c49baf79579651d4c776753f8cfd9ec5079acf328ce85f3077`；叶 `33445631d38569a8941ce48eebd0865cc87745e86dcdcd34b41ad5ad243182ae`。

`git diff --check bce31c1 045c172`、`git diff --check bce31c1 HEAD`、合并后 `git diff --check` 通过；产品路径相对 045c172 无额外变化。合并命令：

```text
git merge --no-ff 045c172633e5c681f58c9d6461e714ee95419425 -m 'merge: integrate research mandate foundation (#49)'
```

无冲突，merge parents 为原 integration 基线和已核源修复。既有 ignored orchestrator notes `spec-48-implementation-notes.md` 在合并前与紧接合并后的 SHA256 均为 `8209ae811635b27d147a1ac2f3c82912e80d65de4d74995b41278d5366ec242e`。提交本记录后的最终检查发现该文件已变为 `99fb22bf52d17fd8de0f2bfe7c15319ed3716b1eb5bcdd0ea10d1f2764b4e07d`（mtime Oct 21 10:40:59，5892 bytes）；本 worker 的写入/暂存命令均未包含它，故只记录外部并发变化，不覆盖、不恢复、不纳入提交。不能再声称它在整个验收窗口内未变化。

## 决策、偏离与遗留

- 未发现本票阻断；接受用户已允许的历史失败，未通过改产品/削弱检查制造全绿。
- 旧 `/tmp` 安装不是最终修复。为不写出授权目录、不覆盖旧证据，重新实装到 integration ignored 证据目录；这是对证据新鲜度的补验，不是新 feature。
- Worker notes 称全包20条相对链接断链。本次独立按 Markdown 链接（含类似图片/占位行文）扫描，新全包和旧 `/tmp` 全包均得到 **21条**，逐条证据见 `all-install-links.txt`：research-improvement 14、paper-writing/ml-paper-writing/systems-paper-writing各1、setup-research-os 4。全部位于本票未改能力，本票两代表能力为0。此统计口径不把占位文本当可用真实链接；保留为后续 #60 全包安装检查问题，不外推全包完整可达。
- 其余叶/旧 playbook、PHASE-BOUNDARIES、pickup 恢复与阶段停点等按 expand 尚未统一；后续票继续迁移。未迁移资源仍可能含旧串行表述，不据本票宣称已解决整个套件。
- 根 GLOSSARY/ADR 等背景资产未随本票提交；README/英文说明/验收资料中的既有固定数目和终态同步待后续票；本次未擅动背景文件。
- 未实测真实宿主缺子代理时模型是否遵约、全宿主实际交互、长期自治、服务器、真实科研与数学正确性。安装发现/资源读取、静态合同、checker 正反例不是上述质量证明。
- 所有本地证据与快照保留，未清理任何 worktree。只有本文件另行提交为独立验收记录，不改 orchestrator notes。
