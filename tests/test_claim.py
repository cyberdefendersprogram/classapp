"""Tests for claim routes."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.db.sqlite import init_db
from app.models.roster import RosterEntry


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    """Initialize database before each test."""
    init_db()


@pytest.fixture
def unclaimed_entry():
    """An unclaimed roster entry fixture."""
    return RosterEntry(
        student_id="stu_001",
        full_name="Student, Test",
        preferred_email=None,  # Not claimed
        claimed_at=None,
    )


@pytest.fixture
def claimed_entry():
    """An already claimed roster entry fixture."""
    return RosterEntry(
        student_id="stu_002",
        full_name="Student, Claimed",
        preferred_email="claimed@example.com",
        claimed_at=datetime(2024, 1, 1),
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


class TestClaimSubmit:
    """Tests for claim submission."""

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_success(self, mock_sheets, client, unclaimed_entry):
        """Successful claim redirects to onboarding."""
        sheets = MagicMock()
        sheets.get_roster_by_id.return_value = unclaimed_entry
        sheets.claim_student.return_value = True
        sheets.update_roster.return_value = True
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_001",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/onboarding" in response.headers["location"]
        assert "session" in response.cookies
        sheets.claim_student.assert_called_once_with("stu_001", "new@example.com")

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_student_not_found(self, mock_sheets, client):
        """Non-existent student shows error."""
        sheets = MagicMock()
        sheets.get_roster_by_id.return_value = None
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_999",
            },
        )

        assert response.status_code == 200
        assert "invalid" in response.text.lower() or "not found" in response.text.lower()

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_already_claimed(self, mock_sheets, client, claimed_entry):
        """Already claimed student shows error."""
        sheets = MagicMock()
        sheets.get_roster_by_id.return_value = claimed_entry
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "another@example.com",
                "student_id": "stu_002",
            },
        )

        assert response.status_code == 200
        assert "already" in response.text.lower()

    @patch("app.routers.claim.get_sheets_client")
    def test_claim_failure_shows_error(self, mock_sheets, client, unclaimed_entry):
        """Claim failure shows error message."""
        sheets = MagicMock()
        sheets.get_roster_by_id.return_value = unclaimed_entry
        sheets.claim_student.return_value = False  # Claim fails
        mock_sheets.return_value = sheets

        response = client.post(
            "/claim",
            data={
                "email": "new@example.com",
                "student_id": "stu_001",
            },
        )

        assert response.status_code == 200
        assert "error" in response.text.lower()
