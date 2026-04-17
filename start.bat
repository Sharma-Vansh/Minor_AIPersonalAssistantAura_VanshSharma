@echo off
title Aura - Voice AI Assistant

echo.
echo  ╔══════════════════════════════════════╗
echo  ║       ✦  AURA  Voice AI  ✦          ║
echo  ╚══════════════════════════════════════╝
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found! Please install Python 3.9+
    echo  Download: https://www.python.org/downloads/
    pause
    exit /b
)

:: Check if virtual environment exists, activate it if so
if exist "venv\Scripts\activate.bat" (
    echo  [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo  [INFO] No venv found, using system Python.
)

:: Check if dependencies are installed
python -c "import groq" >nul 2>&1
if errorlevel 1 (
    echo  [INFO] Installing dependencies...
    pip install -r requirements.txt
    echo.
)

:: Run Aura
echo  [INFO] Starting Aura...
echo.
python main.py %*

:: If Aura crashes, pause so user can see the error
if errorlevel 1 (
    echo.
    echo  [ERROR] Aura crashed. See error above.
    pause
)