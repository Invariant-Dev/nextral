from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Label, RichLog

from nextral.config import app_config
from nextral.monitoring.log_watcher import LogWatcher

_SEVERITY_COLORS = {
    "error": "red",
    "err": "red",
    "warn": "yellow",
    "warning": "yellow",
    "crit": "bold red",
    "critical": "bold red",
    "info": "cyan",
    "debug": "dim",
}


def _colorize(line: str) -> str:
    lower = line.lower()
    for keyword, color in _SEVERITY_COLORS.items():
        if keyword in lower:
            return f"[{color}]{line}[/]"
    return line


class LogScreen(Screen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("ctrl+f", "focus_filter", "Filter"),
    ]

    def __init__(self, cfg: app_config) -> None:
        super().__init__()
        self._cfg = cfg
        self._watcher: LogWatcher | None = None
        self._filter = ""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="log file path...", id="log-path-input")
            yield Input(placeholder="filter (grep)...", id="log-filter-input")
            yield Label("[dim]enter a log file path and press enter[/]", id="log-status")
            yield RichLog(highlight=False, markup=True, id="log-output")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "log-path-input":
            self._start_watcher(event.value.strip())
        elif event.input.id == "log-filter-input":
            self._filter = event.value.strip().lower()

    def _start_watcher(self, path_str: str) -> None:
        if self._watcher:
            self._watcher.stop()
            self._watcher = None

        path = Path(path_str).expanduser()
        if not path.exists():
            self.query_one("#log-status", Label).update(f"[red]not found: {path_str}[/]")
            return

        self.query_one("#log-status", Label).update(f"[dim]watching {path_str}[/]")
        self.query_one("#log-output", RichLog).clear()
        self._watcher = LogWatcher(str(path), self._receive_line)
        self._watcher.start()

    def _receive_line(self, line: str) -> None:
        def _append() -> None:
            if self._filter and self._filter not in line.lower():
                return
            try:
                self.query_one("#log-output", RichLog).write(_colorize(line))
            except Exception:
                pass
        self.call_from_thread(_append)

    def action_focus_filter(self) -> None:
        self.query_one("#log-filter-input", Input).focus()

    def on_unmount(self) -> None:
        if self._watcher:
            self._watcher.stop()
