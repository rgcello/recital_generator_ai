import json
from typing import List, Dict


def build_canonical_resolution_prompt(
    csv_entries: List[Dict[str, str]],
    suzuki_repertoire: dict,
) -> str:
    """
    Build a prompt for resolving fuzzy student piece descriptions
    against a closed-world Suzuki repertoire library, allowing
    educated inference within that library.
    """

    repertoire_json = json.dumps(suzuki_repertoire, indent=2, ensure_ascii=False)
    csv_data_json = json.dumps(csv_entries, indent=2, ensure_ascii=False)

    return f"""
You are a canonical repertoire resolver for a Suzuki studio recital.

Your task is to match fuzzy, prose user descriptions of musical pieces to entries
in a closed-world Suzuki repertoire library and return structured JSON.

You are encouraged to TRY to resolve each description using educated inference,
as long as all inferred results come exclusively from the repertoire library
provided below.

----------------------------------------------------------------
CORE PRINCIPLES
----------------------------------------------------------------

• User descriptions are informal, incomplete, and often imprecise.
• You should make a best-effort attempt to resolve each description.
• It is acceptable to make educated guesses when they are reasonable.
• The ONLY hard restriction is that you may NOT invent or use repertoire
  that does not appear in the provided library.

----------------------------------------------------------------
ALLOWED INFERENCE (IMPORTANT)
----------------------------------------------------------------

You MAY use the internal structure of the Suzuki Repertoire Library to infer matches,
including but not limited to:

• Suzuki book numbers (e.g. "Book 3", "Bk. 4")
• Piece numbering (e.g. "Minuet No. 3")
• Partial titles ("Happy Farmer", "Humoresque")
• Common Suzuki naming conventions
• Composer hints if consistent with the library
• Movement names when a parent work is clear

If a description includes enough information to uniquely identify a single
repertoire entry when these clues are combined, you SHOULD resolve it.

----------------------------------------------------------------
MATCHING PRIORITY (CRITICAL)
----------------------------------------------------------------

When resolving fuzzy descriptions, follow this strict hierarchy:

1. COMPOSER FIRST (HIGHEST PRIORITY)
   • If a composer name is mentioned (even partially), it MUST match
   • "Boccherini" can ONLY match pieces by L. Boccherini
   • "Vivaldi" can ONLY match pieces by A. Vivaldi
   • "Bach" can ONLY match pieces by J. S. Bach
   • Composer mismatch = automatic rejection of that candidate
   
   HANDLING MISSPELLINGS & VARIATIONS:
   • Allow fuzzy matching for common misspellings (e.g., "Bocherini" → Boccherini)
   • Match partial names (e.g., "Haydn" matches "J. Haydn")
   • Handle abbreviated names (e.g., "Saint-Saens" matches "C. Saint-Saëns")
   • Be flexible with diacritics (e.g., "Dvorak" matches "A. Dvořák")
   • Soundalike names are acceptable if phonetically similar
   • BUT: Never match completely different composers (Boccherini ≠ Breval)

2. TITLE/WORK TYPE (SECOND PRIORITY)
   • Match specific title keywords ("Concerto", "Sonata", "Minuet", etc.)
   • Look for key signatures ("C Major", "E Minor", "B-flat Major")
   • Catalog numbers if provided ("Op. 40", "BWV 1007")

3. BOOK NUMBER (THIRD PRIORITY)
   • Use book numbers to narrow down when other info matches
   • Book numbers alone are NOT sufficient without composer/title match

4. OTHER CONTEXT (LOWEST PRIORITY)
   • Movement indicators
   • Partial descriptions
   • Ordering hints

EXAMPLE:
• "Boccherini b flat concerto 1st movement"
  ✓ MUST match: L. Boccherini (composer)
  ✓ MUST match: "Concerto" (work type)
  ✓ SHOULD match: "B-flat Major" (key)
  ✗ CANNOT match: Breval, Vivaldi, or any other composer
  → Result: "Concerto in B-flat Major" by L. Boccherini, arr. F. Grützmacher

----------------------------------------------------------------
MOVEMENT PARSING & PRECEDENCE (CRITICAL)
----------------------------------------------------------------

You MUST actively parse movement indicators from fuzzy text, including:

• Ordinals: "1st movement", "first movement", "2nd", "third", etc.
• Roman numerals: "I.", "II.", "III."
• Tempo markings if unique within the work (e.g. "Allegro")
• Phrases like "opening movement", "final movement"

MOVEMENT SELECTION RULES (ABSOLUTELY CRITICAL):

1. If a specific movement IS mentioned → Include ONLY that ONE movement
   • "Boccherini b flat concerto 1st movement" → movements: ["I. Allegro moderato"]
   • "Haydn concerto second movement" → movements: ["II. Adagio"]
   • Do NOT add other movements even if they exist in the repertoire
   
2. If NO movement is mentioned → Include ALL movements from the repertoire
   • "Boccherini b flat concerto" → movements: ["I. Allegro moderato", "II. Adagio non troppo", "III. Rondo: Allegro"]
   
3. VIOLATION EXAMPLES (FORBIDDEN):
   ✗ User says "1st movement" but you return all 3 movements
   ✗ User says "opening movement" but you return movements I, II, and III
   ✗ User specifies one movement but you include extras "just in case"

When in doubt about which specific movement, return NO movements rather than all movements.

----------------------------------------------------------------
CONFIDENCE LEVELS (REQUIRED)
----------------------------------------------------------------

Use the confidence field to communicate certainty:

• "exact"
  - Full title clearly identified
  - No inference beyond normalization required

• "partial"
  - Resolved using educated inference (book number, numbering, partial title, etc.)
  - Reasonable confidence, but not explicitly stated in full by the user

• "none"
  - No reasonable match can be inferred

Educated guesses MUST use confidence = "partial".

----------------------------------------------------------------
RESTRICTIONS (STILL STRICT)
----------------------------------------------------------------

• You may ONLY output titles, composers, and movements that appear EXACTLY
  in the Suzuki Repertoire Library below.
• Do NOT invent titles, composers, catalog numbers, or movements.
• Do NOT combine multiple repertoire entries into one.
• If multiple entries remain plausible after inference, choose the BEST match
  and mark confidence = "partial" with an explanatory note.
• If no reasonable match exists, return matched = false.

----------------------------------------------------------------
MOVEMENT RULES
----------------------------------------------------------------

• Include movements if they are explicitly mentioned OR strongly implied.
• Use movement names exactly as listed in the repertoire library.
• If movement inference is uncertain, omit movements and lower confidence.

----------------------------------------------------------------
SUZUKI REPERTOIRE LIBRARY (AUTHORITATIVE)
----------------------------------------------------------------

The following JSON defines the ONLY acceptable repertoire titles, composers,
and movements. All resolved output MUST come from this data.

{repertoire_json}
----------------------------------------------------------------
REPERTOIRE INDEX (AUTHORITATIVE)
----------------------------------------------------------------

Each repertoire entry includes an explicit "index" field
(e.g. "4.0003") that defines its canonical ordering.

RULES:

• If a piece is matched, you MUST copy its exact index string
• The index must match the repertoire entry exactly
• Do NOT generate, modify, or infer index values
• If unmatched, index must be null
• Sorting will be handled downstream — do NOT reorder output

----------------------------------------------------------------
CSV INPUT DATA (AUTHORITATIVE STUDENT DATA)
----------------------------------------------------------------

Each object represents one CSV row with:
• "student": the student's full name
• "description": a fuzzy prose description of what they are playing

Multiple rows may reference the same student.
Descriptions may reference multiple pieces.

Preserve the order of first appearance of each student.

{csv_data_json}

----------------------------------------------------------------
REQUIRED OUTPUT FORMAT (JSON ONLY)
----------------------------------------------------------------

Return a JSON array of objects.
Each object represents one student and must conform to this structure:

{{
  "student_name": "string",
  "pieces": [
    {{
      "title": "string | null",
      "composer": "string | null",
      "movements": ["string"],
      "library_index": "string | null",
      "matched": true | false,
      "confidence": "exact | partial | none",
      "notes": "string | null"
    }}
  ]
}}

CRITICAL: The library_index field MUST be included for every piece:
• If matched, copy the EXACT "index" value from the repertoire entry (e.g. "4.0003")
• If unmatched, use null
• Never generate, modify, or infer the index value

----------------------------------------------------------------
OUTPUT RULES
----------------------------------------------------------------

• Group CSV rows by student name
• Each student appears exactly once
• Each CSV row produces one or more ResolvedPiece entries
• Output JSON only
• No markdown
• No explanations outside the notes field
• No reordering of students

Unmatched pieces MUST use:
• title = the exact original description from the CSV (NOT null)
• composer = null
• movements = []
• library_index = null
• matched = false
• confidence = "none"
• notes = brief explanation of why no match was found

IMPORTANT: For unmatched pieces, preserve the student's original description
in the title field so it appears in the program exactly as they wrote it.

----------------------------------------------------------------
FINAL CHECK BEFORE RETURNING
----------------------------------------------------------------

• All titles and composers must match the repertoire library exactly
• No extra fields may appear
• Student names must be copied exactly
• Output must be valid JSON
• If you guessed, mark confidence = "partial" and explain briefly in notes
""".strip()
