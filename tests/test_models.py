"""Tests for data models."""

from datetime import datetime

from app.models.quiz import QuizMeta, QuizSubmission, Question, Quiz
from app.models.student import Student


class TestStudent:
    """Tests for Student model."""

    def test_from_row_basic(self):
        """Test creating student from row data."""
        row = {
            "student_id": "stu_001",
            "first_name": "Alice",
            "last_name": "Smith",
            "claim_code": "ABC123",
            "email": "",
            "status": "active",
        }

        student = Student.from_row(row)

        assert student.student_id == "stu_001"
        assert student.first_name == "Alice"
        assert student.last_name == "Smith"
        assert student.claim_code == "ABC123"
        assert student.email is None
        assert student.status == "active"

    def test_from_row_with_email(self):
        """Test creating claimed student from row data."""
        row = {
            "student_id": "stu_001",
            "first_name": "Alice",
            "last_name": "Smith",
            "claim_code": "ABC123",
            "email": "alice@example.com",
            "status": "active",
            "claimed_at": "2025-01-01T10:00:00",
        }

        student = Student.from_row(row)

        assert student.email == "alice@example.com"
        assert student.claimed_at == datetime(2025, 1, 1, 10, 0, 0)

    def test_is_claimed_false(self):
        """Test is_claimed returns False for unclaimed student."""
        student = Student(
            student_id="stu_001",
            first_name="Alice",
            last_name="Smith",
            claim_code="ABC123",
        )

        assert student.is_claimed is False

    def test_is_claimed_true(self):
        """Test is_claimed returns True for claimed student."""
        student = Student(
            student_id="stu_001",
            first_name="Alice",
            last_name="Smith",
            claim_code="ABC123",
            email="alice@example.com",
            claimed_at=datetime.now(),
        )

        assert student.is_claimed is True

    def test_is_onboarded(self):
        """Test is_onboarded property."""
        student = Student(
            student_id="stu_001",
            first_name="Alice",
            last_name="Smith",
            claim_code="ABC123",
        )

        assert student.is_onboarded is False

        student.onboarded_at = datetime.now()
        assert student.is_onboarded is True

    def test_display_name_uses_preferred(self):
        """Test display_name uses preferred_name when set."""
        student = Student(
            student_id="stu_001",
            first_name="Alice",
            last_name="Smith",
            claim_code="ABC123",
            preferred_name="Ali",
        )

        assert student.display_name == "Ali"

    def test_display_name_fallback(self):
        """Test display_name falls back to first_name."""
        student = Student(
            student_id="stu_001",
            first_name="Alice",
            last_name="Smith",
            claim_code="ABC123",
        )

        assert student.display_name == "Alice"

    def test_full_name(self):
        """Test full_name property."""
        student = Student(
            student_id="stu_001",
            first_name="Alice",
            last_name="Smith",
            claim_code="ABC123",
        )

        assert student.full_name == "Alice Smith"


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
