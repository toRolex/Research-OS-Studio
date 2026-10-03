# 最后合并与独立六项合同复验

## 提交、范围、结论

- `76af6a3 --no-ff 9091baf` 合并提交 **`1e67d82`**；同六项内独立发现 relative base 残余，最小修复 **`d426eb6`**。原 main 保持原 tip `837d1e86b18f1f753964d51d18a64e069011209a`；无 tag/push/PR，#37/#46最终关闭留主。
- 完整读两份原review、六项修复报告/notes、全部产品diff、入口/improvement/shared batch、approved。只复核六项和当前受影响宿主路径，不扩到无关旧科研任务。
- **六项原反例均独立复现 pre-fix GREEN → fixed RED；同范围新遗漏已TDD闭合。** 静态不是行为证据；真实role/过期拒绝/失败占attempt分别亲核原session与账。历史UV/存储越界不追认。

## 独立损坏副本与新遗漏

新建Git追踪副本，用真实默认 `uv run --no-project python scripts/check-skills.py`，未调用作者回归测试函数替代CLI：

| Counterexample | `76af6a3` checker | 合后checker |
|---|---:|---:|
| 不存在 `./references/INDEPENDENT-NONEXISTENT.md` | exit0 | exit1 |
| README迁移说明之后另加“现在请使用 /ask-research-os” | exit0 | exit1 |
| 重复disable true/false | exit0 | exit1 |
| 空currency | exit0 | exit1 |
| 非法日历ISO `2031-02-29T12:00:00Z` | exit0 | exit1 |
| 重复scalar cost_limit | exit0 | exit1 |

另外 `../` missing、false/true反序、坏offset、无时区、重复expiry、重复allow均红；同副本最初/restore正例exit0，共12种反例。新增残余不属扩审：improvement里的 `./references/batch-authorization.md` **source.parent下不存在**，原修复仍fallback skill-root同名而绿。新增到既有test方法先RED1，再限定显式 `./` / `../` 仅相对引用文件，GREEN；合法 `../references/batch-authorization.md`继续绿。只改checker条件+现有test case，测试数仍74，skills字节未改。

## 真实Role与补实验账证据（独立只读核原包）

- 直接读归档原session `model_change/thinking_level_change`：父gpt-6.1-sol/medium；一个fresh implementer glm-5.3-flash/high；两个各自独立fresh reviewer gpt-6.1-sol/medium。CLI显式model+thinking与本项目角色表相同，无fork/resume；未把prompt请求名当身份。
- expired-retest原22工具实读UTC `2026-10-03T12:56:38Z` 对2020 expiry，**0job，项目before=after，包括research-log，0新文件**；未冒充独立审查完成。
- valid-retest两个真实meter命令及toolResult：a1 **exit7**，a2 **exit0**。session中成功的账本edit先于各真实job；先完成失败账再记a2预留，第三拒绝在a2后。一个失败edit保留且不当成功预留。失败同占2/2名额；第三无reservation/started_at/产物，retry3和CPU余量不创造attempt。
- 原meter累计用Decimal复算 **0.000016298333333333333 cpu-core-hour**（单次均<0.001、累计<0.004）；0USD仅明确toy job范围，覆盖innerUV与evaluator后代，排除宿主/wrapper，不虚填模型费用。五行a2 MAE独算0；CSV仍仅表头，a1 n0无MAE不能赋零。
- 8类冻结物与前快照/当前源字节一致；两原review最终assistant文本在canonical逐字相同。此核实不宣称执行时源码身份或完整历史文件系统/独立admission已认证。
- 原裸Python失败、3MB越界、超限后写入纪律问题保持**FAIL**。唯一明确20MB/15min追加只允许余下复审/日志，不增attempt/dialog/轮数/expiry，不删失败。TOY9/ready仅当前产物有限PASS，完整历史流程FAIL，不是publication-ready。

## 2.49MB原归档独立安全核

原包 `evidence/v2-final-contract-fixes.tar.gz`：**2,489,643 bytes**；SHA256 **`f2657476febf3689258397dc35d924b0e32ba5b4ca505d946374438d056b2df1`**。

- 456常规文件（无link/绝对路径/`..`逃逸），455 manifest payload的bytes+SHA全部匹配。
- 包内272份skills文件与当前仓库逐字一致；无把旧宿主全矩阵当新skill验证。
- 所有payload及解码JSON字符串扫描 private key/provider key/Bearer/URL userinfo/signed token query，候选**0**，不输出值，不重打/改写原包，不抹失败。

