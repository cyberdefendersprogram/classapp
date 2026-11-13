"""Student progress for the admin check-in page, built from the Canvas_Progress sheet tab.

``scripts/sync_canvas_progress.py`` writes one row per student per assignment with a status
of excused, graded, submitted, missing (past due, nothing turned in) or upcoming. This
module groups those rows by student and ranks students for a check-in: anyone who has
turned in nothing first, then the most missing work.
"""

from dataclasses import dataclass, field

DONE = {"graded", "submitted", "excused"}


@dataclass
class Cell:
    assignment_id: str
    status: str
    score: str
    points: str
    late: bool


@dataclass
class StudentProgress:
    canvas_user_id: str
    name: str
    email: str
    last_activity_at: str
    cells: dict[str, Cell] = field(default_factory=dict)

    @property
    def done(self) -> int:
        return sum(1 for c in self.cells.values() if c.status in DONE)

    @property
    def missing(self) -> int:
        return sum(1 for c in self.cells.values() if c.status == "missing")

    @property
    def due(self) -> int:
        """Assignments already due (done or missing); upcoming work is not counted."""
        return self.done + self.missing

    @property
    def nothing_submitted(self) -> bool:
        return self.done == 0

    @property
    def level(self) -> str:
        """Check-in priority: none, low (one missing), medium, or high (nothing turned in)."""
        if self.nothing_submitted and self.due:
            return "high"
        if self.missing >= 3:
            return "medium"
        if self.missing:
            return "low"
        return "none"


@dataclass
class ProgressView:
    assignments: list[dict]
    students: list[StudentProgress]
    synced_at: str | None


def build_progress(records: list[dict]) -> ProgressView:
    """Group long-format Canvas_Progress records into per-student rows, highest priority first."""
    assignments: dict[str, dict] = {}
    students: dict[str, StudentProgress] = {}
    for r in records:
        uid = str(r.get("canvas_user_id", "")).strip()
        aid = str(r.get("assignment_id", "")).strip()
        if not uid or not aid:
            continue
        assignments.setdefault(
            aid,
            {"id": aid, "name": str(r.get("assignment", "")), "due_at": str(r.get("due_at", ""))},
        )
        s = students.setdefault(
            uid,
            StudentProgress(
                uid,
                str(r.get("name", "")),
                str(r.get("email", "")),
                str(r.get("last_activity_at", "")),
            ),
        )
        s.cells[aid] = Cell(
            aid,
            str(r.get("status", "")),
            str(r.get("score", "")),
            str(r.get("points_possible", "")),
            str(r.get("late", "")) in ("1", "True", "true"),
        )
    order = {"high": 0, "medium": 1, "low": 2, "none": 3}
    ranked = sorted(students.values(), key=lambda s: (order[s.level], -s.missing, s.name.lower()))
    cols = sorted(assignments.values(), key=lambda a: (a["due_at"] or "9999", a["id"]))
    synced = max((str(r.get("synced_at", "")) for r in records), default="") or None
    return ProgressView(cols, ranked, synced)
