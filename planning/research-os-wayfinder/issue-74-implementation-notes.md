# Issue #74 实施记录

## 验收映射

- 显式启动：Codex tracer 要求精确确认串；错误时不进入宿主 seam。
- discipline 边界：投影不发布 discipline 顶层入口。
- Core 复用：成功路径由受信宿主回调调用 canonical `research_charter`；Adapter 只做投影、准入、调用和结果核验。
- 语义一致：差分测试比较 direct CLI 与受信宿主 seam 生成的 Artifact、workflow report、停止行为和退出状态。
- 安全隔离：生产 CLI 在离线或隔离未验证时结构化 BLOCKED，不启动 Codex、不回退 direct CLI。

## 决策

- 真实 Codex 外发当前禁止，不能把 mock 或配置存在冒充真实成功。
- 在宿主执行通道建立可注入 seam；测试宿主实际调用 canonical Core，而非伪造 Artifact。
- 隔离许可不是环境变量或宿主自报字段；生产入口不暴露测试放行开关。
- Adapter 成功前重新验证 projection，并验证受控输出与 canonical Core 的完整结果；宿主 receipt 仅作为执行证据，不作为产物正确性的真源。

## 执行记录

- red：新增 direct CLI 与注入宿主 seam 的成功差分测试，以及伪造 receipt、运行中投影漂移负例。
- green：新增固定 `CodexHostRequest`/`CodexHostReceipt` 协议；宿主只获得一次性 canonical Core 回调。
- 核验：成功前再次检查 projection，并按 canonical Core 逐字节验证 Artifact、workflow report 和停止结果；异常时删除本次输出。
- 加固：宿主回调调用即关闭且命令返回后失效；Core 用法/输出冲突保持 direct CLI 的退出 2/1；失败不删除既有、并发或已生成 Artifact，保留失败现场；projection 以单次读取快照验证并在完成时按文件摘要复核。
- 运行：24 个全量 unittest 通过；CLI 实测离线返回 3/`codex.offline` 且无输出，错误确认串返回 2，投影漂移返回 3。

- Ticket 原本要求真实 Codex 成功执行；当前恢复约束禁止真实外发。因此保留生产 BLOCKED，补齐安全可测试的成功路径边界与契约，不宣称已完成真实外发验收。
