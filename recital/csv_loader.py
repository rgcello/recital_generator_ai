import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def get_csv_files(
    inbox_dir: str = "csv_inbox",
) -> List[Tuple[Path, List[Dict[str, str]]]]:
    """
    Get all CSV files from the inbox directory with their data.

    Args:
        inbox_dir: Path to the directory containing CSV files

    Returns:
        List of tuples (csv_path, entries) for each valid CSV file
    """
    inbox_path = Path(inbox_dir)

    if not inbox_path.exists():
        print(f"Warning: Directory '{inbox_dir}' does not exist")
        return []

    csv_files = []

    for csv_file in inbox_path.glob("*.csv"):
        entries = _load_single_csv(csv_file)
        if entries:
            csv_files.append((csv_file, entries))

    return csv_files


def load_csv_files(inbox_dir: str = "csv_inbox") -> List[Dict[str, str]]:
    """
    Load CSV files from the inbox directory and convert to JSON format.

    Expected CSV format (no headers):
    student,description
    student,description
    ...

    Args:
        inbox_dir: Path to the directory containing CSV files

    Returns:
        List of dictionaries with 'student' and 'description' keys
    """
    inbox_path = Path(inbox_dir)

    if not inbox_path.exists():
        print(f"Warning: Directory '{inbox_dir}' does not exist")
        return []

    all_entries = []

    for csv_file in inbox_path.glob("*.csv"):
        entries = _load_single_csv(csv_file)
        if entries:
            all_entries.extend(entries)

    return all_entries


def _load_single_csv(csv_path: Path) -> Optional[List[Dict[str, str]]]:
    """
    Load a single CSV file with strict format validation.

    Args:
        csv_path: Path to the CSV file

    Returns:
        List of entries if valid format, None if invalid
    """
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            entries = []

            for row_num, row in enumerate(reader, start=1):
                # Skip empty rows
                if not row or all(cell.strip() == "" for cell in row):
                    continue

                # Strict validation: exactly 2 columns
                if len(row) != 2:
                    print(
                        f"Skipping '{csv_path.name}': Row {row_num} has {len(row)} columns (expected 2)"
                    )
                    return None

                student, description = row

                # Validate both fields are non-empty
                if not student.strip() or not description.strip():
                    print(f"Skipping '{csv_path.name}': Row {row_num} has empty fields")
                    return None

                entries.append(
                    {"student": student.strip(), "description": description.strip()}
                )

            if entries:
                print(f"Loaded {len(entries)} entries from '{csv_path.name}'")
                return entries
            else:
                print(f"Skipping '{csv_path.name}': No valid entries found")
                return None

    except Exception as e:
        print(f"Error reading '{csv_path.name}': {e}")
        return None
