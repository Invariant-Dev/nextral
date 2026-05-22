from __future__ import annotations

from collections import deque

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from nextral.utils.formatting import pct_bar


class CpuWidget(Widget):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._history: deque[float] = deque(maxlen=20)

    def on_mount(self) -> None:
        self.border_title = "CPU"

    def compose(self) -> ComposeResult:
        yield Label("", id="cpu-bar")
        yield Label("", id="cpu-spark")

    def update(self, pct: float) -> None:
        self._history.append(pct)
        try:
            bar = pct_bar(pct)
            color = "red" if pct >= 90 else "yellow" if pct >= 70 else "green"
            self.query_one("#cpu-bar", Label).update(f"[{color}]{bar}[/] {pct:.1f}%")
            spark = "".join(_spark_char(v) for v in self._history)
            self.query_one("#cpu-spark", Label).update(f"[dim]{spark}[/]")
        except Exception:
            pass


def _spark_char(v: float) -> str:
    chars = "▁▂▃▄▅▆▇█"
    idx = min(int(v / 100 * len(chars)), len(chars) - 1)
    return chars[idx]
