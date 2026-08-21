"""General page routes for authenticated users."""

import logging
from datetime import datetime
from pathlib import Path

import markdown
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import settings
from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates
from app.services.sheets import get_sheets_client

# Project root for resolving content files
_BASE_PATH = Path(__file__).parent.parent.parent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Render the home/dashboard page.

    Requires authentication and completed onboarding.
    """
    sheets = get_sheets_client()

    # Get course info from config
    course_title = sheets.get_config("course_title") or "Class Portal"
    term = sheets.get_config("term") or ""

    # Rate professor notice — default true if key is absent
    rmp_raw = sheets.get_config("RATE_PROFESSOR_NOTICE")
    show_rate_notice = (rmp_raw is None) or (rmp_raw.strip().lower() not in ("false", "0", "no"))
    rate_professor_url = sheets.get_config("rate_professor_url") or ""

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "student": student,
            "course_title": course_title,
            "term": term,
            "is_admin": is_admin(session),
            "show_rate_notice": show_rate_notice,
            "rate_professor_url": rate_professor_url,
        },
    )


@router.get("/me", response_class=HTMLResponse)
async def profile_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Render the profile page with edit form.

    Requires authentication and completed onboarding.
    """
    return templates.TemplateResponse(
        "me.html",
        {
            "request": request,
            "student": student,
            "success": None,
            "error": None,
            "is_admin": is_admin(session),
        },
    )


