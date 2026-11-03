@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [Aegis Health] Creating virtual environment...
    where py >nul 2>nul
    if errorlevel 1 (
        python -m venv .venv
    ) else (
        py -3 -m venv .venv
    )
    if errorlevel 1 (
        echo.
        echo Could not create the virtual environment. Please install Python 3.10+.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" -c "import customtkinter" >nul 2>nul
if errorlevel 1 (
    echo [Aegis Health] Installing dependencies...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Dependency installation failed. Check your internet connection.
        pause
        exit /b 1
    )
)

echo [Aegis Health] Starting desktop application...
".venv\Scripts\python.exe" main.py
if errorlevel 1 (
    echo.
    echo Aegis Health exited with an error. See the traceback above.
    pause
)
endlocal
