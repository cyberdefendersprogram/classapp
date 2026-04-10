"""Book reading assignment model."""

from dataclasses import dataclass


@dataclass
class BookChapter:
    """Represents a chapter row from the Book_Reading sheet."""

    chapter: str
    class_num: str  # maps to the 'class' column — session/class number (e.g. "3")
    primary_reader: str
    secondary_reader: str
    chapter_presentation_link: str

    @classmethod
    def from_row(cls, row: dict) -> "BookChapter":
        return cls(
            chapter=row.get("chapter", ""),
            class_num=str(row.get("class", "") or ""),
            primary_reader=row.get("primary_reader", "") or "",
            secondary_reader=row.get("secondary_reader", "") or "",
            chapter_presentation_link=row.get("chapter_presentation_link", "") or "",
        )

    @property
    def has_primary(self) -> bool:
        return bool(self.primary_reader)

    @property
    def has_secondary(self) -> bool:
        return bool(self.secondary_reader)
