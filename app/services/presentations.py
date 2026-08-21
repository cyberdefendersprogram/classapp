"""Shared helper for building per-student presentation rows.

Used by the admin Presentations page (ordering/grading) and by the
student-facing /final-projects page when a course's final_project_mode
is "individual" (one student, one topic — e.g. CIS52's breach reviews)
rather than "teams" (e.g. CIS60's group projects).
"""

import json


def build_presentation_rows(sheets, quiz_id: str) -> list[dict]:
    """
    Join a presentation sign-up quiz's submissions with the roster.

    Returns a list of dicts with keys:
        student_id, name, full_name, email, title, timing, order, grade, submitted
    Sorted with ordered students first (by order number), unordered at the bottom.
    """
    roster = sheets.get_all_roster()
    submissions = sheets.get_all_quiz_submissions(quiz_id)

    # Best (most recent) submission per student
    by_student: dict[str, dict] = {}
    for sub in sorted(submissions, key=lambda s: s.submitted_at):
        try:
            answers = json.loads(sub.answers_json)
        except (json.JSONDecodeError, TypeError):
            answers = {}
        by_student[sub.student_id] = answers

    rows = []
    for student in roster:
        if not student.is_claimed:
            continue
        answers = by_student.get(student.student_id, {})
        rows.append(
            {
                "student_id": student.student_id,
                "name": student.display_name,
                "full_name": student.full_name,
                "email": student.preferred_email or "",
                "title": answers.get("q1", ""),
                "timing": answers.get("q2", ""),
                "order": student.presentation_order,
                "grade": student.presentation_grade,
                "submitted": bool(answers),
            }
        )

    rows.sort(key=lambda r: (r["order"] is None, r["order"] or 0, r["name"]))
    return rows
