#!/usr/bin/env python3
"""
Update desc_link in the Schedule sheet to point to CIS 60 notes files.

Usage:
    python scripts/update_schedule_links.py [--dry-run]

Requires:
    - GOOGLE_SHEETS_ID environment variable (set to CIS 60 sheet)
    - GOOGLE_SERVICE_ACCOUNT_PATH environment variable
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Maps class number (extracted from desc) → notes file path
NOTES_LINKS = {
    "1": "content/cis60/notes/001-intro.md",
    "2": "content/cis60/notes/002-expert-witness.md",
    "5": "content/cis60/notes/005-mobile-social-cloud-ai.md",
}


def get_client() -> gspread.Client:
    sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
    if not sa_path:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_PATH not set")
    creds = Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet(client: gspread.Client) -> gspread.Spreadsheet:
    sheets_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not sheets_id:
        raise ValueError("GOOGLE_SHEETS_ID not set")
    return client.open_by_key(sheets_id)


def extract_class_number(desc: str) -> str | None:
    """Extract leading class number from desc like '1 - Introduction'."""
    import re

    match = re.match(r"^(\d+)\s*[-–—]\s*", desc.strip())
    return match.group(1) if match else None


def update_schedule_links(dry_run: bool = False) -> None:
    print("Connecting to Google Sheets...")
    client = get_client()
    spreadsheet = get_spreadsheet(client)
    print(f"Opened: {spreadsheet.title}")

    worksheet = spreadsheet.worksheet("Schedule")
    records = worksheet.get_all_records()
    headers = worksheet.row_values(1)

    if "desc_link" not in headers:
        print("ERROR: 'desc_link' column not found in Schedule sheet.")
        sys.exit(1)

    desc_link_col = headers.index("desc_link") + 1

    updated = 0
    skipped = 0

    for i, row in enumerate(records, start=2):  # row 1 is header
        desc = row.get("desc", "").strip()
        current_link = row.get("desc_link", "").strip()
        class_num = extract_class_number(desc)

        if class_num not in NOTES_LINKS:
            continue

        target_link = NOTES_LINKS[class_num]

        if current_link == target_link:
            print(f"  [skip]   Row {i}: '{desc}' already set to '{target_link}'")
            skipped += 1
            continue

        print(f"  [update] Row {i}: '{desc}'")
        print(f"           {current_link or '(empty)'!r} → {target_link!r}")

        if not dry_run:
            worksheet.update_cell(i, desc_link_col, target_link)
        updated += 1

    print(f"\nDone. {updated} updated, {skipped} already correct.")
    if dry_run:
        print("(dry-run — no changes written)")


def main():
    parser = argparse.ArgumentParser(description="Update Schedule desc_link for CIS 60 notes")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()
    update_schedule_links(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
