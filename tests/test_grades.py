"""Tests for Canvas grade sync display: roster parsing, view building, and per-student isolation."""

from unittest.mock import patch

import pytest

from app.db.sqlite import init_db
from app.models.roster import RosterEntry
from app.services.grades import build_grades_view
from app.services.sessions import create_session_token

TEST_STUDENT_IDS = ("111", "222", "333", "444")


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    """Init the DB and make sure the student cache doesn't leak between tests."""
    from app.db.sqlite import invalidate_cached_student

    init_db()
    for sid in TEST_STUDENT_IDS:
        invalidate_cached_student(sid)
    yield
    for sid in TEST_STUDENT_IDS:
        invalidate_cached_student(sid)


def entry(student_id="12345", email="a@example.com", **kw) -> RosterEntry:
    return RosterEntry(
        student_id=student_id,
        full_name="Test, Student",
        preferred_email=email,
        onboarding_completed_at="2024-01-01",
        **kw,
    )


class TestRosterParsing:
    def test_from_row_reads_grade_columns(self):
        row = {
            "student_id": "1",
            "full_name": "A, B",
            "grade_lab1": "88/100",
            "grade_quiz1": "100/100",
            "grade_lab2": "",
            "grade_total": 96.71,
            "grade_letter": "A",
            "grades_synced_at": "2026-10-16T08:33:56Z",
        }
        e = RosterEntry.from_row(row)
        assert e.grades == {"lab1": "88/100", "quiz1": "100/100"}
        assert e.grade_total == 96.71
        assert e.grade_letter == "A"
        assert e.grades_synced_at is not None

    def test_from_row_without_grade_columns(self):
        e = RosterEntry.from_row({"student_id": "1", "full_name": "A, B"})
        assert e.grades == {} and e.grade_total is None and e.grade_letter is None


class TestGradesView:
    def test_rows_and_percent(self):
        view = build_grades_view(entry(grades={"lab1": "86/100", "lab4": "108/120"}))
        by_key = {r.key: r for r in view.rows}
        assert by_key["lab1"].percent == 86.0
        assert by_key["lab4"].percent == 90.0
        assert by_key["lab2"].score is None

    def test_lowest_per_category_marked_dropped(self):
        grades = {
            "lab1": "70/100",
            "lab2": "95/100",
            "lab3": "102/100",
            "quiz1": "100/100",
            "quiz2": "40/100",
            "quiz3": "100/100",
        }
        by_key = {r.key: r for r in build_grades_view(entry(grades=grades)).rows}
        assert by_key["lab1"].dropped and not by_key["lab2"].dropped
        assert by_key["quiz2"].dropped and not by_key["quiz1"].dropped

    def test_single_graded_item_not_dropped(self):
        view = build_grades_view(entry(grades={"lab1": "50/100"}))
        assert not any(r.dropped for r in view.rows)

    def test_empty_has_no_grades(self):
        assert build_grades_view(entry()).has_any is False


class TestGradesRoute:
    def test_requires_auth(self, client):
        assert client.get("/grades", follow_redirects=False).status_code == 302

    @patch("app.dependencies.get_sheets_client")
    def test_student_sees_only_own_grades(self, mock_sheets, client):
        mine = entry(
            student_id="111",
            email="me@example.com",
            grades={"lab1": "88/100"},
            grade_total=91.22,
            grade_letter="A",
        )
        mock_sheets.return_value.get_roster_by_id.return_value = mine
        mock_sheets.return_value.get_config.return_value = "true"

        token = create_session_token("me@example.com", "111")
        resp = client.get("/grades", cookies={"session": token})

        assert resp.status_code == 200
        assert b"91.22%" in resp.content
        assert b"88" in resp.content
        # The roster lookup is keyed by the session's student id, never a URL parameter.
        mock_sheets.return_value.get_roster_by_id.assert_called_with("111")

    @patch("app.dependencies.get_sheets_client")
    def test_grades_page_has_no_student_id_parameter(self, mock_sheets, client):
        mock_sheets.return_value.get_roster_by_id.return_value = entry(student_id="222")
        mock_sheets.return_value.get_config.return_value = "true"
        token = create_session_token("b@example.com", "222")
        # Another student's id in the query string must be ignored.
        resp = client.get("/grades?student_id=999", cookies={"session": token})
        assert resp.status_code == 200
        mock_sheets.return_value.get_roster_by_id.assert_called_with("222")


