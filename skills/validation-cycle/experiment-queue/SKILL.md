---
name: experiment-queue
description: "把已授权的多作业实验（多 seed、参数网格、teacher→student 阶段依赖）组织为有界批次：读取或生成作业清单，按可用资源与依赖逐波执行，识别 OOM 与停滞并有限重试，保存可恢复的 attempt 状态。用于“批量实验”“跑 grid”“多 seed sweep”或 run-experiment 的批量阶段；不引入常驻 scheduler、不自动扩预算、不隐藏停止/重试，也不接管未授权作业。"
---
<!-- argument-hint: "[manifest 或 grid 规格；可指定并发上限、重试上限与状态位置]" -->

# Experiment Queue

当单个 [run-experiment](../run-experiment/SKILL.md) 不足以承载多作业实验时，把已授权的作业组织为**有界批次**：逐波执行、按依赖等待、OOM 有限重试、停滞清理、状态可恢复。这是 model-invoked 的内部编排能力：当前 Validation Workflow 可在已授权职责内组合调用，用户也可点名 standalone。批次结束后停止在汇总报告，不自动分析、审计或进入下一轮。

上游 ARIS `experiment-queue` 用远端常驻 Python scheduler 管理 screen 作业。本 Skill 保留其作业清单、波次依赖、OOM 重试、停滞清理和恢复方法，但删除常驻 daemon、无限轮询、provider 绑定和隐藏调度：编排以用户可读的清单、状态表和日志保存，控制权留在用户手中。

## 何时使用

用于：

- ≥10 个作业需要按有限并发分批；
- 多 seed sweep（如 21 seeds × 12 cells）；
- 波次转换（先跑 wave 1，等待，再跑 wave 2）；
- teacher→student 链（teacher 完成后才允许 student）；
- 易 OOM 的配置需要有限重试或换资源。

不用于：单次或少量作业（用 [run-experiment](../run-experiment/SKILL.md)）、需要人工逐步检查的实验、或尚未获得执行授权的作业。不使用嵌套轮询包裹本 Skill 的批次进度——那会重复调度时钟并与波次逻辑竞争；直接读取状态表获取进度。

## 1. 授权与资源门

在任何作业启动前，列出并让用户确认：

- 作业集合与来源（显式清单、grid 规格或自然语言描述）；
- 允许的并发上限、可用资源集合（GPU/CPU/机器/队列）与每作业资源需求；
- 总运行数、重试上限与重试延迟、预计 wall-clock 和资源预算；
- 阶段依赖与哪些作业必须在另一些完成后才能启动；
- 可修改范围、输出/状态位置，以及作业失败时允许的修复动作；
- 谁可以停止、暂停、重排或清理批次；付费与远程写入是否逐项获批。

缺少确认时只构建清单和预检草案，必须停在授权门。默认不安装环境、不申请新凭据、不上传私有材料、不提交或发布。

**完成条件**：作业数、依赖、并发上限、资源与授权状态明确；未授权集合不会进入执行。

## 2. 构建作业清单

输入可以是显式清单、grid 规格或自然语言；先用项目已有格式表达，不建立统一 schema。推荐使用 [批次清单模板](templates/batch-manifest.md)，至少记录：

- **project / cwd / 执行入口**：每个作业在哪个项目目录、用哪个已有命令运行；
- **default_cmd 与每作业 args**：把 grid 或模板展开为具体命令；
- **preconditions**：作业启动前必须存在的文件/检查点/数据（如 teacher checkpoint）；
- **resources**：允许的资源列表、`max_parallel`、空闲阈值；
- **oom_retry**：重试延迟与最大次数；
- **phases / depends_on**：阶段名与依赖列表（即使只有一个依赖也用列表）；
- **jobs**：每个作业的唯一 `id`、`args`、`expected_output`。

Grid 规格按笛卡尔积展开为明确作业；阶段模板在展开时把变量代入命令与 `expected_output`。把展开结果保存为一次运行的可读清单，供 launch、monitor、resume 引用同一组路径与标识。

**完成条件**：每个作业都有唯一 id、明确命令、预期输出和所属阶段；grid 展开可人工复核；依赖关系无环且指向已声明阶段。

## 3. 预检

在执行前逐项检查并记录：

- 执行入口、代码路径、运行目录是否存在且符合授权；
- 每个作业的 precondition 是否满足；不满足的作业标为 `blocked` 并说明原因，不静默跳过；
- 资源是否可用（如 GPU 内存低于空闲阈值）、并发上限是否可满足；
- evaluator 与 ground truth 是否可读且对全部作业一致；
- 输出目录、日志目录与状态位置是否可写；
- 是否有作业会超出预算、写入未授权位置或触发未授权的付费/远程副作用。

若关键 precondition 失败，展示被阻塞的作业与原因，等待用户决定；不通过自动重跑修复 precondition。

**完成条件**：每个作业都有可执行/被阻塞的预检结论和证据；被阻塞项不进入运行波次。

## 4. 逐波执行

把作业按资源与依赖组织为波次（wave）。一个波次只有在下列条件同时满足时启动下一批：

1. 当前波次的运行进程全部退出；
2. 当前波次没有残留的会话/进程占位；
3. 资源已释放到空闲阈值以下；
4. 下一波次作业的 precondition 通过。

执行规则：

