"""Tests for onboarding routes."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.db.sqlite import init_db
from app.models.roster import RosterEntry
from app.services.sessions import create_session_token


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    """Initialize database before each test."""
    init_db()


@pytest.fixture
def claimed_entry():
    """A roster entry who hasn't completed onboarding."""
    return RosterEntry(
        student_id="stu_001",
        full_name="Student, Test",
        preferred_email="test@example.com",
        claimed_at=datetime(2024, 1, 1),
        onboarding_completed_at=None,  # Not onboarded
    )


@pytest.fixture
def onboarded_entry():
    """A roster entry who has completed onboarding."""
    return RosterEntry(
        student_id="stu_002",
        full_name="Student, Onboarded",
        preferred_email="onboarded@example.com",
        claimed_at=datetime(2024, 1, 1),
        onboarding_completed_at=datetime(2024, 1, 2),
        preferred_name="Onby",
    )


@pytest.fixture
def auth_token(claimed_entry):
    """Create an auth token for the claimed entry."""
    return create_session_token(claimed_entry.preferred_email, claimed_entry.student_id)


@pytest.fixture
def onboarded_auth_token(onboarded_entry):
    """Create an auth token for the onboarded entry."""
    return create_session_token(onboarded_entry.preferred_email, onboarded_entry.student_id)


class TestOnboardingForm:
    """Tests for onboarding form page."""

    def test_onboarding_requires_auth(self, client):
        """Unauthenticated users get redirected to login."""
        response = client.get("/onboarding", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/"

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_form_renders(self, mock_sheets, client, auth_token, claimed_entry):
        """Authenticated user sees onboarding form."""
        mock_sheets.return_value.get_roster_by_id.return_value = claimed_entry

        response = client.get("/onboarding", cookies={"session": auth_token})

        assert response.status_code == 200
        assert "Welcome" in response.text

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_redirects_if_already_done(
        self, mock_sheets, client, onboarded_auth_token, onboarded_entry
    ):
        """Already onboarded users are redirected to home."""
        mock_sheets.return_value.get_roster_by_id.return_value = onboarded_entry

        response = client.get(
            "/onboarding",
            cookies={"session": onboarded_auth_token},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/home" in response.headers["location"]


class TestOnboardingSubmit:
    """Tests for onboarding form submission."""

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_success_with_data(self, mock_sheets, client, auth_token, claimed_entry):
        """Successful onboarding with optional data redirects to home."""
        sheets = MagicMock()
        sheets.get_roster_by_id.return_value = claimed_entry
        sheets.update_roster.return_value = True
        sheets.append_onboarding_response.return_value = True
        mock_sheets.return_value = sheets

        response = client.post(
            "/onboarding",
            cookies={"session": auth_token},
            data={
                "preferred_name": "Testy",
                "preferred_pronoun": "they/them",
                "hobbies": "Coding",
                "cs_experience": "intermediate",
                "class_goals": "Learn security",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/home" in response.headers["location"]
        sheets.update_roster.assert_called_once()

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_success_empty_form(self, mock_sheets, client, auth_token, claimed_entry):
        """Onboarding works with all empty fields (all optional)."""
        sheets = MagicMock()
        sheets.get_roster_by_id.return_value = claimed_entry
        sheets.update_roster.return_value = True
        mock_sheets.return_value = sheets

        response = client.post(
            "/onboarding",
            cookies={"session": auth_token},
            data={},  # All fields are optional
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/home" in response.headers["location"]

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_update_failure(self, mock_sheets, client, auth_token, claimed_entry):
        """Update failure shows error."""
        sheets = MagicMock()
        sheets.get_roster_by_id.return_value = claimed_entry
        sheets.update_roster.return_value = False  # Fails
        mock_sheets.return_value = sheets

        response = client.post(
            "/onboarding",
            cookies={"session": auth_token},
            data={
                "preferred_name": "Testy",
            },
        )

        assert response.status_code == 200
        assert "error" in response.text.lower()

    def test_onboarding_requires_auth(self, client):
        """Unauthenticated submission redirects to login."""
        response = client.post(
            "/onboarding",
            data={"preferred_name": "Test"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["location"] == "/"