class TestGradesRelease:
    @patch("app.dependencies.get_sheets_client")
    def test_hidden_until_released(self, mock_sheets, client):
        mine = entry(
            student_id="444", email="h@example.com", grades={"lab1": "88/100"}, grade_total=91.22
        )
        mock_sheets.return_value.get_roster_by_id.return_value = mine
        mock_sheets.return_value.get_config.return_value = None  # grades_visible not set
        token = create_session_token("h@example.com", "444")
        resp = client.get("/grades", cookies={"session": token})
        assert resp.status_code == 200
        assert b"end of the course" in resp.content
        assert b"91.22" not in resp.content and b"88" not in resp.content
        assert b'href="/grades"' not in resp.content  # nav link hidden too

    @patch("app.dependencies.get_sheets_client")
    def test_visible_when_released(self, mock_sheets, client):
        mine = entry(
            student_id="444", email="h@example.com", grades={"lab1": "88/100"}, grade_total=91.22
        )
        mock_sheets.return_value.get_roster_by_id.return_value = mine
        mock_sheets.return_value.get_config.return_value = "yes"
        token = create_session_token("h@example.com", "444")
        resp = client.get("/grades", cookies={"session": token})
        assert b"91.22%" in resp.content


class TestCachedStudentRoundTrip:
    def test_grades_survive_sqlite_student_cache(self):
        """The /grades page reads the student from the SQLite cache; grades must round-trip."""
        from app.db.sqlite import get_cached_student, set_cached_student

        e = entry(
            student_id="333",
            email="c@example.com",
            grades={"lab1": "88/100", "quiz1": "100/100"},
            grade_total=91.22,
            grade_letter="A",
        )
        set_cached_student(e)
        got = get_cached_student("333")
        assert got.grades == {"lab1": "88/100", "quiz1": "100/100"}
        assert got.grade_total == 91.22 and got.grade_letter == "A"


class TestAdminCanvasGrades:
    @patch("app.dependencies.get_sheets_client")
    def test_non_admin_forbidden(self, mock_sheets, client):
        mock_sheets.return_value.get_config.return_value = "admin@example.com"
        token = create_session_token("d@example.com", "444")
        resp = client.get(
            "/admin/canvas-grades", cookies={"session": token}, follow_redirects=False
        )
        assert resp.status_code == 403

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_admin_sees_all_students_and_csv(self, mock_dep, mock_router, client):
        mock_dep.return_value.get_config.return_value = "admin@example.com"
        roster = [
            entry(
                "1", "a@example.com", grades={"lab1": "88/100"}, grade_total=91.2, grade_letter="A"
            ),
            entry(
                "2", "b@example.com", grades={"quiz1": "70/100"}, grade_total=70.5, grade_letter="C"
            ),
            entry("3", "c@example.com"),  # no synced grades -> omitted
        ]
        roster[0].full_name, roster[1].full_name, roster[2].full_name = (
            "Zed, Z",
            "Abe, A",
            "Nope, N",
        )
        mock_router.return_value.get_all_roster.return_value = roster
        token = create_session_token("admin@example.com", "999")

        page = client.get("/admin/canvas-grades", cookies={"session": token})
        assert page.status_code == 200
        assert b"Abe, A" in page.content and b"Zed, Z" in page.content
        assert b"Nope, N" not in page.content
        assert page.content.index(b"Abe, A") < page.content.index(b"Zed, Z")  # sorted

        csv_resp = client.get("/admin/canvas-grades/csv", cookies={"session": token})
        assert csv_resp.status_code == 200
        assert "88/100" in csv_resp.text and "Letter" in csv_resp.text
