from __future__ import annotations

import datetime

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Label

from nextral.utils.platform import hostname


class StatusBar(Widget):
    cwd: reactive[str] = reactive("~")
    alert_count: reactive[int] = reactive(0)
    task_count: reactive[int] = reactive(0)
    cpu_pct: reactive[float] = reactive(0.0)

    def compose(self) -> ComposeResult:
        yield Label("", id="sb-left")
        yield Label("", id="sb-center")
        yield Label("", id="sb-right")

    def on_mount(self) -> None:
        self._host = hostname()
        self._timer: Timer = self.set_interval(1.0, self._tick)
        self._refresh_all()

    def _tick(self) -> None:
        self._refresh_all()

    def _refresh_all(self) -> None:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            self.query_one("#sb-left",   Label).update(f" {self._host}  {self.cwd}")
            center_parts = []
            if self.task_count:
                center_parts.append(f"tasks {self.task_count}")
            if self.cpu_pct:
                cpu_color = "red" if self.cpu_pct >= 90 else "yellow" if self.cpu_pct >= 70 else "green"
                center_parts.append(f"cpu [{cpu_color}]{self.cpu_pct:.0f}%[/]")
            self.query_one("#sb-center", Label).update("  ".join(center_parts))
            alert_str = f"[red]⚠ {self.alert_count}[/red]" if self.alert_count else ""
            self.query_one("#sb-right",  Label).update(
                f"{alert_str}  [dim]{now}[/dim] "
            )
        except Exception:
            pass

    def watch_cwd(self, _: str) -> None:
        self._refresh_all()

    def watch_alert_count(self, _: int) -> None:
        self._refresh_all()

    def watch_cpu_pct(self, _: float) -> None:
        self._refresh_all()
