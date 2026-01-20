# YouTube-DL GUI

A clean, modern graphical interface for downloading videos and audio from YouTube, built with Python, `customtkinter`, and `yt-dlp`.

## Features
- **Easy to Use**: Simple paste-and-click interface.
- **Format Selection**: Choose between Best Quality (Auto), Audio Only (High Quality MP3), 1080p, or 720p.
- **Real-time Progress**: View download percentage directly in the app title.
- **Modern UI**: Dark mode interface using CustomTkinter.

## Requirements

### 1. Python Libraries
Install the required dependencies:
```bash
pip install customtkinter yt-dlp
```

### 2. FFmpeg (Critical)
**FFmpeg must be installed and added to your system PATH** for:
- Converting video to MP3/Audio.
- Merging separate video and audio streams (required for high-quality 1080p downloads).

**If FFmpeg is missing:**
- High-quality video downloads might fail or have no audio.
- "Best Audio" conversion will fail.

## How to Run

1. **Option 1 (Batch Launcher)**: Double-click `start_gui.bat`.
2. **Option 2 (Command Line)**:
   ```bash
   python gui.py
   ```

## Usage
1. Paste a YouTube URL into the input box.
2. Click **Fetch Formats**.
3. Select your desired quality (e.g., "Best Video + Audio" or "Best Audio Only").
4. Click **Download Selected**.
5. Files will be saved in the same folder as the script.
