"""Index of standalone HTML demos stored per class under content/<class>/demos."""

import html
import re
from pathlib import Path

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.IGNORECASE)
_CLASS_RE = re.compile(r'<meta\s+name="class"\s+content="(\d+)"', re.IGNORECASE)
_NUMBER_RE = re.compile(r"^(\d+)-")


def is_valid_demo_id(demo_id: str) -> bool:
    """Demo ids are filename stems; reject anything that could escape the directory."""
    return bool(_ID_RE.match(demo_id))


def read_demo_meta(path: Path) -> dict:
    """Read title, description and class number from a demo's <title> and <meta> tags."""
    text = path.read_text(encoding="utf-8")
    title_match = _TITLE_RE.search(text)
    desc_match = _DESC_RE.search(text)
    class_match = _CLASS_RE.search(text)
    number_match = _NUMBER_RE.match(path.stem)
    return {
        "id": path.stem,
        "number": int(number_match.group(1)) if number_match else None,
        "class_no": int(class_match.group(1)) if class_match else None,
        "title": html.unescape(title_match.group(1).strip()) if title_match else path.stem,
        "description": html.unescape(desc_match.group(1).strip()) if desc_match else "",
    }


def get_available_demos(demos_dir: Path) -> list[dict]:
    """List demos in filename order; files starting with '_' are hidden."""
    if not demos_dir.exists():
        return []
    return [
        read_demo_meta(p)
        for p in sorted(demos_dir.glob("*.html"))
        if not p.name.startswith("_") and is_valid_demo_id(p.stem)
    ]
