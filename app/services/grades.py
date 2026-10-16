"""Student-facing grade view built from the Canvas grades synced into the Roster sheet.

Canvas is the official gradebook. The sync script writes, per student, one
``grade_<assignment>`` column holding ``"score/max"`` plus ``grade_total`` (the
Canvas course total %), ``grade_letter`` and ``grades_synced_at``. Nothing here
recalculates the total — it only displays what Canvas reported.
"""

from dataclasses import dataclass

from app.models.roster import RosterEntry

# (sheet key, label, category) in display order.
ASSIGNMENTS: list[tuple[str, str, str]] = [
    ("lab1", "Lab 1 — AWS Account Setup and IAM Fundamentals", "Labs"),
    ("lab2", "Lab 2 — IAM Policies, Conditions, and KMS", "Labs"),
    ("lab3", "Lab 3 — Network Segmentation, Encryption, and Cloud Security Posture", "Labs"),
    ("lab4", "Lab 4 — Container, IaC, and Pipeline Security", "Labs"),
    ("lab5", "Lab 5 — Breach Case Study", "Labs"),
    ("quiz1", "Quiz 1", "Quizzes"),
    ("quiz2", "Quiz 2", "Quizzes"),
    ("quiz3", "Quiz 3", "Quizzes"),
    ("quiz4", "Quiz 4", "Quizzes"),
    ("quiz5", "Quiz 5", "Quizzes"),
]

DROP_LOWEST_PER_CATEGORY = 1  # per the syllabus / Canvas assignment-group rules


@dataclass
class GradeRow:
    key: str
    label: str
    category: str
    score: float | None
    max_points: float | None
    dropped: bool = False

    @property
    def percent(self) -> float | None:
        if self.score is None or not self.max_points:
            return None
        return round(100 * self.score / self.max_points, 1)


@dataclass
class GradesView:
    rows: list[GradeRow]
    total: float | None
    letter: str | None
    synced_at: object | None

    @property
    def has_any(self) -> bool:
        return self.total is not None or any(r.score is not None for r in self.rows)


def _parse_cell(value: str | None) -> tuple[float | None, float | None]:
    """Parse "92/100" (or just "92") into (score, max)."""
    if not value:
        return None, None
    text = value.strip()
    try:
        if "/" in text:
            score, max_points = text.split("/", 1)
            return float(score), float(max_points)
        return float(text), None
    except ValueError:
        return None, None


def build_grades_view(student: RosterEntry) -> GradesView:
    rows: list[GradeRow] = []
    for key, label, category in ASSIGNMENTS:
        score, max_points = _parse_cell(student.grades.get(key))
        rows.append(GradeRow(key, label, category, score, max_points))

    # Mark the lowest graded item in each category as dropped, mirroring the
    # drop-lowest rule Canvas applies to the total. Display only.
    for category in {r.category for r in rows}:
        graded = [r for r in rows if r.category == category and r.percent is not None]
        if len(graded) > DROP_LOWEST_PER_CATEGORY:
            for r in sorted(graded, key=lambda r: r.percent)[:DROP_LOWEST_PER_CATEGORY]:
                r.dropped = True

    return GradesView(
        rows=rows,
        total=student.grade_total,
        letter=student.grade_letter,
        synced_at=student.grades_synced_at,
    )
