# Weyland-Yutani Music Extractor

> *Building better music. One track at a time.*

A YouTube audio and video downloader with intelligent track splitting — automatically cuts albums and concert recordings into individual songs based on timestamps found in descriptions or comments.

## Features

- **Auto-split tracks** — detects `00:00 Song`, `Song 00:00` and `Song (00:00 - 03:45)` timestamp formats in descriptions and comments, then splits the download into numbered files. On by default.
- **Manual tracklist fallback** — when no track list is found, a box opens where you can paste the times and names, or read them from a screenshot (**Read From Image...**, or Ctrl+V with a copied image). You correct the text, then confirm before anything is cut.
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
pillow
winsdk
```
`winsdk` and `pillow` are optional and Windows-only in practice: `winsdk` powers "Read From Image..." in the manual tracklist dialog using Windows' built-in text recognition, and `pillow` lets you paste a copied image with Ctrl+V. Without them, pasting text still works.

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

### When no track list is found

If the description and comments hold no track list, the **Enter Tracklist Manually** box opens:

1. Paste the list, one track per line. Accepted forms include `0:00 Intro`, `Intro 0:00`, `[0:00] Intro`, `1. Intro - 0:00` and `Intro (0:00 - 3:45)`.
2. Or click **Read From Image...** and pick a screenshot of the list, or press Ctrl+V with an image copied. The recognised text lands in the box.
3. Check the text. Image reading can drop a time, most often hour-format ones like `1:02:30`; a line with no time is skipped, so add it back by hand.
4. Click **Use This Tracklist** (or press Ctrl+Enter), then confirm the tracks in the next popup.

Leave the box empty or click **Skip (single file)** to download one uncut file.

## Development

Parsing lives in `tracklist.py`, image reading in `ocr.py`, and the windows in `gui.py`. Run the tests with:

```
python -m pytest -q
```

The dialog tests build their windows hidden and never take focus.
