"""Analytics computation service for quiz performance."""

import json
from dataclasses import dataclass, field

from app.models.quiz import Quiz, QuizSubmission


@dataclass
class QuestionStats:
    """Statistics for a single quiz question."""

    question_id: str
    text: str
    correct_count: int
    total_count: int
    correct_pct: float
    option_distribution: dict[str, int] = field(default_factory=dict)
    correct_answer: str | list[str] | None = None


@dataclass
class QuizAnalytics:
    """Analytics data for a quiz."""

    quiz_id: str
    title: str
    total_students: int
    completed_students: int
    avg_score: float
    question_stats: list[QuestionStats] = field(default_factory=list)

    @property
    def completion_rate(self) -> float:
        """Calculate completion rate as percentage."""
        if self.total_students == 0:
            return 0.0
        return (self.completed_students / self.total_students) * 100


def get_best_submissions(
    submissions: list[QuizSubmission],
) -> dict[str, QuizSubmission]:
    """
    Get the best submission for each student.

    Returns dict of student_id -> best submission (highest score).
    """
    best: dict[str, QuizSubmission] = {}

    for sub in submissions:
        student_id = sub.student_id
        if student_id not in best or sub.score > best[student_id].score:
            best[student_id] = sub

    return best


def compute_quiz_analytics(
    quiz: Quiz,
    submissions: list[QuizSubmission],
    total_students: int,
) -> QuizAnalytics:
    """
    Compute per-question analytics for a quiz.

    Uses only the best submission per student.
    """
    best_submissions = get_best_submissions(submissions)
    completed_students = len(best_submissions)

    # Calculate average score
    if completed_students > 0:
        total_score = sum(sub.score for sub in best_submissions.values())
        total_max = sum(sub.max_score for sub in best_submissions.values())
        avg_score = (total_score / total_max * 100) if total_max > 0 else 0.0
    else:
        avg_score = 0.0

    # Compute per-question stats
    question_stats = []

    for question in quiz.questions:
        correct_count = 0
        option_dist: dict[str, int] = {}

        # Initialize option distribution for MCQ questions
        if question.is_mcq:
            for opt in question.options:
                option_dist[opt] = 0

        # Analyze each best submission
        for sub in best_submissions.values():
            try:
                autograde = json.loads(sub.autograde_json)
            except (json.JSONDecodeError, TypeError):
                autograde = {}

            try:
                answers = json.loads(sub.answers_json)
            except (json.JSONDecodeError, TypeError):
                answers = {}

            # Check if question was answered correctly
            q_result = autograde.get(question.id, {})
            if q_result.get("correct", False):
                correct_count += 1

            # Tally MCQ option selections
            if question.is_mcq:
                answer = answers.get(question.id)
                if answer:
                    if isinstance(answer, list):
                        for opt in answer:
                            if opt in option_dist:
                                option_dist[opt] += 1
                    elif answer in option_dist:
                        option_dist[answer] += 1

        # Calculate correct percentage
        correct_pct = (correct_count / completed_students * 100) if completed_students > 0 else 0.0

        question_stats.append(
            QuestionStats(
                question_id=question.id,
                text=question.text,
                correct_count=correct_count,
                total_count=completed_students,
                correct_pct=correct_pct,
                option_distribution=option_dist,
                correct_answer=question.correct,
            )
        )

    return QuizAnalytics(
        quiz_id=quiz.quiz_id,
        title=quiz.title,
        total_students=total_students,
        completed_students=completed_students,
        avg_score=avg_score,
        question_stats=question_stats,
    )
