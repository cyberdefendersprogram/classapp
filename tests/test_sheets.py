"""Tests for the sheets service with mocked gspread."""

from unittest.mock import MagicMock, patch

import pytest

from app.models.roster import RosterEntry
from app.models.quiz import QuizMeta
from app.services.cache import invalidate_all


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    invalidate_all()
    yield
    invalidate_all()


@pytest.fixture
def mock_worksheet():
    """Create a mock worksheet."""
    worksheet = MagicMock()
    return worksheet


@pytest.fixture
def mock_spreadsheet(mock_worksheet):
    """Create a mock spreadsheet."""
    spreadsheet = MagicMock()
    spreadsheet.worksheet.return_value = mock_worksheet
    return spreadsheet


@pytest.fixture
def mock_gspread(mock_spreadsheet):
    """Mock gspread authorize and open_by_key."""
    with patch("app.services.sheets.gspread") as mock_gs:
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_gs.authorize.return_value = mock_client
        yield mock_gs


@pytest.fixture
def mock_credentials():
    """Mock Google credentials."""
    with patch("app.services.sheets.Credentials") as mock_creds:
        mock_creds.from_service_account_file.return_value = MagicMock()
        yield mock_creds


@pytest.fixture
def mock_sa_file(tmp_path, monkeypatch):
    """Create a mock service account file."""
    sa_file = tmp_path / "service-account.json"
    sa_file.write_text('{"type": "service_account"}')
    monkeypatch.setattr("app.services.sheets.settings.google_service_account_path", str(sa_file))
    monkeypatch.setattr("app.services.sheets.settings.google_sheets_id", "test-sheet-id")
    return sa_file


@pytest.fixture
def sheets_client(mock_gspread, mock_credentials, mock_sa_file):
    """Create a SheetsClient with mocked dependencies."""
    # Reset the singleton
    import app.services.sheets as sheets_module
    sheets_module._sheets_client = None

    from app.services.sheets import SheetsClient
    return SheetsClient()


class TestSheetsClientConnection:
    """Tests for sheets client connection."""

    def test_check_connection_success(self, sheets_client, mock_spreadsheet):
        """Test successful connection check."""
        mock_spreadsheet.worksheet.return_value = MagicMock()

        result = sheets_client.check_connection()

        assert result is True
        mock_spreadsheet.worksheet.assert_called_with("Config")

    def test_check_connection_failure(self, sheets_client, mock_spreadsheet):
        """Test connection check failure."""
        mock_spreadsheet.worksheet.side_effect = Exception("Connection failed")

        result = sheets_client.check_connection()

        assert result is False


class TestSheetsClientConfig:
    """Tests for config methods."""

    def test_get_config(self, sheets_client, mock_worksheet):
        """Test getting a config value."""
        mock_worksheet.get_all_records.return_value = [
            {"key": "course_title", "value": "Security 101"},
            {"key": "term", "value": "Spring 2025"},
        ]

        result = sheets_client.get_config("course_title")

        assert result == "Security 101"

    def test_get_config_not_found(self, sheets_client, mock_worksheet):
        """Test getting a non-existent config value."""
        mock_worksheet.get_all_records.return_value = [
            {"key": "course_title", "value": "Security 101"},
        ]

        result = sheets_client.get_config("nonexistent")

        assert result is None

    def test_get_all_config(self, sheets_client, mock_worksheet):
        """Test getting all config values."""
        mock_worksheet.get_all_records.return_value = [
            {"key": "course_title", "value": "Security 101"},
            {"key": "term", "value": "Spring 2025"},
        ]

        result = sheets_client.get_all_config()

        assert result == {
            "course_title": "Security 101",
            "term": "Spring 2025",
        }


