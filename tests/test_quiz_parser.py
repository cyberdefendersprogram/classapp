"""Tests for quiz markdown parser."""

import pytest

from app.services.quiz_parser import parse_quiz_content


class TestQuizParser:
    """Tests for parsing quiz markdown."""

    def test_parse_frontmatter_title(self):
        """Parser extracts title from frontmatter."""
        content = """---
title: Test Quiz
---

## Q1 [mcq_single, 2pts]

What is 1+1?

- [ ] 1
- [x] 2
- [ ] 3
"""
        quiz = parse_quiz_content(content, "q001")
        assert quiz.title == "Test Quiz"

    def test_parse_mcq_single(self):
        """Parser correctly parses single-choice MCQ."""
        content = """---
title: Test
---

## Q1 [mcq_single, 2pts]

What is 2+2?

- [ ] 3
- [x] 4
- [ ] 5
"""
        quiz = parse_quiz_content(content, "q001")
        assert len(quiz.questions) == 1

        q = quiz.questions[0]
        assert q.id == "q1"
        assert q.type == "mcq_single"
        assert q.points == 2
        assert q.options == ["3", "4", "5"]
        assert q.correct == "4"

    def test_parse_mcq_multi(self):
        """Parser correctly parses multi-choice MCQ."""
        content = """---
title: Test
---

## Q1 [mcq_multi, 3pts]

Select prime numbers:

- [x] 2
- [x] 3
- [ ] 4
- [x] 5
"""
        quiz = parse_quiz_content(content, "q001")
        q = quiz.questions[0]

        assert q.type == "mcq_multi"
        assert q.points == 3
        assert q.options == ["2", "3", "4", "5"]
        assert set(q.correct) == {"2", "3", "5"}

    def test_parse_numeric(self):
        """Parser correctly parses numeric question."""
        content = """---
title: Test
---

## Q1 [numeric, 1pt]

How many bits in a byte?

answer: 8
"""
        quiz = parse_quiz_content(content, "q001")
        q = quiz.questions[0]

        assert q.type == "numeric"
        assert q.points == 1
        assert q.correct == "8"
        assert "bits" in q.text.lower()

    def test_parse_short_text(self):
        """Parser correctly parses short text question."""
        content = """---
title: Test
---

## Q1 [short_text, 2pts]

What command lists files?

answer: ls
"""
        quiz = parse_quiz_content(content, "q001")
        q = quiz.questions[0]

        assert q.type == "short_text"
        assert q.points == 2
        assert q.correct == "ls"

    def test_parse_multiple_questions(self):
        """Parser handles multiple questions."""
        content = """---
title: Multi Question Quiz
---

## Q1 [mcq_single, 1pt]

Question 1?

- [x] A
- [ ] B

## Q2 [numeric, 2pts]

Question 2?

answer: 42

## Q3 [short_text, 1pt]

Question 3?

answer: test
"""
        quiz = parse_quiz_content(content, "q001")

        assert quiz.title == "Multi Question Quiz"
        assert len(quiz.questions) == 3
        assert quiz.total_points == 4  # 1 + 2 + 1

        assert quiz.questions[0].type == "mcq_single"
        assert quiz.questions[1].type == "numeric"
        assert quiz.questions[2].type == "short_text"

    def test_parse_no_frontmatter(self):
        """Parser handles missing frontmatter."""
        content = """## Q1 [mcq_single, 1pt]

Test?

- [x] Yes
- [ ] No
"""
        quiz = parse_quiz_content(content, "q001")

        assert quiz.title == "Untitled Quiz"
        assert len(quiz.questions) == 1

    def test_quiz_id_assigned(self):
        """Parser assigns provided quiz ID."""
        content = """---
title: Test
---

## Q1 [mcq_single, 1pt]

Test?

- [x] A
- [ ] B
"""
        quiz = parse_quiz_content(content, "quiz_123")
        assert quiz.quiz_id == "quiz_123"
