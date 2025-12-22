# MidiArt-Pro

A powerful and customizable MIDI music visualizer that turns your music into art.

## Upstream Repository

This project is a macOS version based on [Aclameta/MidiArt-Pro](https://github.com/Aclameta/MidiArt-Pro).

[中文](README.md)

## Requirements

- macOS
- Python 3.9 or higher
- Recommended: install Python via Homebrew

## How to Run

1. Clone or download this project
2. Navigate to the project directory in terminal
3. Run the startup script:

```bash
chmod +x run.sh
./run.sh
```

The script will automatically:
- Check and create Python virtual environment
- Install required dependencies
- Launch the application

## How to Build

### Production Build

```bash
chmod +x build_macos.sh
./build_macos.sh
```

After building, the application will be located at `dist/MidiArt Pro.app`

### Debug Build

If you need to see console output for debugging, use the debug build:

```bash
chmod +x build_macos_debug.sh
./build_macos_debug.sh
```

**Important Notes:**
- The debug build **must** be opened using terminal command to see console output:
  ```bash
  open "dist/MidiArt Pro.app"
  ```
  Or run the executable directly:
  ```bash
  "dist/MidiArt Pro.app/Contents/MacOS/MidiArt Pro"
  ```
- If opened via Finder (double-click), the console window will not be displayed
- Error logs are also saved to `~/MidiArt_Pro_error.log`
- First run may require right-clicking and selecting "Open" (due to unsigned app)

## Dependencies

Main dependencies include:
- mido
- opencv-python
- moviepy
- customtkinter
- pygame
- librosa
- numpy

For complete dependency list, see `requirements.txt`

