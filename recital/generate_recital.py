import sys
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

import openai

from csv_loader import get_csv_files
from ai.prompts import build_canonical_resolution_prompt
from ai.models import StudentPerformance  # your Pydantic model
from ai.llm_parser import parse_llm_recital_response
from docx_generator import generate_recital_docx
from sort_students import student_sort_key

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("Error: OPENAI_API_KEY not found in environment variables")
    print("Please create a .env file with your OpenAI API key")
    sys.exit(1)


def main():
    print("=== Recital Program Generator ===\n")

    # ------------------------------------------------------------
    # 1. Load CSV files from inbox
    # ------------------------------------------------------------
    csv_files = get_csv_files("csv_inbox")

    if not csv_files:
        print("Error: No valid CSV files found in csv_inbox")
        sys.exit(1)

    print(f"Found {len(csv_files)} CSV file(s) to process\n")

    # ------------------------------------------------------------
    # 2. Load Suzuki repertoire JSON
    # ------------------------------------------------------------
    repertoire_path = Path("repertoire/suzuki_repertoire.json")

    if not repertoire_path.exists():
        print("Error: suzuki_repertoire.json not found")
        sys.exit(1)

    with open(repertoire_path, "r", encoding="utf-8") as f:
        suzuki_repertoire = json.load(f)

    # ------------------------------------------------------------
    # 3. Process each CSV file separately
    # ------------------------------------------------------------
    for file_idx, (csv_path, csv_data) in enumerate(csv_files, start=1):
        print(f"\n{'='*60}")
        print(f"Processing file {file_idx}/{len(csv_files)}: '{csv_path.name}'")
        print(f"{'='*60}\n")

        # Prompt for recital details for THIS CSV file
        studio_name = input(f"[{csv_path.name}] Enter studio name: ").strip()
        recital_title = input(f"[{csv_path.name}] Enter recital title: ").strip()
        recital_date = input(f"[{csv_path.name}] Enter recital date/time: ").strip()
        accompanist = input(f"[{csv_path.name}] Enter accompanist name: ").strip()
        footer_text = input(f"[{csv_path.name}] Enter footer text: ").strip()

        print(f"\n  Loaded {len(csv_data)} entries")

        # Build canonical-resolution prompt
        prompt = build_canonical_resolution_prompt(
            csv_entries=csv_data,
            suzuki_repertoire=suzuki_repertoire,
        )

        # Call OpenAI (Responses API)
        print("  Resolving repertoire with AI...")
        response = openai.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0.3,
        )
        raw_output = response.output_text

        performances = parse_llm_recital_response(raw_output)
        performances = sorted(performances, key=student_sort_key)

        print(f"  Resolved {len(performances)} student performances")

        # Generate output filename from CSV name
        base_name = csv_path.stem  # filename without extension
        output_path = Path("output") / f"{base_name}.docx"

        # If file exists, append timestamp
        if output_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path("output") / f"{base_name}_{timestamp}.docx"

        # Generate DOCX
        generate_recital_docx(
            performances=performances,
            studio_name=studio_name,
            recital_title=recital_title,
            recital_date=recital_date,
            accompanist=accompanist,
            footer_text=footer_text,
            filename=output_path.name,
        )

        print(f"  ✓ Generated: {output_path}")

    print(f"\n{'='*60}")
    print(f"✓ Successfully processed {len(csv_files)} file(s)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
