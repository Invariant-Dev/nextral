from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from nextral.shell.router import CommandRouter


def _make_router():
    session = MagicMock()
    pm = MagicMock()
    router = CommandRouter(session, pm)
    pane = MagicMock()
    return router, session, pm, pane


def test_empty_command_ignored():
    router, session, pm, pane = _make_router()
    router.dispatch("", pane)
    session.send.assert_not_called()


def test_shell_command_goes_to_session():
    router, session, pm, pane = _make_router()
    pm.get_by_alias.return_value = None
    router.dispatch("ls -la", pane)
    session.send.assert_called_once_with("ls -la")


def test_plugin_alias_routes_to_plugin():
    router, session, pm, pane = _make_router()
    plugin = MagicMock()
    pm.get_by_alias.return_value = plugin
    router.dispatch("!ping 8.8.8.8", pane)
    plugin.run.assert_called_once_with(["8.8.8.8"], pane)
    session.send.assert_not_called()


def test_unknown_plugin_alias():
    router, session, pm, pane = _make_router()
    pm.get_by_alias.return_value = None
    router.dispatch("!notreal", pane)
    pane.append_line.assert_called_once()
    assert "unknown" in pane.append_line.call_args[0][0]


def test_plugin_exception_shows_error():
    router, session, pm, pane = _make_router()
    plugin = MagicMock()
    plugin.run.side_effect = RuntimeError("boom")
    pm.get_by_alias.return_value = plugin
    router.dispatch("!ping host", pane)
    pane.append_line.assert_called_once()
    assert "plugin error" in pane.append_line.call_args[0][0]
