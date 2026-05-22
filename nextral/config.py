from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json

_config_dir = Path.home() / ".nextral"
_config_path = _config_dir / "config.toml"

_defaults_toml = """\
[general]
theme = "dark"
history_limit = 5000
log_level = "info"

[shell]
history_file = "~/.nextral/history.json"
max_suggestions = 10

[monitoring]
poll_interval_seconds = 2
cpu_alert_threshold = 90.0
disk_alert_threshold = 95.0
cert_expiry_warn_days = 14

[plugins]
user_plugin_dir = "~/.nextral/plugins"
"""


@dataclass
class general_config:
    theme: str = "dark"
    history_limit: int = 5000
    log_level: str = "info"


@dataclass
class shell_config:
    history_file: str = "~/.nextral/history.json"
    max_suggestions: int = 10


@dataclass
class monitoring_config:
    poll_interval_seconds: int = 2
    cpu_alert_threshold: float = 90.0
    disk_alert_threshold: float = 95.0
    cert_expiry_warn_days: int = 14


@dataclass
class plugins_config:
    user_plugin_dir: str = "~/.nextral/plugins"


@dataclass
class app_config:
    general: general_config = field(default_factory=general_config)
    shell: shell_config = field(default_factory=shell_config)
    monitoring: monitoring_config = field(default_factory=monitoring_config)
    plugins: plugins_config = field(default_factory=plugins_config)


def _write_defaults() -> None:
    _config_dir.mkdir(parents=True, exist_ok=True)
    _config_path.write_text(_defaults_toml, encoding="utf-8")


def _validate(raw: dict) -> app_config:
    g = raw.get("general", {})
    s = raw.get("shell", {})
    m = raw.get("monitoring", {})
    p = raw.get("plugins", {})

    theme = g.get("theme", "dark")
    if theme not in ("dark", "light"):
        raise ValueError(f"invalid theme: {theme!r}")

    log_level = g.get("log_level", "info")
    if log_level not in ("debug", "info", "warning", "error"):
        raise ValueError(f"invalid log_level: {log_level!r}")

    poll = m.get("poll_interval_seconds", 2)
    if not isinstance(poll, int) or poll < 1:
        raise ValueError("poll_interval_seconds must be a positive integer")

    return app_config(
        general=general_config(
            theme=theme,
            history_limit=int(g.get("history_limit", 5000)),
            log_level=log_level,
        ),
        shell=shell_config(
            history_file=str(s.get("history_file", "~/.nextral/history.json")),
            max_suggestions=int(s.get("max_suggestions", 10)),
        ),
        monitoring=monitoring_config(
            poll_interval_seconds=poll,
            cpu_alert_threshold=float(m.get("cpu_alert_threshold", 90.0)),
            disk_alert_threshold=float(m.get("disk_alert_threshold", 95.0)),
            cert_expiry_warn_days=int(m.get("cert_expiry_warn_days", 14)),
        ),
        plugins=plugins_config(
            user_plugin_dir=str(p.get("user_plugin_dir", "~/.nextral/plugins")),
        ),
    )


def load_config() -> app_config:
    if not _config_path.exists():
        _write_defaults()
    raw = tomllib.loads(_config_path.read_text(encoding="utf-8"))
    return _validate(raw)
