from __future__ import annotations

import pytest
import tomllib
from pathlib import Path
from unittest.mock import patch, mock_open

from nextral.config import _validate, load_config, app_config


def test_defaults_on_empty_dict():
    cfg = _validate({})
    assert cfg.general.theme == "dark"
    assert cfg.general.history_limit == 5000
    assert cfg.monitoring.cpu_alert_threshold == 90.0


def test_valid_config():
    raw = {
        "general": {"theme": "light", "history_limit": 1000, "log_level": "debug"},
        "shell": {"history_file": "~/.test_history.json", "max_suggestions": 5},
        "monitoring": {
            "poll_interval_seconds": 5,
            "cpu_alert_threshold": 85.0,
            "disk_alert_threshold": 80.0,
            "cert_expiry_warn_days": 7,
        },
        "plugins": {"user_plugin_dir": "~/.test_plugins"},
    }
    cfg = _validate(raw)
    assert cfg.general.theme == "light"
    assert cfg.general.history_limit == 1000
    assert cfg.monitoring.poll_interval_seconds == 5
    assert cfg.plugins.user_plugin_dir == "~/.test_plugins"


def test_invalid_theme():
    with pytest.raises(ValueError, match="invalid theme"):
        _validate({"general": {"theme": "rainbow"}})


def test_invalid_log_level():
    with pytest.raises(ValueError, match="invalid log_level"):
        _validate({"general": {"log_level": "verbose"}})


def test_invalid_poll_interval():
    with pytest.raises(ValueError):
        _validate({"monitoring": {"poll_interval_seconds": 0}})
