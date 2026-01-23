#!/usr/bin/env python3
"""
Seed Google Sheets with initial data structure and test data.

Usage:
    python scripts/seed_sheets.py --create-structure
    python scripts/seed_sheets.py --seed-test-data
    python scripts/seed_sheets.py --all

Requires:
    - GOOGLE_SHEETS_ID environment variable
    - GOOGLE_SERVICE_ACCOUNT_PATH environment variable
"""

import argparse
import os
import secrets
import string
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Sheet structures: name -> headers
SHEET_STRUCTURES = {
    "Students": [
        "student_id",
        "first_name",
        "last_name",
        "claim_code",
        "email",
        "status",
        "claimed_at",
        "first_seen_at",
        "onboarded_at",
        "last_login_at",
        "preferred_name",
        "pronouns",
        "notes",
    ],
    "Onboarding_Responses": [
        "timestamp",
        "student_id",
        "email",
        "form_version",
        "question_key",
        "question_label",
        "answer",
        "answer_type",
        "source",
    ],
    "MagicLink_Requests": [
        "requested_at",
        "email",
        "result",
        "note",
    ],
    "Quizzes": [
        "quiz_id",
        "title",
        "content_path",
        "open_at",
        "close_at",
        "attempts_allowed",
        "status",
        "total_points",
    ],
    "Quiz_Submissions": [
        "submitted_at",
        "quiz_id",
        "attempt",
        "student_id",
        "email",
        "answers_json",
        "score",
        "max_score",
        "autograde_json",
        "source",
    ],
    "Config": [
        "key",
        "value",
    ],
}

# Default config values
DEFAULT_CONFIG = {
    "course_title": "Security 101",
    "term": "Spring 2025",
    "magic_link_ttl_minutes": "15",
    "rate_limit_per_email_15m": "3",
    "onboarding_form_version": "v1",
}

# Test students data
TEST_STUDENTS = [
    {"student_id": "stu_001", "first_name": "Alice", "last_name": "Smith", "status": "active"},
    {"student_id": "stu_002", "first_name": "Bob", "last_name": "Johnson", "status": "active"},
    {"student_id": "stu_003", "first_name": "Charlie", "last_name": "Williams", "status": "active"},
    {"student_id": "stu_004", "first_name": "Diana", "last_name": "Brown", "status": "active"},
    {"student_id": "stu_005", "first_name": "Eve", "last_name": "Davis", "status": "active"},
]

# Test quiz data
TEST_QUIZZES = [
    {
        "quiz_id": "q001",
        "title": "Introduction Quiz",
        "content_path": "content/quizzes/001-intro.md",
        "open_at": "",
        "close_at": "",
        "attempts_allowed": "2",
        "status": "published",
        "total_points": "10",
    },
]


def generate_claim_code() -> str:
    """Generate a random 6-character claim code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(6))


def get_client() -> gspread.Client:
    """Get authenticated gspread client."""
    sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
    if not sa_path:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_PATH environment variable not set")

    creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet(client: gspread.Client) -> gspread.Spreadsheet:
    """Open the spreadsheet."""
    sheets_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not sheets_id:
        raise ValueError("GOOGLE_SHEETS_ID environment variable not set")

    return client.open_by_key(sheets_id)


def create_structure(spreadsheet: gspread.Spreadsheet) -> None:
    """Create all required worksheets with headers."""
    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]

    for sheet_name, headers in SHEET_STRUCTURES.items():
        if sheet_name in existing_sheets:
            print(f"  Sheet '{sheet_name}' already exists, skipping...")
            continue

        print(f"  Creating sheet '{sheet_name}'...")
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(headers))
        worksheet.update("A1", [headers])

        # Format header row (bold)
        worksheet.format("A1:Z1", {"textFormat": {"bold": True}})

    # Remove default Sheet1 if it exists and is empty
    try:
        sheet1 = spreadsheet.worksheet("Sheet1")
        if sheet1.get_all_values() == []:
            spreadsheet.del_worksheet(sheet1)
            print("  Removed empty 'Sheet1'")
    except gspread.WorksheetNotFound:
        pass

    print("Structure creation complete!")


def seed_config(spreadsheet: gspread.Spreadsheet) -> None:
    """Seed the Config sheet with default values."""
    print("  Seeding Config...")
    worksheet = spreadsheet.worksheet("Config")

    # Check if already has data
    existing = worksheet.get_all_records()
    existing_keys = {r.get("key") for r in existing}

    rows_to_add = []
    for key, value in DEFAULT_CONFIG.items():
        if key not in existing_keys:
            rows_to_add.append([key, value])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} config entries")
    else:
        print("    Config already seeded")


def seed_students(spreadsheet: gspread.Spreadsheet) -> None:
    """Seed the Students sheet with test data."""
    print("  Seeding Students...")
    worksheet = spreadsheet.worksheet("Students")

    # Check if already has data
    existing = worksheet.get_all_records()
    existing_ids = {r.get("student_id") for r in existing}

    headers = SHEET_STRUCTURES["Students"]
    rows_to_add = []

    for student in TEST_STUDENTS:
        if student["student_id"] in existing_ids:
            continue

        row_data = {h: "" for h in headers}
        row_data.update(student)
        row_data["claim_code"] = generate_claim_code()

        rows_to_add.append([row_data.get(h, "") for h in headers])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} students")
    else:
        print("    Students already seeded")


def seed_quizzes(spreadsheet: gspread.Spreadsheet) -> None:
    """Seed the Quizzes sheet with test data."""
    print("  Seeding Quizzes...")
    worksheet = spreadsheet.worksheet("Quizzes")

    # Check if already has data
    existing = worksheet.get_all_records()
    existing_ids = {r.get("quiz_id") for r in existing}

    headers = SHEET_STRUCTURES["Quizzes"]
    rows_to_add = []

    for quiz in TEST_QUIZZES:
        if quiz["quiz_id"] in existing_ids:
            continue

        rows_to_add.append([quiz.get(h, "") for h in headers])

    if rows_to_add:
        worksheet.append_rows(rows_to_add, value_input_option="RAW")
        print(f"    Added {len(rows_to_add)} quizzes")
    else:
        print("    Quizzes already seeded")


def main():
    parser = argparse.ArgumentParser(description="Seed Google Sheets with data")
    parser.add_argument("--create-structure", action="store_true", help="Create sheet structure")
    parser.add_argument("--seed-test-data", action="store_true", help="Seed test data")
    parser.add_argument("--all", action="store_true", help="Create structure and seed data")

    args = parser.parse_args()

    if not any([args.create_structure, args.seed_test_data, args.all]):
        parser.print_help()
        return

    print("Connecting to Google Sheets...")
    client = get_client()
    spreadsheet = get_spreadsheet(client)
    print(f"Opened: {spreadsheet.title}")

    if args.create_structure or args.all:
        print("\nCreating structure...")
        create_structure(spreadsheet)

    if args.seed_test_data or args.all:
        print("\nSeeding test data...")
        seed_config(spreadsheet)
        seed_students(spreadsheet)
        seed_quizzes(spreadsheet)

    print("\nDone!")


if __name__ == "__main__":
    main()
