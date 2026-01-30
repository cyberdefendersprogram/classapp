"""Onboarding routes for new student profile setup."""

import logging
from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import RequiredSession, templates
from app.services.sheets import get_sheets_client

logger = logging.getLogger(__name__)
router = APIRouter()

# Form version for tracking changes to onboarding questions
FORM_VERSION = "v1"

# Onboarding form fields configuration
# All fields are optional. Only fields that are empty in the Roster are shown.
ONBOARDING_FIELDS = [
    {
        "key": "preferred_name",
        "label": "Preferred Name",
        "type": "text",
        "placeholder": "What should we call you?",
        "help": "This is how you'll appear in the class.",
    },
    {
        "key": "preferred_name_phonetic",
        "label": "How to pronounce your name",
        "type": "text",
        "placeholder": "e.g., Vai-bha-v",
        "help": "Help us pronounce your name correctly.",
    },
    {
        "key": "preferred_pronoun",
        "label": "Preferred Pronouns",
        "type": "text",
        "placeholder": "e.g., she/her, he/him, they/them",
        "help": "Optional. Helps us address you correctly.",
    },
    {
        "key": "linkedin",
        "label": "LinkedIn URL",
        "type": "text",
        "placeholder": "linkedin.com/in/yourprofile",
        "help": "Optional. Share your professional profile.",
    },
    {
        "key": "cs_experience",
        "label": "CS/Tech Experience",
        "type": "text",
        "placeholder": "e.g., 2 years of programming, beginner",
        "help": "Describe your computer science or tech background.",
    },
    {
        "key": "computer_system",
        "label": "What Computer System (H/W-OS)",
        "type": "text",
        "placeholder": "e.g., Mac Pro M1 (OSX 13), Windows 11 laptop",
        "help": "What computer will you use for class?",
    },
    {
        "key": "hobbies",
        "label": "Hobbies",
        "type": "text",
        "placeholder": "What do you enjoy doing outside of class?",
        "help": "Help us get to know you better.",
    },
    {
        "key": "used_netlabs",
        "label": "Have you used Netlabs before?",
        "type": "select",
        "options": [
            {"value": "", "label": "-- Select --"},
            {"value": "Yes", "label": "Yes"},
            {"value": "No", "label": "No"},
        ],
        "help": "Prior experience with Netlabs virtual lab environment.",
    },
    {
        "key": "used_tryhackme",
        "label": "Have you used TryHackMe before?",
        "type": "select",
        "options": [
            {"value": "", "label": "-- Select --"},
            {"value": "Yes", "label": "Yes"},
            {"value": "No", "label": "No"},
        ],
        "help": "Prior experience with TryHackMe security training.",
    },
    {
        "key": "class_goals",
        "label": "What do you want from this class?",
        "type": "textarea",
        "placeholder": "What do you hope to learn or achieve?",
        "help": "What would make this course successful for you?",
    },
    {
        "key": "support_request",
        "label": "Any special support request for the teacher?",
        "type": "textarea",
        "placeholder": "Anything we should know to support your learning?",
        "help": "Optional. Any accommodations or preferences.",
    },
]


def get_fields_to_show(student) -> list[dict]:
    """Get only the fields that are empty for this student."""
    empty_fields = student.get_empty_profile_fields()
    return [f for f in ONBOARDING_FIELDS if f["key"] in empty_fields]


@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_form(request: Request, session: RequiredSession):
    """
    Render the onboarding form.

    Requires authentication. Redirects to /home if already onboarded.
    Only shows fields that are empty in the Roster.
    """
    sheets = get_sheets_client()
    student = sheets.get_roster_by_id(session.student_id)

    if not student:
        logger.warning("Student not found for session: %s", session.student_id)
        return RedirectResponse(url="/auth/logout", status_code=302)

    # If already onboarded, redirect to home
    if student.onboarding_completed_at:
        return RedirectResponse(url="/home", status_code=302)

    # Get only fields that need to be filled
    fields_to_show = get_fields_to_show(student)

    return templates.TemplateResponse(
        "onboarding.html",
        {
            "request": request,
            "student": student,
            "fields": fields_to_show,
            "error": None,
        },
    )


@router.post("/onboarding", response_class=HTMLResponse)
async def onboarding_submit(
    request: Request,
    session: RequiredSession,
    preferred_name: str = Form(""),
    preferred_name_phonetic: str = Form(""),
    preferred_pronoun: str = Form(""),
    linkedin: str = Form(""),
    cs_experience: str = Form(""),
    computer_system: str = Form(""),
    hobbies: str = Form(""),
    used_netlabs: str = Form(""),
    used_tryhackme: str = Form(""),
    class_goals: str = Form(""),
    support_request: str = Form(""),
):
    """
    Process onboarding form submission.

    All fields are optional. Updates roster and logs responses to Sheets.
    """
    sheets = get_sheets_client()
    student = sheets.get_roster_by_id(session.student_id)

    if not student:
        logger.warning("Student not found for session: %s", session.student_id)
        return RedirectResponse(url="/auth/logout", status_code=302)

    # Prepare form data - only include non-empty values
    form_data = {}
    field_values = {
        "preferred_name": preferred_name.strip(),
        "preferred_name_phonetic": preferred_name_phonetic.strip(),
        "preferred_pronoun": preferred_pronoun.strip(),
        "linkedin": linkedin.strip(),
        "cs_experience": cs_experience.strip(),
        "computer_system": computer_system.strip(),
        "hobbies": hobbies.strip(),
        "used_netlabs": used_netlabs.strip(),
        "used_tryhackme": used_tryhackme.strip(),
        "class_goals": class_goals.strip(),
        "support_request": support_request.strip(),
    }

    # Only include fields that have values
    for key, value in field_values.items():
        if value:
            form_data[key] = value

    now = datetime.utcnow().isoformat()

    # Update roster with non-empty fields and mark onboarding complete
    update_fields = {**form_data, "onboarding_completed_at": now}
    success = sheets.update_roster(session.student_id, **update_fields)

    if not success:
        logger.error("Failed to update roster %s during onboarding", session.student_id)
        fields_to_show = get_fields_to_show(student)
        return templates.TemplateResponse(
            "onboarding.html",
            {
                "request": request,
                "student": student,
                "fields": fields_to_show,
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
