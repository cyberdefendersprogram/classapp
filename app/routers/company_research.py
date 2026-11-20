"""Company research page: highlights from each student's incident-response startup case study."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app import dependencies
from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates

router = APIRouter()


@router.get("/company-research", response_class=HTMLResponse)
async def company_research_page(
    request: Request, student: OnboardedStudent, session: CurrentSession
):
    """Show the published rows of the class sheet's Company_Research tab, grouped by company."""
    rows = dependencies.get_sheets_client().get_company_research()
    return templates.TemplateResponse(
        "company_research.html",
        {"request": request, "student": student, "rows": rows, "is_admin": is_admin(session)},
    )
