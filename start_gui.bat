@echo off
cd /d "%~dp0"
echo Starting Youtube-DL GUI...
pip install -r requirements.txt >nul 2>&1
python gui.py
pause
