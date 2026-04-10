"""Book reading assignment routes."""

import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates
from app.services.sheets import get_sheets_client

logger = logging.getLogger(__name__)
router = APIRouter()


def _page_context(request, student, session, sheets, error=None, success=None):
    chapters = sheets.get_book_readings()

    my_name = student.display_name
    my_name_lower = my_name.lower()
    my_primary_chapter = None
    my_secondary_chapter = None
    for ch in chapters:
        if ch.primary_reader.lower() == my_name_lower:
            my_primary_chapter = ch.chapter
        if ch.secondary_reader.lower() == my_name_lower:
            my_secondary_chapter = ch.chapter

    return {
        "request": request,
        "student": student,
        "chapters": chapters,
        "my_primary_chapter": my_primary_chapter,
        "my_secondary_chapter": my_secondary_chapter,
        "is_admin": is_admin(session),
        "error": error,
        "success": success,
    }


@router.get("/book-reading", response_class=HTMLResponse)
async def book_reading_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    sheets = get_sheets_client()
    ctx = _page_context(request, student, session, sheets)
    return templates.TemplateResponse("book_reading.html", ctx)


@router.post("/book-reading/signup", response_class=HTMLResponse)
async def book_reading_signup(
    request: Request,
    student: OnboardedStudent,
    session: CurrentSession,
    chapter: str = Form(...),
    role: str = Form(...),
):
    sheets = get_sheets_client()

    if role not in ("primary", "secondary"):
        ctx = _page_context(request, student, session, sheets, error="Invalid role.")
        return templates.TemplateResponse("book_reading.html", ctx)

    chapters = sheets.get_book_readings()
    my_name = student.display_name
    my_name_lower = my_name.lower()

    # Enforce one-role-per-type constraint
    for ch in chapters:
        if role == "primary" and ch.primary_reader.lower() == my_name_lower:
            ctx = _page_context(
                request,
                student,
                session,
                sheets,
                error="You are already signed up as a primary reader for another chapter.",
            )
            return templates.TemplateResponse("book_reading.html", ctx)
        if role == "secondary" and ch.secondary_reader.lower() == my_name_lower:
            ctx = _page_context(
                request,
                student,
                session,
                sheets,
                error="You are already signed up as a secondary reader for another chapter.",
            )
            return templates.TemplateResponse("book_reading.html", ctx)

    ok, err = sheets.assign_book_reader(chapter, my_name, role)

    if ok:
        logger.info("Student %s signed up as %s for '%s'", student.student_id, role, chapter)
        ctx = _page_context(
            request,
            student,
            session,
            sheets,
            success=f'You are now the {role} reader for "{chapter}".',
        )
    else:
        ctx = _page_context(request, student, session, sheets, error=err)

    return templates.TemplateResponse("book_reading.html", ctx)
