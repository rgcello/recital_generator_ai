from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class ResolvedPiece(BaseModel):
    title: Optional[str] = Field(
        default=None,
        description=(
            "Exact canonical title from the repertoire list if matched, "
            "OR the original description from CSV if unmatched. "
            "Never null - always contains either the matched title or original description."
        ),
    )
    composer: Optional[str] = Field(
        default=None,
        description="Exact canonical composer name from the repertoire list, or null if no match",
    )
    movements: List[str] = Field(
        default_factory=list,
        description=(
            "Exact canonical movement strings from repertoire. "
            "CRITICAL: If user specifies a single movement (e.g., '1st movement'), "
            "include ONLY that one movement. If no movement specified, include all. "
            "Never include extra movements beyond what was specified."
        ),
    )
    library_index: Optional[str] = Field(
        default=None,
        description=(
            "Exact index string from the matched repertoire entry "
            "(e.g. '4.0003'). Null if unmatched. Used only for sorting."
        ),
    )

    matched: bool = Field(
        description="True only if a canonical repertoire entry was matched"
    )
    confidence: Literal["exact", "partial", "none"] = Field(
        description="Degree of certainty in the match"
    )
    notes: Optional[str] = Field(
        default=None, description="Explanation for partial or failed matches"
    )

    model_config = ConfigDict(
        extra="forbid",  # 🚫 No hallucinated fields
        frozen=True,  # 🔒 Immutable once created
    )


class StudentPerformance(BaseModel):
    student_name: str = Field(
        description="Full name of the student as it should appear in the program"
    )
    pieces: List[ResolvedPiece] = Field(
        description="One or more resolved repertoire entries for this student"
    )

    model_config = ConfigDict(extra="forbid")
