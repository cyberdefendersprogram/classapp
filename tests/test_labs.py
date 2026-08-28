"""Tests for labs routes and admin-only solution gating."""

from unittest.mock import patch

import pytest

from app.db.sqlite import init_db
from app.models.roster import RosterEntry
from app.services.sessions import create_session_token


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    """Initialize database before each test."""
    init_db()


def make_roster_entry(student_id: str = "12345", email: str = "test@example.com") -> RosterEntry:
    """Create a RosterEntry for testing."""
    return RosterEntry(
        student_id=student_id,
        full_name="Test Student",
        preferred_email=email,
        onboarding_completed_at="2024-01-01",
    )


class TestLabsRoutes:
    """Tests for labs landing and detail pages."""

    def test_labs_landing_requires_auth(self, client):
        """Labs landing page requires authentication."""
        response = client.get("/labs", follow_redirects=False)
        assert response.status_code == 302

    @patch("app.routers.labs.get_available_labs")
    @patch("app.dependencies.get_sheets_client")
    def test_labs_landing_page(self, mock_sheets, mock_labs, client):
        """Labs landing page loads with lab list."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_labs.return_value = [
            {
                "id": "001-aws-iam-fundamentals",
                "title": "Lab 1",
                "due": "Sept 4",
                "has_solution": True,
            },
        ]

        token = create_session_token("test@example.com", "12345")
        response = client.get("/labs", cookies={"session": token})

        assert response.status_code == 200
        assert b"Lab 1" in response.content

    @patch("app.dependencies.get_sheets_client")
    def test_lab_not_found_returns_404(self, mock_sheets, client):
        """A nonexistent lab id returns 404."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        token = create_session_token("test@example.com", "12345")
        response = client.get("/labs/does-not-exist", cookies={"session": token})

        assert response.status_code == 404

    @patch("app.dependencies.get_sheets_client")
    def test_non_admin_does_not_see_solution_link(self, mock_sheets, client, tmp_path, monkeypatch):
        """Non-admin students never see the solution link, even if a solution file exists."""
        import app.routers.labs as labs_module

        labs_dir = tmp_path / "labs"
        solutions_dir = labs_dir / "solutions"
        labs_dir.mkdir()
        solutions_dir.mkdir()
        (labs_dir / "test-lab.md").write_text("# Test Lab\n\nDo the thing.")
        (solutions_dir / "test-lab.md").write_text("# Test Lab Solution\n\nDo it this way.")

        monkeypatch.setattr(labs_module, "LABS_DIR", labs_dir)
        monkeypatch.setattr(labs_module, "SOLUTIONS_DIR", solutions_dir)

        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None  # not admin

        token = create_session_token("test@example.com", "12345")
        response = client.get("/labs/test-lab", cookies={"session": token})

        assert response.status_code == 200
        assert b"admin only" not in response.content.lower()

    @patch("app.dependencies.get_sheets_client")
    def test_admin_sees_solution_link(self, mock_sheets, client, tmp_path, monkeypatch):
        """Admins see the solution link when a solution file exists."""
        import app.routers.labs as labs_module

        labs_dir = tmp_path / "labs"
        solutions_dir = labs_dir / "solutions"
        labs_dir.mkdir()
        solutions_dir.mkdir()
        (labs_dir / "test-lab.md").write_text("# Test Lab\n\nDo the thing.")
        (solutions_dir / "test-lab.md").write_text("# Test Lab Solution\n\nDo it this way.")

        monkeypatch.setattr(labs_module, "LABS_DIR", labs_dir)
        monkeypatch.setattr(labs_module, "SOLUTIONS_DIR", solutions_dir)

        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry(
            email="admin@example.com"
        )
        mock_sheets.return_value.get_config.return_value = "admin@example.com"

        token = create_session_token("admin@example.com", "12345")
        response = client.get("/labs/test-lab", cookies={"session": token})

        assert response.status_code == 200
        assert b"admin only" in response.content.lower()

    @patch("app.dependencies.get_sheets_client")
    def test_solution_route_403_for_non_admin(self, mock_sheets, client, tmp_path, monkeypatch):
        """Non-admins get 403 on the solution route directly, not just a hidden link."""
        import app.routers.labs as labs_module

        labs_dir = tmp_path / "labs"
        solutions_dir = labs_dir / "solutions"
        labs_dir.mkdir()
        solutions_dir.mkdir()
        (solutions_dir / "test-lab.md").write_text("# Solution\n\nSecret steps.")

        monkeypatch.setattr(labs_module, "LABS_DIR", labs_dir)
        monkeypatch.setattr(labs_module, "SOLUTIONS_DIR", solutions_dir)

        mock_sheets.return_value.get_config.return_value = "admin@example.com"

        token = create_session_token("student@example.com", "12345")
        response = client.get("/labs/test-lab/solution", cookies={"session": token})

        assert response.status_code == 403

    @patch("app.dependencies.get_sheets_client")
    def test_solution_route_200_for_admin(self, mock_sheets, client, tmp_path, monkeypatch):
        """Admins can load the solution route directly and see its content."""
        import app.routers.labs as labs_module

        labs_dir = tmp_path / "labs"
        solutions_dir = labs_dir / "solutions"
        labs_dir.mkdir()
        solutions_dir.mkdir()
        (solutions_dir / "test-lab.md").write_text("# Solution\n\nSecret steps go here.")

        monkeypatch.setattr(labs_module, "LABS_DIR", labs_dir)
        monkeypatch.setattr(labs_module, "SOLUTIONS_DIR", solutions_dir)

        mock_sheets.return_value.get_config.return_value = "admin@example.com"

        token = create_session_token("admin@example.com", "12345")
        response = client.get("/labs/test-lab/solution", cookies={"session": token})

        assert response.status_code == 200
        assert b"Secret steps go here" in response.content

    @patch("app.dependencies.get_sheets_client")
    def test_solution_route_404_when_missing(self, mock_sheets, client, tmp_path, monkeypatch):
        """Solution route 404s when no solution file exists for that lab."""
        import app.routers.labs as labs_module

        labs_dir = tmp_path / "labs"
        solutions_dir = labs_dir / "solutions"
        labs_dir.mkdir()
        solutions_dir.mkdir()

        monkeypatch.setattr(labs_module, "LABS_DIR", labs_dir)
        monkeypatch.setattr(labs_module, "SOLUTIONS_DIR", solutions_dir)

        mock_sheets.return_value.get_config.return_value = "admin@example.com"

        token = create_session_token("admin@example.com", "12345")
        response = client.get("/labs/test-lab/solution", cookies={"session": token})

        assert response.status_code == 404