class TestSheetsClientRoster:
    """Tests for roster methods."""

    def test_get_student_by_email(self, sheets_client, mock_worksheet):
        """Test getting a roster entry by email."""
        mock_worksheet.get_all_records.return_value = [
            {
                "student_id": "stu_001",
                "full_name": "Smith, Alice",
                "preferred_email": "alice@example.com",
                "claimed_at": "2025-01-01T10:00:00",
            },
        ]

        result = sheets_client.get_student_by_email("alice@example.com")

        assert result is not None
        assert isinstance(result, RosterEntry)
        assert result.student_id == "stu_001"
        assert result.preferred_email == "alice@example.com"

    def test_get_student_by_email_not_found(self, sheets_client, mock_worksheet):
        """Test getting a non-existent roster entry."""
        mock_worksheet.get_all_records.return_value = []

        result = sheets_client.get_student_by_email("unknown@example.com")

        assert result is None

    def test_get_student_by_email_case_insensitive(self, sheets_client, mock_worksheet):
        """Test that email lookup is case-insensitive."""
        mock_worksheet.get_all_records.return_value = [
            {
                "student_id": "stu_001",
                "full_name": "Smith, Alice",
                "preferred_email": "Alice@Example.com",
            },
        ]

        result = sheets_client.get_student_by_email("alice@example.com")

        assert result is not None
        assert result.student_id == "stu_001"

    def test_get_roster_by_id(self, sheets_client, mock_worksheet):
        """Test getting a roster entry by ID."""
        mock_worksheet.get_all_records.return_value = [
            {
                "student_id": "stu_001",
                "full_name": "Smith, Alice",
                "preferred_email": "",
            },
        ]

        result = sheets_client.get_roster_by_id("stu_001")

        assert result is not None
        assert result.student_id == "stu_001"

    def test_claim_student_success(self, sheets_client, mock_worksheet):
        """Test successful student claim (no claim code needed)."""
        mock_worksheet.get_all_records.return_value = [
            {
                "student_id": "stu_001",
                "full_name": "Smith, Alice",
                "preferred_email": "",  # Not yet claimed
            },
        ]
        mock_worksheet.row_values.return_value = [
            "student_id", "full_name", "preferred_email", "claimed_at",
        ]

        result = sheets_client.claim_student("stu_001", "alice@example.com")

        assert result is True
        assert mock_worksheet.update_cell.call_count == 2  # email + claimed_at

    def test_claim_student_already_claimed(self, sheets_client, mock_worksheet):
        """Test claim on already claimed student."""
        mock_worksheet.get_all_records.return_value = [
            {
                "student_id": "stu_001",
                "full_name": "Smith, Alice",
                "preferred_email": "existing@example.com",  # Already claimed
            },
        ]

        result = sheets_client.claim_student("stu_001", "alice@example.com")

        assert result is False


class TestSheetsClientQuizzes:
    """Tests for quiz methods."""

    def test_get_quizzes(self, sheets_client, mock_worksheet):
        """Test getting all quizzes."""
        mock_worksheet.get_all_records.return_value = [
            {
                "quiz_id": "q001",
                "title": "Intro Quiz",
                "content_path": "content/quizzes/001-intro.md",
                "status": "published",
                "attempts_allowed": "2",
                "total_points": "10",
            },
        ]

        result = sheets_client.get_quizzes()

        assert len(result) == 1
        assert isinstance(result[0], QuizMeta)
        assert result[0].quiz_id == "q001"

    def test_get_quiz_by_id(self, sheets_client, mock_worksheet):
        """Test getting quiz by ID."""
        mock_worksheet.get_all_records.return_value = [
            {
                "quiz_id": "q001",
                "title": "Intro Quiz",
                "content_path": "content/quizzes/001-intro.md",
                "status": "published",
            },
            {
                "quiz_id": "q002",
                "title": "Advanced Quiz",
                "content_path": "content/quizzes/002-advanced.md",
                "status": "draft",
            },
        ]

        result = sheets_client.get_quiz_by_id("q002")

        assert result is not None
        assert result.quiz_id == "q002"
        assert result.title == "Advanced Quiz"

    def test_append_quiz_submission(self, sheets_client, mock_worksheet):
        """Test appending a quiz submission."""
        mock_worksheet.row_values.return_value = [
            "submitted_at", "quiz_id", "attempt", "student_id", "email",
            "answers_json", "score", "max_score", "autograde_json", "source",
        ]

        data = {
            "submitted_at": "2025-01-01T10:00:00",
            "quiz_id": "q001",
            "attempt": 1,
            "student_id": "stu_001",
            "email": "alice@example.com",
            "answers_json": "{}",
            "score": 8,
            "max_score": 10,
            "autograde_json": "{}",
            "source": "web",
        }

        result = sheets_client.append_quiz_submission(data)

        assert result is True
        mock_worksheet.append_row.assert_called_once()
