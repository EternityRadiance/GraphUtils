@echo off
cd /d "%~dp0" || exit /b 1

if not exist "venv\" (
    echo "Create venv..."
    python -m venv venv
    if errorlevel 1 exit /b 1
)

echo "Activate venv..."
call venv\Scripts\activate.bat
echo "Installing requirements..."
pip install -r requirements.txt >nul 2>&1
echo "Start..."
python main.py
exit /b %errorlevel%
