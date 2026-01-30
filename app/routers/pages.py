"""General page routes for authenticated users."""

import logging
from pathlib import Path
import markdown
from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates
from app.services.sheets import get_sheets_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Render the home/dashboard page.

    Requires authentication and completed onboarding.
    """
    sheets = get_sheets_client()

    # Get course info from config
    course_title = sheets.get_config("course_title") or "Class Portal"
    term = sheets.get_config("term") or ""

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "student": student,
            "course_title": course_title,
            "term": term,
            "is_admin": is_admin(session),
        },
    )


@router.get("/me", response_class=HTMLResponse)
async def profile_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Render the profile page with edit form.

    Requires authentication and completed onboarding.
    """
    return templates.TemplateResponse(
        "me.html",
        {
            "request": request,
            "student": student,
            "success": None,
            "error": None,
            "is_admin": is_admin(session),
        },
    )


@router.post("/me", response_class=HTMLResponse)
async def profile_update(
    request: Request,
    student: OnboardedStudent,
    session: CurrentSession,
    preferred_name: str = Form(""),
    preferred_name_phonetic: str = Form(""),
    preferred_pronoun: str = Form(""),
    linkedin: str = Form(""),
    cs_experience: str = Form(""),
    computer_system: str = Form(""),
    hobbies: str = Form(""),
    used_netlabs: str = Form(""),
    used_tryhackme: str = Form(""),
    class_goals: str = Form(""),
    support_request: str = Form(""),
):
    """
    Update profile information.

    Requires authentication and completed onboarding.
    """
    sheets = get_sheets_client()

    # Build update fields
    update_fields = {
        "preferred_name": preferred_name.strip(),
        "preferred_name_phonetic": preferred_name_phonetic.strip(),
        "preferred_pronoun": preferred_pronoun.strip(),
        "linkedin": linkedin.strip(),
        "cs_experience": cs_experience.strip(),
        "computer_system": computer_system.strip(),
        "hobbies": hobbies.strip(),
        "used_netlabs": used_netlabs.strip(),
        "used_tryhackme": used_tryhackme.strip(),
        "class_goals": class_goals.strip(),
        "support_request": support_request.strip(),
    }

    success = sheets.update_roster(student.student_id, **update_fields)

    # Refresh student data
    updated_student = sheets.get_roster_by_id(student.student_id) or student

    if success:
        logger.info("Profile updated for student %s", student.student_id)
        return templates.TemplateResponse(
            "me.html",
            {
                "request": request,
                "student": updated_student,
                "success": "Profile updated successfully.",
                "error": None,
                "is_admin": is_admin(session),
            },
        )
    else:
        logger.error("Failed to update profile for student %s", student.student_id)
        return templates.TemplateResponse(
            "me.html",
            {
                "request": request,
                "student": updated_student,
                "success": None,
                "error": "An error occurred. Please try again.",
                "is_admin": is_admin(session),
            },
        )


@router.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Render the class schedule page.

    Requires authentication and completed onboarding.
    """
    sheets = get_sheets_client()

    # Get schedule entries
    schedule = sheets.get_schedule()

    # Get course info from config
    course_title = sheets.get_config("course_title") or "Class Portal"

    return templates.TemplateResponse(
        "schedule.html",
        {
            "request": request,
            "student": student,
            "schedule": schedule,
            "course_title": course_title,
            "is_admin": is_admin(session),
        },
    )

# Map class IDs to markdown files on disk
CLASS_CONTENT_PATHS = {
    "1": "content/notes/001-intro.md",
    "2": "content/notes/002-ethics-ir-and-crypto.md",
}


@router.get("/class/{id}", response_class=HTMLResponse)
async def class_page(request: Request, id: str, student: OnboardedStudent, session: CurrentSession):
    """
    Render lecture/class content page from markdown file on disk.
    """
    content_path = CLASS_CONTENT_PATHS.get(id)
    if not content_path:
        return templates.TemplateResponse(
            "class.html",
            {
                "request": request,
                "student": student,
                "title": "Class Not Found",
                "content": "<p>Lecture not found.</p>",
                "is_admin": is_admin(session),
            },
            status_code=404,
        )

    base_path = Path(__file__).parent.parent.parent  # project root
    file_path = base_path / content_path

    if not file_path.exists():
        return templates.TemplateResponse(
            "class.html",
            {
                "request": request,
                "student": student,
                "title": "Content Missing",
                "content": "<p>Lecture file missing on server.</p>",
                "is_admin": is_admin(session),
            },
            status_code=500,
        )

    try:
        markdown_text = file_path.read_text(encoding="utf-8")
        html_content = markdown.markdown(
                markdown_text,
                extensions=["fenced_code", "tables", "toc", "codehilite"]
        )
    except Exception as e:
        logger.exception("Failed reading class content %s: %s", id, e)
        return templates.TemplateResponse(
            "class.html",
            {
                "request": request,
                "student": student,
                "title": "Error",
                "content": "<p>Error loading lecture content.</p>",
                "is_admin": is_admin(session),
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        "class.html",
        {
            "request": request,
            "student": student,
            "title": id.replace("-", " ").title(),
            "content": html_content,
            "is_admin": is_admin(session),
        },
    )