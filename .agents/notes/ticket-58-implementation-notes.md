# Ticket #58 实施记录：研究发现、检索与绘图随包闭环

Spec #48 / Ticket #58。worktree `/Users/rolex/.t3/worktrees/Research OS Studio/t3-da263918`，分支 `t3/da263918`。开始时 HEAD `98e4333` 且工作区干净；随后安全 fast-forward 合入本地 `integration/spec-48` @ `e84f779`。

## 状态

| 单元 | 交付目标 | 状态 | 产物 | 验收证据 |
|---|---|---|---|---|
| U1 委托迁移 | idea-cycle 全叶与 academic-plotting 遵循委托合同，去掉阶段门但保留职责约束 | done | 8 个 SKILL.md、迁移边界与 checker 登记 | `tests/test_spec48_ticket58.py::MigratedSet` |
| U2 发现配方 | Discovery 转为一次委托内可组合配方，保留独立叶能力与目标替换/越权门 | done | `idea-discovery/SKILL.md`、composition notes、playbook | `tests/test_spec48_ticket58.py::DiscoveryRecipe` |
| U3 共享随包资产 | 复用既有检索、来源处理和绘图资产，不新增重复 Skill；记录许可与资源边界 | done | research-lit / novelty-check / academic-plotting 合同与测试 | `tests/test_spec48_ticket58.py::SharedAssets` |
| U4 安装可达 | 独立安装时入口、发现配方、检索/绘图能力与共置资源可达 | done | 测试与本文证据 | `tests/test_spec48_ticket58.py::FlatInstall`；skills CLI 实测 |

## 决策

1. 不新增检索或绘图 Skill：`research-lit`、`novelty-check` 已覆盖文献检索/来源处理/查新，`academic-plotting` 已覆盖数据图与示意图。本票只迁移语义、整理配方和登记资源；不凭数量补重复能力。
2. Discovery 不再默认逐阶段停：一次委托连续组合 `research-lit` → `idea-generation` → `novelty-check` → `idea-review` → `idea-refinement`。只有目标替换、越权、超额或既有文件冲突等合同保留门阻塞该分支。
3. `creative-thinking-for-research` 暂留：继续作为生成职责内的认知转换方法，不合并、不删除；没有比较独立收益的新证据。
4. 共享资源继续由各能力共置，保证独立安装时能从自身目录解析；不在发布资源中引用 `/tmp` 或个人目录。

## 逐 AC 证据

1. **保留成熟能力且不添重复**：未新增 Skill；`research-lit`、`novelty-check` 和 `academic-plotting` 继续作为共享检索/来源处理/绘图能力。`tests/test_spec48_ticket58.py::SharedAssets::test_existing_retrieval_and_plotting_assets_are_reused`。
2. **阶段控制转组合配方**：Discovery 一次委托连续走 Phase 1–4.5；阶段顺序和降级在 `references/composition-notes.md`，入口 playbook 同步。`DiscoveryRecipe` 覆盖。
3. **creative-thinking 暂留**：目录、SKILL 与 references 均存在，仍被 Phase 2 作为生成职责内的认知转换方法；未做合并或删除。
4. **许可/资源/外部服务**：各能力保留 MIT LICENSE，`SharedAssets::test_bundled_sources_licenses_and_resources_resolve` 覆盖；`test_external_services_and_writes_stay_authorized` 覆盖付费、凭据、远程写入、上传和本地环境边界。
5. **独立安装不依赖开发路径**：`FlatInstall::test_core_bundle_survives_flat_install` 复制扁平布局并验证资源。另用 skills CLI 1.7.4 在 `/tmp/spec48-58-install-all.RjAmMX` 实装 41 个 Skill；10 个代表资源均可达，包括 mandate、migration boundary、composition notes、source methods、novelty source verification、creative frameworks、plotting resources 和 LICENSE。
6. **分工**：未改 `citation-audit` 或 `apply-citation-fixes`；只迁移 academic-plotting 并把它登记为共享绘图能力。

## 红绿证据

所有命令在 worktree 根目录执行。

```text
# 红：tests/test_spec48_ticket58.py 先行，实现未完成时
$ uv run --with pytest python -m pytest tests/test_spec48_ticket58.py -q
14 failed, 5 passed, 16 subtests passed

# 绿：实现后，本票独立测试
$ uv run --with pytest python -m pytest tests/test_spec48_ticket58.py -q
12 passed, 28 subtests passed

# 全量：仅保留开始前同一组 7 个历史 evidence 断链失败
$ uv run --with pytest python -m pytest tests scripts/test_check_skills_ticket*.py -q
7 failed, 127 passed, 72 subtests passed

$ uv run python scripts/check-skills.py
FAIL: 9 个问题（全部为开始前已有的 docs/acceptance evidence tarball 断链）

$ git diff --check
0
```

## 未完成 / 限制

1. 静态合同、结构可达性和扁平安装已验证；未验证真实宿主会在每次委托中完美执行 Discovery 配方或检索/绘图质量。
2. 未新增付费检索 provider 清单；外部账号、订阅与付费服务仍按各能力授权门处理，缺授权时如实阻塞。
