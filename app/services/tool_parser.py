"""Parser for tool reference markdown files with custom interactive blocks."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import markdown
import yaml


@dataclass
class ToolScenario:
    """A scenario/exercise for a tool."""

    id: str
    title: str
    level: str  # beginner, intermediate
    goal: str
    hint: str = ""
    command: str = ""
    expected_output: str = ""


@dataclass
class ToolQuiz:
    """An inline quiz question."""

    id: str
    question: str
    options: list[dict]  # [{"text": "...", "correct": bool}, ...]


@dataclass
class CommandBuilder:
    """Configuration for the command builder UI."""

    id: str
    tool_name: str
    scan_types: list[dict] = field(
        default_factory=list
    )  # [{"name": "...", "flag": "...", "desc": "..."}, ...]
    options: list[dict] = field(
        default_factory=list
    )  # [{"name": "...", "flag": "...", "desc": "..."}, ...]
    target_placeholder: str = "192.168.1.1"


def get_available_tools(tools_dir: Path) -> list[dict]:
    """
    Get list of available tools from the tools directory.

    Returns list of dicts with 'id', 'name', 'description'.
    """
    tools = []

    if not tools_dir.exists():
        return tools

    for md_file in sorted(tools_dir.glob("*.md")):
        if md_file.name.startswith("_"):
            continue

        tool_id = md_file.stem
        content = md_file.read_text(encoding="utf-8")

        # Extract title from first # header
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else tool_id.title()

        # Extract description from first paragraph after title
        desc_match = re.search(r"^#\s+.+\n\n(.+?)(?:\n\n|$)", content, re.MULTILINE | re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        # Truncate description
        if len(description) > 150:
            description = description[:147] + "..."

        tools.append(
            {
                "id": tool_id,
                "name": title,
                "description": description,
            }
        )

    return tools


def parse_tool_content(content: str, tool_id: str) -> dict[str, Any]:
    """
    Parse tool markdown content with custom blocks.

    Returns dict with:
    - title: str
    - content: str (HTML)
    - scenarios: list[ToolScenario]
    - command_builder: CommandBuilder | None
    - quizzes: list[ToolQuiz]
    """
    # Extract frontmatter if present
    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                pass
            body = parts[2]

    # Extract title from first # header
    title = frontmatter.get("title", "")
    if not title:
        title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        title = title_match.group(1) if title_match else tool_id.title()

    # Parse custom blocks before converting markdown
    scenarios = []
    quizzes = []
    command_builder = None

    # Parse :::command-builder blocks
    cb_pattern = r":::command-builder\{id=[\"']([^\"']+)[\"']\}\n(.*?):::"
    cb_match = re.search(cb_pattern, body, re.DOTALL)
    if cb_match:
        cb_id = cb_match.group(1)
        cb_yaml = cb_match.group(2).strip()
        try:
            cb_config = yaml.safe_load(cb_yaml) or {}
            command_builder = CommandBuilder(
                id=cb_id,
                tool_name=cb_config.get("tool_name", tool_id),
                scan_types=cb_config.get("scan_types", []),
                options=cb_config.get("options", []),
                target_placeholder=cb_config.get("target_placeholder", "192.168.1.1"),
            )
        except yaml.YAMLError:
            pass
        # Remove from body
        body = body[: cb_match.start()] + body[cb_match.end() :]

    # Parse :::scenario blocks
    scenario_pattern = (
        r":::scenario\{id=[\"']([^\"']+)[\"']\s+level=[\"']([^\"']+)[\"']\}\n(.*?):::"
    )
    for match in re.finditer(scenario_pattern, body, re.DOTALL):
        s_id = match.group(1)
        s_level = match.group(2)
        s_content = match.group(3).strip()

        # Parse scenario content (YAML-like)
        try:
            s_config = yaml.safe_load(s_content) or {}
            scenarios.append(
                ToolScenario(
                    id=s_id,
                    title=s_config.get("title", "Scenario"),
                    level=s_level,
                    goal=s_config.get("goal", ""),
                    hint=s_config.get("hint", ""),
                    command=s_config.get("command", ""),
                    expected_output=s_config.get("expected_output", ""),
                )
            )
        except yaml.YAMLError:
            pass

    # Remove scenario blocks from body
    body = re.sub(scenario_pattern, "", body, flags=re.DOTALL)

    # Parse :::quiz blocks
    quiz_pattern = r":::quiz\{id=[\"']([^\"']+)[\"']\}\n(.*?):::"
    for match in re.finditer(quiz_pattern, body, re.DOTALL):
        q_id = match.group(1)
        q_content = match.group(2).strip()

        # Parse quiz content
        lines = q_content.split("\n")
        question = ""
        options = []

        for line in lines:
            line = line.strip()
            if line.startswith("Q:"):
                question = line[2:].strip()
            elif line.startswith("- [x]"):
                options.append({"text": line[5:].strip(), "correct": True})
            elif line.startswith("- [ ]"):
                options.append({"text": line[5:].strip(), "correct": False})

        if question and options:
            quizzes.append(ToolQuiz(id=q_id, question=question, options=options))

    # Remove quiz blocks from body
    body = re.sub(quiz_pattern, "", body, flags=re.DOTALL)

    # Parse :::hint blocks and convert to HTML details
    hint_pattern = r":::hint\{title=[\"']([^\"']+)[\"']\}\n(.*?):::"

    def replace_hint(match):
        hint_title = match.group(1)
        hint_content = match.group(2).strip()
        return f'<details class="hint-block"><summary>{hint_title}</summary><div class="hint-content">{hint_content}</div></details>'

    body = re.sub(hint_pattern, replace_hint, body, flags=re.DOTALL)

    # Parse :::output blocks and convert to HTML details
    output_pattern = r":::output\{title=[\"']([^\"']+)[\"']\}\n(.*?):::"

    def replace_output(match):
        output_title = match.group(1)
        output_content = match.group(2).strip()
        # Escape HTML in output
        output_content = (
            output_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        return f'<details class="output-block"><summary>{output_title}</summary><pre class="output-content">{output_content}</pre></details>'

    body = re.sub(output_pattern, replace_output, body, flags=re.DOTALL)

    # Convert remaining markdown to HTML
    html_content = markdown.markdown(
        body, extensions=["fenced_code", "tables", "toc", "codehilite"]
    )

    return {
        "title": title,
        "content": html_content,
        "scenarios": scenarios,
        "command_builder": command_builder,
        "quizzes": quizzes,
    }
