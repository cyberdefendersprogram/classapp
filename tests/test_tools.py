"""Tests for tools routes."""

import tempfile
from pathlib import Path
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


class TestToolsRoutes:
    """Tests for tools landing and detail pages."""

    def test_tools_landing_requires_auth(self, client):
        """Tools landing page requires authentication."""
        response = client.get("/tools", follow_redirects=False)
        assert response.status_code == 302

    @patch("app.routers.tools.get_available_tools")
    @patch("app.dependencies.get_sheets_client")
    def test_tools_landing_page(self, mock_sheets, mock_tools, client):
        """Tools landing page loads with tool list."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_tools.return_value = [
            {"id": "nmap", "name": "Nmap", "description": "Network scanner"},
            {"id": "sqlmap", "name": "SQLMap", "description": "SQL injection"},
        ]

        token = create_session_token("test@example.com", "12345")

        response = client.get("/tools", cookies={"session": token})

        assert response.status_code == 200
        assert b"Nmap" in response.content
        assert b"SQLMap" in response.content
        assert b"Security Tools Reference" in response.content

    @patch("app.routers.tools.get_available_tools")
    @patch("app.dependencies.get_sheets_client")
    def test_tools_landing_empty(self, mock_sheets, mock_tools, client):
        """Tools landing page handles empty tool list."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_tools.return_value = []

        token = create_session_token("test@example.com", "12345")

        response = client.get("/tools", cookies={"session": token})

        assert response.status_code == 200
        assert b"No tools available" in response.content

    def test_tool_page_requires_auth(self, client):
        """Individual tool page requires authentication."""
        response = client.get("/tools/nmap", follow_redirects=False)
        assert response.status_code == 302

    @patch("app.routers.tools.get_available_tools")
    @patch("app.routers.tools.TOOLS_DIR")
    @patch("app.dependencies.get_sheets_client")
    def test_tool_page_loads(self, mock_sheets, mock_dir, mock_tools, client):
        """Individual tool page loads successfully."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_tools.return_value = [
            {"id": "nmap", "name": "Nmap", "description": "Network scanner"},
        ]

        token = create_session_token("test@example.com", "12345")

        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = Path(tmpdir) / "nmap.md"
            tool_path.write_text("""# Nmap

Network scanner tool.

## Overview

Nmap is great.
""")
            mock_dir.__truediv__ = lambda self, x: Path(tmpdir) / x
            mock_dir.exists.return_value = True

            with patch("app.routers.tools.TOOLS_DIR", Path(tmpdir)):
                response = client.get("/tools/nmap", cookies={"session": token})

                assert response.status_code == 200
                assert b"Nmap" in response.content

    @patch("app.routers.tools.get_available_tools")
    @patch("app.dependencies.get_sheets_client")
    def test_tool_page_not_found(self, mock_sheets, mock_tools, client):
        """Tool page returns 404 for unknown tool."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_tools.return_value = []

        token = create_session_token("test@example.com", "12345")

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.routers.tools.TOOLS_DIR", Path(tmpdir)):
                response = client.get("/tools/nonexistent", cookies={"session": token})

                assert response.status_code == 404
                assert b"Tool Not Found" in response.content

    @patch("app.routers.tools.get_available_tools")
    @patch("app.dependencies.get_sheets_client")
    def test_tool_page_with_command_builder(self, mock_sheets, mock_tools, client):
        """Tool page renders command builder."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_tools.return_value = [{"id": "nmap", "name": "Nmap", "description": "Scanner"}]

        token = create_session_token("test@example.com", "12345")

        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = Path(tmpdir) / "nmap.md"
            tool_path.write_text("""# Nmap

:::command-builder{id="nmap-builder"}
tool_name: nmap
scan_types:
  - name: "SYN Scan"
    flag: "-sS"
    desc: "Stealth scan"
options:
  - name: "Version"
    flag: "-sV"
    desc: "Version detection"
:::

## Overview
Test tool.
""")
            with patch("app.routers.tools.TOOLS_DIR", Path(tmpdir)):
                response = client.get("/tools/nmap", cookies={"session": token})

                assert response.status_code == 200
                assert b"Command Builder" in response.content
                assert b"SYN Scan" in response.content

    @patch("app.routers.tools.get_available_tools")
    @patch("app.dependencies.get_sheets_client")
    def test_tool_page_with_scenarios(self, mock_sheets, mock_tools, client):
        """Tool page renders scenarios."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_tools.return_value = [{"id": "nmap", "name": "Nmap", "description": "Scanner"}]

        token = create_session_token("test@example.com", "12345")

        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = Path(tmpdir) / "nmap.md"
            tool_path.write_text("""# Nmap

:::scenario{id="s1" level="beginner"}
title: "Basic Scan"
goal: "Learn to scan a target."
hint: "Use nmap with an IP."
command: "nmap 192.168.1.1"
:::

## Overview
Test tool.
""")
            with patch("app.routers.tools.TOOLS_DIR", Path(tmpdir)):
                response = client.get("/tools/nmap", cookies={"session": token})

                assert response.status_code == 200
                assert b"Basic Scan" in response.content
                assert b"beginner" in response.content

    @patch("app.routers.tools.get_available_tools")
    @patch("app.dependencies.get_sheets_client")
    def test_tool_page_with_quiz(self, mock_sheets, mock_tools, client):
        """Tool page renders inline quizzes."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_tools.return_value = [{"id": "nmap", "name": "Nmap", "description": "Scanner"}]

        token = create_session_token("test@example.com", "12345")

        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = Path(tmpdir) / "nmap.md"
            tool_path.write_text("""# Nmap

:::quiz{id="q1"}
Q: What does -sV do?
- [ ] OS detection
- [x] Version detection
- [ ] Ping scan
:::

## Overview
Test tool.
""")
            with patch("app.routers.tools.TOOLS_DIR", Path(tmpdir)):
                response = client.get("/tools/nmap", cookies={"session": token})

                assert response.status_code == 200
                assert b"Knowledge Check" in response.content
                assert b"Version detection" in response.content


class TestToolsNavigation:
    """Tests for tools navigation integration."""

    @patch("app.routers.tools.get_available_tools")
    @patch("app.dependencies.get_sheets_client")
    def test_tools_link_visible(self, mock_sheets, mock_tools, client):
        """Tools link appears in navigation."""
        mock_sheets.return_value.get_roster_by_id.return_value = make_roster_entry()
        mock_sheets.return_value.get_config.return_value = None

        mock_tools.return_value = []

        token = create_session_token("test@example.com", "12345")

        response = client.get("/tools", cookies={"session": token})

        assert response.status_code == 200
        assert b'href="/tools"' in response.content
