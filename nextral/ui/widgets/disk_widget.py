from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from nextral.utils.formatting import bytes_to_human, pct_bar, truncate


class DiskWidget(Widget):
    def on_mount(self) -> None:
        self.border_title = "DISK"

    def compose(self) -> ComposeResult:
        yield Label("", id="disk-content")

    def update(self, partitions: list[dict]) -> None:
        try:
            lines: list[str] = []
            for part in partitions[:6]:
                pct = part["pct"]
                color = "red" if pct >= 95 else "yellow" if pct >= 80 else "green"
                mp = truncate(part["mountpoint"], 12)
                bar = pct_bar(pct, 12)
                lines.append(f"{mp:12} [{color}]{bar}[/] {pct:.0f}%")
            self.query_one("#disk-content", Label).update("\n".join(lines))
        except Exception:
            pass
