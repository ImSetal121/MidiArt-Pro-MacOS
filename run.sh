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