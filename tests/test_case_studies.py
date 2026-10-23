"""Tests for the case studies pages and index."""

from pathlib import Path
from unittest.mock import patch

import pytest

from app.db.sqlite import init_db
from app.models.roster import RosterEntry
from app.routers import case_studies as cs_router
from app.services.case_study_index import (
    format_due,
    get_available_case_studies,
    is_valid_case_study_id,
    read_case_study,
)
from app.services.sessions import create_session_token

SAMPLE = (
    '<!--case-study {"number": 1, "title": "Sample  Case   Study", '
    '"due_at": "2026-10-30T16:00:00Z", "canvas_url": "https://canvas.example/a/1"}-->\n'
    "<p>Write about the <b>thing</b>.</p>\n"
)


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    init_db()


@pytest.fixture
def cs_dir(tmp_path, monkeypatch):
    (tmp_path / "001-sample.html").write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(cs_router, "CASE_STUDIES_DIR", tmp_path)
    return tmp_path


def authed(mock_sheets):
    mock_sheets.return_value.get_roster_by_id.return_value = RosterEntry(
        student_id="12345",
        full_name="Test Student",
        preferred_email="test@example.com",
        onboarding_completed_at="2024-01-01",
    )
    mock_sheets.return_value.get_config.return_value = None
    return {"session": create_session_token("test@example.com", "12345")}


class TestIndex:
    def test_format_due_pacific(self):
        assert format_due("2026-10-30T16:00:00Z") == "Fri Oct 30, 2026, 9:00 a.m. PT"
        assert format_due("2026-11-06T17:00:00Z") == "Fri Nov 6, 2026, 9:00 a.m. PT"
        assert format_due("2026-11-14T07:59:00Z") == "Fri Nov 13, 2026, 11:59 p.m. PT"
        assert format_due(None) is None

    def test_read(self, tmp_path):
        p = tmp_path / "001-sample.html"
        p.write_text(SAMPLE, encoding="utf-8")
        cs = read_case_study(p)
        assert cs["number"] == 1
        assert cs["due"] == "Fri Oct 30, 2026, 9:00 a.m. PT"
        assert cs["canvas_url"] == "https://canvas.example/a/1"
        assert cs["body"].startswith("<p>Write about")

    def test_hidden_and_invalid_skipped(self, tmp_path):
        (tmp_path / "_draft.html").write_text(SAMPLE, encoding="utf-8")
        (tmp_path / "ok.html").write_text(SAMPLE, encoding="utf-8")
        assert [c["id"] for c in get_available_case_studies(tmp_path)] == ["ok"]

    @pytest.mark.parametrize("bad", ["../x", "a/b", ".hidden", ""])
    def test_invalid_ids(self, bad):
        assert not is_valid_case_study_id(bad)


class TestRoutes:
    def test_requires_auth(self, client):
        for path in ("/case-studies", "/case-studies/001-sample"):
            assert client.get(path, follow_redirects=False).status_code == 302

    @patch("app.dependencies.get_sheets_client")
    def test_landing(self, mock_sheets, client, cs_dir):
        r = client.get("/case-studies", cookies=authed(mock_sheets))
        assert r.status_code == 200
        assert b"Sample  Case   Study" in r.content
        assert b"Due: Fri Oct 30, 2026, 9:00 a.m. PT" in r.content

    @patch("app.dependencies.get_sheets_client")
    def test_detail_shows_canvas_text_and_link(self, mock_sheets, client, cs_dir):
        r = client.get("/case-studies/001-sample", cookies=authed(mock_sheets))
        assert r.status_code == 200
        assert b"Write about the <b>thing</b>." in r.content
        assert b"https://canvas.example/a/1" in r.content

    @patch("app.dependencies.get_sheets_client")
    def test_unknown_404(self, mock_sheets, client, cs_dir):
        assert client.get("/case-studies/nope", cookies=authed(mock_sheets)).status_code == 404


def test_cis53_case_studies_match_canvas_assignments():
    base = Path(__file__).parent.parent / "content" / "cis53" / "case_studies"
    items = {c["number"]: c for c in get_available_case_studies(base)}
    assert sorted(items) == [1, 2, 3, 4, 5]
    assert "Mitnick" in items[1]["title"]
    assert items[1]["due"] == "Fri Oct 30, 2026, 9:00 a.m. PT"
    assert all(
        c["canvas_url"].startswith("https://peralta.instructure.com/") for c in items.values()
    )
