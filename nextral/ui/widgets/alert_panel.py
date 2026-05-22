from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable

from nextral.monitoring.alert_engine import alert, severity


class AlertPanel(Widget):
    BINDINGS = [
        Binding("a", "ack_selected", "Ack", show=True),
        Binding("d", "dismiss_selected", "Dismiss", show=True),
    ]

    class Acked(Message):
        def __init__(self, alert_id: str) -> None:
            super().__init__()
            self.alert_id = alert_id

    class Dismissed(Message):
        def __init__(self, alert_id: str) -> None:
            super().__init__()
            self.alert_id = alert_id

    def on_mount(self) -> None:
        self.border_title = "ALERTS"

    def compose(self) -> ComposeResult:
        table = DataTable(id="alert-table", cursor_type="row")
        table.add_columns("Sev", "Message", "Time")
        yield table

    def refresh_alerts(self, alerts: list[alert]) -> None:
        try:
            table = self.query_one("#alert-table", DataTable)
            table.clear()
            for a in alerts:
                sev_str = a.sev.value.upper()
                css = f"[bold red]{sev_str}[/]" if a.sev == severity.critical else f"[yellow]{sev_str}[/]"
                table.add_row(css, a.message, a.ts[:19], key=a.id)
        except Exception:
            pass

    def action_ack_selected(self) -> None:
        table = self.query_one("#alert-table", DataTable)
        row_key = table.cursor_row
        if row_key is not None:
            key = table.get_row_at(row_key)
            self.post_message(self.Acked(str(table.cursor_coordinate)))

    def action_dismiss_selected(self) -> None:
        table = self.query_one("#alert-table", DataTable)
        if table.cursor_row is not None:
            try:
                row_key = list(table._row_locations.keys())[table.cursor_row]
                self.post_message(self.Dismissed(str(row_key.value)))
            except (IndexError, AttributeError):
                pass
