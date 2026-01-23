"""Onboarding routes for new student profile setup."""

import logging
from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import CurrentStudent, RequiredSession, templates
from app.services.sheets import get_sheets_client

logger = logging.getLogger(__name__)
router = APIRouter()

# Form version for tracking changes to onboarding questions
FORM_VERSION = "v1"

# Onboarding form fields configuration
ONBOARDING_FIELDS = [
    {
        "key": "preferred_name",
        "label": "Preferred Name",
        "type": "text",
        "required": True,
        "placeholder": "What should we call you?",
        "help": "This is how you'll appear in the class.",
    },
    {
        "key": "pronouns",
        "label": "Pronouns",
        "type": "text",
        "required": False,
        "placeholder": "e.g., she/her, he/him, they/them",
        "help": "Optional. Helps us address you correctly.",
    },
    {
        "key": "hobbies",
        "label": "Hobbies & Interests",
        "type": "textarea",
        "required": False,
        "placeholder": "What do you enjoy doing outside of class?",
        "help": "Help us get to know you better.",
    },
    {
        "key": "computer_experience",
        "label": "Computer Experience",
        "type": "select",
        "required": False,
        "options": [
            {"value": "", "label": "Select your experience level"},
            {"value": "beginner", "label": "Beginner - New to computers"},
            {"value": "intermediate", "label": "Intermediate - Comfortable with basics"},
            {"value": "advanced", "label": "Advanced - Very experienced"},
        ],
        "help": "This helps us tailor the course content.",
    },
    {
        "key": "security_experience",
        "label": "Security Experience",
        "type": "textarea",
        "required": False,
        "placeholder": "Any prior experience with cybersecurity?",
        "help": "It's okay if you have none!",
    },
    {
        "key": "goals",
        "label": "Goals",
        "type": "textarea",
        "required": False,
        "placeholder": "What do you hope to learn or achieve?",
        "help": "What would make this course successful for you?",
    },
    {
        "key": "support_needs",
        "label": "Support Needs",
        "type": "textarea",
        "required": False,
        "placeholder": "Anything we should know to support your learning?",
        "help": "Optional. Any accommodations or preferences.",
    },
]


@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_form(request: Request, session: RequiredSession):
    """
    Render the onboarding form.

    Requires authentication. Redirects to /home if already onboarded.
    """
    sheets = get_sheets_client()
    student = sheets.get_student_by_id(session.student_id)

    if not student:
        logger.warning("Student not found for session: %s", session.student_id)
        return RedirectResponse(url="/auth/logout", status_code=302)

    # If already onboarded, redirect to home
    if student.onboarded_at:
        return RedirectResponse(url="/home", status_code=302)

    return templates.TemplateResponse(
        "onboarding.html",
        {
            "request": request,
            "student": student,
            "fields": ONBOARDING_FIELDS,
            "error": None,
        },
    )


@router.post("/onboarding", response_class=HTMLResponse)
async def onboarding_submit(
    request: Request,
    session: RequiredSession,
    preferred_name: str = Form(...),
    pronouns: str = Form(""),
    hobbies: str = Form(""),
    computer_experience: str = Form(""),
    security_experience: str = Form(""),
    goals: str = Form(""),
    support_needs: str = Form(""),
):
    """
    Process onboarding form submission.

    Updates student record and logs responses to Sheets.
    """
    sheets = get_sheets_client()
    student = sheets.get_student_by_id(session.student_id)

    if not student:
        logger.warning("Student not found for session: %s", session.student_id)
        return RedirectResponse(url="/auth/logout", status_code=302)

    # Validate preferred_name
    preferred_name = preferred_name.strip()
    if not preferred_name:
        return templates.TemplateResponse(
            "onboarding.html",
            {
                "request": request,
                "student": student,
                "fields": ONBOARDING_FIELDS,
                "error": "Preferred name is required.",
            },
        )

    # Prepare form data
    form_data = {
        "preferred_name": preferred_name,
        "pronouns": pronouns.strip(),
        "hobbies": hobbies.strip(),
        "computer_experience": computer_experience.strip(),
        "security_experience": security_experience.strip(),
        "goals": goals.strip(),
        "support_needs": support_needs.strip(),
    }

    now = datetime.utcnow().isoformat()

    # Update student record
    success = sheets.update_student(
        session.student_id,
        preferred_name=preferred_name,
        pronouns=pronouns.strip() if pronouns else "",
        onboarded_at=now,
    )

    if not success:
        logger.error("Failed to update student %s during onboarding", session.student_id)
        return templates.TemplateResponse(
            "onboarding.html",
            {
                "request": request,
                "student": student,
                "fields": ONBOARDING_FIELDS,
                "error": "An error occurred. Please try again.",
            },
        )

    # Log each field to Onboarding_Responses
    for field in ONBOARDING_FIELDS:
        key = field["key"]
        value = form_data.get(key, "")

        if value:  # Only log non-empty responses
            response_data = {
                "timestamp": now,
                "student_id": session.student_id,
                "email": session.email,
                "form_version": FORM_VERSION,
                "question_key": key,
                "question_label": field["label"],
                "answer": value,
                "answer_type": field["type"],
                "source": "web",
            }
            sheets.append_onboarding_response(response_data)

    logger.info("Onboarding completed for student %s", session.student_id)
    return RedirectResponse(url="/home", status_code=302)
