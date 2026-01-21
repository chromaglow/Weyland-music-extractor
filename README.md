# YouTube-DL GUI

A clean, modern graphical interface for downloading videos and audio from YouTube, built with Python, `customtkinter`, and `yt-dlp`.

## Features
- **Easy to Use**: Simple paste-and-click interface.
- **Auto-Cut Tracks**: Automatically splits videos (like concerts or albums) into individual tracks based on timestamps in the description or comments.
- **Smart Tracklist**: Detects "00:00 Song" and "Song 00:00" formats. Includes a manual editor to confirm or tweak splits before cutting.
- **Format Selection**: Choose between Best Quality (Auto), Audio Only (High Quality MP3), 1080p, or 720p.
- **Output Control**: Select exactly where you want your files to go.
- **Real-time Progress**: View download percentage directly in the app title.
- **Modern UI**: Dark mode interface using CustomTkinter.

## Requirements

### 1. Python Libraries
The included `start_gui.bat` will automatically install these for you.
```bash
pip install customtkinter yt-dlp
```

### 2. FFmpeg (Bundled/Local)
This tool uses `ffmpeg` for splitting videos and converting audio.
- The script looks for `ffmpeg.exe` in the application folder first.
- If not found, it falls back to the system `ffmpeg` (if installed in PATH).

**Note:** Ensure `ffmpeg.exe` is present in this folder for the best experience.

## How to Run

1. **Double-click `start_gui.bat`**.
   - This checks for updates, installs requirements, and launches the app.

## Usage
1. Paste a YouTube URL (e.g., a concert or album) into the input box.
2. Click **Fetch Formats**.
3. Select your desired quality.
   - *Tip:* Select "Best Audio (High Quality)" for music albums.
4. (Optional) Check **Auto Split by Chapters/Tracklist** to cut the video into songs.
5. Click **Download Selected**.
6. If Auto Split is on, a popup will ask you to confirm the track names and times.
7. Files will be saved to your selected **Output Folder**.
