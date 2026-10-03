# v2 发布验收（#46）

静态全绿只证明合同文本。下表的「通过」只用于本票实际留下工具轨迹的格子。前票轨迹不在本次重跑，不能当成集成后已验。

## 静态

- 入口：`uv run python scripts/check-skills.py`。结果：OK，39 个 Skill，U 38 / M 1。
- 组合：`uv run python -m unittest` 覆盖 #38 #39 #40 #42 #43 #44 #45 #46 的现有测试文件，50 项通过。
- 反例：路由表去掉 pickup 报缺行；产品文档含「完成后立即停止，绝不自动跳转」或 `No Automatic Chaining` 报残留。
- 链接与清单：同一条 `check-skills.py`，零豁免失败。

## 三宿主限定安装

目录：`/tmp/ros46-install-k0vn`。Skills CLI 1.5.26，`--skill '*' --agent claude-code --agent codex --agent pi --copy --yes`，只写该临时项目。未使用 `--global`。

`file:` 安装被本机 `127.0.0.1:7890` 代理中断。改为 `git clone --local` 后再装。三份副本各 39 个 Skill，与源目录逐文件 SHA-256 相同。`setup-research-os` 无 `disable-model-invocation`，`allow_implicit_invocation: true`。`research-os` 为 `disable-model-invocation: true`。

## 本票行为

| 场景 | 宿主 | 结果 | 轨迹 |
|---|---|---|---|
| 只读意图夹带「写论文并跑实验」 | pi，`cliproxy/glm-5.3-flash`，工具仅 read | 读了路由表、route-only、PRODUCT-MAP、idea-cycle。推荐 idea-discovery，并给出备选。项目快照不变 | `pi-route3.jsonl` |
| 同上 | Claude Code，`--model haiku`，实际用量记 `gpt-6-luna` 与 `glm-5.3-flash`，工具 Read，`permission_mode plan` | 命中 route-only，声明未写文件。`web_search_requests` 为 0。快照不变。第一次文本输出只有 `/research-os`，不采用 | `claude-route2.json`，session `ce398e80-1b39-4460-9681-211572445938` |
| 同上 | Codex `deepseek-v4.1-flash`，read-only sandbox，ephemeral | 读了入口、route-only 与地图；reasoning 明确选择 route-only，最终推荐 experiment-plan，无执行证据。未读推荐叶正文，且「论文骨架」描述无叶依据；不作为完整通过 | `codex-route.jsonl` |
| 无子代理，点名「设计实验」 | pi，工具仅 read | 命中 experiment-plan，只读两份编排文件，未写文件；明确因扁平安装路径不知而停止，未冒充已读。叶 `experiment-plan` 正文未读，串行降级未走完级联 | `pi-serial.jsonl` |

pi 第一次把 `--skill` 指到 research-os 时，实际读的是 setup，推荐 setup。第二次 `--no-skills` 未给出绝对路径，四次 read 都 ENOENT。这两次不作通过证据。

## 前票证据

|#| 已有轨迹 | 本票状态 |
|---|---|---|
| 38 | 入口与 route-only 的静态合同 | 行为未在集成树上重跑 |
| 39 | 叶门声明基线 | 真实级联停点未汇总到可复核轨迹 |
| 40 | setup 合同与字段 | 真实模型确认对话未在本票重跑 |
| 41 | arXiv 两次 `SSL_ERROR_SYSCALL`，候选到 Proposal 未跑通 | 仍缺 |
| 42 | `/tmp/ros42-cases` 十个授权场景 | 文件还在；本次未重跑，不算集成后已验 |
| 43 | 授权前读路径 | 三变体真实材料交付仍缺 |
| 44 | `/tmp/ros-t44-throwaway` 三条路线 | 文件还在；本次未重跑 |
| 45 | `/tmp/ros-pickup2-xa6P/session2.jsonl` | 文件还在；本次未重跑 |

## #37 review 修复后状态

在修复分支合入 integration tip `70306a9` 后，checker 仍通过；tests/ 16 项、scripts/ 41 项，共 57 项通过。新静态反例覆盖 none 混用、当前 skill 来源边界（含 symlink）、异构算力逐单位上限与配对、默认角色闭合、未追踪级联引用。入口补 todolist/核实产物、当前 route-only 与推荐对象区分、扁平安装路径映射及串行叶全文读取。

这些是合同修复，不是原失败场景重跑结果；上述宿主轨迹来自修复前。未重跑，不把正文增强视为行为已通过。

## 发布

未打 `v2.0.0`。未关票，未 push，未开 PR。缺的是：完整路线边界的工具轨迹、三宿主上只读优先都成立、串行降级读完叶正文、前票行为在当前 tip 上复核。
