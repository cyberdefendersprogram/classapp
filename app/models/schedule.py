"""Schedule data model."""

from dataclasses import dataclass


@dataclass
class ScheduleEntry:
    """Represents a session from the Schedule sheet."""

    session: str  # Date string like "1/23/2026"
    desc: str  # Session description
    notes: str  # Additional notes (can contain newlines)
    slides_link: str  # URL to slides (optional)
    recording_link: str  # URL to recording (optional)

    @classmethod
    def from_row(cls, row: dict) -> "ScheduleEntry":
        """Create ScheduleEntry from a sheet row dictionary."""
        return cls(
            session=row.get("session", ""),
            desc=row.get("desc", ""),
            notes=row.get("notes", ""),
            slides_link=row.get("slides_link", ""),
            recording_link=row.get("recording_link", ""),
        )

    @property
    def has_materials(self) -> bool:
        """Check if this session has any materials linked."""
        return bool(self.slides_link or self.recording_link)
