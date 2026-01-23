"""Quiz data models."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Question:
    """Represents a single quiz question."""

    id: str
    type: str  # mcq_single, mcq_multi, numeric, short_text
    text: str
    points: int
    options: list[str] = field(default_factory=list)  # For MCQ types
    correct: str | list[str] | None = None  # Expected answer(s)

    @property
    def is_mcq(self) -> bool:
        """Check if question is multiple choice."""
        return self.type in ("mcq_single", "mcq_multi")


@dataclass
class Quiz:
    """Represents a quiz with its questions."""

    quiz_id: str
    title: str
    questions: list[Question] = field(default_factory=list)
    total_points: int = 0

    def __post_init__(self):
        """Calculate total points if not set."""
        if not self.total_points and self.questions:
            self.total_points = sum(q.points for q in self.questions)


@dataclass
class QuizMeta:
    """Quiz metadata from the Quizzes sheet (without parsed questions)."""

    quiz_id: str
    title: str
    content_path: str
    open_at: datetime | None = None
    close_at: datetime | None = None
    attempts_allowed: int = 1
    status: str = "draft"
    total_points: int = 0

    @property
    def is_published(self) -> bool:
        """Check if quiz is published."""
        return self.status == "published"

    @property
    def is_open(self) -> bool:
        """Check if quiz is currently open for submissions."""
        if not self.is_published:
            return False

        now = datetime.utcnow()

        if self.open_at and now < self.open_at:
            return False

        if self.close_at and now > self.close_at:
            return False

        return True

    @classmethod
    def from_row(cls, row: dict) -> "QuizMeta":
        """Create QuizMeta from a sheet row dictionary."""
        return cls(
            quiz_id=row.get("quiz_id", ""),
            title=row.get("title", ""),
            content_path=row.get("content_path", ""),
            open_at=_parse_datetime(row.get("open_at")),
            close_at=_parse_datetime(row.get("close_at")),
            attempts_allowed=_parse_int(row.get("attempts_allowed"), default=1),
            status=row.get("status", "draft"),
            total_points=_parse_int(row.get("total_points"), default=0),
        )


@dataclass
class QuizSubmission:
    """Represents a quiz submission."""

    submitted_at: datetime
    quiz_id: str
    attempt: int
    student_id: str
    email: str
    answers_json: str
    score: float
    max_score: float
    autograde_json: str
    source: str = "web"

    @classmethod
    def from_row(cls, row: dict) -> "QuizSubmission":
        """Create QuizSubmission from a sheet row dictionary."""
        return cls(
            submitted_at=_parse_datetime(row.get("submitted_at")) or datetime.utcnow(),
            quiz_id=row.get("quiz_id", ""),
            attempt=_parse_int(row.get("attempt"), default=1),
            student_id=row.get("student_id", ""),
            email=row.get("email", ""),
            answers_json=row.get("answers_json", "{}"),
            score=_parse_float(row.get("score"), default=0),
            max_score=_parse_float(row.get("max_score"), default=0),
            autograde_json=row.get("autograde_json", "{}"),
            source=row.get("source", "web"),
        )


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO datetime string."""
    if not value:
        return None
    try:
        if "." in value:
            return datetime.fromisoformat(value)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _parse_int(value: str | int | None, default: int = 0) -> int:
    """Parse integer value."""
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _parse_float(value: str | float | None, default: float = 0) -> float:
    """Parse float value."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
