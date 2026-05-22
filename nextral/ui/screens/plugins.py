from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Label

from nextral.plugins.manager import PluginManager


class PluginScreen(Screen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]

    def __init__(self, pm: PluginManager) -> None:
        super().__init__()
        self._pm = pm

    def compose(self) -> ComposeResult:
        yield Label("[bold]loaded plugins[/]", id="plugin-title")
        table = DataTable(id="plugin-table", cursor_type="row")
        table.add_columns("Name", "Aliases", "Description")
        yield table

    def on_mount(self) -> None:
        table = self.query_one("#plugin-table", DataTable)
        for plugin in self._pm.all_plugins():
            table.add_row(
                plugin.name,
                ", ".join(f"!{a}" for a in plugin.aliases),
                plugin.description,
            )
