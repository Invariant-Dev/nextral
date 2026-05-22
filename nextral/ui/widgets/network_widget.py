from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from nextral.utils.formatting import bytes_to_human


class NetworkWidget(Widget):
    def on_mount(self) -> None:
        self.border_title = "NETWORK"

    def compose(self) -> ComposeResult:
        yield Label("", id="net-throughput")
        yield Label("", id="net-totals")

    def update(self, sent_delta: int, recv_delta: int, total_sent: int, total_recv: int) -> None:
        try:
            self.query_one("#net-throughput", Label).update(
                f"[green]↑[/] {bytes_to_human(sent_delta)}/s  [cyan]↓[/] {bytes_to_human(recv_delta)}/s"
            )
            self.query_one("#net-totals", Label).update(
                f"[dim]total: ↑{bytes_to_human(total_sent)}  ↓{bytes_to_human(total_recv)}[/]"
            )
        except Exception:
            pass
