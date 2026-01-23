"""Tests for onboarding routes."""

from unittest.mock import MagicMock, patch

import pytest

from app.db.sqlite import init_db
from app.models.student import Student
from app.services.sessions import create_session_token


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    """Initialize database before each test."""
    init_db()


@pytest.fixture
def unclaimed_student():
    """A student who hasn't completed onboarding."""
    return Student(
        student_id="stu_001",
        first_name="Test",
        last_name="Student",
        claim_code="ABC123",
        email="test@example.com",
        status="active",
        claimed_at="2024-01-01T00:00:00",
        onboarded_at=None,  # Not onboarded
    )


@pytest.fixture
def onboarded_student():
    """A student who has completed onboarding."""
    return Student(
        student_id="stu_002",
        first_name="Onboarded",
        last_name="Student",
        claim_code="DEF456",
        email="onboarded@example.com",
        status="active",
        claimed_at="2024-01-01T00:00:00",
        onboarded_at="2024-01-02T00:00:00",
        preferred_name="Onby",
    )


@pytest.fixture
def auth_token(unclaimed_student):
    """Create an auth token for the unclaimed student."""
    return create_session_token(unclaimed_student.email, unclaimed_student.student_id)


@pytest.fixture
def onboarded_auth_token(onboarded_student):
    """Create an auth token for the onboarded student."""
    return create_session_token(onboarded_student.email, onboarded_student.student_id)


class TestOnboardingForm:
    """Tests for onboarding form page."""

    def test_onboarding_requires_auth(self, client):
        """Unauthenticated users get 401."""
        response = client.get("/onboarding")
        assert response.status_code == 401

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_form_renders(self, mock_sheets, client, auth_token, unclaimed_student):
        """Authenticated user sees onboarding form."""
        mock_sheets.return_value.get_student_by_id.return_value = unclaimed_student

        response = client.get("/onboarding", cookies={"session": auth_token})

        assert response.status_code == 200
        assert "Welcome" in response.text
        assert "preferred_name" in response.text.lower()

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_redirects_if_already_done(
        self, mock_sheets, client, onboarded_auth_token, onboarded_student
    ):
        """Already onboarded users are redirected to home."""
        mock_sheets.return_value.get_student_by_id.return_value = onboarded_student

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
    def test_onboarding_success(self, mock_sheets, client, auth_token, unclaimed_student):
        """Successful onboarding redirects to home."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = unclaimed_student
        sheets.update_student.return_value = True
        sheets.append_onboarding_response.return_value = True
        mock_sheets.return_value = sheets

        response = client.post(
            "/onboarding",
            cookies={"session": auth_token},
            data={
                "preferred_name": "Testy",
                "pronouns": "they/them",
                "hobbies": "Coding",
                "computer_experience": "intermediate",
                "security_experience": "None yet",
                "goals": "Learn security",
                "support_needs": "",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/home" in response.headers["location"]
        sheets.update_student.assert_called_once()
        # Should log responses for non-empty fields
        assert sheets.append_onboarding_response.call_count >= 5

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_requires_preferred_name(
        self, mock_sheets, client, auth_token, unclaimed_student
    ):
        """Empty preferred name shows error."""
        mock_sheets.return_value.get_student_by_id.return_value = unclaimed_student

        response = client.post(
            "/onboarding",
            cookies={"session": auth_token},
            data={
                "preferred_name": "   ",  # Whitespace only
                "pronouns": "",
                "hobbies": "",
                "computer_experience": "",
                "security_experience": "",
                "goals": "",
                "support_needs": "",
            },
        )

        assert response.status_code == 200
        assert "required" in response.text.lower()

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_minimal_data(self, mock_sheets, client, auth_token, unclaimed_student):
        """Onboarding works with only required fields."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = unclaimed_student
        sheets.update_student.return_value = True
        sheets.append_onboarding_response.return_value = True
        mock_sheets.return_value = sheets

        response = client.post(
            "/onboarding",
            cookies={"session": auth_token},
            data={
                "preferred_name": "Testy",
                "pronouns": "",
                "hobbies": "",
                "computer_experience": "",
                "security_experience": "",
                "goals": "",
                "support_needs": "",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/home" in response.headers["location"]

    @patch("app.routers.onboarding.get_sheets_client")
    def test_onboarding_update_failure(
        self, mock_sheets, client, auth_token, unclaimed_student
    ):
        """Update failure shows error."""
        sheets = MagicMock()
        sheets.get_student_by_id.return_value = unclaimed_student
        sheets.update_student.return_value = False  # Fails
        mock_sheets.return_value = sheets

        response = client.post(
            "/onboarding",
            cookies={"session": auth_token},
            data={
                "preferred_name": "Testy",
                "pronouns": "",
                "hobbies": "",
                "computer_experience": "",
                "security_experience": "",
                "goals": "",
                "support_needs": "",
            },
        )

        assert response.status_code == 200
        assert "error" in response.text.lower()

    def test_onboarding_requires_auth(self, client):
        """Unauthenticated submission returns 401."""
        response = client.post(
            "/onboarding",
            data={"preferred_name": "Test"},
        )
        assert response.status_code == 401
