# Research OS 双版本教程实现记录

## 目标

创建一个可直接双击打开的单文件中文 HTML，帮助不熟悉当前产品的用户：

1. 理解“理想中的纯 Skill 仓库”和当前两个仓库的差别；
2. 分别完成 `Research OS` 与 `Research OS Studio` 的安装和第一次运行；
3. 知道日常应选哪个版本；
4. 避免两个同名 `research-os` CLI 互相覆盖。

## 已核实事实

- 两个包均名为 `research-os`、版本 `0.1.0`、入口均为 `research-os`。
- 旧版 `Research OS` 推荐在源码目录用 `uv run --offline --frozen research-os ...`，不会依赖全局同名命令。
- `Research OS Studio` README 推荐 `uv tool install .` 后使用全局 `research-os`。
- 旧版 workflow 是每条命令一套参数，例如 `research-charter --input --output --report`。
- Studio 提供统一入口：`research-os workflow <name> --project ... --request ...`。
- Studio 的 request 引用输入相对路径与 SHA-256；validator 通过不表示科研结论正确。

## 设计决策

- 模式：Read / 操作教程，而非宣传页。
- 核心隐喻：两条有清晰站台和换乘警告的“研究线路图”。
- 页面不依赖框架、CDN、字体或图片；断网可用。
- 默认推荐新用户先使用 Studio；旧版作为高级、诊断或兼容路径。
- 提供版本切换、目标选择器、步骤清单、命令复制、目录示意和 FAQ。
- 不假装两者是纯 Skill 仓库；明确解释 Python CLI、contracts、validators 与 Skills 的关系。

## Deviations

- `modern-web-guidance` 的在线 `npx` 查询被权限策略拒绝。没有绕过；改用已加载的本地 skill 指南和原生、渐进增强实现。
- 未使用生成图片：此教程核心是路径理解与命令准确性，离线信息图和交互控件比装饰图片更合适。

## 验证结果

- 实际读取双方 `README.md`、`pyproject.toml` 与 CLI `--help`。
- HTML 使用 Python 标准解析器成功解析。
- Playwright 桌面 1440×1000 与移动 390×844 均无横向溢出。
- Studio/Classic Tab 切换正常；控制台无错误或警告。
- 修复首次路线图文字重叠，改为结构化双列线路。
- 修复 Studio 教程缺少创建 request 文件命令。
- 修复首次运行后修订输入可能覆盖追溯链的问题，改为 v2 文件与新输出。
- 修复 Skill 路线未明确 request 和输出路径的问题。
- 修复无 JavaScript 时旧版教程不可见。
- 修复 URL fragment、推荐链接与隐藏面板不同步。
- 打印前自动展开 FAQ，打印后恢复状态。
- 内联 favicon，消除浏览器 404 控制台噪声。

## 架构决策补充

用户随后询问哪个仓库更适合改造成 ARIS 风格纯 Skill 仓库。强模型顾问给出明确建议：选择 `Research OS Studio` 原地改造。原因是 B 的 canonical Skills、ports 产品 Skill、templates 与方法文本更接近可独立重组资产；A 的主要优势恰是本次要剥离的执行 runtime 与低层 CLI。建议冻结当前 runtime 版本后，以 3 个 Skill 试点脱钩，再切换发行模型。
