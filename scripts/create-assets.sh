#!/bin/bash
# Research OS Studio 素材制作脚本

echo "🎨 Research OS Studio 素材制作工具"
echo "=================================="
echo ""

# 检查依赖
check_dependency() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1 已安装"
        return 0
    else
        echo "❌ $1 未安装"
        return 1
    fi
}

echo "🔍 检查依赖工具..."
echo ""

# 检查工具
TOOLS=("asciinema" "ffmpeg" "convert" "node" "npm")
MISSING_TOOLS=()

for tool in "${TOOLS[@]}"; do
    if ! check_dependency $tool; then
        MISSING_TOOLS+=($tool)
    fi
done

echo ""

# 安装缺失工具
if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "📦 需要安装以下工具:"
    for tool in "${MISSING_TOOLS[@]}"; do
        echo "   - $tool"
    done
    echo ""
    echo "🍎 Mac 安装命令:"
    echo "   brew install asciinema ffmpeg imagemagick node"
    echo ""
    echo "🐧 Ubuntu/Debian 安装命令:"
    echo "   sudo apt-get install asciinema ffmpeg imagemagick nodejs npm"
    echo ""
    echo "💡 或者使用在线工具:"
    echo "   - GIF 录制: https://www.screentogif.com/"
    echo "   - 图表制作: https://excalidraw.com/"
    echo "   - 终端录制: https://asciinema.org/"
    exit 1
fi

echo "🎉 所有依赖工具已安装！"
echo ""

# 创建目录
mkdir -p docs/assets/screenshots
echo "📁 创建目录: docs/assets/screenshots"

# 执行演示脚本
echo ""
echo "🎬 开始录制演示..."
echo "💡 提示: 按 Ctrl+D 结束录制"
echo ""

asciinema rec docs/assets/demo.cast

echo ""
echo "🎥 录制完成！"
echo ""

# 转换为 GIF
if command -v asciicast2gif &> /dev/null; then
    echo "🔄 转换为 GIF..."
    asciicast2gif docs/assets/demo.cast docs/assets/demo.gif
    echo "✅ GIF 已保存: docs/assets/demo.gif"
else
    echo "💡 安装 asciicast2gif 进行转换:"
    echo "   npm install -g asciicast2gif"
    echo ""
    echo "🌐 或使用在线转换工具:"
    echo "   https://dstein64.github.io/gifcast/"
fi

echo ""
echo "📋 下一步操作:"
echo "1. 制作工作流程图 (使用 Excalidraw)"
echo "2. 添加界面截图"
echo "3. 更新 README.md 中的图片链接"
echo ""
echo "📖 详细指导: docs/assets/README.md"
