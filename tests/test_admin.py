"""Tests for admin routes."""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from app.db.sqlite import init_db
from app.models.quiz import QuizMeta, QuizSubmission
from app.models.roster import RosterEntry
from app.services.sessions import create_session_token


@pytest.fixture(autouse=True)
def setup_db(setup_test_env):
    """Initialize database before each test."""
    init_db()


def make_quiz_meta(quiz_id: str, title: str) -> QuizMeta:
    """Create a QuizMeta for testing."""
    return QuizMeta(
        quiz_id=quiz_id,
        title=title,
        content_path=f"content/quizzes/{quiz_id}.md",
        status="published",
        total_points=10,
    )


def make_submission(
    student_id: str,
    quiz_id: str,
    score: float,
    max_score: float = 10.0,
    attempt: int = 1,
) -> QuizSubmission:
    """Create a QuizSubmission for testing."""
    return QuizSubmission(
        submitted_at=datetime.utcnow(),
        quiz_id=quiz_id,
        attempt=attempt,
        student_id=student_id,
        email=f"{student_id}@example.com",
        answers_json=json.dumps({"q1": "A"}),
        score=score,
        max_score=max_score,
        autograde_json=json.dumps({"q1": {"correct": True}}),
        source="web",
    )


def make_roster_entry(student_id: str, full_name: str, email: str = None) -> RosterEntry:
    """Create a RosterEntry for testing."""
    return RosterEntry(
        student_id=student_id,
        full_name=full_name,
        preferred_email=email or f"{student_id}@example.com",
    )


