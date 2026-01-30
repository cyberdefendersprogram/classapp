"""Admin routes for quiz analytics dashboard."""

import csv
import io
import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from app.dependencies import AdminSession, templates
from app.services.analytics import compute_quiz_analytics, get_best_submissions
from app.services.quiz_parser import get_parsed_quiz
from app.services.sheets import get_sheets_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_overview(request: Request, session: AdminSession):
    """
    Admin overview page showing all quizzes with completion rates.
    """
    sheets = get_sheets_client()

    quizzes = sheets.get_quizzes()
    total_students = sheets.get_roster_count()

    quiz_summaries = []
    for quiz_meta in quizzes:
        submissions = sheets.get_all_quiz_submissions(quiz_meta.quiz_id)

        # Count unique students who submitted
        unique_students = len(set(sub.student_id for sub in submissions))

        # Calculate average score from best submissions
        if submissions:
            from app.services.analytics import get_best_submissions

            best_subs = get_best_submissions(submissions)
            if best_subs:
                total_score = sum(s.score for s in best_subs.values())
                total_max = sum(s.max_score for s in best_subs.values())
                avg_score = (total_score / total_max * 100) if total_max > 0 else 0.0
            else:
                avg_score = 0.0
        else:
            avg_score = 0.0

        completion_rate = (unique_students / total_students * 100) if total_students > 0 else 0.0

        quiz_summaries.append(
            {
                "quiz": quiz_meta,
                "completed_students": unique_students,
                "total_students": total_students,
                "completion_rate": completion_rate,
                "avg_score": avg_score,
            }
        )

    return templates.TemplateResponse(
        "admin_analytics.html",
        {
            "request": request,
            "session": session,
            "quiz_summaries": quiz_summaries,
            "total_students": total_students,
        },
    )


@router.get("/quiz/{quiz_id}", response_class=HTMLResponse)
async def quiz_analytics(request: Request, quiz_id: str, session: AdminSession):
    """
    Detailed per-question analytics for a specific quiz.
    """
    sheets = get_sheets_client()

    # Get quiz metadata
    quiz_meta = sheets.get_quiz_by_id(quiz_id)
    if not quiz_meta:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Quiz not found.",
            },
            status_code=404,
        )

    # Parse quiz content
    quiz = get_parsed_quiz(quiz_meta.content_path, quiz_id)
    if not quiz:
        logger.error("Failed to parse quiz content: %s", quiz_meta.content_path)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Quiz content could not be loaded.",
            },
            status_code=500,
        )

    # Get all submissions and roster count
    submissions = sheets.get_all_quiz_submissions(quiz_id)
    total_students = sheets.get_roster_count()

    # Compute analytics
    analytics = compute_quiz_analytics(quiz, submissions, total_students)

    return templates.TemplateResponse(
        "admin_quiz_analytics.html",
        {
            "request": request,
            "session": session,
            "quiz_meta": quiz_meta,
            "quiz": quiz,
            "analytics": analytics,
        },
    )


def _build_grade_table(sheets) -> tuple[list, list, dict]:
    """
    Build grade table data.

    Returns:
        Tuple of (quizzes, roster, grades_dict)
        grades_dict maps student_id -> quiz_id -> best_score
    """
    quizzes = sheets.get_quizzes()
    roster = sheets.get_all_roster()

    # Build grades: student_id -> quiz_id -> best_score
    grades: dict[str, dict[str, float]] = {
        student.student_id: {quiz.quiz_id: 0 for quiz in quizzes} for student in roster
    }

    # Fill in best scores
    for quiz in quizzes:
        submissions = sheets.get_all_quiz_submissions(quiz.quiz_id)
        best_subs = get_best_submissions(submissions)

        for student_id, submission in best_subs.items():
            if student_id in grades:
                grades[student_id][quiz.quiz_id] = submission.score

    return quizzes, roster, grades


@router.get("/grading", response_class=HTMLResponse)
async def grading_page(request: Request, session: AdminSession):
    """
    Admin grading page showing all students' best scores per quiz.
    """
    sheets = get_sheets_client()
    quizzes, roster, grades = _build_grade_table(sheets)

    return templates.TemplateResponse(
        "admin_grading.html",
        {
            "request": request,
            "session": session,
            "quizzes": quizzes,
            "roster": roster,
            "grades": grades,
        },
    )


@router.get("/grading/csv")
async def grading_csv(session: AdminSession):
    """
    Download grades as CSV.
    """
    sheets = get_sheets_client()
    quizzes, roster, grades = _build_grade_table(sheets)

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    header = ["Student Name", "Email", "Student ID"]
    header.extend([quiz.title for quiz in quizzes])
    writer.writerow(header)

    # Data rows
    for student in roster:
        row = [
            student.full_name,
            student.preferred_email or "",
            student.student_id,
        ]
        for quiz in quizzes:
            score = grades.get(student.student_id, {}).get(quiz.quiz_id, 0)
            row.append(score)
        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=grades.csv"},
    )
