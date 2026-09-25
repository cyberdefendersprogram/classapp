#!/usr/bin/env python3
"""
Safe, targeted admin operations against the Class Portal Data spreadsheet.

Unlike a full-file upload/overwrite, every operation here updates only the
specific cell(s) named — it looks up the target row by a key column (session
date, or quiz_id) and writes with value_input_option=RAW, the same approach
app/services/sheets.py uses, so Sheets never reinterprets/reformats a value.

Usage:
    # Update (or leave blank to skip) the Schedule row for a session date
    python scripts/sheets_admin.py schedule --session 09/25/2026 \\
        --desc-link content/cis52/notes/005-detect-the-attack.md \\
        --slides-link "https://docs.google.com/presentation/d/.../edit"

    # Add a new quiz row, or update fields on an existing quiz_id
    python scripts/sheets_admin.py quiz --quiz-id q005 \\
        --title "Detect the Attack" \\
        --content-path content/cis52/quizzes/005-detect-the-attack.md \\
        --attempts-allowed 2 --status published --total-points 10

Add --dry-run to preview without writing. Add --sheet-id / --service-account
to target a spreadsheet other than the one in GOOGLE_SHEETS_ID / .env (e.g.
the CIS 52 prod sheet vs. the dev sheet) — the .env's GOOGLE_SHEETS_ID
currently points at the *dev* sheet, not the shared production one.

Requires:
    GOOGLE_SHEETS_ID and GOOGLE_SERVICE_ACCOUNT_PATH in the environment or
    .env (loaded automatically), unless overridden with --sheet-id /
    --service-account.
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_client(service_account_path: str) -> gspread.Client:
    creds = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet(client: gspread.Client, sheet_id: str) -> gspread.Spreadsheet:
    return client.open_by_key(sheet_id)


def _find_row(
    worksheet: gspread.Worksheet, key_col_name: str, key_value: str
) -> tuple[int, dict, list[str]]:
    """Return (1-indexed row number, row dict, headers) for the first row where
    key_col_name == key_value, or (0, {}, headers) if not found."""
    headers = worksheet.row_values(1)
    records = worksheet.get_all_records()
    for i, row in enumerate(records, start=2):  # row 1 is the header
        if str(row.get(key_col_name, "")).strip() == key_value.strip():
            return i, row, headers
    return 0, {}, headers


def update_schedule(
    worksheet: gspread.Worksheet,
    session: str,
    desc_link: str | None,
    slides_link: str | None,
    recording_link: str | None,
    dry_run: bool,
) -> None:
    row_num, row, headers = _find_row(worksheet, "session", session)
    if row_num == 0:
        print(f"ERROR: no Schedule row found for session={session!r}")
        sys.exit(1)

    updates = {
        "desc_link": desc_link,
        "slides_link": slides_link,
        "recording_link": recording_link,
    }
    for col_name, new_value in updates.items():
        if new_value is None:
            continue
        if col_name not in headers:
            print(f"ERROR: column {col_name!r} not found in Schedule sheet")
            sys.exit(1)
        col_num = headers.index(col_name) + 1
        current = str(row.get(col_name, "")).strip()
        print(
            f"[{'dry-run' if dry_run else 'write'}] Schedule row {row_num} ({session}) {col_name}:"
        )
        print(f"    {current or '(empty)'!r} -> {new_value!r}")
        if not dry_run:
            worksheet.update(
                range_name=gspread.utils.rowcol_to_a1(row_num, col_num),
                values=[[new_value]],
                raw=True,
            )


def upsert_quiz(
    worksheet: gspread.Worksheet,
    quiz_id: str,
    title: str | None,
    content_path: str | None,
    open_at: str | None,
    close_at: str | None,
    attempts_allowed: str | None,
    status: str | None,
    total_points: str | None,
    dry_run: bool,
) -> None:
    headers = worksheet.row_values(1)
    row_num, row, _ = _find_row(worksheet, "quiz_id", quiz_id)

    fields = {
        "quiz_id": quiz_id,
        "title": title,
        "content_path": content_path,
        "open_at": open_at,
        "close_at": close_at,
        "attempts_allowed": attempts_allowed,
        "status": status,
        "total_points": total_points,
    }

    if row_num == 0:
        # New quiz — every field except quiz_id must be given, in header order.
        missing = [k for k in headers if fields.get(k) is None]
        if missing:
            print(
                f"ERROR: quiz_id={quiz_id!r} not found (new row) but missing values for: {missing}"
            )
            sys.exit(1)
        new_row = [str(fields[h]) for h in headers]
        print(
            f"[{'dry-run' if dry_run else 'write'}] Quizzes: append new row for {quiz_id}: {new_row}"
        )
        if not dry_run:
            worksheet.append_row(new_row, value_input_option="RAW")
        return

    # Existing quiz — update only the fields explicitly given.
    for col_name, new_value in fields.items():
        if new_value is None or col_name == "quiz_id":
            continue
        col_num = headers.index(col_name) + 1
        current = str(row.get(col_name, "")).strip()
        print(
            f"[{'dry-run' if dry_run else 'write'}] Quizzes row {row_num} ({quiz_id}) {col_name}:"
        )
        print(f"    {current or '(empty)'!r} -> {new_value!r}")
        if not dry_run:
            worksheet.update(
                range_name=gspread.utils.rowcol_to_a1(row_num, col_num),
                values=[[new_value]],
                raw=True,
            )


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--sheet-id", default=os.environ.get("GOOGLE_SHEETS_ID", ""))
    parser.add_argument(
        "--service-account", default=os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH", "")
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sched = sub.add_parser("schedule", help="Update a Schedule row's link columns")
    p_sched.add_argument(
        "--session", required=True, help="Session date exactly as it appears, e.g. 09/25/2026"
    )
    p_sched.add_argument("--desc-link", default=None)
    p_sched.add_argument("--slides-link", default=None)
    p_sched.add_argument("--recording-link", default=None)

    p_quiz = sub.add_parser("quiz", help="Add or update a row in the Quizzes sheet")
    p_quiz.add_argument("--quiz-id", required=True)
    p_quiz.add_argument("--title", default=None)
    p_quiz.add_argument("--content-path", default=None)
    p_quiz.add_argument("--open-at", default=None)
    p_quiz.add_argument("--close-at", default=None)
    p_quiz.add_argument("--attempts-allowed", default=None)
    p_quiz.add_argument("--status", default=None)
    p_quiz.add_argument("--total-points", default=None)

    args = parser.parse_args()

    if not args.sheet_id:
        print("ERROR: no sheet id — set GOOGLE_SHEETS_ID or pass --sheet-id")
        sys.exit(1)
    if not args.service_account:
        print(
            "ERROR: no service account path — set GOOGLE_SERVICE_ACCOUNT_PATH or pass --service-account"
        )
        sys.exit(1)

    client = get_client(args.service_account)
    spreadsheet = get_spreadsheet(client, args.sheet_id)
    print(f"Opened: {spreadsheet.title} ({args.sheet_id})")

    if args.command == "schedule":
        worksheet = spreadsheet.worksheet("Schedule")
        update_schedule(
            worksheet,
            session=args.session,
            desc_link=args.desc_link,
            slides_link=args.slides_link,
            recording_link=args.recording_link,
            dry_run=args.dry_run,
        )
    elif args.command == "quiz":
        worksheet = spreadsheet.worksheet("Quizzes")
        upsert_quiz(
            worksheet,
            quiz_id=args.quiz_id,
            title=args.title,
            content_path=args.content_path,
            open_at=args.open_at,
            close_at=args.close_at,
            attempts_allowed=args.attempts_allowed,
            status=args.status,
            total_points=args.total_points,
            dry_run=args.dry_run,
        )

    print("\nDone." + (" (dry-run — no changes written)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