class TestAdminAccessControl:
    """Tests for admin access control."""

    def test_unauthenticated_returns_401(self, client):
        """Unauthenticated user gets 401."""
        response = client.get("/admin/analytics")
        assert response.status_code == 401

    @patch("app.dependencies.get_sheets_client")
    def test_non_admin_returns_403(self, mock_sheets, client):
        """Non-admin user gets 403."""
        mock_sheets.return_value.get_config.return_value = "admin@example.com"

        token = create_session_token("user@example.com", "stu_001")

        response = client.get(
            "/admin/analytics",
            cookies={"session": token},
        )
        assert response.status_code == 403

    @patch("app.dependencies.get_sheets_client")
    def test_no_admin_email_configured_returns_403(self, mock_sheets, client):
        """No admin email configured returns 403."""
        mock_sheets.return_value.get_config.return_value = None

        token = create_session_token("user@example.com", "stu_001")

        response = client.get(
            "/admin/analytics",
            cookies={"session": token},
        )
        assert response.status_code == 403

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_admin_can_access(self, mock_dep_sheets, mock_router_sheets, client):
        """Admin user can access analytics."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = []
        mock_router_sheets.return_value.get_roster_count.return_value = 0

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/analytics",
            cookies={"session": token},
        )
        assert response.status_code == 200

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_admin_email_case_insensitive(self, mock_dep_sheets, mock_router_sheets, client):
        """Admin email check is case insensitive."""
        mock_dep_sheets.return_value.get_config.return_value = "Admin@Example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = []
        mock_router_sheets.return_value.get_roster_count.return_value = 0

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/analytics",
            cookies={"session": token},
        )
        assert response.status_code == 200


class TestAnalyticsOverview:
    """Tests for analytics overview page."""

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_shows_quiz_list(self, mock_dep_sheets, mock_router_sheets, client):
        """Analytics overview shows quiz list."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = [
            make_quiz_meta("q001", "Quiz 1"),
            make_quiz_meta("q002", "Quiz 2"),
        ]
        mock_router_sheets.return_value.get_roster_count.return_value = 10
        mock_router_sheets.return_value.get_all_quiz_submissions.return_value = []

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/analytics",
            cookies={"session": token},
        )

        assert response.status_code == 200
        assert "Quiz 1" in response.text
        assert "Quiz 2" in response.text
        assert "10" in response.text  # total students

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_calculates_completion_rate(self, mock_dep_sheets, mock_router_sheets, client):
        """Analytics overview calculates completion rate."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = [
            make_quiz_meta("q001", "Quiz 1"),
        ]
        mock_router_sheets.return_value.get_roster_count.return_value = 10
        mock_router_sheets.return_value.get_all_quiz_submissions.return_value = [
            make_submission("stu_001", "q001", 8),
            make_submission("stu_002", "q001", 9),
            make_submission("stu_003", "q001", 10),
        ]

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/analytics",
            cookies={"session": token},
        )

        assert response.status_code == 200
        assert "3/10" in response.text  # 3 students completed
        assert "30" in response.text  # 30% completion


class TestQuizAnalytics:
    """Tests for per-quiz analytics page."""

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_quiz_not_found_returns_404(self, mock_dep_sheets, mock_router_sheets, client):
        """Non-existent quiz returns 404."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"
        mock_router_sheets.return_value.get_quiz_by_id.return_value = None

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/quiz/nonexistent",
            cookies={"session": token},
        )

        assert response.status_code == 404

    @patch("app.routers.admin.get_parsed_quiz")
    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_quiz_content_not_found_returns_500(
        self, mock_dep_sheets, mock_router_sheets, mock_parser, client
    ):
        """Quiz with unparseable content returns 500."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"
        mock_router_sheets.return_value.get_quiz_by_id.return_value = make_quiz_meta(
            "q001", "Quiz 1"
        )
        mock_parser.return_value = None

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/quiz/q001",
            cookies={"session": token},
        )

        assert response.status_code == 500

    @patch("app.routers.admin.get_parsed_quiz")
    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_shows_quiz_analytics(self, mock_dep_sheets, mock_router_sheets, mock_parser, client):
        """Quiz analytics page shows statistics."""
        from app.models.quiz import Question, Quiz

        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"
        mock_router_sheets.return_value.get_quiz_by_id.return_value = make_quiz_meta(
            "q001", "Test Quiz"
        )
        mock_router_sheets.return_value.get_all_quiz_submissions.return_value = [
            make_submission("stu_001", "q001", 10),
        ]
        mock_router_sheets.return_value.get_roster_count.return_value = 5

        mock_parser.return_value = Quiz(
            quiz_id="q001",
            title="Test Quiz",
            questions=[
                Question(
                    id="q1",
                    type="mcq_single",
                    text="Sample question?",
                    points=10,
                    options=["A", "B", "C"],
                    correct="A",
                ),
            ],
        )

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/quiz/q001",
            cookies={"session": token},
        )

        assert response.status_code == 200
        assert "Test Quiz" in response.text
        assert "1/5" in response.text  # 1 student completed out of 5
        assert "Sample question" in response.text


class TestGradingPage:
    """Tests for grading page."""

    def test_unauthenticated_returns_401(self, client):
        """Unauthenticated user gets 401."""
        response = client.get("/admin/grading")
        assert response.status_code == 401

    @patch("app.dependencies.get_sheets_client")
    def test_non_admin_returns_403(self, mock_sheets, client):
        """Non-admin user gets 403."""
        mock_sheets.return_value.get_config.return_value = "admin@example.com"

        token = create_session_token("user@example.com", "stu_001")

        response = client.get(
            "/admin/grading",
            cookies={"session": token},
        )
        assert response.status_code == 403

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_admin_can_access_grading(self, mock_dep_sheets, mock_router_sheets, client):
        """Admin user can access grading page."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = []
        mock_router_sheets.return_value.get_all_roster.return_value = []

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/grading",
            cookies={"session": token},
        )
        assert response.status_code == 200
        assert "Grading" in response.text

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_grading_shows_all_students(self, mock_dep_sheets, mock_router_sheets, client):
        """Grading page shows all students."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = [
            make_quiz_meta("q001", "Quiz 1"),
        ]
        mock_router_sheets.return_value.get_all_roster.return_value = [
            make_roster_entry("stu_001", "Smith, John"),
            make_roster_entry("stu_002", "Doe, Jane"),
        ]
        mock_router_sheets.return_value.get_all_quiz_submissions.return_value = []

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/grading",
            cookies={"session": token},
        )

        assert response.status_code == 200
        assert "Smith, John" in response.text
        assert "Doe, Jane" in response.text

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_grading_shows_zero_for_no_submissions(
        self, mock_dep_sheets, mock_router_sheets, client
    ):
        """Grading page shows 0 for students with no submissions."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = [
            make_quiz_meta("q001", "Quiz 1"),
        ]
        mock_router_sheets.return_value.get_all_roster.return_value = [
            make_roster_entry("stu_001", "Smith, John"),
        ]
        mock_router_sheets.return_value.get_all_quiz_submissions.return_value = []

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/grading",
            cookies={"session": token},
        )

        assert response.status_code == 200
        # Check that 0 is shown in the score cell
        assert ">0</td>" in response.text

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_grading_shows_best_score(self, mock_dep_sheets, mock_router_sheets, client):
        """Grading page shows best score for multiple attempts."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = [
            make_quiz_meta("q001", "Quiz 1"),
        ]
        mock_router_sheets.return_value.get_all_roster.return_value = [
            make_roster_entry("stu_001", "Smith, John"),
        ]
        mock_router_sheets.return_value.get_all_quiz_submissions.return_value = [
            make_submission("stu_001", "q001", 5, attempt=1),
            make_submission("stu_001", "q001", 8, attempt=2),
            make_submission("stu_001", "q001", 6, attempt=3),
        ]

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/grading",
            cookies={"session": token},
        )

        assert response.status_code == 200
        # Should show 8 (best score), not 5 or 6
        assert ">8</td>" in response.text


class TestGradingCSV:
    """Tests for grading CSV download."""

    def test_unauthenticated_returns_401(self, client):
        """Unauthenticated user gets 401."""
        response = client.get("/admin/grading/csv")
        assert response.status_code == 401

    @patch("app.dependencies.get_sheets_client")
    def test_non_admin_returns_403(self, mock_sheets, client):
        """Non-admin user gets 403."""
        mock_sheets.return_value.get_config.return_value = "admin@example.com"

        token = create_session_token("user@example.com", "stu_001")

        response = client.get(
            "/admin/grading/csv",
            cookies={"session": token},
        )
        assert response.status_code == 403

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_csv_returns_correct_content_type(self, mock_dep_sheets, mock_router_sheets, client):
        """CSV download returns correct content type."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = []
        mock_router_sheets.return_value.get_all_roster.return_value = []

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/grading/csv",
            cookies={"session": token},
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        assert "grades.csv" in response.headers["content-disposition"]

    @patch("app.routers.admin.get_sheets_client")
    @patch("app.dependencies.get_sheets_client")
    def test_csv_contains_correct_headers_and_data(
        self, mock_dep_sheets, mock_router_sheets, client
    ):
        """CSV contains correct headers and data."""
        mock_dep_sheets.return_value.get_config.return_value = "admin@example.com"

        mock_router_sheets.return_value.get_quizzes.return_value = [
            make_quiz_meta("q001", "Quiz 1"),
            make_quiz_meta("q002", "Quiz 2"),
        ]
        mock_router_sheets.return_value.get_all_roster.return_value = [
            make_roster_entry("stu_001", "Smith, John", "john@example.com"),
        ]

        def mock_submissions(quiz_id):
            if quiz_id == "q001":
                return [make_submission("stu_001", "q001", 8)]
            return []

        mock_router_sheets.return_value.get_all_quiz_submissions.side_effect = mock_submissions

        token = create_session_token("admin@example.com", "stu_admin")

        response = client.get(
            "/admin/grading/csv",
            cookies={"session": token},
        )

        assert response.status_code == 200

        content = response.text
        lines = content.strip().split("\n")

        # Check header
        assert "Student Name" in lines[0]
        assert "Email" in lines[0]
        assert "Student ID" in lines[0]
        assert "Quiz 1" in lines[0]
        assert "Quiz 2" in lines[0]

        # Check data row
        assert "Smith, John" in lines[1]
        assert "john@example.com" in lines[1]
        assert "stu_001" in lines[1]
        assert ",8," in lines[1] or lines[1].endswith(",8")  # Quiz 1 score
        assert ",0" in lines[1]  # Quiz 2 score (no submission)
