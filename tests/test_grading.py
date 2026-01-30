"""Tests for quiz grading service."""

from app.models.quiz import Question, Quiz
from app.services.grading import grade_question, grade_quiz


class TestGradeQuestion:
    """Tests for grading individual questions."""

    def test_mcq_single_correct(self):
        """Correct single-choice MCQ gets full points."""
        q = Question(id="q1", type="mcq_single", text="?", points=2, correct="B")
        result = grade_question(q, "B")

        assert result.correct is True
        assert result.points == 2
        assert result.max_points == 2

    def test_mcq_single_incorrect(self):
        """Incorrect single-choice MCQ gets zero points."""
        q = Question(id="q1", type="mcq_single", text="?", points=2, correct="B")
        result = grade_question(q, "A")

        assert result.correct is False
        assert result.points == 0
        assert result.expected == "B"
        assert result.got == "A"

    def test_mcq_single_no_answer(self):
        """No answer for single-choice MCQ gets zero points."""
        q = Question(id="q1", type="mcq_single", text="?", points=2, correct="B")
        result = grade_question(q, None)

        assert result.correct is False
        assert result.points == 0

    def test_mcq_multi_all_correct(self):
        """All correct selections for multi-choice gets full points."""
        q = Question(
            id="q1",
            type="mcq_multi",
            text="?",
            points=3,
            correct=["A", "C"],
        )
        result = grade_question(q, ["A", "C"])

        assert result.correct is True
        assert result.points == 3

    def test_mcq_multi_partial(self):
        """Partial selection for multi-choice gets zero points."""
        q = Question(
            id="q1",
            type="mcq_multi",
            text="?",
            points=3,
            correct=["A", "C"],
        )
        result = grade_question(q, ["A"])  # Missing C

        assert result.correct is False
        assert result.points == 0
        assert set(result.expected) == {"A", "C"}

    def test_mcq_multi_extra_selection(self):
        """Extra incorrect selection for multi-choice gets zero points."""
        q = Question(
            id="q1",
            type="mcq_multi",
            text="?",
            points=3,
            correct=["A", "C"],
        )
        result = grade_question(q, ["A", "B", "C"])  # B is wrong

        assert result.correct is False
        assert result.points == 0

    def test_mcq_multi_no_answer(self):
        """No answer for multi-choice gets zero points."""
        q = Question(
            id="q1",
            type="mcq_multi",
            text="?",
            points=3,
            correct=["A", "C"],
        )
        result = grade_question(q, None)

        assert result.correct is False
        assert result.points == 0

    def test_numeric_correct(self):
        """Correct numeric answer gets full points."""
        q = Question(id="q1", type="numeric", text="?", points=1, correct="8")
        result = grade_question(q, "8")

        assert result.correct is True
        assert result.points == 1

    def test_numeric_correct_as_int(self):
        """Numeric comparison works with different types."""
        q = Question(id="q1", type="numeric", text="?", points=1, correct="42")
        result = grade_question(q, "42.0")

        assert result.correct is True

    def test_numeric_incorrect(self):
        """Incorrect numeric answer gets zero points."""
        q = Question(id="q1", type="numeric", text="?", points=1, correct="8")
        result = grade_question(q, "7")

        assert result.correct is False
        assert result.points == 0

    def test_short_text_correct(self):
        """Correct short text gets full points."""
        q = Question(id="q1", type="short_text", text="?", points=2, correct="ls")
        result = grade_question(q, "ls")

        assert result.correct is True
        assert result.points == 2

    def test_short_text_case_insensitive(self):
        """Short text comparison is case-insensitive."""
        q = Question(id="q1", type="short_text", text="?", points=2, correct="ls")
        result = grade_question(q, "LS")

        assert result.correct is True

    def test_short_text_trimmed(self):
        """Short text comparison ignores leading/trailing whitespace."""
        q = Question(id="q1", type="short_text", text="?", points=2, correct="ls")
        result = grade_question(q, "  ls  ")

        assert result.correct is True

    def test_short_text_incorrect(self):
        """Incorrect short text gets zero points."""
        q = Question(id="q1", type="short_text", text="?", points=2, correct="ls")
        result = grade_question(q, "dir")

        assert result.correct is False
        assert result.points == 0


class TestGradeQuiz:
    """Tests for grading entire quizzes."""

    def test_grade_quiz_all_correct(self):
        """All correct answers gives max score."""
        quiz = Quiz(
            quiz_id="q001",
            title="Test",
            questions=[
                Question(id="q1", type="mcq_single", text="?", points=2, correct="A"),
                Question(id="q2", type="numeric", text="?", points=1, correct="8"),
            ],
        )

        result = grade_quiz(quiz, {"q1": "A", "q2": "8"})

        assert result.score == 3
        assert result.max_score == 3
        assert result.percentage == 100.0
        assert result.questions["q1"].correct is True
        assert result.questions["q2"].correct is True

    def test_grade_quiz_partial(self):
        """Partial correct answers gives partial score."""
        quiz = Quiz(
            quiz_id="q001",
            title="Test",
            questions=[
                Question(id="q1", type="mcq_single", text="?", points=2, correct="A"),
                Question(id="q2", type="numeric", text="?", points=1, correct="8"),
            ],
        )

        result = grade_quiz(quiz, {"q1": "A", "q2": "7"})

        assert result.score == 2
        assert result.max_score == 3
        assert result.questions["q1"].correct is True
        assert result.questions["q2"].correct is False

    def test_grade_quiz_none_correct(self):
        """All wrong answers gives zero score."""
        quiz = Quiz(
            quiz_id="q001",
            title="Test",
            questions=[
                Question(id="q1", type="mcq_single", text="?", points=2, correct="A"),
                Question(id="q2", type="numeric", text="?", points=1, correct="8"),
            ],
        )

        result = grade_quiz(quiz, {"q1": "B", "q2": "7"})

        assert result.score == 0
        assert result.max_score == 3
        assert result.percentage == 0.0

    def test_grade_quiz_missing_answers(self):
        """Missing answers are treated as incorrect."""
        quiz = Quiz(
            quiz_id="q001",
            title="Test",
            questions=[
                Question(id="q1", type="mcq_single", text="?", points=2, correct="A"),
                Question(id="q2", type="numeric", text="?", points=1, correct="8"),
            ],
        )

        result = grade_quiz(quiz, {"q1": "A"})  # q2 missing

        assert result.score == 2
        assert result.max_score == 3
        assert result.questions["q2"].correct is False

    def test_to_autograde_json(self):
        """Result can be converted to JSON format."""
        quiz = Quiz(
            quiz_id="q001",
            title="Test",
            questions=[
                Question(id="q1", type="mcq_single", text="?", points=2, correct="A"),
            ],
        )

        result = grade_quiz(quiz, {"q1": "B"})
        json_result = result.to_autograde_json()

        assert "q1" in json_result
        assert json_result["q1"]["correct"] is False
        assert json_result["q1"]["points"] == 0
        assert json_result["q1"]["max"] == 2
