from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from nextral.utils.formatting import bytes_to_human, pct_bar


class MemoryWidget(Widget):
    def on_mount(self) -> None:
        self.border_title = "MEMORY"

    def compose(self) -> ComposeResult:
        yield Label("", id="mem-bar")
        yield Label("", id="mem-detail")

    def update(self, pct: float, used: int, total: int) -> None:
        try:
            bar = pct_bar(pct)
            color = "red" if pct >= 90 else "yellow" if pct >= 70 else "green"
            self.query_one("#mem-bar", Label).update(f"[{color}]{bar}[/] {pct:.1f}%")
            self.query_one("#mem-detail", Label).update(
                f"[dim]{bytes_to_human(used)} / {bytes_to_human(total)}[/]"
            )
        except Exception:
            pass
