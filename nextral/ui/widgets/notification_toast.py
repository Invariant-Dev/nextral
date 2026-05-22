from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Vertical


class Toast(Widget):
    def __init__(self, message: str, level: str = "info", duration: float = 4.0) -> None:
        super().__init__(classes=f"toast {level}")
        self._message = message
        self._duration = duration

    def compose(self) -> ComposeResult:
        yield Label(self._message, id="toast-msg")

    def on_mount(self) -> None:
        self.set_timer(self._duration, self.remove)


class NotificationStack(Widget):
    def __init__(self) -> None:
        super().__init__(id="notification-stack")

    def compose(self) -> ComposeResult:
        yield Vertical(id="toast-list")

    def push(self, message: str, level: str = "info", duration: float = 4.0) -> None:
        toast = Toast(message, level, duration)
        try:
            self.query_one("#toast-list", Vertical).mount(toast)
        except Exception:
            pass