- **资源隔离**：同一资源上不重叠启动作业；启动前确认资源空闲，等待而不是抢占。
- **有限并发**：并发数不超过已确认的 `max_parallel` 或可用资源数。
- **每作业一个 attempt 记录**：记录 run id、phase、资源、命令、开始/结束时间、状态、expected_output、错误摘要和原始日志位置。
- **状态机**：`pending → running → completed`；OOM 走 `failed_oom → pending`（有限重试）；其他失败进入 `failed_other → stuck`（等待人工检查）；停滞会话按第 5 节处理。
- **完成判定以预期输出为准**：不只相信会话状态；检查 `expected_output` 文件/结果实际存在且未损坏。
- **依赖在启动时强制**：阶段作业只在所依赖阶段的全部作业到达终态后启动。注意“终态”包含 `stuck`——失败的 teacher 不会永久阻塞 student，因此启动依赖波次前先检查状态表中的 `stuck` 项，不把缺失 precondition 当成通过。

**完成条件**：每个已启动作业都有状态、资源、原始日志与预期输出核对结果；没有跨越未满足依赖或未释放资源的波次。

## 5. 停滞、OOM 与有限重试

**停滞检测**：对每个 `running` 作业定期检查进程/会话是否仍在运行，以及预期输出是否出现。若会话存活但执行进程已退出：

- 预期输出存在 → 标 `completed`，清理残留会话；
- 预期输出不存在 → 标 `failed_other` 并清理会话，进入 `stuck`。

**OOM 处理**：从日志识别内存不足（如 CUDA out of memory）。检测到后：

1. 标 `failed_oom`，清理该作业的残留会话/进程；
2. 等待已确认的重试延迟；
3. 确认资源已释放后再分配（优先换到空闲资源）；
4. 重新入队为 `pending`，attempts 计数加一；
5. 超过 `max_attempts` 后标 `stuck`。

**有限原则**：重试只针对同一失败类型且有明确上限。重复失败、依赖 precondition 缺失或单次失败原因不明时，不要无限重试；保留每次 attempt 的原始日志并把最小决策问题交给用户。

**完成条件**：每次重试都有触发原因、attempt 计数和新资源；达到上限的作业停在 `stuck` 且有原始证据；没有隐藏的自动重试。

## 6. 状态、恢复与停止

- **状态持久化**：每次状态变化都写入用户可读的状态表（沿用项目已有 tracker 或清单格式）；包含 meta（project、run 标识、开始时间、执行位置）、phases 状态和逐作业状态。状态表用于恢复和人工核对，不是中央数据库。
- **可恢复**：批次中断后，读取状态表；`running` 作业先核对其会话/进程是否仍存活，存活则保留，否则按第 5 节重新判定；`pending` 继续；`completed`/`stuck` 不重跑。恢复时复用原有 run 标识与路径，不重新生成清单。
- **幂等**：恢复只补齐未完成项，不覆盖 manifest、状态历史或已有结果。
- **停止条件**：以下任一情况立即停止当前职责并报告：授权被撤回、预算耗尽、达到超时、重复失败超过批准的重试/修复上限、资源或副作用超出确认范围、precondition 无法满足、用户要求停止、或全部作业到达终态。
- **停止与重启权限**：暂停、kill、重启、扩大资源或迁移机器都必须由用户授权；本 Skill 只能建议并分开记录建议与实际动作。

**完成条件**：状态表与实际尝试一致；恢复路径可重放且不丢失历史；停止原因、未完成任务和已执行的控制动作都可核对。

## 7. 汇总与交回

批次全部到达终态或被停止后，读取状态表和原始日志，生成自然格式汇总（沿用 [run-experiment 报告模板](../run-experiment/templates/run-report.md) 的 attempts 表）：

- 逐阶段/逐作业状态统计：completed、failed、invalid、timeout、oom、cancelled、stuck、not-run；
- 成功、失败、无效、超时与重试的完整历史，不只列出成功项；
- 每个作业的原始结果与日志位置、实际资源消耗与 wall-clock；
- 未运行作业、被阻塞的 precondition、未解决缺口与最小决策问题；
- 付费/远程动作与清理结果。

汇总只报告编排与运行事实。是否接受结果、如何解释指标、是否补实验或进入分析/审计/Results-to-Claims，由用户或父 Workflow 决定；本 Skill 不自动调用它们，也不自动开启下一批。

**完成条件**：汇总反映完整 attempt history 和真实资源消耗；所有 `stuck`/被阻塞项都有证据与下一步；交付后停止。

## 来源与适配

改编自 wanshuiyin / ARIS `skills/experiment-queue/SKILL.md`，revision `0472e530251cdbd3364c33b110063c58f819edd7`。上游仓库 MIT 许可，完整 notice 见 [LICENSE](LICENSE)，采用边界记录在仓库 `docs/upstream-sources-and-licenses.md`；使用本 Skill 不依赖上游仓库、中央 runtime 或其其他 Skill。

保留：作业清单与 grid 展开、precondition 预检、按资源与依赖的波次调度、OOM 有限重试、停滞清理、预期输出完成判定、状态持久化与 resume、完整 attempt 汇总。适配：删除常驻 `queue_manager.py` scheduler、nohup/screen/SSH/conda/provider 固定绑定、60s 无限轮询、`os.execv` shim 和自动调用分析；改为纯 Markdown 的清单 + 状态表 + 宿主已有执行工具，控制与重试显式可见，并把 precondition / 存在性判定留作人工可核对项。上游 `scripts/` 中的调度实现不作为本产品 runtime 复制。
