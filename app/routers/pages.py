"""General page routes for authenticated users."""

import logging

from fastapi import APIRouter, Request
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
    Render the profile page.

    Requires authentication and completed onboarding.
    """
    return templates.TemplateResponse(
        "me.html",
        {
            "request": request,
            "student": student,
        },
    )
