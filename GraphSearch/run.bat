@echo off
cd /d "%~dp0" || exit /b 1

if not exist "venv\" (
    python -m venv venv
    if errorlevel 1 exit /b 1
)

call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
python main.py
exit /b %errorlevel%
