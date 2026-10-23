"""Case studies copied from Canvas into content/<class>/case_studies by scripts/sync_case_studies.py."""

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_META_RE = re.compile(r"^<!--case-study (\{.*?\})-->\n?", re.DOTALL)
_PACIFIC = ZoneInfo("America/Los_Angeles")


def is_valid_case_study_id(case_study_id: str) -> bool:
    return bool(_ID_RE.match(case_study_id))


def format_due(due_at: str | None) -> str | None:
    """Format a Canvas UTC timestamp as Pacific time, e.g. 'Fri Oct 30, 2026, 9:00 a.m. PT'."""
    if not due_at:
        return None
    dt = datetime.fromisoformat(due_at.replace("Z", "+00:00")).astimezone(_PACIFIC)
    hour = dt.hour % 12 or 12
    ampm = "a.m." if dt.hour < 12 else "p.m."
    return f"{dt:%a %b} {dt.day}, {dt.year}, {hour}:{dt.minute:02d} {ampm} PT"


def read_case_study(path: Path) -> dict:
    """Return id, number, title, due, canvas_url and body HTML for one synced file."""
    text = path.read_text(encoding="utf-8")
    match = _META_RE.match(text)
    meta = json.loads(match.group(1)) if match else {}
    body = text[match.end() :] if match else text
    return {
        "id": path.stem,
        "number": meta.get("number"),
        "title": meta.get("title") or path.stem.replace("-", " ").title(),
        "due": format_due(meta.get("due_at")),
        "canvas_url": meta.get("canvas_url"),
        "body": body,
    }


def get_available_case_studies(directory: Path) -> list[dict]:
    if not directory.exists():
        return []
    return [
        read_case_study(p)
        for p in sorted(directory.glob("*.html"))
        if not p.name.startswith("_") and is_valid_case_study_id(p.stem)
    ]
