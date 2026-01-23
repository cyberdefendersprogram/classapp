"""Shared dependencies for FastAPI application."""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.models.student import Student
from app.services.sessions import COOKIE_NAME, SessionData, verify_session_token
from app.services.sheets import get_sheets_client

logger = logging.getLogger(__name__)

# Templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_current_session(
    session: Annotated[str | None, Cookie(alias=COOKIE_NAME)] = None,
) -> SessionData | None:
    """
    Get current session from cookie.

    Returns None if no valid session.
    """
    if not session:
        return None

    return verify_session_token(session)


def require_session(
    session: Annotated[SessionData | None, Depends(get_current_session)],
) -> SessionData:
    """
    Require a valid session.

    Raises 401 if no valid session.
    """
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return session


def get_current_student(
    session: Annotated[SessionData, Depends(require_session)],
) -> Student:
    """
    Get the current student from session.

    Raises 401 if session invalid or student not found.
    """
    sheets = get_sheets_client()
    student = sheets.get_student_by_id(session.student_id)

    if not student:
        logger.warning("Student not found for session: %s", session.student_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found",
        )

    return student


def require_onboarded(
    student: Annotated[Student, Depends(get_current_student)],
) -> Student:
    """
    Require that the student has completed onboarding.

    Raises 403 if not onboarded (should redirect to /onboarding).
    """
    if not student.onboarded_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Onboarding required",
        )
    return student


# Type aliases for cleaner dependency injection
CurrentSession = Annotated[SessionData | None, Depends(get_current_session)]
RequiredSession = Annotated[SessionData, Depends(require_session)]
CurrentStudent = Annotated[Student, Depends(get_current_student)]
OnboardedStudent = Annotated[Student, Depends(require_onboarded)]
