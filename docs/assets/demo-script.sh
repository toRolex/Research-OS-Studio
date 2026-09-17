#!/bin/bash
# Research OS Studio 演示脚本
# 用于制作 README 演示 GIF

echo "🚀 Research OS Studio 演示"
echo "=========================="
echo ""
sleep 1

# 场景1: 安装
echo "📦 步骤1: 安装 Skills 套件"
echo "$ npx skills@latest add toRolex/Research-OS-Studio --list"
sleep 2
echo "📋 发现 39 个可安装的 Skills..."
sleep 1
echo "$ npx skills@latest add toRolex/Research-OS-Studio --all"
sleep 2
echo "✅ 安装完成！"
echo ""
sleep 1

# 场景2: 初始化
echo "🔧 步骤2: 项目初始化"
echo "$ /setup-research-os"
sleep 2
echo "🤖 正在探索项目结构..."
sleep 1
echo "📁 发现已有目录: src/, docs/, tests/"
sleep 1
echo "📝 建议创建工作区: research/"
echo "❓ 是否继续? (y/n): y"
sleep 2
echo "✅ 初始化完成！"
echo ""
sleep 1

# 场景3: Idea Discovery
echo "💡 步骤3: Idea Discovery 工作流"
echo "$ /idea-discovery"
sleep 2
echo "🎯 请输入研究方向: 基于深度学习的蛋白质结构预测"
sleep 2
echo "📚 Phase 1: 文献调研中..."
sleep 1
echo "💡 Phase 2: 生成 5 个候选 Idea"
sleep 1
echo "🔍 Phase 3: 查新检查"
sleep 1
echo "👥 Phase 4: 独立评审"
sleep 2
echo "📋 交付: IDEA_DISCOVERY.md"
echo "✅ 工作流完成，等待用户决策"
echo ""
sleep 1

# 场景4: 实验计划
echo "📊 步骤4: 实验计划"
echo "$ /experiment-plan"
sleep 2
echo "📊 为选定的 Idea 制定实验计划..."
sleep 1
echo "💰 预算约束: GPU 10小时"
echo "📈 评估指标: Accuracy, F1-score, RMSE"
sleep 2
echo "✅ 计划已保存: experiment_plan.md"
echo ""
sleep 1

echo "🎉 演示完成！"
echo ""
echo "📖 详细文档: docs/user-acceptance-guide.md"
echo "🐛 报告问题: github.com/toRolex/Research-OS-Studio/issues"
