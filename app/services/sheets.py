"""Google Sheets client for data access."""

import logging
from datetime import datetime
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from app.config import settings
from app.models.quiz import QuizMeta, QuizSubmission
from app.models.roster import RosterEntry
from app.models.schedule import ScheduleEntry
from app.services.cache import cached, invalidate

logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# Cache TTLs (in seconds)
CACHE_TTL_CONFIG = 300  # 5 minutes
CACHE_TTL_ROSTER = 120  # 2 minutes
CACHE_TTL_QUIZZES = 300  # 5 minutes
CACHE_TTL_SCHEDULE = 300  # 5 minutes
CACHE_TTL_SUBMISSIONS = 120  # 2 minutes


class SheetsClient:
    """Client for interacting with Google Sheets."""

    def __init__(self):
        self._client: gspread.Client | None = None
        self._spreadsheet: gspread.Spreadsheet | None = None

    def _get_client(self) -> gspread.Client:
        """Get or create gspread client."""
        if self._client is None:
            sa_path = Path(settings.google_service_account_path)
            if not sa_path.exists():
                raise FileNotFoundError(f"Service account file not found: {sa_path}")

            creds = Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
            self._client = gspread.authorize(creds)
            logger.info("Google Sheets client initialized")

        return self._client

    def _get_spreadsheet(self) -> gspread.Spreadsheet:
        """Get or open the spreadsheet."""
        if self._spreadsheet is None:
            client = self._get_client()
            self._spreadsheet = client.open_by_key(settings.google_sheets_id)
            logger.info("Opened spreadsheet: %s", self._spreadsheet.title)

        return self._spreadsheet

    def _get_worksheet(self, name: str) -> gspread.Worksheet:
        """Get worksheet by name."""
        spreadsheet = self._get_spreadsheet()
        return spreadsheet.worksheet(name)

    def check_connection(self) -> bool:
        """Check if Sheets connection is working."""
        try:
            if not settings.google_sheets_id or not settings.google_service_account_path:
                return False

            sa_path = Path(settings.google_service_account_path)
            if not sa_path.exists():
                return False

            # Try to access the spreadsheet
            spreadsheet = self._get_spreadsheet()
            # Try to read Config sheet to verify access
            spreadsheet.worksheet("Config")
            return True
        except Exception as e:
            logger.warning("Sheets connection check failed: %s", e)
            return False

    # -------------------------------------------------------------------------
    # Config methods
    # -------------------------------------------------------------------------

    @cached(ttl_seconds=CACHE_TTL_CONFIG, prefix="config")
    def get_config(self, key: str) -> str | None:
        """Get a config value by key."""
        try:
            worksheet = self._get_worksheet("Config")
            records = worksheet.get_all_records()

            for record in records:
                if record.get("key") == key:
                    return str(record.get("value", ""))

            return None
        except Exception as e:
            logger.error("Failed to get config '%s': %s", key, e)
            return None

    @cached(ttl_seconds=CACHE_TTL_CONFIG, prefix="config")
    def get_all_config(self) -> dict[str, str]:
        """Get all config values as a dictionary."""
        try:
            worksheet = self._get_worksheet("Config")
            records = worksheet.get_all_records()

            return {str(r.get("key", "")): str(r.get("value", "")) for r in records if r.get("key")}
        except Exception as e:
            logger.error("Failed to get all config: %s", e)
            return {}

    # -------------------------------------------------------------------------
    # Roster methods
    # -------------------------------------------------------------------------

    @cached(ttl_seconds=CACHE_TTL_ROSTER, prefix="roster")
    def get_roster_by_email(self, email: str) -> RosterEntry | None:
        """Get roster entry by email address."""
        try:
            worksheet = self._get_worksheet("Roster")
            records = worksheet.get_all_records()

            for record in records:
                if record.get("preferred_email", "").lower() == email.lower():
                    return RosterEntry.from_row(record)

            return None
        except Exception as e:
            logger.error("Failed to get roster by email '%s': %s", email, e)
            return None

    @cached(ttl_seconds=CACHE_TTL_ROSTER, prefix="roster")
    def get_roster_by_id(self, student_id: str) -> RosterEntry | None:
        """Get roster entry by student_id."""
        try:
            worksheet = self._get_worksheet("Roster")
            records = worksheet.get_all_records()

            for record in records:
                if str(record.get("student_id")) == str(student_id):
                    return RosterEntry.from_row(record)

            return None
        except Exception as e:
            logger.error("Failed to get roster by id '%s': %s", student_id, e)
            return None

    def claim_student(self, student_id: str, email: str) -> bool:
        """
        Claim a student account by binding email to student_id.

        Returns True if successful, False otherwise.
        """
        try:
            worksheet = self._get_worksheet("Roster")
            records = worksheet.get_all_records()

            # Find the student row
            for idx, record in enumerate(records):
                if str(record.get("student_id")) == str(student_id):
                    # Check not already claimed
                    if record.get("preferred_email"):
                        logger.warning("Student %s already claimed", student_id)
                        return False

                    # Update the row (row index is 2-based: 1 for header, 1 for 0-index)
                    row_num = idx + 2

                    # Find column indices
                    headers = worksheet.row_values(1)
                    email_col = headers.index("preferred_email") + 1
                    claimed_at_col = headers.index("claimed_at") + 1

                    # Update cells
                    now = datetime.utcnow().isoformat()
                    worksheet.update_cell(row_num, email_col, email)
                    worksheet.update_cell(row_num, claimed_at_col, now)

                    # Invalidate cache
                    invalidate("roster")

                    logger.info("Student %s claimed by %s", student_id, email)
                    return True

            logger.warning("Student not found: %s", student_id)
            return False

        except Exception as e:
            logger.error("Failed to claim student %s: %s", student_id, e)
            return False

    def update_roster(self, student_id: str, **fields) -> bool:
        """
        Update roster entry fields.

        Args:
            student_id: Student ID to update
            **fields: Fields to update (e.g., preferred_name="Alex")

        Returns True if successful.
        """
        try:
            worksheet = self._get_worksheet("Roster")
            records = worksheet.get_all_records()
            headers = worksheet.row_values(1)

            # Find the student row
            for idx, record in enumerate(records):
                if str(record.get("student_id")) == str(student_id):
                    row_num = idx + 2

                    # Update each field
                    for field_name, value in fields.items():
                        if field_name in headers:
                            col_num = headers.index(field_name) + 1
                            worksheet.update_cell(row_num, col_num, value if value else "")

                    # Invalidate cache
                    invalidate("roster")

                    logger.info("Updated roster %s: %s", student_id, list(fields.keys()))
                    return True

            logger.warning("Student not found for update: %s", student_id)
            return False

        except Exception as e:
            logger.error("Failed to update roster %s: %s", student_id, e)
            return False

    # -------------------------------------------------------------------------
    # Schedule methods
    # -------------------------------------------------------------------------

    @cached(ttl_seconds=CACHE_TTL_SCHEDULE, prefix="schedule")
    def get_schedule(self) -> list[ScheduleEntry]:
        """Get all schedule entries."""
        try:
            worksheet = self._get_worksheet("Schedule")
            records = worksheet.get_all_records()

            return [ScheduleEntry.from_row(r) for r in records if r.get("session")]
        except Exception as e:
            logger.error("Failed to get schedule: %s", e)
            return []

    # -------------------------------------------------------------------------
    # Quiz methods
    # -------------------------------------------------------------------------

    @cached(ttl_seconds=CACHE_TTL_QUIZZES, prefix="quizzes")
    def get_quizzes(self) -> list[QuizMeta]:
        """Get all quizzes metadata."""
        try:
            worksheet = self._get_worksheet("Quizzes")
            records = worksheet.get_all_records()

            return [QuizMeta.from_row(r) for r in records if r.get("quiz_id")]
        except Exception as e:
            logger.error("Failed to get quizzes: %s", e)
            return []

    @cached(ttl_seconds=CACHE_TTL_QUIZZES, prefix="quizzes")
    def get_quiz_by_id(self, quiz_id: str) -> QuizMeta | None:
        """Get quiz metadata by ID."""
        quizzes = self.get_quizzes()
        for quiz in quizzes:
            if quiz.quiz_id == quiz_id:
                return quiz
        return None

    @cached(ttl_seconds=CACHE_TTL_SUBMISSIONS, prefix="submissions")
    def get_quiz_submissions(self, student_id: str, quiz_id: str) -> list[QuizSubmission]:
        """Get all submissions for a student on a quiz."""
        try:
            worksheet = self._get_worksheet("Quiz_Submissions")
            records = worksheet.get_all_records()

            submissions = []
            for record in records:
                if str(record.get("student_id")) == str(student_id) and str(
                    record.get("quiz_id", "")
                ) == str(quiz_id):
                    submissions.append(QuizSubmission.from_row(record))

            return submissions
        except Exception as e:
            logger.error("Failed to get submissions for %s/%s: %s", student_id, quiz_id, e)
            return []

    @cached(ttl_seconds=CACHE_TTL_SUBMISSIONS, prefix="all_submissions")
    def get_all_quiz_submissions(self, quiz_id: str) -> list[QuizSubmission]:
        """Get ALL submissions for a quiz (all students)."""
        try:
            worksheet = self._get_worksheet("Quiz_Submissions")
            records = worksheet.get_all_records()

            submissions = []
            for record in records:
                if str(record.get("quiz_id", "")) == str(quiz_id):
                    submissions.append(QuizSubmission.from_row(record))

            return submissions
        except Exception as e:
            logger.error("Failed to get all submissions for quiz %s: %s", quiz_id, e)
            return []

    @cached(ttl_seconds=CACHE_TTL_ROSTER, prefix="roster_count")
    def get_roster_count(self) -> int:
        """Get total number of students in roster."""
        try:
            worksheet = self._get_worksheet("Roster")
            records = worksheet.get_all_records()

            # Count only rows with a student_id
            return sum(1 for r in records if r.get("student_id"))
        except Exception as e:
            logger.error("Failed to get roster count: %s", e)
            return 0

    @cached(ttl_seconds=CACHE_TTL_ROSTER, prefix="all_roster")
    def get_all_roster(self) -> list[RosterEntry]:
        """Get all roster entries."""
        try:
            worksheet = self._get_worksheet("Roster")
            records = worksheet.get_all_records()

            return [RosterEntry.from_row(r) for r in records if r.get("student_id")]
        except Exception as e:
            logger.error("Failed to get all roster: %s", e)
            return []

    def append_quiz_submission(self, data: dict) -> bool:
        """Append a new quiz submission."""
        try:
            worksheet = self._get_worksheet("Quiz_Submissions")
            headers = worksheet.row_values(1)

            # Build row in correct column order
            row = [data.get(h, "") for h in headers]
            worksheet.append_row(row, value_input_option="RAW")

            # Invalidate submissions cache
            invalidate("submissions")
            invalidate("all_submissions")

            logger.info(
                "Appended quiz submission: %s/%s", data.get("student_id"), data.get("quiz_id")
            )
            return True
        except Exception as e:
            logger.error("Failed to append quiz submission: %s", e)
            return False

    # -------------------------------------------------------------------------
    # Onboarding methods
    # -------------------------------------------------------------------------

    def append_onboarding_response(self, data: dict) -> bool:
        """Append a new onboarding response row."""
        try:
            worksheet = self._get_worksheet("Onboarding_Responses")
            headers = worksheet.row_values(1)

            row = [data.get(h, "") for h in headers]
            worksheet.append_row(row, value_input_option="RAW")

            logger.info("Appended onboarding response: %s", data.get("student_id"))
            return True
        except Exception as e:
            logger.error("Failed to append onboarding response: %s", e)
            return False

    # -------------------------------------------------------------------------
    # Magic Link audit methods
    # -------------------------------------------------------------------------

    def append_magic_link_request(self, data: dict) -> bool:
        """Append a magic link request to audit log."""
        try:
            worksheet = self._get_worksheet("MagicLink_Requests")
            headers = worksheet.row_values(1)

            row = [data.get(h, "") for h in headers]
            worksheet.append_row(row, value_input_option="RAW")

            return True
        except Exception as e:
            logger.error("Failed to append magic link request: %s", e)
            return False

    # -------------------------------------------------------------------------
    # Backward compatibility aliases
    # -------------------------------------------------------------------------

    def get_student_by_email(self, email: str) -> RosterEntry | None:
        """Alias for get_roster_by_email for backward compatibility."""
        return self.get_roster_by_email(email)

    def get_student_by_id(self, student_id: str) -> RosterEntry | None:
        """Alias for get_roster_by_id for backward compatibility."""
        return self.get_roster_by_id(student_id)

    def update_student(self, student_id: str, **fields) -> bool:
        """Alias for update_roster for backward compatibility."""
        return self.update_roster(student_id, **fields)


# Singleton instance
_sheets_client: SheetsClient | None = None


def get_sheets_client() -> SheetsClient:
    """Get the singleton SheetsClient instance."""
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = SheetsClient()
    return _sheets_client
