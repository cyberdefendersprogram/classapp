"""Tests for the company research page and the Company_Research tab reader."""

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
    mock_sheets.return_value.get_company_research.return_value = rows
    return {"session": create_session_token("test@example.com", "12345")}


ROW = {
    "published": "TRUE",
    "student": "Pat Q.",
    "company": "ExampleCo",
    "what_it_sells": "An AI SOC analyst",
    "verdict": "Promising but unproven",
    "data_read": "Alerts, identity",
    "ai_role": "Summarizes alerts",
    "build_it": "Sigma plus a SIEM",
    "attack_mapping": "T1078",
    "demo_question": "Show me a wrong verdict",
    "risk": "Over-trusting the AI",
    "class_link": "",
}


def test_requires_auth(client):
    assert client.get("/company-research", follow_redirects=False).status_code == 302


@patch("app.dependencies.get_sheets_client")
def test_page_shows_rows(mock_sheets, client):
    r = client.get("/company-research", cookies=authed(mock_sheets, [ROW]))
    assert r.status_code == 200
    assert b"ExampleCo" in r.content and b"Pat Q." in r.content
    assert b"Show me a wrong verdict" in r.content


@patch("app.dependencies.get_sheets_client")
def test_empty_state(mock_sheets, client):
    r = client.get("/company-research", cookies=authed(mock_sheets, []))
    assert r.status_code == 200
    assert b"No company research has been published yet." in r.content


def test_reader_keeps_only_published_rows_and_tolerates_missing_tab():
    client = SheetsClient.__new__(SheetsClient)
    ws = MagicMock()
    ws.get_all_records.return_value = [ROW, {**ROW, "company": "Hidden", "published": "FALSE"}]
    client._get_worksheet = MagicMock(return_value=ws)
    rows = SheetsClient.get_company_research.__wrapped__(client)
    assert [r["company"] for r in rows] == ["ExampleCo"]
    client._get_worksheet = MagicMock(side_effect=Exception("no tab"))
    assert SheetsClient.get_company_research.__wrapped__(client) == []
