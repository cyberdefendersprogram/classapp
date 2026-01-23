"""Tests for authentication routes."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.sqlite import init_db
from app.services.email import EmailResult


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    """Initialize database before each test."""
    init_db()


class TestSigninPage:
    """Tests for sign-in page."""

    def test_signin_page_renders(self, client):
        """Sign-in page renders successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Class Portal" in response.text
        assert "email" in response.text.lower()

    def test_signin_redirects_if_logged_in(self, client):
        """Logged-in users are redirected to home."""
        from app.services.sessions import create_session_token

        token = create_session_token("test@example.com", "stu_001")

        response = client.get("/", cookies={"session": token}, follow_redirects=False)
        assert response.status_code == 302
        assert "/home" in response.headers["location"]


class TestRequestMagicLink:
    """Tests for magic link request endpoint."""

    @patch("app.routers.auth.send_magic_link_email")
    @patch("app.routers.auth.get_sheets_client")
    def test_request_link_success(self, mock_sheets, mock_email, client):
        """Magic link request shows success message."""
        mock_sheets.return_value.append_magic_link_request.return_value = True
        mock_email.return_value = EmailResult(success=True, message_id="123")

        # Use unique email to avoid rate limit state from other tests
        email = f"test-{uuid.uuid4()}@example.com"
        response = client.post(
            "/auth/request-link",
            data={"email": email},
        )

        assert response.status_code == 200
        assert "check your inbox" in response.text.lower()
        mock_email.assert_called_once()

    @patch("app.routers.auth.get_sheets_client")
    def test_request_link_rate_limited(self, mock_sheets, client):
        """Rate limiting returns error after too many requests."""
        mock_sheets.return_value.append_magic_link_request.return_value = True

        # Use unique email to avoid state from other tests
        email = f"ratelimited-{uuid.uuid4()}@example.com"

        # Make requests up to the limit
        with patch("app.routers.auth.send_magic_link_email") as mock_email:
            mock_email.return_value = EmailResult(success=True)

            for _ in range(3):
                client.post("/auth/request-link", data={"email": email})

        # Next request should be rate limited
        response = client.post("/auth/request-link", data={"email": email})

        assert response.status_code == 200
        assert "too many requests" in response.text.lower()

    @patch("app.routers.auth.send_magic_link_email")
    @patch("app.routers.auth.get_sheets_client")
    def test_request_link_same_response_for_unknown_email(
        self, mock_sheets, mock_email, client
    ):
        """Unknown emails get same response to prevent enumeration."""
        mock_sheets.return_value.append_magic_link_request.return_value = True
        mock_email.return_value = EmailResult(success=True)

        # Use unique email to avoid rate limit state from other tests
        email = f"unknown-{uuid.uuid4()}@nonexistent.com"
        response = client.post(
            "/auth/request-link",
            data={"email": email},
        )

        # Should still show success (not reveal email doesn't exist)
        assert response.status_code == 200
        assert "check your inbox" in response.text.lower()


class TestVerifyMagicLink:
    """Tests for magic link verification."""

    def test_invalid_token_shows_error(self, client):
        """Invalid token shows error message."""
        response = client.get("/auth/verify?token=invalid-token")

        assert response.status_code == 200
        assert "invalid" in response.text.lower() or "expired" in response.text.lower()

    @patch("app.routers.auth.get_sheets_client")
    def test_valid_token_claimed_user_redirects_to_home(self, mock_sheets, client):
        """Valid token for claimed user redirects to home."""
        from datetime import datetime
        from app.models.roster import RosterEntry
        from app.services.tokens import create_magic_token

        # Create a token
        token = create_magic_token("claimed@example.com")

        # Mock a claimed roster entry
        mock_entry = RosterEntry(
            student_id="stu_001",
            full_name="User, Test",
            preferred_email="claimed@example.com",
            claimed_at=datetime(2024, 1, 1),
            onboarding_completed_at=datetime(2024, 1, 1),
        )
        mock_sheets.return_value.get_student_by_email.return_value = mock_entry
        mock_sheets.return_value.update_roster.return_value = True

        response = client.get(f"/auth/verify?token={token}", follow_redirects=False)

        assert response.status_code == 302
        assert "/home" in response.headers["location"]
        assert "session" in response.cookies

    @patch("app.routers.auth.get_sheets_client")
    def test_valid_token_unclaimed_redirects_to_claim(self, mock_sheets, client):
        """Valid token for unclaimed email redirects to claim."""
        from app.services.tokens import create_magic_token

        token = create_magic_token("new@example.com")

        # No student found for this email
        mock_sheets.return_value.get_student_by_email.return_value = None

        response = client.get(f"/auth/verify?token={token}", follow_redirects=False)

        assert response.status_code == 302
        assert "/claim" in response.headers["location"]


class TestLogout:
    """Tests for logout."""

    def test_logout_clears_session(self, client):
        """Logout clears session cookie."""
        from app.services.sessions import create_session_token

        token = create_session_token("test@example.com", "stu_001")

        response = client.post(
            "/auth/logout",
            cookies={"session": token},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/" == response.headers["location"]

    def test_logout_get_works(self, client):
        """GET logout also works."""
        response = client.get("/auth/logout", follow_redirects=False)
        assert response.status_code == 302
