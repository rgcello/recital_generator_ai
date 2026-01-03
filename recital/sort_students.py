from ai.models import StudentPerformance


def student_sort_key(perf: StudentPerformance) -> tuple:
    """
    Returns a tuple suitable for sorting StudentPerformance objects
    according to their highest (most advanced) library_index.
    """

    # Extract matched indices only
    indices = [
        piece.library_index for piece in perf.pieces if piece.library_index is not None
    ]

    if not indices:
        # No matched repertoire → sort last
        return (True, (999, 9999))  # True = unmatched group

    # Parse indices as (book, piece) tuples for proper numeric sorting
    # e.g. "4.0003" -> (4, 3)
    parsed_indices = []
    for idx in indices:
        try:
            book, piece = idx.split(".")
            parsed_indices.append((int(book), int(piece)))
        except (ValueError, AttributeError):
            # If parsing fails, treat as unmatched
            continue

    if not parsed_indices:
        return (True, (999, 9999))

    # Highest (most advanced) piece determines placement
    highest_index = max(parsed_indices)

    return (False, highest_index)
