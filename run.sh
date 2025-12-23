#!/bin/bash
# MidiArt Pro 运行脚本

cd "$(dirname "$0")"

# 检查 Python 3 是否可用
command -v python3 >/dev/null 2>&1 || {
    echo "错误: 未找到 Python 3，请先安装:"
    echo "  brew install python@3.12"
    exit 1
}

# 显示 Python 信息（可选，用于调试）
echo "使用 Python: $(python3 --version)"

# 检查并安装 python-tk（Tkinter 支持）
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "检测到缺少 Tkinter 支持，正在安装 python-tk..."
    if command -v brew &> /dev/null; then
        brew install python-tk || {
            echo "警告: 无法通过 Homebrew 安装 python-tk"
            echo "请手动运行: brew install python-tk"
            exit 1
        }
        echo "✓ python-tk 安装完成，请重新运行此脚本"
        exit 0
    else
        echo "错误: 未找到 Homebrew，无法安装 python-tk"
        echo "请先安装 Homebrew 或手动安装 python-tk"
        exit 1
    fi
fi

# 创建虚拟环境（如果不存在）
[ ! -d "venv" ] && {
    echo "正在创建虚拟环境..."
    python3 -m venv venv || exit 1
}

# 激活虚拟环境
source venv/bin/activate

# 检查依赖是否已安装
if ! python3 -c "import mido, cv2, moviepy, customtkinter, pygame, librosa, numpy" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
fi

# 运行应用
echo "启动 MidiArt Pro..."
python3 visualizer.py