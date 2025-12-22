# MidiArt-Pro

A powerful and customizable MIDI music visualizer that turns your music into art.

![MidiArt Pro Running on macOS](images/run_in_macos.png)

## Upstream Repository

This project is a macOS version based on [Aclameta/MidiArt-Pro](https://github.com/Aclameta/MidiArt-Pro).

**Original Author:**
- GitHub: [@Aclameta](https://github.com/Aclameta)
- Bilibili: [Aclameta](https://space.bilibili.com/109275196)

[中文](README.md)

## Requirements

- macOS
- Python 3.9 or higher
- Recommended: install Python via Homebrew

## How to Run

### Download from Releases (Recommended)

1. Go to the [Releases page](https://github.com/ImSetal121/MidiArt-Pro-MacOS/releases) and download the latest version
2. Download the latest `MidiArt_Pro_*_macOS.zip` file (* represents version number)
3. Unzip the archive
4. Double-click `MidiArt Pro.app` to launch

**Important Notes:**
- First run: If you see a security warning, right-click the app and select "Open", then click "Open" in the dialog
- System Requirements: macOS 10.13 or later
- The app is unsigned, so you may need to allow it in System Settings > Privacy & Security

### Run from Source

If you want to run from source or for development:

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

**License Notice:**
- This project is licensed under [CC BY-NC-SA 4.0](LICENSE)
- When using the source code, please comply with the license terms: Attribution, NonCommercial, ShareAlike
- For detailed terms, please see the [LICENSE](LICENSE) file

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

