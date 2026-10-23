"""Copy the Case Study assignments from Canvas into content/<course>/case_studies.

The class portal shows the same text students see in Canvas. Re-run this after
editing a case study assignment in Canvas.

    python scripts/sync_case_studies.py --canvas-env ~/.env.secrets [--apply]

--canvas-env points at a dotenv file containing CANVAS_TOKEN (and optionally
CANVAS_BASE_URL / CANVAS_COURSE_ID). The token is never printed. Without --apply
the script only lists what it would write.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import requests
from dotenv import dotenv_values

# Case study number -> (Canvas assignment id, file slug)
CASE_STUDIES = {
    1: (1820966, "mitnick"),
    2: (1820971, "target"),
    3: (1820967, "apt1-or-ir-startup"),
    4: (1820973, "opm"),
    5: (1820975, "your-choice"),
}

DEFAULT_COURSE_ID = "89432"
DEFAULT_BASE_URL = "https://peralta.instructure.com"


def file_name(number: int, slug: str) -> str:
    return f"{number:03d}-{slug}.html"


def render(number: int, assignment: dict, canvas_url: str) -> str:
    meta = {
        "number": number,
        "title": re.sub(r"\s+", " ", assignment["name"]).strip(),
        "due_at": assignment.get("due_at"),
        "canvas_url": canvas_url,
    }
    return f"<!--case-study {json.dumps(meta)}-->\n{assignment.get('description') or ''}\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--canvas-env", required=True, help="dotenv file with CANVAS_TOKEN")
    p.add_argument("--course", default="cis53")
    p.add_argument("--apply", action="store_true", help="write files (default: dry-run)")
    args = p.parse_args()

    env = dotenv_values(Path(args.canvas_env).expanduser())
    if not env.get("CANVAS_TOKEN"):
        sys.exit("ERROR: CANVAS_TOKEN not found in --canvas-env file")
    base = (env.get("CANVAS_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    course_id = env.get("CANVAS_COURSE_ID") or DEFAULT_COURSE_ID
    out_dir = Path(__file__).parent.parent / "content" / args.course / "case_studies"

    for number, (assignment_id, slug) in sorted(CASE_STUDIES.items()):
        resp = requests.get(
            f"{base}/api/v1/courses/{course_id}/assignments/{assignment_id}",
            headers={"Authorization": f"Bearer {env['CANVAS_TOKEN']}"},
            timeout=30,
        )
        resp.raise_for_status()
        canvas_url = f"{base}/courses/{course_id}/assignments/{assignment_id}"
        text = render(number, resp.json(), canvas_url)
        path = out_dir / file_name(number, slug)
        print(f"{'write' if args.apply else 'would write'} {path.name} ({len(text)} chars)")
        if args.apply:
            out_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
