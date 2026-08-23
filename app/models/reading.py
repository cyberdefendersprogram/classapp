"""Reading list model (simple read-only list, distinct from book-reading signups)."""

from dataclasses import dataclass


@dataclass
class ReadingItem:
    """Represents a row from the Reading sheet."""

    class_num: str
    title: str
    link: str
    author: str = ""
    required_or_optional: str = ""
    estimated_time: str = ""
    reading_question: str = ""

    @property
    def is_optional(self) -> bool:
        return self.required_or_optional.strip().lower() == "optional"

    @classmethod
    def from_row(cls, row: dict) -> "ReadingItem":
        return cls(
            class_num=str(row.get("class", "") or ""),
            title=row.get("title", "") or "",
            link=row.get("link", "") or "",
            author=row.get("author", "") or "",
            required_or_optional=row.get("required_or_optional", "") or "",
            estimated_time=row.get("estimated_time", "") or "",
            reading_question=row.get("reading_question", "") or "",
        )
