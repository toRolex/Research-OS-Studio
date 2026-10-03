# #38 / #39 / #40 / #46 宿主实际验收

## 基线、安装与证据

- 开工 HEAD = integration `67a04ff5b3714f7d6883cb9a33b1b4259348fabf`；祖先检查成功。完成前 `git merge integration/research-os-v2` 返回已是最新；未改 main、全局配置，未 tag/push/PR/关票。
- 行为安装先源 `54f2ada`，最后重装源 `a15c586`（本轮两处正文小修）；在 `/tmp/research-os-v2-hosts/project` 用 Skills CLI **1.7.0**，`add /tmp/research-os-v2-hosts/tickets --skill '*' --agent claude-code --agent codex --agent pi --copy --yes` 三次限定安装。第二次网络 npm 超时，改缓存 `npx --offline` 成功。三份各39技能，每个源文件与安装副本SHA-256一致，0 mismatch；没有 `--global`。
- 版本：pi 1.0.0、Claude Code 2.1.228、Codex 0.151.0、UV 0.12.22。模型分别请求 `cliproxy/glm-5.3-flash`、Claude `haiku`（真实响应模型见session）、Codex `deepseek-v4.1-flash`。不把CLI存在当登录证明：79个真实调用均有tool/session输出。
- 默认工具均未限制成read-only。pi多数轮关闭extension discovery但保留默认read/bash/edit/write，另 **route-all-default/pi** 不关闭extension，完整默认工具也通过。Claude默认工具、bypassPermissions只在toy测试进程；Codex默认工具workspace-write，setup第一次写被`.agents`沙箱保护拒绝，随后仅toy进程danger-full-access重启重试，没有改用户配置。
- 完整证据已归档 [v2-accept-hosts.tar.gz](evidence/v2-accept-hosts.tar.gz)，8.15MB，SHA256 `cab141490a54d13564d27723a6f8cfcff726d555698da26668111d0eb3cefa9e`。解包后根 `v2-accept-hosts/`；`SHA256SUMS.json`逐文件hash，`evidence-index.json`79轮exit/耗时/变动，`installation-manifest.json`完整安装hash。每场景有prompt、命令、stdout JSONL、stderr、结果、前后快照、全局表stat/hash。Claude宿主session在`host-sessions/`；pi session在各场景目录；Codex原始thread events包含thread id。临时原件 `/tmp/research-os-v2-hosts`仍保留。

## 真实发现与小修

首次pi按产品示例 `/research-os`，**只读setup而未加载router**，继而错误声称setup是其他流程前置。pi官方本机docs/skills.md明确原生命令是 `/skill:name`，隐藏的显式skill仍通过该命令加载。先加公开文档合同回归，8项中1红；最小修router宿主映射与README，commit **54f2ada**，8绿。pi原生 `/skill:research-os`真实重跑读到route-only和推荐叶全文；没有修改科研逻辑。

下文的`/research-os`是逻辑入口：pi `/skill:research-os`、Claude `/research-os`、Codex `$research-os`；叶直接点名同理。

## 路由 / 显式 / 级联逐场景

所有以下只读场景项目文件SHA快照相同；原始工具trace而非仅最终声明用于判定。prompt内toy证明、toy评审都明确不是论文或真实外部评审。

