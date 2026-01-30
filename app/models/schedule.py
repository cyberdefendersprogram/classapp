"""Schedule data model."""

import re
from dataclasses import dataclass


@dataclass
class ScheduleEntry:
    """Represents a session from the Schedule sheet."""

    session: str  # Date string like "1/23/2026"
    desc: str  # Session description
    desc_link: str  # Description link
    notes: str  # Additional notes (can contain newlines)
    slides_link: str  # URL to slides (optional)
    recording_link: str  # URL to recording (optional)

    @classmethod
    def from_row(cls, row: dict) -> "ScheduleEntry":
        """Create ScheduleEntry from a sheet row dictionary."""
        return cls(
            session=row.get("session", ""),
            desc=row.get("desc", ""),
            desc_link=row.get("desc_link", ""),
            notes=row.get("notes", ""),
            slides_link=row.get("slides_link", ""),
            recording_link=row.get("recording_link", ""),
        )

    @property
    def has_materials(self) -> bool:
        """Check if this session has any materials linked."""
        return bool(self.slides_link or self.recording_link)

    @property
    def class_number(self) -> str | None:
        """Extract class number from desc (e.g., '1 - Introduction' → '1')."""
        if not self.desc:
            return None
        match = re.match(r"^(\d+)\s*[-–—]\s*", self.desc)
        return match.group(1) if match else None

    @property
    def has_content(self) -> bool:
        """Check if this session has linked content."""
        return bool(self.desc_link and self.class_number)
