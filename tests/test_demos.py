"""Tests for the demos pages and index."""

from pathlib import Path
from unittest.mock import patch

import pytest

from app.db.sqlite import init_db
from app.models.roster import RosterEntry
from app.routers import demos as demos_router
from app.services.demo_index import get_available_demos, is_valid_demo_id, read_demo_meta
from app.services.sessions import create_session_token

DEMO_HTML = (
    "<!doctype html><html><head><title>Sample &amp; Demo</title>"
    '<meta name="description" content="A sample demo.">'
    '<meta name="class" content="1"></head><body>hi</body></html>'
)


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    init_db()


@pytest.fixture
def demos_dir(tmp_path, monkeypatch):
    (tmp_path / "files").mkdir()
    (tmp_path / "001-sample.html").write_text(DEMO_HTML, encoding="utf-8")
    (tmp_path / "files" / "cap.pcapng").write_bytes(b"\x0a\x0d\x0d\x0a")
    monkeypatch.setattr(demos_router, "DEMOS_DIR", tmp_path)
    monkeypatch.setattr(demos_router, "FILES_DIR", tmp_path / "files")
    return tmp_path


def entry() -> RosterEntry:
    return RosterEntry(
        student_id="12345",
        full_name="Test Student",
        preferred_email="test@example.com",
        onboarding_completed_at="2024-01-01",
    )


def authed(client, mock_sheets):
    mock_sheets.return_value.get_roster_by_id.return_value = entry()
    mock_sheets.return_value.get_config.return_value = None
    return {"session": create_session_token("test@example.com", "12345")}


class TestDemoIndex:
    def test_read_meta(self, tmp_path):
        p = tmp_path / "001-sample.html"
        p.write_text(DEMO_HTML, encoding="utf-8")
        meta = read_demo_meta(p)
        assert meta == {
            "id": "001-sample",
            "class_no": 1,
            "title": "Sample & Demo",
            "description": "A sample demo.",
        }

    def test_hidden_and_invalid_names_skipped(self, tmp_path):
        (tmp_path / "_draft.html").write_text(DEMO_HTML, encoding="utf-8")
        (tmp_path / "ok.html").write_text(DEMO_HTML, encoding="utf-8")
        assert [d["id"] for d in get_available_demos(tmp_path)] == ["ok"]

    def test_missing_dir(self, tmp_path):
        assert get_available_demos(tmp_path / "nope") == []

    @pytest.mark.parametrize("bad", ["../x", "a/b", ".hidden", ""])
    def test_invalid_ids(self, bad):
        assert not is_valid_demo_id(bad)


class TestDemoRoutes:
    def test_requires_auth(self, client):
        for path in (
            "/demos",
            "/demos/001-sample",
            "/demos/001-sample/raw",
            "/demos/files/cap.pcapng",
        ):
            assert client.get(path, follow_redirects=False).status_code == 302

    @patch("app.dependencies.get_sheets_client")
    def test_landing_lists_by_class(self, mock_sheets, client, demos_dir):
        cookies = authed(client, mock_sheets)
        r = client.get("/demos", cookies=cookies)
        assert r.status_code == 200
        assert b"Class 1" in r.content
        assert b"Sample &amp; Demo" in r.content

    @patch("app.dependencies.get_sheets_client")
    def test_demo_page_embeds_sandboxed_iframe(self, mock_sheets, client, demos_dir):
        cookies = authed(client, mock_sheets)
        r = client.get("/demos/001-sample", cookies=cookies)
        assert r.status_code == 200
        assert b'src="/demos/001-sample/raw"' in r.content
        assert b'sandbox="allow-scripts"' in r.content

    @patch("app.dependencies.get_sheets_client")
    def test_raw_is_sandboxed(self, mock_sheets, client, demos_dir):
        cookies = authed(client, mock_sheets)
        r = client.get("/demos/001-sample/raw", cookies=cookies)
        assert r.status_code == 200
        assert r.headers["content-security-policy"] == "sandbox allow-scripts"
        assert b"<body>hi</body>" in r.content

    @patch("app.dependencies.get_sheets_client")
    def test_unknown_demo_404(self, mock_sheets, client, demos_dir):
        cookies = authed(client, mock_sheets)
        assert client.get("/demos/nope", cookies=cookies).status_code == 404
        assert client.get("/demos/nope/raw", cookies=cookies).status_code == 404

    @patch("app.dependencies.get_sheets_client")
    def test_file_download_and_traversal(self, mock_sheets, client, demos_dir):
        cookies = authed(client, mock_sheets)
        assert client.get("/demos/files/cap.pcapng", cookies=cookies).status_code == 200
        assert client.get("/demos/files/missing.pcapng", cookies=cookies).status_code == 404
        assert client.get("/demos/files/..%2Fsecret", cookies=cookies).status_code == 404


def test_cis53_demos_ship_with_files():
    base = Path(__file__).parent.parent / "content" / "cis53" / "demos"
    ids = {d["id"]: d for d in get_available_demos(base)}
    assert ids["001-osi-and-tcpip-layers"]["class_no"] == 1
    assert ids["002-blocked-cert-vs-dead-port"]["class_no"] == 1
    assert (base / "files" / "emudhra-demo.pcapng").is_file()
    assert (base / "files" / "badssl-untrusted-root.pcapng").is_file()