| 场景 / 证据目录 | pi | Claude | Codex | 判断范围 |
|---|---|---|---|---|
| 只读夹带写ML论文/跑实验，只有方向 `route-all-default` / `route-current` | 通过 | 通过 | 通过 | 命中route-only，读地图、idea-cycle、推荐idea-discovery全文；未网络/任务启动/写入/派发；材料不会因未来ML目标而伪造 |
| 未点名普通算术 `implicit` | 通过 | 通过 | 通过 | 无skill/工具调用；有限代表，不宣称所有prompt绝不触发 |
| 直接proof-review `direct` | 通过入口 | 通过入口 | 通过入口 | 原生宿主加载正文，指出x=0反例，不修命题/不写；不是独立评审AC完整证明，见fresh限制 |
| 串行experiment-plan `serial-plan` | 通过入口/边界 | 首轮timeout，`serial-plan-retry`交付压缩BLOCKED草稿 | 通过入口/边界 | 都读叶全文+模板/block-checks/batch授权；预算未知保留；未实现或实验。Claude改写清单而非逐字抄playbook，完整模板未满足，不判完整科研计划AC通过 |
| 材料不匹配ML `mismatch` | 安全通过 | 安全通过 | 首轮模型错误exit1，未完成 | pi/Claude按普通数学材料走general授权门，不读ML叶执行，不造训练结果；Codex首轮只读到general叶后API失败；`mismatch-retry`已真实重跑，route-only下拒绝虚构ML，读proof/general/ML叶，只推荐不执行。材料安全通过，首选proof与写作目标不一致仍保留匹配质量局限 |
| 无匹配但无真歧义 `custom` | 通过 | 通过 | 通过 | 设计库存人工归架有界流程，缺条目标缺口，不因缺项先追问，未执行 |
| 真歧义 `ambiguity` | 通过 | 通过 | 通过 | 标记去重与删除两条实质不同流程，停询问，不删记录 |
| 已有门级联 `cascade-gate` | 通过代表门 | 通过代表门 | 通过代表门 | 读rebuttal与资源；toy x²反例拆concern/策略；strategy-confirm前不起草已确认回复，无外发/写入 |
| “继续/下一阶段” `sticky` | 通过边界 | 首轮timeout且草稿严重重复，重跑恢复原计划 | 通过边界 | 不重匹配为实验bridge，不因继续启动实验；Claude不判完整交付质量 |
| `new task`只读重新匹配 `new-task` | 通过 | 首轮失败；修后`new-task-retry`通过代表边界 | 通过 | 都读route-only+writing-cycle+rebuttal全文、未写/网络；Claude首轮先TaskUpdate旧任务，先红回归后补明确只读任务状态，a15c586，原session修后仅Read、无TaskUpdate |

`fresh-review/pi`：**宿主自己**通过pi CLI新建非fork/resume独立session，子context原始proof文件只读、x=0反例；主宿主读回原材料和session核覆盖。原件`fresh-toy/reviewer-prompt.md`、`reviewer-session.jsonl`、`reviewer-trace.jsonl`。不把同context自审当独立。该主宿主曾误用`-e SKILL.md`失败后改`--skill`，运行了裸python3解析并创建/删除额外自己生成的报告文件，违反本轮UV/仅3文件严格许可；因此只证明**fresh隔离能力**，不判整个操作纪律全通过，不隐去失败轨迹。

## setup：真实多轮，不是手写模板

### pi（setup-01至setup-13、setup-conflict-*）

- 宿主自己`pi --list-models`真实清单；8角色逐轮明确确认 `cliproxy/glm-5.3-flash | off`。
- `setup-02-invalid`：`imaginary/not-available`不在清单，停重问，零写入，不静默替换。
- 首完整稿省略日志全文、文件计数错；操作者拒批，`setup-11-full-draft`补全真实日志模板全文；直到`setup-12-write`明确批准7路径才实际write。全部字段、零额度、非授权声明和8角色回读。
- `setup-13-rerun`：重新Explore和当前清单，相同7文件零写入，无重复角色/额度。
- conflict toy已存在原日志、材料和AGENTS周围两个KEEP区块：宿主展示旧/新区块、逐项选择、再次完整稿批准，最终仅改AGENTS指定区块+补缺findings。旧日志、project、角色表、政策、README字节不变，周围指令保留。

### Codex（setup-native、setup-codex-*）

- 宿主自己发现`codex debug models`一手清单（非bundled目录），slug `deepseek-v4.1-flash`，支持low/high/max。目录没有provider，要求补核；宿主只输出非凭据配置`model_provider=custom`，形成`custom/deepseek-v4.1-flash | low`，8角色逐轮确认。
- 全文7文件展示后明确批准，`setup-codex-write`真实apply_patch被workspace-write保护拒绝，0/7。操作者仅toy重启放开写域，`setup-codex-write-retry`真实7/7落盘与读回。
- `setup-codex-rerun`真实当前目录+逐文件diff，全部IDENTICAL，零写入。初次及重跑曾裸python3解析，随后UV重跑；记录纪律失败，不冒充全程UV。

