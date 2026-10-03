# v2 final contract fixes

## 输入与边界
- 起点76af6a3；approved全文、CONTEXT、原spec/ADR0006/0007、validation及release原报告已读。单implementer；只扩既有checker、编排正文与reference，不重写叶科研流程。
- 六项均可从当前代码复现：improvement无批次reference；Role仅示例；policy空值/重复/时间；dot级联跳过；migration整文件豁免；invocation子串/首match。
- TDD先红绿，全部Python经UV。未动main/global/push/tag/PR/票。

## 决策
- 政策模板保留未指定零额度；静态不把默认模板升级为许可。异构compute三字段允许按单位配对，其余字段唯一。
- 角色声明落每条playbook的实际阶段；入口解释dispatch执行语义，不更改宿主进程。

## 验证与纠错
- RED18失败→GREEN6测试。附加offset +01:99被datetime自动规范化，scope纯数字可漏检：新增RED2→GREEN，主动拒绝无效offset分钟与非文字scope。
- 全tests29+scripts45=74绿，checker39/U38/M1、主动LSP2文件0；最终merge integration仍76af6a3 already-up-to-date。
- 原review两份从父session完整消息恢复并读全文，存evidence/original-review-{spec,standards}.md；主pane期间gone，不把用户摘要冒充原报告。
- 首真实GLM expired/valid虽有0job/失败+成功/拒第三，但裸python解析违反UV，完整保留不采全纪律PASS。新gpt medium父＋project glm high implementer、gpt medium两fresh review均全UV；expired-retest0写0job、valid-retest2attempt真实7/0，CPU1.629833e-05及两轮回应canonical逐字核。

## Deviations
- 旧异构政策正例把compute额度从0改为1，但run_limit与valid_for_hours仍0且scope/currency/expiry未指定。兼容此不可执行默认政策；不要求任意非零建议额度就是已授权批次。实际运行仍按日志全部门。
- valid-retest raw session+stdout超原3MB后诚实停止；明确追加20MB/15min、不给新attempt/dialog/轮数/expiry，才完成剩余Round2与日志。历史超限保留FAIL，不追认。未新建任何产品runtime；scratch fixture/meter仅TOY计量且覆盖范围明确排除宿主和wrapper。
- 新验收采用当前source-layout逐字副本而非重复安装三宿主；本任务范围补分支，不重演全部长科研流程/宿主矩阵。
