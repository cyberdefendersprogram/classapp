"""Shared dependencies for FastAPI application."""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates

from app.db.sqlite import get_cached_student, set_cached_student
from app.models.roster import RosterEntry
from app.services.sessions import COOKIE_NAME, SessionData, verify_session_token
from app.services.sheets import SheetsUnavailableError, get_sheets_client

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
) -> RosterEntry:
    """
    Get the current student from session.

    Checks SQLite cache first (5-min TTL) to avoid per-request Sheets API calls.
    On cache miss, fetches from Sheets and refreshes cache.
    If Sheets is unavailable, serves stale cache (up to 24h) before returning 503.
    Raises 401 if student genuinely not found.
    """
    # Fast path: serve from local SQLite cache
    student = get_cached_student(session.student_id)
    if student:
        return student

    # Cache miss or expired — fetch from Sheets
    sheets = get_sheets_client()
    try:
        student = sheets.get_roster_by_id(session.student_id)
    except SheetsUnavailableError:
        # Sheets is down — try stale cache (up to 24h) before giving up
        stale = get_cached_student(session.student_id, max_age_seconds=86400)
        if stale:
            logger.warning("Serving stale cache for %s (Sheets unavailable)", session.student_id)
            return stale
        logger.warning("Sheets unavailable for session %s — returning 503", session.student_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again in a moment.",
        )

    if not student:
        logger.warning("Student not found for session: %s", session.student_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found",
        )

    set_cached_student(student)
    return student


def require_onboarded(
    student: Annotated[RosterEntry, Depends(get_current_student)],
) -> RosterEntry:
    """
    Require that the student has completed onboarding.

    Raises 403 if not onboarded (should redirect to /onboarding).
    """
    if not student.onboarding_completed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Onboarding required",
        )
    return student


def _is_admin_email(email: str, admin_email_config: str | None) -> bool:
    """Check email against the Config sheet's admin_email, a comma-separated list."""
    if not admin_email_config:
        return False

    admin_emails = {e.strip().lower() for e in admin_email_config.split(",") if e.strip()}
    return email.lower() in admin_emails


def require_admin(
    session: Annotated[SessionData, Depends(require_session)],
) -> SessionData:
    """
    Require admin access.

    Raises 403 if user is not one of the configured admins.
    """
    sheets = get_sheets_client()
    admin_email = sheets.get_config("admin_email")

    if not _is_admin_email(session.email, admin_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return session


# Type aliases for cleaner dependency injection
CurrentSession = Annotated[SessionData | None, Depends(get_current_session)]
RequiredSession = Annotated[SessionData, Depends(require_session)]
CurrentStudent = Annotated[RosterEntry, Depends(get_current_student)]
OnboardedStudent = Annotated[RosterEntry, Depends(require_onboarded)]
AdminSession = Annotated[SessionData, Depends(require_admin)]


def is_admin(session: SessionData | None) -> bool:
    """Check if session belongs to one of the configured admin users."""
    if not session:
        return False

    sheets = get_sheets_client()
    admin_email = sheets.get_config("admin_email")

    return _is_admin_email(session.email, admin_email)


def nav_reading_link() -> dict | None:
    """
    Which reading nav link (if any) to show, driven by the active course's
    Config sheet key "reading_mode":
      - "list"    -> the new read-only Reading page (/reading)
      - "signup"  -> the existing chapter-claim Book Reading page (/book-reading)
      - anything else / absent -> hidden (defaults to "signup" for courses that
        predate this key, so existing Book Reading behavior doesn't change)
    """
    sheets = get_sheets_client()
    mode = sheets.get_config("reading_mode") or "signup"

    if mode == "list":
        return {"url": "/reading", "label": "Reading"}
    if mode == "signup":
        return {"url": "/book-reading", "label": "Book Reading"}
    return None


# Exposed to templates so nav blocks can render the right reading link without
# every route having to thread it through their context dict.
templates.env.globals["nav_reading_link"] = nav_reading_link
