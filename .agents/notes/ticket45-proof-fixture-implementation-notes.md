# Ticket45 proof fixture 修复

## 状态

- 单 unit：done；仅修 `scripts/test_check_skills_ticket45.py` 和本 notes。单测红 rc=1 → 绿 rc=0；#45（4）/#55（17）/M（4）共 25 tests 全绿 rc=0；证据 `/tmp/spec48-ticket45-fixture-fix/logs/`。下一步由 parent 验收本提交。

## 入口与决策

- 用户指定实现 worker，直接执行、不继续派发，预算 <=10% 上下文。使用已新建的隔离 worktree `t3/fix-ticket45-proof-fixture`，先 fast-forward merge `f7b03400a4b77bc77265e9076199977815163a87`；不动 integration/主目录、不 push/tracker。
- 已读全局 Multi-Agent/model 可用性/CODING_STANDARDS、仓库规则、TDD skill 及测试/Mock 指南、pre-implement、领域规则与 ADR-0005。沿用用户指定的既有 checker 级联 seam，不扩展产品。
- 旧控制器退休后，proof 配方使用 `proof-review` slug。测试 fixture 将实际 slug 展开为现有入口路径，先用真实追踪集合验证正例，再把同一路径替换为缺失交接资源；不向产品重新加入源码路径依赖。
- 保留原正向文件组、`assertNotEqual` 与缺失资源诊断断言，不复活旧控制器，不处理六个历史失败或九条 archive 诊断。
- 独立 checker 探针用真实 checkout/追踪集合核验：正例无诊断；仅损坏目标后恰好一条 `proof.md:9` 的 `proof-review/references/missing-handoff.md` 不存在/未追踪诊断。记录 `logs/corrupt-checker.log`，rc=0。
- 验收逐项核对 KISS/YAGNI/DRY：沿用现有 helper/seam，只增加 slug→真实入口的正向 fixture，无产品改动或额外抽象；`git diff --check` rc=0。所有 Python 经 uv 离线执行、树外 TMPDIR、串行且使用 120 秒 timeout；未调查其他测试。

## Deviations

- 无范围偏离；不是给新配方添加路径，而是使路径级联测试 fixture 适配 slug 路由。
