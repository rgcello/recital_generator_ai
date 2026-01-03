#!/bin/bash
# Universal launcher script for Recital Program Generator (macOS)
# Double-click this file to run the application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        echo "Press any key to exit..."
        read -n 1
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
fi

# Run the application
cd recital
python generate_recital.py

# Deactivate virtual environment when done
deactivate

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo "Press any key to exit..."
    read -n 1
fi
