"""Standalone HTML demos, stored per class under content/<class>/demos."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

from app.config import settings
from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates
from app.services.demo_index import get_available_demos, is_valid_demo_id, read_demo_meta

router = APIRouter()

DEMOS_DIR = Path(__file__).parent.parent.parent / "content" / settings.active_class / "demos"
FILES_DIR = DEMOS_DIR / "files"

# Demos run in an opaque origin: scripts may run, but they cannot read the session cookie.
DEMO_CSP = "sandbox allow-scripts"


@router.get("/demos", response_class=HTMLResponse)
async def demos_landing(request: Request, student: OnboardedStudent, session: CurrentSession):
    """List the demos for the active class."""
    return templates.TemplateResponse(
        "demos.html",
        {
            "request": request,
            "student": student,
            "demos": get_available_demos(DEMOS_DIR),
            "is_admin": is_admin(session),
        },
    )


@router.get("/demos/files/{filename}")
async def demo_file(filename: str, student: OnboardedStudent):
    """Download a capture or other file that a demo refers to."""
    path = FILES_DIR / filename
    if "/" in filename or "\\" in filename or filename.startswith(".") or not path.is_file():
        return Response("Not found", status_code=404)
    return FileResponse(path, filename=filename)


@router.get("/demos/{demo_id}/raw", response_class=HTMLResponse)
async def demo_raw(demo_id: str, student: OnboardedStudent):
    """Serve the demo's HTML itself, sandboxed. The demo page embeds this in an iframe."""
    path = DEMOS_DIR / f"{demo_id}.html"
    if not is_valid_demo_id(demo_id) or not path.is_file():
        return Response("Not found", status_code=404)
    return HTMLResponse(
        path.read_text(encoding="utf-8"), headers={"Content-Security-Policy": DEMO_CSP}
    )


@router.get("/demos/{demo_id}", response_class=HTMLResponse)
async def demo_page(
    request: Request, demo_id: str, student: OnboardedStudent, session: CurrentSession
):
    """Show one demo inside the class page, with the nav bar."""
    path = DEMOS_DIR / f"{demo_id}.html"
    if not is_valid_demo_id(demo_id) or not path.is_file():
        return templates.TemplateResponse(
            "demo.html",
            {
                "request": request,
                "student": student,
                "demo": None,
                "is_admin": is_admin(session),
            },
            status_code=404,
        )
    return templates.TemplateResponse(
        "demo.html",
        {
            "request": request,
            "student": student,
            "demo": read_demo_meta(path),
            "is_admin": is_admin(session),
        },
    )
