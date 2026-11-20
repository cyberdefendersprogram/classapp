"""Tests for the incident research page and the Incident_Research tab reader."""

from unittest.mock import MagicMock, patch

import pytest

from app.db.sqlite import init_db
from app.models.roster import RosterEntry
from app.services.sessions import create_session_token
from app.services.sheets import SheetsClient


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    init_db()


def authed(mock_sheets, rows):
    mock_sheets.return_value.get_roster_by_id.return_value = RosterEntry(
        student_id="12345",
        full_name="Test Student",
        preferred_email="test@example.com",
        onboarding_completed_at="2024-01-01",
    )
    mock_sheets.return_value.get_config.return_value = None
    mock_sheets.return_value.get_incident_research.return_value = rows
    return {"session": create_session_token("test@example.com", "12345")}


ROW = {
    "published": "TRUE",
    "student": "Pat Q.",
    "incident": "ExampleBreach",
    "track": "A: Breach detection",
    "bottom_line": "Stolen token reused for months",
    "timeline": "Three dated steps",
    "attack_mapping": "T1078",
    "evidence": "Sign-in logs",
    "deliverable": "Sigma rule on token reuse",
    "intel_quality": "High: vendor advisory",
    "lesson": "Rotate tokens",
    "ai_question": "Could an agent find the reuse?",
}


def test_requires_auth(client):
    assert client.get("/incident-research", follow_redirects=False).status_code == 302


@patch("app.dependencies.get_sheets_client")
def test_page_shows_rows(mock_sheets, client):
    r = client.get("/incident-research", cookies=authed(mock_sheets, [ROW]))
    assert r.status_code == 200
    assert b"ExampleBreach" in r.content and b"Pat Q." in r.content
    assert b"Sigma rule on token reuse" in r.content


@patch("app.dependencies.get_sheets_client")
def test_empty_state(mock_sheets, client):
    r = client.get("/incident-research", cookies=authed(mock_sheets, []))
    assert r.status_code == 200
    assert b"No incident research has been published yet." in r.content


def test_reader_keeps_only_published_rows_and_tolerates_missing_tab():
    client = SheetsClient.__new__(SheetsClient)
    ws = MagicMock()
    ws.get_all_records.return_value = [ROW, {**ROW, "incident": "Hidden", "published": "FALSE"}]
    client._get_worksheet = MagicMock(return_value=ws)
    rows = SheetsClient.get_incident_research.__wrapped__(client)
    assert [r["incident"] for r in rows] == ["ExampleBreach"]
    client._get_worksheet = MagicMock(side_effect=Exception("no tab"))
    assert SheetsClient.get_incident_research.__wrapped__(client) == []
