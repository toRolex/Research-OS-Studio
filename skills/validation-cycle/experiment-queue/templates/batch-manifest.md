# Experiment Queue 批次清单

这是人类可读的作业清单，不是中央 schema 或数据库。使用项目已有格式即可（Markdown 表、YAML 或 JSON）；下面的 YAML 展示字段含义，实际执行前与用户确认并保存到本次授权位置。

## 运行标识

- project / cwd / 执行入口：
- 允许资源与 `max_parallel`：
- 空闲阈值：
- 本次预算（作业数 / wall-clock / 资源）：
- 状态表位置：
- 日志与输出位置：
- 谁可以停止或重排：

## Grid / 阶段（可选）

```yaml
grid:
  <param>: [<values>]
template:
  id: "<pattern using ${param}>"
  cmd: "<command using ${param}>"
  expected_output: "<path pattern using ${param}>"

phases:
  - name: <phase>
    depends_on: []        # 列表；依赖阶段的全部作业到达终态后才启动
    grid: {...}
    template: {...}
```

Grid 在构建清单时展开为明确的逐作业条目，展开口径可人工复核。

## 作业清单

| Job id | Phase | 命令 / args | Preconditions | Expected output | 状态 |
|---|---|---|---|---|---|
| | | | | | pending |

## OOM / 重试策略

- OOM 识别：日志中出现内存不足错误；
- `retry_delay`（等待多久，如 `10m`）/ `max_attempts`（每作业最多几次，如 `3`）：
- 超过上限后的动作：标 `stuck`，保留日志并交给用户。

## 已知风险与停止条件

- 会阻塞下一波次的 precondition：
- 可能超出预算或触发付费/远程写入的作业：
- 停止条件：预算耗尽 / 达到超时 / 重复失败超限 / 资源或副作用越界 / 用户要求停止。
