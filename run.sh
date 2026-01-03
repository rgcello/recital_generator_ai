#!/bin/bash
# Universal launcher script for Recital Program Generator

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import openai, docx, pydantic, tkinter" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install openai python-docx pydantic
    
    # Check for tkinter
    if ! python -c "import tkinter" 2>/dev/null; then
        echo ""
        echo "WARNING: tkinter is not installed."
        echo "Please install it using your system package manager:"
        echo "  - Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "  - Fedora: sudo dnf install python3-tkinter"
        echo "  - macOS: Already included with Python"
        echo ""
        exit 1
    fi
fi

# Run the application
cd recital
python generate_recital.py

# Deactivate virtual environment when done
deactivate
