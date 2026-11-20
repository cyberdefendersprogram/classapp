"""Incident research page: highlights from each student's Case Study 5 incident."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app import dependencies
from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates

router = APIRouter()


@router.get("/incident-research", response_class=HTMLResponse)
async def incident_research_page(
    request: Request, student: OnboardedStudent, session: CurrentSession
):
    """Show the published rows of the class sheet's Incident_Research tab, sorted by incident."""
    rows = dependencies.get_sheets_client().get_incident_research()
    return templates.TemplateResponse(
        "incident_research.html",
        {"request": request, "student": student, "rows": rows, "is_admin": is_admin(session)},
    )
