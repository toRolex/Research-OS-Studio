# 🎬 演示素材制作指南

这个目录用于存放 Research OS Studio 的演示素材。

## 📋 需要的素材清单

### 1. 主演示 GIF (`demo.gif`) - 最重要！
**建议时长**: 30-60 秒  
**内容建议**:
```bash
# 场景1: 项目初始化
$ /setup-research-os
🤖 正在探索项目结构...
📁 发现已有目录: src/, docs/, tests/
📝 建议创建工作区: research/
❓ 是否继续? (y/n): y
✅ 初始化完成！

# 场景2: Idea Discovery 工作流
$ /idea-discovery
🎯 请输入研究方向: "基于深度学习的蛋白质结构预测"
📚 Phase 1: 文献调研中...
💡 Phase 2: 生成 5 个候选 Idea
🔍 Phase 3: 查新检查
👥 Phase 4: 独立评审
📋 交付: IDEA_DISCOVERY.md
✅ 工作流完成，等待用户决策

# 场景3: 实验计划
$ /experiment-plan
📊 为选定的 Idea 制定实验计划...
💰 预算约束: GPU 10小时
📈 评估指标: Accuracy, F1-score, RMSE
✅ 计划已保存: experiment_plan.md
```

### 2. 工作流程图 (`workflow-overview.png`)
**建议尺寸**: 1200x800px  
**内容**: 三大流程的关系图

### 3. 界面截图 (`screenshots/`)
- `setup-process.png` - 初始化界面
- `skill-execution.png` - Skills 执行过程
- `results-delivery.png` - 结果交付界面

## 🛠️ 制作工具推荐

### GIF 录制工具
1. **LICEcap** (Mac/Windows) - 轻量级 GIF 录制
2. **ScreenToGif** (Windows) - 功能强大
3. **asciinema** (跨平台) - 终端录制，可转 GIF
4. **OBS Studio** - 专业录屏软件

### 图表制作工具
1. **Excalidraw** - 手绘风格，适合技术图表
2. **Draw.io** - 专业流程图
3. **Figma** - 设计工具，适合精美图表
4. **Mermaid** - 代码生成图表（已提供示例）

### 截图工具
1. **CleanShot X** (Mac) - 专业截图
2. **Snagit** - 功能丰富
3. **ShareX** (Windows) - 开源免费
4. **浏览器开发者工具** - 网页截图

## 📐 尺寸建议

- **演示 GIF**: 800x600px 或 1200x675px (16:9)
- **工作流程图**: 1200x800px (3:2)
- **界面截图**: 保持原始分辨率，建议压缩到 1920px 宽度

## 🎨 设计建议

1. **配色方案**: 使用项目主题色
2. **字体**: 使用等宽字体展示代码
3. **动画**: 保持流畅，避免过快
4. **标注**: 添加关键步骤的文字说明
5. **品牌**: 保持与项目 README 风格一致

## 📝 制作完成后

1. 将素材文件放入此目录
2. 更新主 README.md 中的图片链接
3. 删除 HTML 注释占位符
4. 提交到 GitHub

---

**需要帮助？** 查看 [workflow-diagrams.md](workflow-diagrams.md) 获取 Mermaid 图表示例。
