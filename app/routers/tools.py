"""Tools reference pages for security tools."""

import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies import CurrentSession, OnboardedStudent, is_admin, templates
from app.services.tool_parser import get_available_tools, parse_tool_content

logger = logging.getLogger(__name__)
router = APIRouter()

TOOLS_DIR = Path(__file__).parent.parent.parent / "content" / "tools"


@router.get("/tools", response_class=HTMLResponse)
async def tools_landing(request: Request, student: OnboardedStudent, session: CurrentSession):
    """
    Render the tools landing page listing all available tools.
    """
    tools = get_available_tools(TOOLS_DIR)

    return templates.TemplateResponse(
        "tools.html",
        {
            "request": request,
            "student": student,
            "tools": tools,
            "is_admin": is_admin(session),
        },
    )


@router.get("/tools/{tool_id}", response_class=HTMLResponse)
async def tool_page(request: Request, tool_id: str, student: OnboardedStudent, session: CurrentSession):
    """
    Render an individual tool reference page.
    """
    tools = get_available_tools(TOOLS_DIR)
    tool_path = TOOLS_DIR / f"{tool_id}.md"

    if not tool_path.exists():
        return templates.TemplateResponse(
            "tool.html",
            {
                "request": request,
                "student": student,
                "tool_id": tool_id,
                "title": "Tool Not Found",
                "content": "<p>Tool not found.</p>",
                "scenarios": [],
                "command_builder": None,
                "tools": tools,
                "is_admin": is_admin(session),
            },
            status_code=404,
        )

    try:
        markdown_text = tool_path.read_text(encoding="utf-8")
        parsed = parse_tool_content(markdown_text, tool_id)
    except Exception as e:
        logger.exception("Failed to parse tool content %s: %s", tool_id, e)
        return templates.TemplateResponse(
            "tool.html",
            {
                "request": request,
                "student": student,
                "tool_id": tool_id,
                "title": "Error",
                "content": "<p>Error loading tool content.</p>",
                "scenarios": [],
                "command_builder": None,
                "tools": tools,
                "is_admin": is_admin(session),
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        "tool.html",
        {
            "request": request,
            "student": student,
            "tool_id": tool_id,
            "title": parsed["title"],
            "content": parsed["content"],
            "scenarios": parsed["scenarios"],
            "command_builder": parsed["command_builder"],
            "quizzes": parsed["quizzes"],
            "tools": tools,
            "is_admin": is_admin(session),
        },
    )
