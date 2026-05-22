from __future__ import annotations

import json
import pytest
from pathlib import Path

from nextral.shell.history import CommandHistory


@pytest.fixture
def history_file(tmp_path):
    return str(tmp_path / "history.json")


def test_push_and_recall(history_file):
    h = CommandHistory(history_file, limit=100)
    h.push("ls")
    h.push("pwd")
    assert h.recall_prev() == "pwd"
    assert h.recall_prev() == "ls"
    assert h.recall_next() == "pwd"


def test_push_dedupes_consecutive(history_file):
    h = CommandHistory(history_file)
    h.push("ls")
    h.push("ls")
    entries = h.all_entries()
    assert entries.count("ls") == 1


def test_search(history_file):
    h = CommandHistory(history_file)
    h.push("ls -la")
    h.push("ls /tmp")
    h.push("pwd")
    results = h.search("ls")
    assert "ls /tmp" in results
    assert "ls -la" in results
    assert "pwd" not in results


def test_recall_next_clears_at_end(history_file):
    h = CommandHistory(history_file)
    h.push("a")
    h.recall_prev()
    result = h.recall_next()
    assert result == ""


def test_persistence(history_file):
    h = CommandHistory(history_file)
    h.push("echo hello")
    h2 = CommandHistory(history_file)
    assert "echo hello" in h2.all_entries()


def test_limit_respected(history_file):
    h = CommandHistory(history_file, limit=5)
    for i in range(10):
        h.push(f"cmd{i}")
    assert len(h.all_entries()) <= 5
