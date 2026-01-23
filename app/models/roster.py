"""Roster data model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class RosterEntry:
    """Represents a student from the Roster sheet."""

    student_id: str
    full_name: str
    preferred_email: str | None = None
    preferred_name: str | None = None
    preferred_name_phonetic: str | None = None
    preferred_pronoun: str | None = None
    linkedin: str | None = None
    program_plan: str | None = None
    student_level: str | None = None
    cs_experience: str | None = None
    computer_system: str | None = None
    hobbies: str | None = None
    used_netlabs: str | None = None
    used_tryhackme: str | None = None
    class_goals: str | None = None
    support_request: str | None = None
    claimed_at: datetime | None = None
    onboarding_completed_at: datetime | None = None
    last_login_at: datetime | None = None

    @property
    def is_claimed(self) -> bool:
        """Check if student has claimed their account."""
        return self.preferred_email is not None and self.claimed_at is not None

    @property
    def is_onboarded(self) -> bool:
        """Check if student has completed onboarding."""
        return self.onboarding_completed_at is not None

    @property
    def display_name(self) -> str:
        """Get the name to display (preferred name or parsed first name from full_name)."""
        if self.preferred_name:
            return self.preferred_name
        # full_name is "Last, First" format - extract first name
        if self.full_name and "," in self.full_name:
            parts = self.full_name.split(",", 1)
            if len(parts) > 1:
                return parts[1].strip().split()[0]  # Get first word after comma
        return self.full_name or "Student"

    @property
    def email(self) -> str | None:
        """Alias for preferred_email for backward compatibility."""
        return self.preferred_email

    @classmethod
    def from_row(cls, row: dict) -> "RosterEntry":
        """Create RosterEntry from a sheet row dictionary."""
        return cls(
            student_id=str(row.get("student_id", "")),
            full_name=row.get("full_name", ""),
            preferred_email=row.get("preferred_email") or None,
            preferred_name=row.get("preferred_name") or None,
            preferred_name_phonetic=row.get("preferred_name_phonetic") or None,
            preferred_pronoun=row.get("preferred_pronoun") or None,
            linkedin=row.get("linkedin") or None,
            program_plan=row.get("program_plan") or None,
            student_level=row.get("student_level") or None,
            cs_experience=row.get("cs_experience") or None,
            computer_system=row.get("computer_system") or None,
            hobbies=row.get("hobbies") or None,
            used_netlabs=row.get("used_netlabs") or None,
            used_tryhackme=row.get("used_tryhackme") or None,
            class_goals=row.get("class_goals") or None,
            support_request=row.get("support_request") or None,
            claimed_at=_parse_datetime(row.get("claimed_at")),
            onboarding_completed_at=_parse_datetime(row.get("onboarding_completed_at")),
            last_login_at=_parse_datetime(row.get("last_login_at")),
        )

    def get_empty_profile_fields(self) -> list[str]:
        """Get list of profile fields that are empty (for onboarding)."""
        profile_fields = [
            "preferred_name",
            "preferred_name_phonetic",
            "preferred_pronoun",
            "linkedin",
            "cs_experience",
            "computer_system",
            "hobbies",
            "used_netlabs",
            "used_tryhackme",
            "class_goals",
            "support_request",
        ]
        return [f for f in profile_fields if not getattr(self, f)]


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
