#!/bin/bash
# Research OS Studio 演示脚本
# 用于制作 README 演示 GIF
# 所有命令与结果均为模拟台词，不进行真实扫描、安装或研究操作。

echo "🚀 Research OS Studio 演示"
echo "=========================="
echo "🧪 以下全部为模拟演示，不执行真实扫描、安装、初始化或计划写入。"
echo ""
sleep 1

# 场景1: 安装
echo "📦 步骤1: 安装 Skills 套件"
echo "$ npx skills@latest add toRolex/Research-OS-Studio --list"
sleep 2
echo "📋 [模拟] 展示当前套件可安装的 Skills 列表（未执行真实扫描）..."
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

# 场景3: Research OS Discovery
echo "💡 步骤3: Research OS Discovery 配方"
echo "$ /research-os"
sleep 2
echo "🎯 用户目标: 从研究方向和已有材料形成 Proposal"
echo "🧭 按缺口选择、重排或回访所需的发现能力"
echo "👥 需要挑战时由 fresh 独立 reviewer 审查原始材料"
echo "📋 按授权交付发现报告和/或 Proposal；完成后停止"
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
