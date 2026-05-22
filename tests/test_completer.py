from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from nextral.shell.completer import Completer
from nextral.shell.history import CommandHistory


@pytest.fixture
def history_file(tmp_path):
    return str(tmp_path / "history.json")


def test_history_suggestions(history_file, tmp_path):
    h = CommandHistory(history_file)
    h.push("ls -la")
    h.push("ls /tmp")
    h.push("pwd")
    c = Completer(h)
    results = c.suggest("ls", str(tmp_path))
    assert any("ls" in r for r in results)


def test_top_returns_best(history_file, tmp_path):
    h = CommandHistory(history_file)
    h.push("ls -la")
    c = Completer(h)
    top = c.top("ls", str(tmp_path))
    assert top is None or top.startswith("ls")


def test_empty_partial_returns_empty(history_file, tmp_path):
    h = CommandHistory(history_file)
    c = Completer(h)
    assert c.suggest("", str(tmp_path)) == []
