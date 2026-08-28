"""Lab assignment pages. Worked solutions are restricted to admins."""

import logging
import re
from pathlib import Path

import markdown
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from app.config import settings
from app.dependencies import AdminSession, CurrentSession, OnboardedStudent, is_admin, templates

logger = logging.getLogger(__name__)
router = APIRouter()

LABS_DIR = Path(__file__).parent.parent.parent / "content" / settings.active_class / "labs"
SOLUTIONS_DIR = LABS_DIR / "solutions"

TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
DUE_PATTERN = re.compile(r"^\*\*Due:\*\*\s*(.+)$", re.MULTILINE)


def _extract_title(content: str, fallback: str) -> str:
    match = TITLE_PATTERN.search(content)
    return match.group(1).strip() if match else fallback


def _extract_due(content: str) -> str | None:
    match = DUE_PATTERN.search(content)
    return match.group(1).strip() if match else None


def get_available_labs() -> list[dict]:
    """List labs from the labs directory, with 'id', 'title', 'due', 'has_solution'."""
    labs = []

    if not LABS_DIR.exists():
        return labs

    for md_file in sorted(LABS_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        labs.append(
            {
                "id": md_file.stem,
                "title": _extract_title(content, md_file.stem.replace("-", " ").title()),
                "due": _extract_due(content),
                "has_solution": (SOLUTIONS_DIR / md_file.name).exists(),
            }
        )

    return labs


@router.get("/labs", response_class=HTMLResponse)
async def labs_landing(request: Request, student: OnboardedStudent, session: CurrentSession):
    """Render the labs landing page listing all available labs."""
    labs = get_available_labs()

    return templates.TemplateResponse(
        "labs.html",
        {
            "request": request,
            "student": student,
            "labs": labs,
            "is_admin": is_admin(session),
        },
    )


@router.get("/labs/{lab_id}", response_class=HTMLResponse)
async def lab_page(
    request: Request, lab_id: str, student: OnboardedStudent, session: CurrentSession
):
    """Render an individual lab assignment page."""
    lab_path = LABS_DIR / f"{lab_id}.md"
    has_solution = (SOLUTIONS_DIR / f"{lab_id}.md").exists()

    if not lab_path.exists():
        return templates.TemplateResponse(
            "lab.html",
            {
                "request": request,
                "student": student,
                "lab_id": lab_id,
                "title": "Lab Not Found",
                "content": "<p>Lab not found.</p>",
                "has_solution": False,
                "is_admin": is_admin(session),
            },
            status_code=404,
        )

    try:
        markdown_text = lab_path.read_text(encoding="utf-8")
        html_content = markdown.markdown(markdown_text, extensions=["fenced_code", "tables", "toc"])
        title = _extract_title(markdown_text, lab_id.replace("-", " ").title())
    except Exception as e:
        logger.exception("Failed reading lab content %s: %s", lab_id, e)
        return templates.TemplateResponse(
            "lab.html",
            {
                "request": request,
                "student": student,
                "lab_id": lab_id,
                "title": "Error",
                "content": "<p>Error loading lab content.</p>",
                "has_solution": False,
                "is_admin": is_admin(session),
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        "lab.html",
        {
            "request": request,
            "student": student,
            "lab_id": lab_id,
            "title": title,
            "content": html_content,
            "has_solution": has_solution,
            "is_admin": is_admin(session),
        },
    )


@router.get("/labs/{lab_id}/solution", response_class=HTMLResponse)
async def lab_solution_page(request: Request, lab_id: str, session: AdminSession):
    """Admin-only worked solution for a lab."""
    solution_path = SOLUTIONS_DIR / f"{lab_id}.md"

    if not solution_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found.")

    try:
        markdown_text = solution_path.read_text(encoding="utf-8")
        html_content = markdown.markdown(markdown_text, extensions=["fenced_code", "tables", "toc"])
        title = _extract_title(markdown_text, f"{lab_id.replace('-', ' ').title()} — Solution")
    except Exception as e:
        logger.exception("Failed reading lab solution %s: %s", lab_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error loading solution."
        ) from e

    return templates.TemplateResponse(
        "lab_solution.html",
        {
            "request": request,
            "lab_id": lab_id,
            "title": title,
            "content": html_content,
        },
    )
