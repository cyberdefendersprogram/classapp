"""Tests for claim routes."""

from unittest.mock import MagicMock, patch

import pytest

from app.db.sqlite import init_db
from app.models.student import Student


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    """Initialize database before each test."""
    init_db()


@pytest.fixture
def unclaimed_student():
    """An unclaimed student fixture."""
    return Student(
        student_id="stu_001",
        first_name="Test",
        last_name="Student",
        claim_code="ABC123",
        email="",  # Not claimed
        status="active",
        claimed_at=None,
        onboarded_at=None,
    )


@pytest.fixture
def claimed_student():
    """An already claimed student fixture."""
    return Student(
        student_id="stu_002",
        first_name="Claimed",
        last_name="Student",
        claim_code="DEF456",
        email="claimed@example.com",
        status="active",
        claimed_at="2024-01-01T00:00:00",
        onboarded_at=None,
    )


class TestClaimForm:
    """Tests for claim form page."""

    def test_claim_form_with_invalid_token(self, client):
        """Invalid token shows error."""
        response = client.get("/claim?token=invalid-token")
        assert response.status_code == 200
        assert "invalid" in response.text.lower() or "expired" in response.text.lower()

    @patch("app.routers.claim.validate_magic_token")
    def test_claim_form_with_valid_token(self, mock_validate, client):
        """Valid token shows claim form."""
        mock_validate.return_value = "new@example.com"

        response = client.get("/claim?token=valid-token")

        assert response.status_code == 200
        assert "new@example.com" in response.text
        assert "student_id" in response.text.lower()
        assert "claim_code" in response.text.lower()


class TestClaimSubmit:
    """Tests for claim submission."""

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_success(self, mock_sheets, client, unclaimed_student):
        """Successful claim redirects to onboarding."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = unclaimed_student
        sheets.claim_student.return_value = True
        sheets.update_student.return_value = True
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_001",
                "claim_code": "ABC123",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/onboarding" in response.headers["location"]
        assert "session" in response.cookies
        sheets.claim_student.assert_called_once_with("stu_001", "ABC123", "new@example.com")

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_student_not_found(self, mock_sheets, client):
        """Non-existent student shows error."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = None
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_999",
                "claim_code": "ABC123",
            },
        )

        assert response.status_code == 200
        assert "invalid" in response.text.lower()

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_wrong_code(self, mock_sheets, client, unclaimed_student):
        """Wrong claim code shows error."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = unclaimed_student
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_001",
                "claim_code": "WRONG",
            },
        )

        assert response.status_code == 200
        assert "invalid" in response.text.lower()

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_already_claimed(self, mock_sheets, client, claimed_student):
        """Already claimed student shows error."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = claimed_student
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "another@example.com",
                "student_id": "stu_002",
                "claim_code": "DEF456",
            },
        )

        assert response.status_code == 200
        assert "already been claimed" in response.text.lower()

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_inactive_student(self, mock_sheets, client):
        """Inactive student shows error."""
        inactive_student = Student(
            student_id="stu_003",
            first_name="Inactive",
            last_name="Student",
            claim_code="GHI789",
            email="",
            status="inactive",
            claimed_at=None,
            onboarded_at=None,
        )
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = inactive_student
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_003",
                "claim_code": "GHI789",
            },
        )

        assert response.status_code == 200
        assert "not active" in response.text.lower()

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_code_case_insensitive(self, mock_sheets, client, unclaimed_student):
        """Claim code is case-insensitive."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = unclaimed_student
        sheets.claim_student.return_value = True
        sheets.update_student.return_value = True
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_001",
                "claim_code": "abc123",  # lowercase
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/onboarding" in response.headers["location"]

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_failure_shows_error(self, mock_sheets, client, unclaimed_student):
        """Claim failure shows error message."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = unclaimed_student
        sheets.claim_student.return_value = False  # Claim fails
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_001",
                "claim_code": "ABC123",
            },
        )

        assert response.status_code == 200
        assert "error" in response.text.lower()
