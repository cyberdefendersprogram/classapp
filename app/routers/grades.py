"""Student grades page — shows the student's own grades synced from Canvas."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies import (
    CurrentSession,
    OnboardedStudent,
    grades_released,
    is_admin,
    templates,
)
from app.services.grades import build_grades_view

router = APIRouter()


@router.get("/grades", response_class=HTMLResponse)
async def my_grades(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Show the logged-in student's grades. Students only ever see their own row, and only
    once grades are released (Config key "grades_visible") at the end of the course.
    """
    admin = is_admin(session)
    released = grades_released() or admin
    return templates.TemplateResponse(
        "grades.html",
        {
            "request": request,
            "student": student,
            "released": released,
            "view": build_grades_view(student) if released else None,
            "is_admin": admin,
        },
    )
