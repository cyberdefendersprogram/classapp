"""Reading list model (simple read-only list, distinct from book-reading signups)."""

from dataclasses import dataclass


@dataclass
class ReadingItem:
    """Represents a row from the Reading sheet."""

    class_num: str
    title: str
    link: str

    @classmethod
    def from_row(cls, row: dict) -> "ReadingItem":
        return cls(
            class_num=str(row.get("class", "") or ""),
            title=row.get("title", "") or "",
            link=row.get("link", "") or "",
        )
