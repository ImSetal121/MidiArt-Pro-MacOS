# MidiArt-Pro

A powerful and customizable MIDI music visualizer that turns your music into art.

![MidiArt Pro Running on macOS](images/run_in_macos.png)

## Original Repository

This project is a macOS version based on [Aclameta/MidiArt-Pro](https://github.com/Aclameta/MidiArt-Pro).

**Original Author:**
- GitHub: [@Aclameta](https://github.com/Aclameta)
- Bilibili: [Aclameta](https://space.bilibili.com/109275196)

[中文](README.md)

## Requirements

- macOS 10.13 or later

## How to Run

### Download from Releases (Recommended)

1. Go to the [Releases page](https://github.com/ImSetal121/MidiArt-Pro-MacOS/releases) and download the latest version
2. Download the latest `MidiArt_Pro_*_macOS.zip` file (* represents version number)
3. Unzip the archive
4. Double-click `MidiArt Pro.app` to launch

**Important Notes:**
- First run: If you see a security warning, right-click the app and select "Open", then click "Open" in the dialog
- The app is unsigned, so you may need to allow it in System Settings > Privacy & Security

**Audio Format Support:**
- Supports **MP3** and **WAV** format audio files
- **MP3 format** is recommended for better compatibility
- If you encounter issues with WAV format, please check debug logs

### Run from Source

If you want to run from source or for development:

**Requirements:**
- macOS 10.13 or later
- Python 3.9 or higher (Recommended: install via Homebrew)
- Homebrew (for installing python-tk, handled automatically by the script)

**Steps:**

1. Clone or download this project
2. Navigate to the project directory in terminal
3. Run the startup script:

```bash
chmod +x run.sh
./run.sh
```

The script will automatically:
- Check and install python-tk (Tkinter support, if missing)
- Check and create Python virtual environment
- Install required dependencies
- Launch the application

**Note:**
- If Tkinter support is missing on first run, the script will automatically install `python-tk` via Homebrew
- After installation, you need to run the script again
- If you encounter permission issues, make sure Homebrew is installed

**License Notice:**
- This project is licensed under [CC BY-NC-SA 4.0](LICENSE)
- When using the source code, please comply with the license terms: Attribution, NonCommercial, ShareAlike
- For detailed terms, please see the [LICENSE](LICENSE) file

## How to Build

```bash
chmod +x build_macos.sh
./build_macos.sh
```

After building, the application will be located at `dist/MidiArt Pro.app`

**Important Notes:**
- First run may require right-clicking and selecting "Open" (due to unsigned app)
- You may need to allow unsigned apps in System Settings

**Debug Information:**
If you need to see console output and debug information, run the executable directly:
```bash
"dist/MidiArt Pro.app/Contents/MacOS/MidiArt Pro"
```
Note: If opened via Finder (double-click) or using the `open` command, the console window will not be displayed. Error logs are saved to `~/MidiArt_Pro_error.log` and `~/MidiArt_Pro_debug.log`

## Dependencies

**System Dependencies:**
- python-tk (installed via Homebrew, handled automatically by the script)

**Python Dependencies:**
Main dependencies include:
- mido
- opencv-python
- moviepy
- customtkinter (requires Tkinter support)
- pygame
- librosa
- numpy

For complete dependency list, see `requirements.txt`

