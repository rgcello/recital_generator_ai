@echo off
REM Universal launcher script for Recital Program Generator (Windows)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import openai, docx, pydantic, tkinter" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install --upgrade pip
    pip install openai python-docx pydantic
    
    REM Check for tkinter again
    python -c "import tkinter" 2>nul
    if errorlevel 1 (
        echo.
        echo WARNING: tkinter is not installed.
        echo Please reinstall Python with the "tcl/tk and IDLE" option checked.
        echo.
        pause
        exit /b 1
    )
)

REM Run the application
cd recital
python generate_recital.py

REM Deactivate virtual environment when done
deactivate
