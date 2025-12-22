#!/bin/bash
# MidiArt Pro macOS 调试版打包脚本（带控制台输出）

cd "$(dirname "$0")"

echo "=== MidiArt Pro macOS 调试版打包脚本 ==="
echo "此版本会显示控制台窗口以便查看错误信息"
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

echo "开始打包（调试模式）..."
echo ""

# 清理之前的构建
rm -rf build dist

# 创建调试版 spec 文件
cat > MidiArt_Pro_debug.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['visualizer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('SourceHanSansSC-Regular.otf', '.'),
        ('SourceHanSansSC-Bold.otf', '.'),
        ('presets', 'presets'),
    ],
    hiddenimports=[
        'pygame',
        'customtkinter',
        'librosa',
        'mido',
        'cv2',
        'moviepy',
        'numpy',
        'tkinter',
        'PIL',
        'imageio',
        'imageio_ffmpeg',
        'scipy',
        'sklearn',
        'numba',
        'llvmlite',
        'soundfile',
        'audioread',
        'moviepy.editor',
        'moviepy.video',
        'moviepy.audio',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=['pyi_rth_imageio.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MidiArt Pro',
    debug=True,  # 启用调试模式
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 调试模式不压缩
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='MidiArt Pro',
)

app = BUNDLE(
    coll,
    name='MidiArt Pro.app',
    icon='icon.ico',
    bundle_identifier='com.midiart.pro',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025',
        'NSRequiresAquaSystemAppearance': 'False',
    },
)
EOF

# 使用调试版 spec 文件打包
pyinstaller MidiArt_Pro_debug.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 调试版打包成功！"
    echo "可执行文件位置: dist/MidiArt Pro.app"
    echo ""
    echo "提示:"
    echo "1. 调试版必须直接运行可执行文件才能看到控制台输出："
    echo "   \"dist/MidiArt Pro.app/Contents/MacOS/MidiArt Pro\""
    echo "2. 如果通过 Finder 双击打开或使用 open 命令，控制台窗口不会显示"
    echo "3. 如果应用崩溃，控制台会显示详细的错误堆栈"
    echo "4. 错误日志也会保存到 ~/MidiArt_Pro_error.log 和 ~/MidiArt_Pro_debug.log"
else
    echo ""
    echo "❌ 打包失败，请检查错误信息"
    exit 1
fi

