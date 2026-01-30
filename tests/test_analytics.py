"""Tests for analytics service."""

import json
from datetime import datetime

import pytest

from app.models.quiz import Question, Quiz, QuizSubmission
from app.services.analytics import (
    QuestionStats,
    QuizAnalytics,
    compute_quiz_analytics,
    get_best_submissions,
)


def make_submission(
    student_id: str,
    quiz_id: str,
    score: float,
    max_score: float,
    answers: dict,
    autograde: dict,
) -> QuizSubmission:
    """Helper to create a QuizSubmission."""
    return QuizSubmission(
        submitted_at=datetime.utcnow(),
        quiz_id=quiz_id,
        attempt=1,
        student_id=student_id,
        email=f"{student_id}@example.com",
        answers_json=json.dumps(answers),
        score=score,
        max_score=max_score,
        autograde_json=json.dumps(autograde),
        source="web",
    )


class TestGetBestSubmissions:
    """Tests for get_best_submissions function."""

    def test_empty_list_returns_empty_dict(self):
        """Empty submissions list returns empty dict."""
        result = get_best_submissions([])
        assert result == {}

    def test_single_submission(self):
        """Single submission is returned."""
        sub = make_submission("stu_001", "q001", 8, 10, {}, {})
        result = get_best_submissions([sub])
        assert len(result) == 1
        assert result["stu_001"] == sub

    def test_returns_highest_score_per_student(self):
        """Returns highest scoring submission for each student."""
        sub1 = make_submission("stu_001", "q001", 5, 10, {}, {})
        sub2 = make_submission("stu_001", "q001", 8, 10, {}, {})
        sub3 = make_submission("stu_001", "q001", 6, 10, {}, {})

        result = get_best_submissions([sub1, sub2, sub3])
        assert len(result) == 1
        assert result["stu_001"].score == 8

    def test_multiple_students(self):
        """Returns best submission for each student separately."""
        subs = [
            make_submission("stu_001", "q001", 5, 10, {}, {}),
            make_submission("stu_001", "q001", 8, 10, {}, {}),
            make_submission("stu_002", "q001", 10, 10, {}, {}),
            make_submission("stu_002", "q001", 7, 10, {}, {}),
        ]

        result = get_best_submissions(subs)
        assert len(result) == 2
        assert result["stu_001"].score == 8
        assert result["stu_002"].score == 10


class TestComputeQuizAnalytics:
    """Tests for compute_quiz_analytics function."""

    @pytest.fixture
    def sample_quiz(self):
        """Create a sample quiz with 2 questions."""
        return Quiz(
            quiz_id="q001",
            title="Test Quiz",
            questions=[
                Question(
                    id="q1",
                    type="mcq_single",
                    text="What is 2+2?",
                    points=5,
                    options=["3", "4", "5"],
                    correct="4",
                ),
                Question(
                    id="q2",
                    type="mcq_single",
                    text="What is Python?",
                    points=5,
                    options=["A snake", "A language", "Both"],
                    correct="Both",
                ),
            ],
        )

    def test_no_submissions(self, sample_quiz):
        """No submissions results in zero stats."""
        analytics = compute_quiz_analytics(sample_quiz, [], 10)

        assert analytics.quiz_id == "q001"
        assert analytics.title == "Test Quiz"
        assert analytics.total_students == 10
        assert analytics.completed_students == 0
        assert analytics.avg_score == 0.0
        assert analytics.completion_rate == 0.0
        assert len(analytics.question_stats) == 2

    def test_basic_analytics(self, sample_quiz):
        """Basic analytics computation with submissions."""
        submissions = [
            make_submission(
                "stu_001",
                "q001",
                10,
                10,
                {"q1": "4", "q2": "Both"},
                {"q1": {"correct": True}, "q2": {"correct": True}},
            ),
            make_submission(
                "stu_002",
                "q001",
                5,
                10,
                {"q1": "3", "q2": "Both"},
                {"q1": {"correct": False}, "q2": {"correct": True}},
            ),
        ]

        analytics = compute_quiz_analytics(sample_quiz, submissions, 10)

        assert analytics.completed_students == 2
        assert analytics.completion_rate == 20.0
        assert analytics.avg_score == 75.0  # (10 + 5) / (10 + 10) * 100

        # Check question stats
        q1_stats = analytics.question_stats[0]
        assert q1_stats.correct_count == 1  # Only stu_001 got it right
        assert q1_stats.correct_pct == 50.0
        assert q1_stats.option_distribution["4"] == 1
        assert q1_stats.option_distribution["3"] == 1

        q2_stats = analytics.question_stats[1]
        assert q2_stats.correct_count == 2  # Both got it right
        assert q2_stats.correct_pct == 100.0

    def test_uses_best_submission_only(self, sample_quiz):
        """Only best submission per student is used for analytics."""
        submissions = [
            # Student 1: first attempt wrong, second attempt correct
            make_submission(
                "stu_001",
                "q001",
                0,
                10,
                {"q1": "3", "q2": "A snake"},
                {"q1": {"correct": False}, "q2": {"correct": False}},
            ),
            make_submission(
                "stu_001",
                "q001",
                10,
                10,
                {"q1": "4", "q2": "Both"},
                {"q1": {"correct": True}, "q2": {"correct": True}},
            ),
        ]

        analytics = compute_quiz_analytics(sample_quiz, submissions, 10)

        # Should only count 1 student (best submission)
        assert analytics.completed_students == 1

        # Should use the correct answers from best attempt
        q1_stats = analytics.question_stats[0]
        assert q1_stats.correct_count == 1
        assert q1_stats.option_distribution["4"] == 1
        assert q1_stats.option_distribution["3"] == 0

    def test_handles_invalid_json(self, sample_quiz):
        """Handles invalid JSON in submissions gracefully."""
        sub = QuizSubmission(
            submitted_at=datetime.utcnow(),
            quiz_id="q001",
            attempt=1,
            student_id="stu_001",
            email="test@example.com",
            answers_json="invalid json",
            score=5,
            max_score=10,
            autograde_json="also invalid",
            source="web",
        )

        analytics = compute_quiz_analytics(sample_quiz, [sub], 10)

        # Should not crash, just have 0 correct
        assert analytics.completed_students == 1
        for qs in analytics.question_stats:
            assert qs.correct_count == 0


class TestQuizAnalyticsCompletionRate:
    """Tests for QuizAnalytics completion_rate property."""

    def test_completion_rate_calculation(self):
        """Completion rate is calculated correctly."""
        analytics = QuizAnalytics(
            quiz_id="q001",
            title="Test",
            total_students=100,
            completed_students=75,
            avg_score=80.0,
        )
        assert analytics.completion_rate == 75.0

    def test_completion_rate_zero_students(self):
        """Completion rate is 0 when no students enrolled."""
        analytics = QuizAnalytics(
            quiz_id="q001",
            title="Test",
            total_students=0,
            completed_students=0,
            avg_score=0.0,
        )
        assert analytics.completion_rate == 0.0