### Claude（setup-native、setup-claude-*）

- 起初尝试help、`--list-models`等无目录，自报不可信，停且零写。**没有永久沿用旧缺口**：合理一手替代由宿主自己通过现有env请求`GET /v1/models`，HTTP200、27个真实id；未打印base/header/key、未读凭据文件，Python用UV。
- 8角色逐轮确认 `anthropic/claude-sonnet-4-6 | high`，id来自目录，provider依据当前Anthropic兼容宿主身份；thinking目录未细列，high按宿主支持档位确认，局限明示。reviewer轮timeout后恢复同session完整稿，不假造输出。
- `setup-claude-draft-retry`完整7文件全文，`setup-claude-write`批准后真实写7文件、回读。`setup-claude-rerun`当前清单与已有文件检查，无写入。

**共同快照**：79轮`global-before/after.json`全部相同（`~/.agents/pstack-models.md`hash+mtime）；只有pi新建、Claude新建、Codex获准重试、pi冲突修补4轮项目变化，变化精确为批准路径。现有研究日志两次幂等及冲突保持字节，全部归档。setup没有研究结论/实验或对外动作。

## 各票AC逐项判断

### #38
1. 共享合同确认：**通过**，approved原件。
2. 限定安装route-only真实无任务/网络：**通过代表三宿主场景**，上表及快照。
3. 删除旧入口、无产品残留、39清单：**通过静态**（迁移/历史例外不误作新入口）。
4. 路由结构/引用图正反例：**通过静态回归**。
5. breaking迁移+宿主派发/串行：**通过文档/代表行为**，本次修pi实际命令映射；不是泛化保证。
6. checker单命令：**通过**。

### #39
1. 全skill策略正反例：**通过静态**。
2. setup唯一非显式例外+yaml：**通过安装hash/字段与静态**。
3. 门基线与反例：**通过静态**，本次没改审批科研语义。
4. 未点名/直接点名/级联旧门：**通过代表三宿主入口与rebuttal策略门**；不宣称穷尽所有门。
5. README U/M：**通过静态**。
6. checker：**通过**。

### #40
1. 新建角色/政策/种子：**通过三宿主真实多轮**，Claude目录替代、Codex写域重试局限如上。
2. 重复幂等：**通过三宿主**，快照零变动。
3. 既有冲突保留、只补缺：**通过pi代表**；Claude/Codex冲突分支本轮未跑。
4. 不可用slug停：**通过pi代表**；其他宿主本轮未跑。
5. 全局表与旧日志不变：**通过全部快照+pi冲突及三宿主重跑**。
6. 模板角色/非法额度正反例：**通过静态**。
7. checker：**通过**。

### #46（仅本agent负责入口部分）
1. 所有前票证据齐备且本票评论汇总：**未完成**；这里只交#38/#39/#40/入口，无GitHub评论授权动作。
2. 全Seam B场景：**未完成**；路由矩阵已实际尝试，但Codex mismatch与Claude new-task已有修后重跑安全证据，但严格逐字todolist/完整计划质量未全过；其他科研路线由对应agent负责。
3. 三宿主安装字段+直接/级联：**通过代表场景**；非所有叶全部行为。
4. 静态、链接、清单：**通过**，39/U38/M1；18 tests +41 scripts tests=59绿。
5. breaking最终核对：**通过**，pi原生命令错误已修。
6. v2.0.0 tag：**未执行**，用户禁止tag，且剩余失败不满足release-gate。

## 重测与剩余事项

完成前合并最新integration（仍67a04ff）后重跑：`uv run python scripts/check-skills.py`、`uv run python -m unittest discover -s tests -v`（18）、`uv run python -m unittest discover -s scripts -p 'test*.py' -v`（41）；`git diff --check`通过。日志在归档根。

可自主继续的小项：逐字todolist与完整模板行为仍不满足；Codex mismatch API失败已重试，Claude route-only旧任务变更已红绿修复并重跑。不要以安装/正文增强代替重跑。不能自主宣称：所有科研路线与全部审批门均已验；也不能tag、push、对外投稿。没有沿用SSL或认证为永久阻碍；本范围公开外部材料并非必需，所有toy身份明确。
