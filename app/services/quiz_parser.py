"""Quiz markdown parser."""

import logging
import re
from pathlib import Path

import yaml

from app.models.quiz import Question, Quiz
from app.services.cache import cached

logger = logging.getLogger(__name__)

# Regex patterns
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
QUESTION_HEADER_PATTERN = re.compile(
    r"^##\s+Q(\d+)\s*\[([^,\]]+),\s*(\d+)\s*pts?\]",
    re.MULTILINE,
)
MCQ_OPTION_PATTERN = re.compile(r"^-\s*\[([ xX])\]\s*(.+)$", re.MULTILINE)
ANSWER_LINE_PATTERN = re.compile(r"^answer:\s*(.+)$", re.MULTILINE | re.IGNORECASE)


def parse_quiz_file(file_path: Path, quiz_id: str) -> Quiz | None:
    """
    Parse a quiz markdown file into a Quiz object.

    Args:
        file_path: Path to the markdown file
        quiz_id: Quiz ID to assign

    Returns:
        Quiz object or None if parsing fails
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        return parse_quiz_content(content, quiz_id)
    except FileNotFoundError:
        logger.error("Quiz file not found: %s", file_path)
        return None
    except Exception as e:
        logger.error("Error parsing quiz file %s: %s", file_path, e)
        return None


def parse_quiz_content(content: str, quiz_id: str) -> Quiz:
    """
    Parse quiz markdown content into a Quiz object.

    Args:
        content: Markdown content string
        quiz_id: Quiz ID to assign

    Returns:
        Quiz object
    """
    # Extract frontmatter
    title = "Untitled Quiz"
    frontmatter_match = FRONTMATTER_PATTERN.match(content)
    if frontmatter_match:
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            title = frontmatter.get("title", title)
        except yaml.YAMLError as e:
            logger.warning("Failed to parse frontmatter: %s", e)

    # Find all questions
    questions = []
    question_matches = list(QUESTION_HEADER_PATTERN.finditer(content))

    for i, match in enumerate(question_matches):
        q_num = match.group(1)
        q_type = match.group(2).strip().lower()
        q_points = int(match.group(3))

        # Get question content (from this header to next header or end)
        start_pos = match.end()
        end_pos = question_matches[i + 1].start() if i + 1 < len(question_matches) else len(content)
        q_content = content[start_pos:end_pos].strip()

        question = parse_question(f"q{q_num}", q_type, q_points, q_content)
        if question:
            questions.append(question)

    return Quiz(quiz_id=quiz_id, title=title, questions=questions)


def parse_question(q_id: str, q_type: str, points: int, content: str) -> Question | None:
    """
    Parse a single question from its content.

    Args:
        q_id: Question ID
        q_type: Question type (mcq_single, mcq_multi, numeric, short_text)
        points: Points for the question
        content: Question content (text + options/answer)

    Returns:
        Question object or None if parsing fails
    """
    # Split content into question text and answer section
    lines = content.split("\n")
    text_lines = []
    options = []
    correct = []

    if q_type in ("mcq_single", "mcq_multi"):
        # Parse MCQ options
        in_options = False
        for line in lines:
            option_match = MCQ_OPTION_PATTERN.match(line)
            if option_match:
                in_options = True
                is_correct = option_match.group(1).lower() == "x"
                option_text = option_match.group(2).strip()
                options.append(option_text)
                if is_correct:
                    correct.append(option_text)
            elif not in_options:
                text_lines.append(line)

        question_text = "\n".join(text_lines).strip()

        # For single choice, correct should be a string
        if q_type == "mcq_single":
            correct_answer = correct[0] if correct else None
        else:
            correct_answer = correct

        return Question(
            id=q_id,
            type=q_type,
            text=question_text,
            points=points,
            options=options,
            correct=correct_answer,
        )

    elif q_type in ("numeric", "short_text"):
        # Parse answer line
        answer_match = ANSWER_LINE_PATTERN.search(content)
        if answer_match:
            answer = answer_match.group(1).strip()
            # Get question text (everything before "answer:")
            question_text = content[: answer_match.start()].strip()
        else:
            logger.warning("No answer found for question %s", q_id)
            question_text = content.strip()
            answer = ""

        return Question(
            id=q_id,
            type=q_type,
            text=question_text,
            points=points,
            correct=answer,
        )

    else:
        logger.warning("Unknown question type: %s", q_type)
        return None


@cached(ttl_seconds=900, prefix="quiz_content")
def get_parsed_quiz(content_path: str, quiz_id: str) -> Quiz | None:
    """
    Get a parsed quiz from a content path (with caching).

    Args:
        content_path: Relative path to quiz markdown file
        quiz_id: Quiz ID

    Returns:
        Parsed Quiz object or None
    """
    # Resolve path relative to project root
    base_path = Path(__file__).parent.parent.parent  # Go up from services to project root
    file_path = base_path / content_path

    return parse_quiz_file(file_path, quiz_id)
