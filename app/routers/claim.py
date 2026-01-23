"""Claim routes for new student account binding."""

import logging
from datetime import datetime

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import templates
from app.services.sessions import create_session_token, get_cookie_settings
from app.services.sheets import get_sheets_client
from app.services.tokens import validate_magic_token

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/claim", response_class=HTMLResponse)
async def claim_form(request: Request, token: str):
    """
    Render the claim form.

    Requires a valid token from the magic link flow.
    """
    # Validate the token (but don't consume it yet)
    # We'll validate again on POST to ensure it's still valid
    email = validate_magic_token(token)

    if not email:
        logger.warning("Invalid or expired claim token")
        return templates.TemplateResponse(
            "signin.html",
            {
                "request": request,
                "error": "This link is invalid or has expired. Please request a new sign-in link.",
                "success": None,
            },
        )

    return templates.TemplateResponse(
        "claim.html",
        {
            "request": request,
            "email": email,
            "error": None,
        },
    )


@router.post("/claim", response_class=HTMLResponse)
async def claim_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    student_id: str = Form(...),
    claim_code: str = Form(...),
):
    """
    Process account claim.

    Binds the email to the student account if student_id and claim_code match.
    """
    email = email.strip().lower()
    student_id = student_id.strip()
    claim_code = claim_code.strip().upper()

    sheets = get_sheets_client()

    # Look up student by ID
    student = sheets.get_student_by_id(student_id)

    if not student:
        logger.warning("Claim attempt for non-existent student: %s", student_id)
        return templates.TemplateResponse(
            "claim.html",
            {
                "request": request,
                "email": email,
                "error": "Invalid student ID or claim code. Please check your information and try again.",
            },
        )

    # Check if already claimed
    if student.email:
        logger.warning("Claim attempt for already claimed student: %s", student_id)
        return templates.TemplateResponse(
            "claim.html",
            {
                "request": request,
                "email": email,
                "error": "This student account has already been claimed. If this is your account, try signing in with your email.",
            },
        )

    # Verify claim code
    if student.claim_code.upper() != claim_code:
        logger.warning("Invalid claim code for student %s", student_id)
        return templates.TemplateResponse(
            "claim.html",
            {
                "request": request,
                "email": email,
                "error": "Invalid student ID or claim code. Please check your information and try again.",
            },
        )

    # Check student status
    if student.status != "active":
        logger.warning("Claim attempt for inactive student: %s (status: %s)", student_id, student.status)
        return templates.TemplateResponse(
            "claim.html",
            {
                "request": request,
                "email": email,
                "error": "This student account is not active. Please contact your instructor.",
            },
        )

    # Claim the account
    success = sheets.claim_student(student_id, claim_code, email)

    if not success:
        logger.error("Failed to claim student %s", student_id)
        return templates.TemplateResponse(
            "claim.html",
            {
                "request": request,
                "email": email,
                "error": "An error occurred while claiming your account. Please try again.",
            },
        )

    # Update first_seen_at if not set
    sheets.update_student(student_id, first_seen_at=datetime.utcnow().isoformat())

    # Create session
    session_token = create_session_token(email, student_id)

    # Redirect to onboarding
    response = RedirectResponse(url="/onboarding", status_code=302)
    cookie_settings = get_cookie_settings()
    response.set_cookie(value=session_token, **cookie_settings)

    logger.info("Student %s claimed by %s", student_id, email)
    return response
