from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from nextral.plugins.manager import PluginManager
from nextral.plugins.base import BasePlugin
from nextral.config import app_config, plugins_config, general_config, shell_config, monitoring_config


def _make_cfg(user_plugin_dir: str = "/nonexistent") -> app_config:
    return app_config(
        general=general_config(),
        shell=shell_config(),
        monitoring=monitoring_config(),
        plugins=plugins_config(user_plugin_dir=user_plugin_dir),
    )


def test_builtin_plugins_load():
    cfg = _make_cfg()
    pm = PluginManager(cfg)
    assert len(pm.all_plugins()) > 0


def test_ping_alias_resolves():
    cfg = _make_cfg()
    pm = PluginManager(cfg)
    plugin = pm.get_by_alias("ping")
    assert plugin is not None
    assert plugin.name == "ping"


def test_unknown_alias_returns_none():
    cfg = _make_cfg()
    pm = PluginManager(cfg)
    assert pm.get_by_alias("notarealcommand123") is None


def test_bad_plugin_skipped(tmp_path):
    bad_plugin = tmp_path / "bad_plugin.py"
    bad_plugin.write_text("raise RuntimeError('intentional failure')\n")

    cfg = _make_cfg(user_plugin_dir=str(tmp_path))
    pm = PluginManager(cfg)
    assert pm.get_by_alias("bad") is None


def test_plugin_without_name_skipped(tmp_path):
    plugin_code = """
from nextral.plugins.base import BasePlugin
class NoNamePlugin(BasePlugin):
    name = ""
    aliases = ["noname"]
    description = ""
    def run(self, args, pane): pass
"""
    (tmp_path / "noname_plugin.py").write_text(plugin_code)
    cfg = _make_cfg(user_plugin_dir=str(tmp_path))
    pm = PluginManager(cfg)
    assert pm.get_by_alias("noname") is None
