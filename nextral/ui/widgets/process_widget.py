from __future__ import annotations

import psutil
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable


class ProcessWidget(Widget):
    BINDINGS = [
        Binding("k", "kill_selected", "Kill", show=True),
    ]

    class KillRequest(Message):
        def __init__(self, pid: int, name: str) -> None:
            super().__init__()
            self.pid = pid
            self.name = name

    def on_mount(self) -> None:
        self.border_title = "PROCESSES"

    def compose(self) -> ComposeResult:
        table = DataTable(id="proc-table", cursor_type="row")
        table.add_columns("PID", "Name", "CPU%", "MEM%")
        yield table

    def update(self, procs: list[dict]) -> None:
        try:
            table = self.query_one("#proc-table", DataTable)
            table.clear()
            for p in procs:
                table.add_row(
                    str(p["pid"]),
                    p["name"],
                    f"{p['cpu']:.1f}",
                    f"{p['mem']:.1f}",
                    key=str(p["pid"]),
                )
        except Exception:
            pass

    def action_kill_selected(self) -> None:
        table = self.query_one("#proc-table", DataTable)
        if table.cursor_row is not None:
            try:
                row_key = list(table._row_locations.keys())[table.cursor_row]
                pid = int(row_key.value)
                try:
                    proc = psutil.Process(pid)
                    name = proc.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    name = "unknown"
                self.post_message(self.KillRequest(pid, name))
            except (IndexError, AttributeError, ValueError):
                pass
