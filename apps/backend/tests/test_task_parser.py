#!/usr/bin/env python3
"""
Tests for task_parser module.

TDD approach: Tests written FIRST, implementation follows.
"""

import pytest


class TestParseTaskIndicators:
    """Test parse_task_indicators() function."""

    def test_todo_prefix_creates_task(self):
        """todo: prefix creates a task with view='todo'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Create dashboard")
        
        assert result["is_task"] is True
        assert result["view"] == "todo"

    def test_kanban_prefix_creates_task(self):
        """kanban: prefix creates a task with view='kanban'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("kanban: Review PR")
        
        assert result["is_task"] is True
        assert result["view"] == "kanban"

    def test_no_task_prefix_returns_not_task(self):
        """Messages without task prefix return is_task=False."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("Just a regular message")
        
        assert result["is_task"] is False

    def test_domain_just_value_normalized(self):
        """domain:just-value normalizes to 'Just-Value'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Task domain:just-value")
        
        assert result["domain"] == "Just-Value"

    def test_domain_personal_normalized(self):
        """domain:personal normalizes to 'Personal'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Task domain:personal")
        
        assert result["domain"] == "Personal"

    def test_domain_ccbh_normalized(self):
        """domain:ccbh normalizes to 'CCBH'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Task domain:ccbh")
        
        assert result["domain"] == "CCBH"

    def test_project_indicator_parsed(self):
        """project:rvm extracts project name."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Build feature project:rvm")
        
        assert result["project"] == "rvm"

    def test_priority_p1_is_high(self):
        """p1 maps to priority='high'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Urgent task p1")
        
        assert result["priority"] == "high"

    def test_priority_p2_is_medium(self):
        """p2 maps to priority='medium'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Normal task p2")
        
        assert result["priority"] == "medium"

    def test_priority_p3_is_low(self):
        """p3 maps to priority='low'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Low priority task p3")
        
        assert result["priority"] == "low"

    def test_no_priority_defaults_to_medium(self):
        """No priority indicator defaults to 'medium'."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Task without priority")
        
        assert result["priority"] == "medium"

    def test_combined_indicators_all_parsed(self):
        """Combined indicators are all parsed correctly."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Create RVM dashboard domain:just-value project:rvm p1")
        
        assert result["is_task"] is True
        assert result["view"] == "todo"
        assert result["domain"] == "Just-Value"
        assert result["project"] == "rvm"
        assert result["priority"] == "high"
        assert result["clean_text"] == "Create RVM dashboard"

    def test_clean_text_strips_all_indicators(self):
        """clean_text contains only the task description."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("kanban: Fix login bug domain:personal project:app p2")
        
        assert result["clean_text"] == "Fix login bug"

    def test_case_insensitive_prefix(self):
        """Task prefixes are case-insensitive."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("TODO: Task with caps")
        
        assert result["is_task"] is True
        assert result["view"] == "todo"

    def test_no_domain_returns_none(self):
        """No domain indicator returns domain=None."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Task without domain")
        
        assert result["domain"] is None

    def test_no_project_returns_none(self):
        """No project indicator returns project=None."""
        from task_parser import parse_task_indicators
        
        result = parse_task_indicators("todo: Task without project")
        
        assert result["project"] is None


class TestStatusCommands:
    """Test status command detection."""

    def test_done_command_detected(self):
        """!done is recognized as status command."""
        from task_parser import is_status_command, parse_status_command
        
        assert is_status_command("!done") is True
        assert parse_status_command("!done") == "done"

    def test_progress_command_detected(self):
        """!progress is recognized as status command."""
        from task_parser import is_status_command, parse_status_command
        
        assert is_status_command("!progress") is True
        assert parse_status_command("!progress") == "in_progress"

    def test_blocked_command_detected(self):
        """!blocked is recognized as status command."""
        from task_parser import is_status_command, parse_status_command
        
        assert is_status_command("!blocked") is True
        assert parse_status_command("!blocked") == "blocked"

    def test_backlog_command_detected(self):
        """!backlog is recognized as status command."""
        from task_parser import is_status_command, parse_status_command
        
        assert is_status_command("!backlog") is True
        assert parse_status_command("!backlog") == "backlog"

    def test_regular_message_not_status_command(self):
        """Regular messages are not status commands."""
        from task_parser import is_status_command
        
        assert is_status_command("regular message") is False
        assert is_status_command("done") is False  # Missing !

    def test_status_command_case_insensitive(self):
        """Status commands are case-insensitive."""
        from task_parser import is_status_command, parse_status_command
        
        assert is_status_command("!DONE") is True
        assert parse_status_command("!Done") == "done"


class TestConstants:
    """Test module constants are exported."""

    def test_priority_map_exported(self):
        """PRIORITY_MAP constant is available."""
        from task_parser import PRIORITY_MAP
        
        assert PRIORITY_MAP["p1"] == "high"
        assert PRIORITY_MAP["p2"] == "medium"
        assert PRIORITY_MAP["p3"] == "low"

    def test_status_commands_exported(self):
        """STATUS_COMMANDS constant is available."""
        from task_parser import STATUS_COMMANDS
        
        assert "!done" in STATUS_COMMANDS
        assert "!progress" in STATUS_COMMANDS
        assert "!blocked" in STATUS_COMMANDS
        assert "!backlog" in STATUS_COMMANDS
