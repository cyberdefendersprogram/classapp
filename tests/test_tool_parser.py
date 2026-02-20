"""Tests for tool markdown parser."""

from app.services.tool_parser import (
    CommandBuilder,
    ToolQuiz,
    ToolScenario,
    get_available_tools,
    parse_tool_content,
)


class TestToolParser:
    """Tests for parsing tool markdown."""

    def test_parse_title_from_header(self):
        """Parser extracts title from # header."""
        content = """# Nmap

A network scanning tool.
"""
        result = parse_tool_content(content, "nmap")
        assert result["title"] == "Nmap"

    def test_parse_title_from_frontmatter(self):
        """Parser extracts title from frontmatter if present."""
        content = """---
title: Network Mapper
---

# Nmap

A network scanning tool.
"""
        result = parse_tool_content(content, "nmap")
        assert result["title"] == "Network Mapper"

    def test_parse_command_builder(self):
        """Parser extracts command builder configuration."""
        content = """# Test Tool

:::command-builder{id="test-builder"}
tool_name: nmap
target_placeholder: "192.168.1.1"
scan_types:
  - name: "Ping Scan"
    flag: "-sn"
    desc: "Host discovery"
options:
  - name: "Version"
    flag: "-sV"
    desc: "Version detection"
:::

Some content.
"""
        result = parse_tool_content(content, "test")
        cb = result["command_builder"]

        assert cb is not None
        assert isinstance(cb, CommandBuilder)
        assert cb.id == "test-builder"
        assert cb.tool_name == "nmap"
        assert cb.target_placeholder == "192.168.1.1"
        assert len(cb.scan_types) == 1
        assert cb.scan_types[0]["name"] == "Ping Scan"
        assert cb.scan_types[0]["flag"] == "-sn"
        assert len(cb.options) == 1
        assert cb.options[0]["name"] == "Version"

    def test_parse_scenario(self):
        """Parser extracts scenarios."""
        content = """# Test Tool

:::scenario{id="scenario-1" level="beginner"}
title: "Test Scenario"
goal: "Learn the basics."
hint: "Try the help command."
command: "tool --help"
expected_output: |
  Usage: tool [options]
:::

Some content.
"""
        result = parse_tool_content(content, "test")
        scenarios = result["scenarios"]

        assert len(scenarios) == 1
        s = scenarios[0]
        assert isinstance(s, ToolScenario)
        assert s.id == "scenario-1"
        assert s.title == "Test Scenario"
        assert s.level == "beginner"
        assert s.goal == "Learn the basics."
        assert s.hint == "Try the help command."
        assert s.command == "tool --help"
        assert "Usage: tool" in s.expected_output

    def test_parse_multiple_scenarios(self):
        """Parser extracts multiple scenarios."""
        content = """# Test Tool

:::scenario{id="s1" level="beginner"}
title: "First"
goal: "Goal 1"
:::

:::scenario{id="s2" level="intermediate"}
title: "Second"
goal: "Goal 2"
:::
"""
        result = parse_tool_content(content, "test")
        scenarios = result["scenarios"]

        assert len(scenarios) == 2
        assert scenarios[0].id == "s1"
        assert scenarios[0].level == "beginner"
        assert scenarios[1].id == "s2"
        assert scenarios[1].level == "intermediate"

    def test_parse_quiz(self):
        """Parser extracts inline quizzes."""
        content = """# Test Tool

:::quiz{id="quiz-1"}
Q: What flag enables version detection?
- [ ] -O
- [x] -sV
- [ ] -sS
:::
"""
        result = parse_tool_content(content, "test")
        quizzes = result["quizzes"]

        assert len(quizzes) == 1
        q = quizzes[0]
        assert isinstance(q, ToolQuiz)
        assert q.id == "quiz-1"
        assert "version detection" in q.question.lower()
        assert len(q.options) == 3
        assert q.options[0]["text"] == "-O"
        assert q.options[0]["correct"] is False
        assert q.options[1]["text"] == "-sV"
        assert q.options[1]["correct"] is True
        assert q.options[2]["text"] == "-sS"
        assert q.options[2]["correct"] is False

    def test_parse_hint_block(self):
        """Parser converts hint blocks to HTML details."""
        content = """# Test Tool

:::hint{title="Helpful Hint"}
This is a hint.
:::
"""
        result = parse_tool_content(content, "test")
        html = result["content"]

        assert '<details class="hint-block">' in html
        assert "<summary>Helpful Hint</summary>" in html
        assert "This is a hint." in html

    def test_parse_output_block(self):
        """Parser converts output blocks to HTML details."""
        content = """# Test Tool

:::output{title="Expected Output"}
Line 1
Line 2
:::
"""
        result = parse_tool_content(content, "test")
        html = result["content"]

        assert '<details class="output-block">' in html
        assert "<summary>Expected Output</summary>" in html
        assert "Line 1" in html

    def test_parse_markdown_conversion(self):
        """Parser converts remaining markdown to HTML."""
        content = """# Test Tool

## Overview

This is a **bold** word.

- Item 1
- Item 2
"""
        result = parse_tool_content(content, "test")
        html = result["content"]

        assert "<h2" in html  # h2 header
        assert "<strong>bold</strong>" in html
        assert "<li>" in html

    def test_parse_complete_tool(self):
        """Parser handles a complete tool file."""
        content = """# Nmap

Network scanner tool.

:::command-builder{id="nmap-builder"}
tool_name: nmap
scan_types:
  - name: "SYN"
    flag: "-sS"
    desc: "SYN scan"
options:
  - name: "Version"
    flag: "-sV"
    desc: "Version detection"
:::

## Overview

Nmap is great.

:::scenario{id="s1" level="beginner"}
title: "Basic Scan"
goal: "Scan a target."
command: "nmap target"
:::

:::quiz{id="q1"}
Q: What is Nmap?
- [x] Network scanner
- [ ] Text editor
:::

## Tips

Use `-T4` for speed.
"""
        result = parse_tool_content(content, "nmap")

        assert result["title"] == "Nmap"
        assert result["command_builder"] is not None
        assert len(result["scenarios"]) == 1
        assert len(result["quizzes"]) == 1
        assert "<h2" in result["content"]


