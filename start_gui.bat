@echo off
cd /d "%~dp0"
echo ==================================================
echo          YouTube Downloader + Auto-Cutter
echo ==================================================
echo.
echo [1/2] Checking and installing requirements...
pip install -r requirements.txt >nul 2>&1
echo       Done.
echo.
echo [2/2] Launching Application...
python gui.py
pause
