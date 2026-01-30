"""Authentication routes for magic link login."""

import logging
from datetime import datetime

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import settings
from app.dependencies import templates
from app.services.email import send_magic_link_email
from app.services.sessions import (
    COOKIE_NAME,
    create_session_token,
    get_cookie_settings,
    verify_session_token,
)
from app.services.sheets import get_sheets_client
from app.services.tokens import check_rate_limit, create_magic_token, validate_magic_token

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def signin_page(request: Request):
    """Render the sign-in page."""
    # Check if already logged in
    session_token = request.cookies.get(COOKIE_NAME)
    if session_token:
        session = verify_session_token(session_token)
        if session:
            return RedirectResponse(url="/home", status_code=302)

    return templates.TemplateResponse(
        "signin.html",
        {"request": request, "error": None, "success": None},
    )


@router.post("/auth/request-link")
async def request_magic_link(request: Request, email: str = Form(...)):
    """
    Request a magic link email.

    Returns same response for known/unknown emails to prevent enumeration.
    """
    email = email.strip().lower()
    sheets = get_sheets_client()

    # Rate limit check
    allowed, count = check_rate_limit(email)
    if not allowed:
        logger.warning("Rate limited magic link request for %s (count: %d)", email, count)
        # Log to sheets
        sheets.append_magic_link_request({
            "requested_at": datetime.utcnow().isoformat(),
            "email": email,
            "result": "rate_limited",
            "note": f"Count: {count}",
        })
        return templates.TemplateResponse(
            "signin.html",
            {
                "request": request,
                "error": "Too many requests. Please try again in 15 minutes.",
                "success": None,
            },
        )

    # Create magic token
    token = create_magic_token(email)
    magic_link = f"{settings.base_url}/auth/verify?token={token}"

    # Send email
    result = await send_magic_link_email(email, magic_link)

    # Log to sheets
    sheets.append_magic_link_request({
        "requested_at": datetime.utcnow().isoformat(),
        "email": email,
        "result": "sent" if result.success else "error",
        "note": result.error or "",
    })

    if not result.success:
        logger.error("Failed to send magic link to %s: %s", email, result.error)
        # Don't reveal email sending errors to user
        # Fall through to success message

    # Always show success (prevents email enumeration)
    logger.info("Magic link requested for %s", email)
    return templates.TemplateResponse(
        "signin.html",
        {
            "request": request,
            "error": None,
            "success": "If this email is registered, you'll receive a sign-in link shortly. Check your inbox.",
        },
    )


@router.get("/auth/verify")
async def verify_magic_link(request: Request, token: str, response: Response):
    """
    Verify magic link token and create session or redirect to claim.
    """
    # Validate token
    email = validate_magic_token(token)
    if not email:
        logger.warning("Invalid or expired magic link")
        return templates.TemplateResponse(
            "signin.html",
            {
                "request": request,
                "error": "This link is invalid or has expired. Please request a new one.",
                "success": None,
            },
        )

    sheets = get_sheets_client()

    # Look up student by email
    student = sheets.get_student_by_email(email)

    if student and student.is_claimed:
        # Existing claimed student - create session
        session_token = create_session_token(email, student.student_id)

        # Update last_login_at
        sheets.update_roster(student.student_id, last_login_at=datetime.utcnow().isoformat())

        # Check if onboarding is needed
        redirect_url = "/home" if student.is_onboarded else "/onboarding"

        response = RedirectResponse(url=redirect_url, status_code=302)
        cookie_settings = get_cookie_settings()
        response.set_cookie(value=session_token, **cookie_settings)

        logger.info("Login successful for %s (student: %s)", email, student.student_id)
        return response

    # Email not claimed yet - need to go through claim flow
    # Create a temporary claim token (valid for 30 min)
    claim_token = create_magic_token(email, ttl_minutes=30)

    logger.info("Email %s needs to claim account", email)
    return RedirectResponse(url=f"/claim?token={claim_token}", status_code=302)


@router.post("/auth/logout")
async def logout(request: Request):
    """Log out the current user."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    logger.info("User logged out")
    return response


@router.get("/auth/logout")
async def logout_get(request: Request):
    """GET version of logout for convenience."""
    return await logout(request)
