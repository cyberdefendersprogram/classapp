"""General page routes for authenticated users."""

import logging
from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import OnboardedStudent, templates
from app.services.sheets import get_sheets_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, student: OnboardedStudent):
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
        },
    )


@router.get("/me", response_class=HTMLResponse)
async def profile_page(request: Request, student: OnboardedStudent):
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
        },
    )


@router.post("/me", response_class=HTMLResponse)
async def profile_update(
    request: Request,
    student: OnboardedStudent,
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
            },
        )


@router.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request, student: OnboardedStudent):
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
        },
    )
