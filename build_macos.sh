#!/bin/bash
# MidiArt Pro macOS 打包脚本

cd "$(dirname "$0")"

echo "=== MidiArt Pro macOS 打包脚本 ==="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "错误: 未找到虚拟环境，请先运行 ./run.sh 创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查 PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "正在安装 PyInstaller..."
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyinstaller
fi

echo "开始打包..."
echo ""

# 清理之前的构建
rm -rf build dist

# 使用 spec 文件打包（推荐，更灵活）
if [ -f "MidiArt_Pro.spec" ]; then
    echo "使用 spec 文件打包..."
    pyinstaller MidiArt_Pro.spec --clean --noconfirm
else
    echo "使用命令行打包..."
    # 对于 macOS，使用 --onedir 创建 .app bundle
    pyinstaller \
        --name="MidiArt Pro" \
        --windowed \
        --onedir \
        --icon=icon.ico \
        --add-data="SourceHanSansSC-Regular.otf:." \
        --add-data="SourceHanSansSC-Bold.otf:." \
        --add-data="presets:presets" \
        --hidden-import=pygame \
        --hidden-import=customtkinter \
        --hidden-import=librosa \
        --hidden-import=mido \
        --hidden-import=cv2 \
        --hidden-import=moviepy \
        --hidden-import=numpy \
        --hidden-import=tkinter \
        --hidden-import=PIL \
        --hidden-import=imageio \
        --hidden-import=imageio_ffmpeg \
        --hidden-import=scipy \
        --hidden-import=sklearn \
        --hidden-import=numba \
        --hidden-import=llvmlite \
        --hidden-import=soundfile \
        --hidden-import=audioread \
        --collect-all=pygame \
        --collect-all=librosa \
        --collect-all=moviepy \
        --collect-all=imageio_ffmpeg \
        --additional-hooks-dir=. \
        --runtime-hook=pyi_rth_imageio.py \
        --noconfirm \
        visualizer.py
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 打包成功！"
    echo "可执行文件位置: dist/MidiArt Pro.app"
    echo ""
    echo "提示:"
    echo "1. 首次运行可能需要右键点击并选择'打开'（因为未签名）"
    echo "2. 可以在系统设置中允许运行未签名的应用"
else
    echo ""
    echo "❌ 打包失败，请检查错误信息"
    exit 1
fi