@router.post("/me", response_class=HTMLResponse)
async def profile_update(
    request: Request,
    student: OnboardedStudent,
    session: CurrentSession,
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
    Update profile information.

    Requires authentication and completed onboarding.
    """
    sheets = get_sheets_client()

    # Build update fields
    update_fields = {
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

    success = sheets.update_roster(student.student_id, **update_fields)

    # Refresh student data
    updated_student = sheets.get_roster_by_id(student.student_id) or student

    if success:
        logger.info("Profile updated for student %s", student.student_id)
        return templates.TemplateResponse(
            "me.html",
            {
                "request": request,
                "student": updated_student,
                "success": "Profile updated successfully.",
                "error": None,
                "is_admin": is_admin(session),
            },
        )
    else:
        logger.error("Failed to update profile for student %s", student.student_id)
        return templates.TemplateResponse(
            "me.html",
            {
                "request": request,
                "student": updated_student,
                "success": None,
                "error": "An error occurred. Please try again.",
                "is_admin": is_admin(session),
            },
        )


@router.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Render the class schedule page.

    Requires authentication and completed onboarding.
    """
    sheets = get_sheets_client()

    # Get schedule entries
    schedule = sheets.get_schedule()

    # Get course info from config
    course_title = sheets.get_config("course_title") or "Class Portal"

    return templates.TemplateResponse(
        "schedule.html",
        {
            "request": request,
            "student": student,
            "schedule": schedule,
            "course_title": course_title,
            "is_admin": is_admin(session),
        },
    )


@router.get("/class/{id}", response_class=HTMLResponse)
async def class_page(request: Request, id: str, student: OnboardedStudent, session: CurrentSession):
    """
    Render lecture/class content page from markdown file on disk.
    """
    sheets = get_sheets_client()
    entry = sheets.get_schedule_entry_by_class_number(id)

    # Get all numbered classes for sidebar navigation
    all_schedule = sheets.get_schedule()
    numbered_classes = [e for e in all_schedule if e.class_number and e.has_content]

    if not entry or not entry.has_content:
        return templates.TemplateResponse(
            "class.html",
            {
                "request": request,
                "student": student,
                "title": "Class Not Found",
                "content": "<p>Lecture not found.</p>",
                "is_admin": is_admin(session),
                "numbered_classes": numbered_classes,
                "current_class_number": id,
            },
            status_code=404,
        )

    content_path = entry.desc_link

    base_path = Path(__file__).parent.parent.parent  # project root
    file_path = base_path / content_path

    if not file_path.exists():
        return templates.TemplateResponse(
            "class.html",
            {
                "request": request,
                "student": student,
                "title": "Content Missing",
                "content": "<p>Lecture file missing on server.</p>",
                "is_admin": is_admin(session),
                "numbered_classes": numbered_classes,
                "current_class_number": id,
            },
            status_code=500,
        )

    try:
        markdown_text = file_path.read_text(encoding="utf-8")
        html_content = markdown.markdown(
            markdown_text, extensions=["fenced_code", "tables", "toc", "codehilite"]
        )
    except Exception as e:
        logger.exception("Failed reading class content %s: %s", id, e)
        return templates.TemplateResponse(
            "class.html",
            {
                "request": request,
                "student": student,
                "title": "Error",
                "content": "<p>Error loading lecture content.</p>",
                "is_admin": is_admin(session),
                "numbered_classes": numbered_classes,
                "current_class_number": id,
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        "class.html",
        {
            "request": request,
            "student": student,
            "title": entry.desc,
            "content": html_content,
            "is_admin": is_admin(session),
            "numbered_classes": numbered_classes,
            "current_class_number": id,
        },
    )


def _final_project_individual_context(request, student, session, sheets, error=None, success=None):
    is_open = (sheets.get_config("final_project_open") or "false").lower() == "true"
    my_entry = sheets.get_final_project_entry(student.student_id)
    entries = sheets.get_final_project_entries()
    entries.sort(key=lambda e: (e.order is None, e.order or 0, e.full_name.lower()))

    return {
        "request": request,
        "student": student,
        "is_admin": is_admin(session),
        "is_open": is_open,
        "my_entry": my_entry,
        "entries": entries,
        "error": error,
        "success": success,
    }


@router.get("/final-projects", response_class=HTMLResponse)
async def final_projects_page(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Render the final projects page.

    Shape is driven by the active course's Config key "final_project_mode":
      - "individual" (e.g. CIS52's one-student-one-breach-review model):
        sign-up form + flat schedule of student/topic/order, sourced from
        the Final_Projects sheet (see get_final_project_entries()).
      - "teams" (default, e.g. CIS60's group case-study model): the
        existing team roster grouped by project, with each team's
        content/<active_class>/projects/<slug>.md rendered as a description.
    """
    sheets = get_sheets_client()
    mode = sheets.get_config("final_project_mode") or "teams"

    if mode == "individual":
        ctx = _final_project_individual_context(request, student, session, sheets)
        return templates.TemplateResponse("final_projects_individual.html", ctx)

    projects = sheets.get_final_projects()

    # Attach rendered markdown description to each project if a content file exists
    projects_dir = _BASE_PATH / "content" / settings.active_class / "projects"
    for project in projects:
        desc_file = projects_dir / f"{project['slug']}.md"
        if desc_file.exists():
            try:
                md_text = desc_file.read_text(encoding="utf-8")
                project["description_html"] = markdown.markdown(
                    md_text, extensions=["fenced_code", "tables"]
                )
            except Exception as e:
                logger.warning("Could not render project description %s: %s", project["slug"], e)
                project["description_html"] = None
        else:
            project["description_html"] = None

    return templates.TemplateResponse(
        "final_projects.html",
        {
            "request": request,
            "student": student,
            "is_admin": is_admin(session),
            "projects": projects,
        },
    )


@router.post("/final-projects/submit", response_class=HTMLResponse)
async def final_project_submit(
    request: Request,
    student: OnboardedStudent,
    session: CurrentSession,
    topic: str = Form(...),
    timing_pref: str = Form(""),
):
    """Submit (or update) this student's Final_Projects sign-up. Individual mode only."""
    sheets = get_sheets_client()
    mode = sheets.get_config("final_project_mode") or "teams"

    if mode != "individual":
        return RedirectResponse(url="/final-projects", status_code=302)

    is_open = (sheets.get_config("final_project_open") or "false").lower() == "true"
    if not is_open:
        ctx = _final_project_individual_context(
            request, student, session, sheets, error="Sign-up isn't open yet."
        )
        return templates.TemplateResponse("final_projects_individual.html", ctx)

    topic = topic.strip()
    if not topic:
        ctx = _final_project_individual_context(
            request, student, session, sheets, error="Please enter a topic."
        )
        return templates.TemplateResponse("final_projects_individual.html", ctx)

    success = sheets.upsert_final_project(
        student.student_id,
        full_name=student.display_name,
        topic=topic,
        timing_pref=timing_pref.strip(),
        submitted_at=datetime.utcnow().isoformat(),
    )

    if not success:
        ctx = _final_project_individual_context(
            request,
            student,
            session,
            sheets,
            error="Something went wrong saving your topic. Please try again.",
        )
        return templates.TemplateResponse("final_projects_individual.html", ctx)

    logger.info("Student %s submitted final project topic", student.student_id)
    return RedirectResponse(url="/final-projects", status_code=302)
