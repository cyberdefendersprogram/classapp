#!/usr/bin/env python3
"""
Sync each student's Canvas grades into the Roster sheet (read-only against Canvas).

Writes these Roster columns (created at the end of the header row if missing):
    grade_lab1..grade_lab5, grade_quiz1..grade_quiz5   "score/max", e.g. "92/100"
    grade_total      Canvas course total, percent (e.g. 91.22)
    grade_letter     Canvas letter grade
    grades_synced_at ISO timestamp (UTC)

Students are matched by Canvas ``sis_user_id`` == Roster ``student_id``. Only
those columns are touched, and only cells for matched students; values are
written RAW (same approach as app/services/sheets.py). The app's /grades page
shows each student only their own row. Canvas stays the official gradebook.

Dry-run by default — nothing is written unless --apply is passed.

Usage:
    python scripts/sync_canvas_grades.py \\
        --canvas-env ../canvasgrader/.env \\
        --sheet-id <GOOGLE_SHEET_ID> --service-account /path/to/sa.json          # dry-run
    python scripts/sync_canvas_grades.py ... --apply                              # write

--canvas-env points at a dotenv file containing CANVAS_TOKEN (and optionally
CANVAS_BASE_URL / CANVAS_COURSE_ID). The token is never printed.
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

# Canvas assignment id -> Roster column
ASSIGNMENT_COLUMNS = {
    1757696: "grade_lab1",
    1757697: "grade_lab2",
    1757698: "grade_lab3",
    1757699: "grade_lab4",
    1757700: "grade_lab5",
    1757701: "grade_quiz1",
    1757702: "grade_quiz2",
    1757703: "grade_quiz3",
    1757704: "grade_quiz4",
    1757705: "grade_quiz5",
}
EXTRA_COLUMNS = ["grade_total", "grade_letter", "grades_synced_at"]
ALL_COLUMNS = list(ASSIGNMENT_COLUMNS.values()) + EXTRA_COLUMNS


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


def fetch_canvas_grades(canvas: Canvas) -> dict[str, dict[str, str]]:
    """Return {sis_user_id: {column: value}} for every student enrollment."""
    users = {
        u["id"]: str(u.get("sis_user_id") or "")
        for u in canvas.get(f"/courses/{canvas.course}/users", enrollment_type=["student"])
    }
    result: dict[str, dict[str, str]] = {sis: {} for sis in users.values() if sis}

    for e in canvas.get(f"/courses/{canvas.course}/enrollments", type=["StudentEnrollment"]):
        sis = users.get(e["user_id"], "")
        if not sis:
            continue
        grades = e.get("grades", {})
        if grades.get("current_score") is not None:
            result[sis]["grade_total"] = f"{grades['current_score']:.2f}"
        if grades.get("current_grade"):
            result[sis]["grade_letter"] = grades["current_grade"]

    for assignment_id, column in ASSIGNMENT_COLUMNS.items():
        assignment = canvas.get(f"/courses/{canvas.course}/assignments/{assignment_id}")
        max_points = assignment["points_possible"]
        for s in canvas.get(f"/courses/{canvas.course}/assignments/{assignment_id}/submissions"):
            sis = users.get(s["user_id"], "")
            if sis and s.get("score") is not None:
                result[sis][column] = f"{s['score']:g}/{max_points:g}"
    return result


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--canvas-env", required=True, help="dotenv file with CANVAS_TOKEN")
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
        cenv.get("CANVAS_COURSE_ID") or "92216",
    )
    grades = fetch_canvas_grades(canvas)
    print(f"Canvas: {len(grades)} students with a SIS id")

    creds = Credentials.from_service_account_file(args.service_account, scopes=SCOPES)
    ss = gspread.authorize(creds).open_by_key(args.sheet_id)
    ws = ss.worksheet("Roster")
    print(f"Sheet: {ss.title} / Roster")

    headers = ws.row_values(1)
    missing = [c for c in ALL_COLUMNS if c not in headers]
    if missing:
        print(f"{'Would add' if not args.apply else 'Adding'} columns: {missing}")
        if args.apply:
            if len(headers) + len(missing) > ws.col_count:
                ws.add_cols(len(headers) + len(missing) - ws.col_count)
            ws.update(
                range_name=gspread.utils.rowcol_to_a1(1, len(headers) + 1),
                values=[missing],
                raw=True,
            )
        headers = headers + missing

    records = ws.get_all_records()
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates, matched = [], set()
    for idx, rec in enumerate(records):
        sid = str(rec.get("student_id", "")).strip()
        if not sid:
            continue
        if sid not in grades:
            print(f"  (no Canvas match for roster student_id {sid} — left untouched)")
            continue
        matched.add(sid)
        values = dict(grades[sid], grades_synced_at=now)
        for col in ALL_COLUMNS:
            new = values.get(col, "")
            if new == "" and not str(rec.get(col, "")).strip():
                continue
            updates.append(
                {
                    "range": gspread.utils.rowcol_to_a1(idx + 2, headers.index(col) + 1),
                    "values": [[new]],
                }
            )
    unmatched = sorted(set(grades) - matched)
    if unmatched:
        print(f"Canvas students not on the Roster (ignored): {unmatched}")
    print(f"Matched {len(matched)} roster students; {len(updates)} cell updates")

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply to write.")
        for sid in sorted(matched)[:3]:
            print(f"  sample {sid}: {grades[sid]}")
        return
    if updates:
        ws.batch_update(updates, value_input_option="RAW")
    print("\nDone — grades written to the Roster sheet.")


if __name__ == "__main__":
    main()
