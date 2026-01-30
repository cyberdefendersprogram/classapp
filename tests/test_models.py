"""Tests for data models."""

from datetime import datetime

from app.models.quiz import Question, Quiz, QuizMeta
from app.models.roster import RosterEntry


class TestRosterEntry:
    """Tests for RosterEntry model."""

    def test_from_row_basic(self):
        """Test creating roster entry from row data."""
        row = {
            "student_id": "stu_001",
            "full_name": "Smith, Alice",
            "preferred_email": "",
            "preferred_name": "",
        }

        entry = RosterEntry.from_row(row)

        assert entry.student_id == "stu_001"
        assert entry.full_name == "Smith, Alice"
        assert entry.preferred_email is None
        assert entry.preferred_name is None

    def test_from_row_with_email(self):
        """Test creating claimed roster entry from row data."""
        row = {
            "student_id": "stu_001",
            "full_name": "Smith, Alice",
            "preferred_email": "alice@example.com",
            "claimed_at": "2025-01-01T10:00:00",
        }

        entry = RosterEntry.from_row(row)

        assert entry.preferred_email == "alice@example.com"
        assert entry.claimed_at == datetime(2025, 1, 1, 10, 0, 0)

    def test_is_claimed_false(self):
        """Test is_claimed returns False for unclaimed entry."""
        entry = RosterEntry(
            student_id="stu_001",
            full_name="Smith, Alice",
        )

        assert entry.is_claimed is False

    def test_is_claimed_true(self):
        """Test is_claimed returns True for claimed entry."""
        entry = RosterEntry(
            student_id="stu_001",
            full_name="Smith, Alice",
            preferred_email="alice@example.com",
            claimed_at=datetime.now(),
        )

        assert entry.is_claimed is True

    def test_is_onboarded(self):
        """Test is_onboarded property."""
        entry = RosterEntry(
            student_id="stu_001",
            full_name="Smith, Alice",
        )

        assert entry.is_onboarded is False

        entry.onboarding_completed_at = datetime.now()
        assert entry.is_onboarded is True

    def test_display_name_uses_preferred(self):
        """Test display_name uses preferred_name when set."""
        entry = RosterEntry(
            student_id="stu_001",
            full_name="Smith, Alice",
            preferred_name="Ali",
        )

        assert entry.display_name == "Ali"

    def test_display_name_fallback(self):
        """Test display_name falls back to first name from full_name."""
        entry = RosterEntry(
            student_id="stu_001",
            full_name="Smith, Alice",
        )

        assert entry.display_name == "Alice"

    def test_email_alias(self):
        """Test email property returns preferred_email."""
        entry = RosterEntry(
            student_id="stu_001",
            full_name="Smith, Alice",
            preferred_email="alice@example.com",
        )

        assert entry.email == "alice@example.com"

    def test_get_empty_profile_fields(self):
        """Test get_empty_profile_fields returns unfilled fields."""
        entry = RosterEntry(
            student_id="stu_001",
            full_name="Smith, Alice",
            preferred_name="Alice",  # filled
            cs_experience="beginner",  # filled
        )

        empty = entry.get_empty_profile_fields()

        assert "preferred_name" not in empty
        assert "cs_experience" not in empty
        assert "linkedin" in empty
        assert "hobbies" in empty


class TestQuizMeta:
    """Tests for QuizMeta model."""

    def test_from_row(self):
        """Test creating quiz meta from row data."""
        row = {
            "quiz_id": "q001",
            "title": "Intro Quiz",
            "content_path": "content/quizzes/001-intro.md",
            "open_at": "2025-01-01T00:00:00",
            "close_at": "2025-12-31T23:59:59",
            "attempts_allowed": "2",
            "status": "published",
            "total_points": "10",
        }

        quiz = QuizMeta.from_row(row)

        assert quiz.quiz_id == "q001"
        assert quiz.title == "Intro Quiz"
        assert quiz.attempts_allowed == 2
        assert quiz.status == "published"
        assert quiz.total_points == 10

    def test_is_published(self):
        """Test is_published property."""
        quiz = QuizMeta(
            quiz_id="q001",
            title="Test",
            content_path="test.md",
            status="draft",
        )
        assert quiz.is_published is False

        quiz.status = "published"
        assert quiz.is_published is True

    def test_is_open_not_published(self):
        """Test is_open returns False for unpublished quiz."""
        quiz = QuizMeta(
            quiz_id="q001",
            title="Test",
            content_path="test.md",
            status="draft",
        )

        assert quiz.is_open is False

    def test_is_open_no_dates(self):
        """Test is_open returns True for published quiz with no date restrictions."""
        quiz = QuizMeta(
            quiz_id="q001",
            title="Test",
            content_path="test.md",
            status="published",
        )

        assert quiz.is_open is True


class TestQuestion:
    """Tests for Question model."""

    def test_is_mcq_single(self):
        """Test is_mcq for single choice."""
        q = Question(id="q1", type="mcq_single", text="Test?", points=1)
        assert q.is_mcq is True

    def test_is_mcq_multi(self):
        """Test is_mcq for multiple choice."""
        q = Question(id="q1", type="mcq_multi", text="Test?", points=1)
        assert q.is_mcq is True

    def test_is_mcq_false(self):
        """Test is_mcq returns False for non-MCQ types."""
        q = Question(id="q1", type="numeric", text="Test?", points=1)
        assert q.is_mcq is False


class TestQuiz:
    """Tests for Quiz model."""

    def test_total_points_calculated(self):
        """Test that total_points is calculated from questions."""
        quiz = Quiz(
            quiz_id="q001",
            title="Test Quiz",
            questions=[
                Question(id="q1", type="mcq_single", text="Q1?", points=2),
                Question(id="q2", type="numeric", text="Q2?", points=3),
            ],
        )

        assert quiz.total_points == 5

    def test_total_points_explicit(self):
        """Test that explicit total_points is preserved."""
        quiz = Quiz(
            quiz_id="q001",
            title="Test Quiz",
            questions=[],
            total_points=10,
        )

        assert quiz.total_points == 10
