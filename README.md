# MidiArt-Pro

一个强大且可定制的MIDI音乐可视化工具，将你的音乐变成艺术。

## 上游仓库

本项目基于 [Aclameta/MidiArt-Pro](https://github.com/Aclameta/MidiArt-Pro) 的 macOS 版本。

[English](README_EN.md)

## 系统要求

- macOS
- Python 3.9 或更高版本
- 推荐使用 Homebrew 安装 Python

## 运行方法

1. 克隆或下载本项目
2. 在终端中进入项目目录
3. 运行启动脚本：

```bash
chmod +x run.sh
./run.sh
```

脚本会自动：
- 检查并创建 Python 虚拟环境
- 安装所需依赖
- 启动应用

## 打包方法

### 生产版本

```bash
chmod +x build_macos.sh
./build_macos.sh
```

打包完成后，应用位于 `dist/MidiArt Pro.app`

### 调试版本

如果需要查看控制台输出以调试问题，可以使用调试版本：

```bash
chmod +x build_macos_debug.sh
./build_macos_debug.sh
```

**重要提示：**
- 调试版本必须使用终端命令打开才能看到控制台输出：
  ```bash
  open "dist/MidiArt Pro.app"
  ```
  或者直接运行可执行文件：
  ```bash
  "dist/MidiArt Pro.app/Contents/MacOS/MidiArt Pro"
  ```
- 如果通过 Finder 双击打开，控制台窗口不会显示
- 错误日志也会保存到 `~/MidiArt_Pro_error.log`
- 首次运行可能需要右键点击并选择"打开"（因为未签名）

## 依赖

主要依赖包括：
- mido
- opencv-python
- moviepy
- customtkinter
- pygame
- librosa
- numpy

完整依赖列表请查看 `requirements.txt`