class TestGetAvailableTools:
    """Tests for tool discovery."""

    def test_get_tools_from_directory(self, tmp_path):
        """Gets tools from directory."""
        # Create test tool files
        (tmp_path / "nmap.md").write_text("# Nmap\n\nNetwork scanner.")
        (tmp_path / "sqlmap.md").write_text("# SQLMap\n\nSQL injection tool.")

        tools = get_available_tools(tmp_path)

        assert len(tools) == 2
        names = [t["name"] for t in tools]
        assert "Nmap" in names
        assert "SQLMap" in names

    def test_get_tools_excludes_underscore_files(self, tmp_path):
        """Excludes files starting with underscore."""
        (tmp_path / "nmap.md").write_text("# Nmap\n\nDescription.")
        (tmp_path / "_index.md").write_text("# Index\n\nLanding page.")

        tools = get_available_tools(tmp_path)

        assert len(tools) == 1
        assert tools[0]["id"] == "nmap"

    def test_get_tools_empty_directory(self, tmp_path):
        """Returns empty list for empty directory."""
        tools = get_available_tools(tmp_path)
        assert tools == []

    def test_get_tools_nonexistent_directory(self, tmp_path):
        """Returns empty list for nonexistent directory."""
        nonexistent = tmp_path / "nonexistent"
        tools = get_available_tools(nonexistent)
        assert tools == []

    def test_get_tools_extracts_description(self, tmp_path):
        """Extracts description from first paragraph."""
        (tmp_path / "tool.md").write_text("# My Tool\n\nThis is a great tool for testing.")

        tools = get_available_tools(tmp_path)

        assert len(tools) == 1
        assert "great tool" in tools[0]["description"]

    def test_get_tools_truncates_long_description(self, tmp_path):
        """Truncates long descriptions."""
        long_desc = "A" * 200
        (tmp_path / "tool.md").write_text(f"# Tool\n\n{long_desc}")

        tools = get_available_tools(tmp_path)

        assert len(tools[0]["description"]) <= 153  # 150 + "..."
        assert tools[0]["description"].endswith("...")
