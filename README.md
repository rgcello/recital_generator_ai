# Recital Program Generator

A Python application for generating formatted recital programs from CSV student data using AI-powered repertoire matching.

## Features

- Loads student performance data from CSV files
- Uses OpenAI to match fuzzy piece descriptions to canonical Suzuki repertoire
- Generates professionally formatted DOCX programs
- Supports multiple pieces per student
- Automatic sorting by repertoire difficulty
- Handles movement specifications

## Setup

1. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install openai python-dotenv python-docx pydantic
   ```

3. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

1. Place CSV files in `recital/csv_inbox/` directory

   - Format: `student,description` (no headers)
   - Example: `John Doe,Twinkle Variations`

2. Run the generator:

   ```bash
   cd recital
   python3 generate_recital.py
   ```

3. Follow the prompts to enter recital details for each CSV file

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
