"""Final project (individual-mode) model — one row per student in the Final_Projects tab."""

from dataclasses import dataclass
from datetime import datetime


def _parse_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


@dataclass
class FinalProjectEntry:
    """Represents a row from the Final_Projects sheet."""

    student_id: str
    full_name: str
    topic: str
    timing_pref: str
    order: int | None
    grade: int | None
    submitted_at: datetime | None

    @classmethod
    def from_row(cls, row: dict) -> "FinalProjectEntry":
        return cls(
            student_id=str(row.get("student_id", "")),
            full_name=row.get("full_name", "") or "",
            topic=row.get("topic", "") or "",
            timing_pref=row.get("timing_pref", "") or "",
            order=_parse_int(row.get("order")),
            grade=_parse_int(row.get("grade")),
            submitted_at=_parse_datetime(row.get("submitted_at")),
        )

    @property
    def has_submitted(self) -> bool:
        return bool(self.submitted_at)
