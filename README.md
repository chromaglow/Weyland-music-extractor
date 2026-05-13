# Weyland-Yutani Music Extractor

> *Building better music. One track at a time.*

A YouTube audio and video downloader with intelligent track splitting — automatically cuts albums and concert recordings into individual songs based on timestamps found in descriptions or comments.

## Features

- **Auto-split tracks** — detects `00:00 Song` and `Song 00:00` timestamp formats in descriptions and comments, then splits the download into numbered files. On by default.
- **Audio quality tiers** — choose High (320 kbps), Medium (128 kbps), or Low (64 kbps) MP3
- **Video download** — Best (auto), 1080p, or 720p
- **Tracklist editor** — confirm or tweak track names and timestamps before cutting
- **Output control** — choose exactly where files are saved
- **Real-time progress** — download percentage shown in the title bar

## Requirements

### Python libraries
`start_gui.bat` installs these automatically:
```
customtkinter
yt-dlp
```

### FFmpeg
Used for audio conversion and track splitting.
- Place `ffmpeg.exe` in the same folder as the app (recommended)
- Or install FFmpeg system-wide and ensure it's on your PATH

## How to run

Double-click `start_gui.bat` — it installs dependencies and launches the app.

## Usage

1. Paste a YouTube URL into the input box
2. Click **Fetch Formats**
3. Select audio quality (High / Medium / Low) or a video format
4. **Auto-split** is on by default — uncheck it if you want a single file
5. Click **Download Selected**
6. If auto-split is on, confirm the detected track list in the popup
7. Files are saved to your chosen output folder (defaults to the app directory)
