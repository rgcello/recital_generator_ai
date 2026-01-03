# Recital Program Generator

A Python application for generating formatted recital programs from CSV student data using AI-powered repertoire matching.

## Features

- Loads student performance data from CSV files
- Uses OpenAI to match fuzzy piece descriptions to canonical Suzuki repertoire
- Generates professionally formatted DOCX programs
- Supports multiple pieces per student
- Automatic sorting by repertoire difficulty
- Handles movement specifications
- Modern GUI interface with file pickers
- Secure API key storage (per-user configuration)

## Quick Start

### Automatic Setup (Recommended)

**Linux/macOS:**

```bash
./run.sh
```

**macOS (double-click):**

```bash
chmod +x run.command
# Then double-click run.command in Finder
```

**Windows:**

```
Double-click run.bat
```

The launcher scripts will automatically:

- Create a virtual environment if needed
- Install all dependencies
- Check for tkinter
- Launch the application

### Manual Setup

1. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install openai python-docx pydantic
   ```

3. **Install tkinter (if not already installed):**

   - **Linux:** `sudo apt-get install python3-tk`
   - **macOS:** Included with Python
   - **Windows:** Included with Python

4. **Run the application:**

   ```bash
   cd recital
   python3 generate_recital.py
   ```

## Usage

1. **First time setup:**

   - Enter your OpenAI API key when prompted
   - The key is saved securely in `~/.recital_generator/config.json`

2. **Using the GUI:**

   - Enter recital header information (title, subtitle, date, location)
   - Click "Select CSV File" to choose your student data file
   - Click "Select Output Folder" for where to save the program
   - Click "Generate Recital Program"

3. **CSV File Format:**

   - Format: `student,description` (no headers)
   - Example: `John Doe,Twinkle Variations`

4. Generated DOCX files will be saved in `recital/output/`

## Project Structure

```
RecitalGenerator/
├── recital/
│   ├── ai/
│   │   ├── models.py          # Pydantic models
│   │   ├── prompts.py         # AI prompt templates
│   │   └── llm_parser.py      # Response parsing
│   ├── repertoire/
│   │   └── suzuki_repertoire.json  # Canonical repertoire library
│   ├── csv_inbox/             # Input CSV files (gitignored)
│   ├── output/                # Generated DOCX files (gitignored)
│   ├── csv_loader.py          # CSV file handling
│   ├── docx_generator.py      # DOCX formatting
│   ├── sort_students.py       # Student sorting logic
│   └── generate_recital.py    # Main entry point
├── .env                       # Environment variables (gitignored)
├── .gitignore
└── README.md
```

## CSV Format

Each CSV file should contain rows with exactly 2 columns:

- Column 1: Student name
- Column 2: Piece description

No headers should be included.

Example:

```
Jane Smith,Boccherini B-flat Concerto 1st movement
Jane Smith,Vivaldi Sonata in E Minor
John Doe,Book 3 Humoresque
```

## License

Private project - All rights reserved