独立复验新轻包 [v2-final-contract-independent-verify.tar.gz](evidence/v2-final-contract-independent-verify.tar.gz)：**31,575 bytes**，SHA256 **`e2107183209155532ccec7e95a9f278ec45508b9418a8f62eb4797be52b4d7d4`**，49常规文件/48payload匹配，含原反例RED/GREEN、所有suite/独立archive与trace audit、GitHub命令结果、额外脚本误计失败日志；不复制损坏源码树，敏感候选0。原失败不删。

## 合后当前skill三宿主轻验

三宿主实际调用及唯一Claude针对性修正见 [配套轻验报告](v2-merged-host-smoke.md)；执行skills来自merge `1e67d82`，后`d426eb6`只checker/test、不影响安装字节。使用已有明确TOY，不生成新长科研正文，不扩资源，不阉割工具。pi真fresh，Codex默认workspace-write无法建立fresh则如实 `independent review not performed`，不改沙箱/越权重试。Claude首轮真实缺口保留，不把重跑追认首轮PASS。

- 四条真实调用均exit0：pi341秒、Claude首193秒、Codex232秒、唯一Claude retry258.77秒。默认tools；仅允许独立review证据域写，科研project前后SHA零变化、科研job0、真实UTC拒过期。
- 三宿主各39/270安装文件，共810源/安装/终验SHA一致；source272文件含额外两个非安装文件 `skills/README.md` 和 `skills/idea-cycle/source-verification.md`，分母不同不是误报。
- pi真fresh gpt medium及全primary直接读；Claude首prompt缺两primary且父预判污染/清单压缩/角色代阶段表述保留失败。唯一retry恢复fresh11primary直接read、project角色传参及过期门，不再派第三。
- **Claude retry仍不是严格首次清单PASS**：步骤4插入读取状态破坏原句连续，伪“长度限制截断”的表后纠正保留。pi/Codex首清单完整；各host资源全文实读由原工具结果核，不由报告自述判定。
- Codex真实fresh尝试EPERM停在凭据锁、无模型回应，明确independent review not performed；有限fallback与过期门可接受，不升成三宿主fresh均成功。

轻验包 [v2-merged-host-smoke.tar.gz](evidence/v2-merged-host-smoke.tar.gz)：1,636,956 bytes，SHA256 `cead0cd3fd83e9ce6c897934e55b30c7fc727b3128830ab141066d8c6ca4db10`。独立亲核447常规文件/446payload全部bytes+SHA、272current源、四项目before/after全同；无安装树重复，无敏感候选。脚本/辅助计数失败保留，以tar机械计数为准。

## UV、LSP、diff

`d426eb6`实现最终复测：checker **39/U38/M1**；`tests` **29** + `scripts` **45** = **74通过**。Python全部UV；两改动Python主动LSP **0**（clean2/unsupported0/unavailable0），工作delta及merge diff check过。最后文档提交HEAD另重跑同组确认，不以缓存空宣称clean。

## GitHub EOF恢复与已闭合票补强

一次REST预算预检 core/GraphQL remaining均5000，reset epoch1791039286；预算足够计划7REST请求，GraphQL无使用。摘要恢复仅**2次有界POST**成功，未重试：原 `final-context.md`全文保留且标明历史tip/68tests，附merge/74新状态，不用新总结覆盖历史失败。

- #37历史总结恢复：[5969835754](https://github.com/toRolex/Research-OS-Studio/issues/37#issuecomment-5969835754)
- #46历史总结恢复：[5969836047](https://github.com/toRolex/Research-OS-Studio/issues/46#issuecomment-5969836047)
- #40已闭合票review补强context：[5969852428](https://github.com/toRolex/Research-OS-Studio/issues/40#issuecomment-5969852428)
- #45已闭合票improvement补强context：[5969852560](https://github.com/toRolex/Research-OS-Studio/issues/45#issuecomment-5969852560)

以上评论发于d426eb6前，定位merge1e67d82及原12反例；新relative错base补漏以本报告/commit记录，不谎称已在原评论内。未push，本机源/归档GitHub尚不可读。只评论、不重开/关闭已闭合票或#37/#46。REST消耗7请求，core剩余保守下界4993，GraphQL仍5000；未重复预检。

## 发布判断

代码/六项合同静态可接受；有限默认工具role+batch路径证据与诚实fallback可作为**提交v2.0.0 tag决策的候选**，不是已发布，也不是所有宿主/每条科研流程纪律全PASS。是否接受Claude首失败保留与Codex独立审查不可用的有限代表，由主/用户决定；tag动作与#37/#46最终状态留主，不自行执行。
