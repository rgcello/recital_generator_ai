#!/bin/bash

# Build script for Recital Program Generator
# This will create a standalone executable

echo "Building Recital Program Generator..."

# Install PyInstaller if not already installed
pip install pyinstaller

# Build the application
pyinstaller --name="RecitalProgramGenerator" \
    --onefile \
    --windowed \
    --add-data "repertoire:repertoire" \
    --add-data "ai:ai" \
    --hidden-import="openai" \
    --hidden-import="docx" \
    --hidden-import="pydantic" \
    --icon=icon.ico \
    generate_recital.py

echo "Build complete! Check the 'dist' folder for the executable."
