"""Quiz routes for listing and taking quizzes."""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates
from app.services.grading import grade_quiz
from app.services.quiz_parser import get_parsed_quiz
from app.services.sheets import get_sheets_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/quizzes", response_class=HTMLResponse)
async def list_quizzes(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    List all available quizzes for the student.
    """
    sheets = get_sheets_client()

    # Get all quizzes
    quizzes = sheets.get_quizzes()

    # Get submission counts for each quiz
    quiz_info = []
    for quiz in quizzes:
        submissions = sheets.get_quiz_submissions(student.student_id, quiz.quiz_id)
        attempt_count = len(submissions)

        # Calculate best score
        best_score = None
        if submissions:
            best_score = max(s.score for s in submissions)

        quiz_info.append({
            "quiz": quiz,
            "attempt_count": attempt_count,
            "best_score": best_score,
            "can_attempt": quiz.is_open and (
                quiz.attempts_allowed == 0 or attempt_count < quiz.attempts_allowed
            ),
            "attempts_remaining": (
                None if quiz.attempts_allowed == 0
                else max(0, quiz.attempts_allowed - attempt_count)
            ),
        })

    return templates.TemplateResponse(
        "quizzes.html",
        {
            "request": request,
            "student": student,
            "quiz_info": quiz_info,
            "is_admin": is_admin(session),
        },
    )


@router.get("/quiz/{quiz_id}", response_class=HTMLResponse)
async def quiz_form(request: Request, quiz_id: str, student: OnboardedStudent, session: CurrentSession):
    """
    Display a quiz form for the student to take.
    """
    sheets = get_sheets_client()
    admin_flag = is_admin(session)

    # Get quiz metadata
    quiz_meta = sheets.get_quiz_by_id(quiz_id)
    if not quiz_meta:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "student": student,
                "error": "Quiz not found.",
                "is_admin": admin_flag,
            },
            status_code=404,
        )

    # Check if quiz is open
    if not quiz_meta.is_open:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "student": student,
                "error": "This quiz is not currently available.",
                "is_admin": admin_flag,
            },
            status_code=403,
        )

    # Check attempts
    submissions = sheets.get_quiz_submissions(student.student_id, quiz_id)
    attempt_count = len(submissions)

    if quiz_meta.attempts_allowed > 0 and attempt_count >= quiz_meta.attempts_allowed:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "student": student,
                "error": f"You have used all {quiz_meta.attempts_allowed} attempts for this quiz.",
                "is_admin": admin_flag,
            },
            status_code=403,
        )

    # Parse quiz content
    quiz = get_parsed_quiz(quiz_meta.content_path, quiz_id)
    if not quiz:
        logger.error("Failed to parse quiz content: %s", quiz_meta.content_path)
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "student": student,
                "error": "Quiz content could not be loaded.",
                "is_admin": admin_flag,
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        "quiz.html",
        {
            "request": request,
            "student": student,
            "quiz_meta": quiz_meta,
            "quiz": quiz,
            "attempt_number": attempt_count + 1,
            "attempts_remaining": (
                None if quiz_meta.attempts_allowed == 0
                else quiz_meta.attempts_allowed - attempt_count
            ),
            "is_admin": admin_flag,
        },
    )


@router.post("/quiz/{quiz_id}", response_class=HTMLResponse)
async def quiz_submit(request: Request, quiz_id: str, student: OnboardedStudent, session: CurrentSession):
    """
    Submit a quiz for grading.
    """
    sheets = get_sheets_client()
    admin_flag = is_admin(session)

    # Get quiz metadata
    quiz_meta = sheets.get_quiz_by_id(quiz_id)
    if not quiz_meta:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "student": student,
                "error": "Quiz not found.",
                "is_admin": admin_flag,
            },
            status_code=404,
        )

    # Check if quiz is still open
    if not quiz_meta.is_open:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "student": student,
                "error": "This quiz is no longer available for submission.",
                "is_admin": admin_flag,
            },
            status_code=403,
        )

    # Check attempts again
    submissions = sheets.get_quiz_submissions(student.student_id, quiz_id)
    attempt_count = len(submissions)

    if quiz_meta.attempts_allowed > 0 and attempt_count >= quiz_meta.attempts_allowed:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "student": student,
                "error": "You have no attempts remaining for this quiz.",
                "is_admin": admin_flag,
            },
            status_code=403,
        )

    # Parse quiz content
    quiz = get_parsed_quiz(quiz_meta.content_path, quiz_id)
    if not quiz:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "student": student,
                "error": "Quiz content could not be loaded.",
                "is_admin": admin_flag,
            },
            status_code=500,
        )

    # Parse form data
    form_data = await request.form()
    answers = {}

    for question in quiz.questions:
        if question.type == "mcq_multi":
            # Multiple values for multi-select
            values = form_data.getlist(question.id)
            answers[question.id] = list(values) if values else []
        else:
            # Single value
            value = form_data.get(question.id)
            answers[question.id] = value if value else ""

    # Grade the quiz
    result = grade_quiz(quiz, answers)

    # Save submission
    now = datetime.utcnow().isoformat()
    submission_data = {
        "submitted_at": now,
        "quiz_id": quiz_id,
        "attempt": attempt_count + 1,
        "student_id": student.student_id,
        "email": student.email,
        "answers_json": json.dumps(answers),
        "score": result.score,
        "max_score": result.max_score,
        "autograde_json": json.dumps(result.to_autograde_json()),
        "source": "web",
    }

    sheets.append_quiz_submission(submission_data)

    logger.info(
        "Quiz submitted: student=%s quiz=%s score=%d/%d",
        student.student_id,
        quiz_id,
        result.score,
        result.max_score,
    )

    # Show results
    return templates.TemplateResponse(
        "quiz_result.html",
        {
            "request": request,
            "student": student,
            "quiz_meta": quiz_meta,
            "quiz": quiz,
            "answers": answers,
            "result": result,
            "attempt_number": attempt_count + 1,
            "is_admin": admin_flag,
        },
    )
