"""Quiz auto-grading service."""

import logging
from dataclasses import dataclass

from app.models.quiz import Question, Quiz

logger = logging.getLogger(__name__)


@dataclass
class QuestionResult:
    """Result of grading a single question."""

    correct: bool
    points: int
    max_points: int
    expected: str | list[str] | None = None
    got: str | list[str] | None = None


@dataclass
class GradeResult:
    """Result of grading an entire quiz."""

    score: int
    max_score: int
    questions: dict[str, QuestionResult]

    @property
    def percentage(self) -> float:
        """Calculate percentage score."""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100

    def to_autograde_json(self) -> dict:
        """Convert to JSON-serializable dict for storage."""
        return {
            q_id: {
                "correct": result.correct,
                "points": result.points,
                "max": result.max_points,
                "expected": result.expected,
                "got": result.got,
            }
            for q_id, result in self.questions.items()
        }


def grade_quiz(quiz: Quiz, answers: dict[str, str | list[str]]) -> GradeResult:
    """
    Grade a quiz submission.

    Args:
        quiz: Quiz object with questions and correct answers
        answers: Dict of question_id -> student answer(s)

    Returns:
        GradeResult with score and per-question results
    """
    results = {}
    total_score = 0

    for question in quiz.questions:
        student_answer = answers.get(question.id)
        result = grade_question(question, student_answer)
        results[question.id] = result
        total_score += result.points

    return GradeResult(
        score=total_score,
        max_score=quiz.total_points,
        questions=results,
    )


def grade_question(question: Question, answer: str | list[str] | None) -> QuestionResult:
    """
    Grade a single question.

    Args:
        question: Question object with correct answer
        answer: Student's answer

    Returns:
        QuestionResult with correctness and points
    """
    if question.type == "mcq_single":
        return grade_mcq_single(question, answer)
    elif question.type == "mcq_multi":
        return grade_mcq_multi(question, answer)
    elif question.type == "numeric":
        return grade_numeric(question, answer)
    elif question.type == "short_text":
        return grade_short_text(question, answer)
    else:
        logger.warning("Unknown question type: %s", question.type)
        return QuestionResult(
            correct=False,
            points=0,
            max_points=question.points,
            expected=question.correct,
            got=answer,
        )


def grade_mcq_single(question: Question, answer: str | None) -> QuestionResult:
    """Grade a single-choice MCQ."""
    expected = question.correct
    correct = answer == expected

    return QuestionResult(
        correct=correct,
        points=question.points if correct else 0,
        max_points=question.points,
        expected=expected if not correct else None,
        got=answer if not correct else None,
    )


def grade_mcq_multi(question: Question, answer: str | list[str] | None) -> QuestionResult:
    """
    Grade a multiple-choice MCQ.

    Student must select ALL correct options and NONE of the incorrect ones.
    """
    expected = set(question.correct) if question.correct else set()

    if answer is None:
        student_set = set()
    elif isinstance(answer, str):
        student_set = {answer}
    else:
        student_set = set(answer)

    correct = student_set == expected

    return QuestionResult(
        correct=correct,
        points=question.points if correct else 0,
        max_points=question.points,
        expected=sorted(expected) if not correct else None,
        got=sorted(student_set) if not correct else None,
    )


def grade_numeric(question: Question, answer: str | None) -> QuestionResult:
    """
    Grade a numeric answer question.

    Compares as strings to handle exact integer matching.
    """
    expected = str(question.correct).strip() if question.correct else ""

    if answer is None:
        student_answer = ""
    else:
        student_answer = str(answer).strip()

    # Try numeric comparison first
    try:
        expected_num = float(expected)
        student_num = float(student_answer)
        correct = expected_num == student_num
    except (ValueError, TypeError):
        # Fall back to string comparison
        correct = student_answer == expected

    return QuestionResult(
        correct=correct,
        points=question.points if correct else 0,
        max_points=question.points,
        expected=expected if not correct else None,
        got=student_answer if not correct else None,
    )


def grade_short_text(question: Question, answer: str | None) -> QuestionResult:
    """
    Grade a short text answer question.

    Case-insensitive, trimmed comparison.
    """
    expected = str(question.correct).strip().lower() if question.correct else ""

    if answer is None:
        student_answer = ""
    else:
        student_answer = str(answer).strip().lower()

    correct = student_answer == expected

    return QuestionResult(
        correct=correct,
        points=question.points if correct else 0,
        max_points=question.points,
        expected=question.correct if not correct else None,
        got=answer if not correct else None,
    )
