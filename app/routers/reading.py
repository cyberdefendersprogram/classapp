"""Reading list routes (read-only, distinct from Book Reading signups)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates
from app.services.sheets import get_sheets_client

router = APIRouter()


@router.get("/reading", response_class=HTMLResponse)
async def reading_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    sheets = get_sheets_client()
    items = sheets.get_reading_list()

    return templates.TemplateResponse(
        "reading.html",
        {
            "request": request,
            "student": student,
            "items": items,
            "is_admin": is_admin(session),
        },
    )
