"""Student data model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Student:
    """Represents a student from the Students sheet."""

    student_id: str
    first_name: str
    last_name: str
    claim_code: str
    email: str | None = None
    status: str = "active"
    claimed_at: datetime | None = None
    first_seen_at: datetime | None = None
    onboarded_at: datetime | None = None
    last_login_at: datetime | None = None
    preferred_name: str | None = None
    pronouns: str | None = None
    notes: str | None = None

    @property
    def is_claimed(self) -> bool:
        """Check if student has claimed their account."""
        return self.email is not None and self.claimed_at is not None

    @property
    def is_onboarded(self) -> bool:
        """Check if student has completed onboarding."""
        return self.onboarded_at is not None

    @property
    def display_name(self) -> str:
        """Get the name to display (preferred or first name)."""
        return self.preferred_name or self.first_name

    @property
    def full_name(self) -> str:
        """Get full legal name."""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_row(cls, row: dict) -> "Student":
        """Create Student from a sheet row dictionary."""
        return cls(
            student_id=row.get("student_id", ""),
            first_name=row.get("first_name", ""),
            last_name=row.get("last_name", ""),
            claim_code=row.get("claim_code", ""),
            email=row.get("email") or None,
            status=row.get("status", "active"),
            claimed_at=_parse_datetime(row.get("claimed_at")),
            first_seen_at=_parse_datetime(row.get("first_seen_at")),
            onboarded_at=_parse_datetime(row.get("onboarded_at")),
            last_login_at=_parse_datetime(row.get("last_login_at")),
            preferred_name=row.get("preferred_name") or None,
            pronouns=row.get("pronouns") or None,
            notes=row.get("notes") or None,
        )


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO datetime string."""
    if not value:
        return None
    try:
        # Handle both with and without microseconds
        if "." in value:
            return datetime.fromisoformat(value)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
