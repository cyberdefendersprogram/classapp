#!/usr/bin/env python3
"""
Snapshot every student's Canvas submission status into the "Canvas_Progress" sheet tab
(read-only against Canvas). The admin page /admin/progress reads that tab.

One row per student per assignment, written RAW. The tab is cleared and rewritten
each run, so it is always a single consistent snapshot. Nothing else in the sheet is touched.

Columns:
    canvas_user_id, name, email, last_activity_at, assignment_id, assignment, due_at,
    points_possible, status, score, late, submitted_at, synced_at

status: excused | graded | submitted | missing (past due, nothing turned in) |
        upcoming (not due yet, nothing turned in)

Only published assignments that take a submission are included (attendance and other
no-submission items are skipped). Students are all active student enrollments.

Dry-run by default; nothing is written unless --apply is passed.

Usage:
    python scripts/sync_canvas_progress.py \\
        --canvas-env ../canvasgrader/.env --course-id 89432 \\
        --sheet-id <GOOGLE_SHEET_ID> --service-account .secrets/service-account.json          # dry-run
    python scripts/sync_canvas_progress.py ... --apply                                       # write

--canvas-env points at a dotenv file containing CANVAS_TOKEN (and optionally
CANVAS_BASE_URL). The token is never printed.
"""

import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import gspread
import requests
from dotenv import dotenv_values, load_dotenv
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TAB = "Canvas_Progress"
HEADERS = [
    "canvas_user_id",
    "name",
    "email",
    "last_activity_at",
    "assignment_id",
    "assignment",
    "due_at",
    "points_possible",
    "status",
    "score",
    "late",
    "submitted_at",
    "synced_at",
]


class Canvas:
    def __init__(self, base_url: str, token: str, course_id: str):
        self.base = base_url.rstrip("/") + "/api/v1"
        self.course = course_id
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str, **params):
        url, out = f"{self.base}{path}", []
        params = dict(params, per_page=100)
        while url:
            r = self.session.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list):
                return data
            out.extend(data)
            url, params = r.links.get("next", {}).get("url"), None
        return out


def submission_status(sub: dict | None, due_at: str | None, now: datetime) -> str:
    """Classify one Canvas submission as excused, graded, submitted, missing or upcoming."""
    sub = sub or {}
    if sub.get("excused"):
        return "excused"
    state = sub.get("workflow_state")
    if state == "graded" and sub.get("score") is not None:
        return "graded"
    if state in ("submitted", "pending_review", "graded") or sub.get("submitted_at"):
        return "submitted"
    if due_at and datetime.fromisoformat(due_at.replace("Z", "+00:00")) < now:
        return "missing"
    return "upcoming"


def build_rows(canvas: Canvas, now: datetime) -> list[list]:
    users = canvas.get(
        f"/courses/{canvas.course}/users",
        enrollment_type=["student"],
        include=["email", "enrollments"],
    )
    assignments = [
        a
        for a in canvas.get(f"/courses/{canvas.course}/assignments")
        if a.get("published") and a.get("submission_types") and a["submission_types"][0] != "none"
    ]
    assignments.sort(key=lambda a: (a.get("due_at") or "9999", a["id"]))
    subs = canvas.get(f"/courses/{canvas.course}/students/submissions", student_ids=["all"])
    by_key = {(s["user_id"], s["assignment_id"]): s for s in subs}
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    rows = []
    for u in sorted(users, key=lambda u: (u.get("sortable_name") or u["name"]).lower()):
        enrollment = (u.get("enrollments") or [{}])[0]
        email = u.get("email") or u.get("login_id") or ""
        for a in assignments:
            s = by_key.get((u["id"], a["id"]))
            status = submission_status(s, a.get("due_at"), now)
            rows.append(
                [
                    u["id"],
                    u["name"],
                    email,
                    enrollment.get("last_activity_at") or "",
                    a["id"],
                    a["name"].strip(),
                    a.get("due_at") or "",
                    a.get("points_possible") if a.get("points_possible") is not None else "",
                    status,
                    "" if not s or s.get("score") is None else s["score"],
                    1 if s and s.get("late") else 0,
                    (s or {}).get("submitted_at") or "",
                    stamp,
                ]
            )
    return rows


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--canvas-env", required=True, help="dotenv file with CANVAS_TOKEN")
    p.add_argument("--course-id", required=True)
    p.add_argument("--sheet-id", default=os.environ.get("GOOGLE_SHEETS_ID", ""))
    p.add_argument("--service-account", default=os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH", ""))
    p.add_argument("--apply", action="store_true", help="write to the sheet (default: dry-run)")
    args = p.parse_args()

    cenv = dotenv_values(args.canvas_env)
    if not cenv.get("CANVAS_TOKEN"):
        sys.exit("ERROR: CANVAS_TOKEN not found in --canvas-env file")
    if not args.sheet_id or not args.service_account:
        sys.exit("ERROR: need --sheet-id and --service-account (or the env vars)")

    canvas = Canvas(
        cenv.get("CANVAS_BASE_URL") or "https://peralta.instructure.com",
        cenv["CANVAS_TOKEN"],
        args.course_id,
    )
    rows = build_rows(canvas, datetime.now(UTC))
    students = {r[0] for r in rows}
    assignments = {r[4] for r in rows}
    print(f"Canvas: {len(students)} students x {len(assignments)} assignments = {len(rows)} rows")

    creds = Credentials.from_service_account_file(args.service_account, scopes=SCOPES)
    ss = gspread.authorize(creds).open_by_key(args.sheet_id)
    print(f"Sheet: {ss.title} / {TAB}")
    if not args.apply:
        print("Dry-run: nothing written. Pass --apply to write.")
        return

    try:
        ws = ss.worksheet(TAB)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(TAB, rows=len(rows) + 10, cols=len(HEADERS))
    ws.clear()
    ws.resize(rows=len(rows) + 1, cols=len(HEADERS))
    ws.update(values=[HEADERS] + rows, range_name="A1", value_input_option="RAW")
    print(f"Wrote {len(rows)} rows to {TAB}.")


if __name__ == "__main__":
    main()
