"""Case study pages. The text is copied from the Canvas assignments."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates
from app.services.case_study_index import (
    get_available_case_studies,
    is_valid_case_study_id,
    read_case_study,
)

router = APIRouter()

CASE_STUDIES_DIR = (
    Path(__file__).parent.parent.parent / "content" / settings.active_class / "case_studies"
)


@router.get("/case-studies", response_class=HTMLResponse)
async def case_studies_landing(
    request: Request, student: OnboardedStudent, session: CurrentSession
):
    """List the case studies for the active class."""
    return templates.TemplateResponse(
        "case_studies.html",
        {
            "request": request,
            "student": student,
            "case_studies": get_available_case_studies(CASE_STUDIES_DIR),
            "is_admin": is_admin(session),
        },
    )


@router.get("/case-studies/{case_study_id}", response_class=HTMLResponse)
async def case_study_page(
    request: Request, case_study_id: str, student: OnboardedStudent, session: CurrentSession
):
    """Show one case study."""
    path = CASE_STUDIES_DIR / f"{case_study_id}.html"
    found = is_valid_case_study_id(case_study_id) and path.is_file()
    return templates.TemplateResponse(
        "case_study.html",
        {
            "request": request,
            "student": student,
            "case_study": read_case_study(path) if found else None,
            "is_admin": is_admin(session),
        },
        status_code=200 if found else 404,
    )
