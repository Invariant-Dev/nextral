from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView


@dataclass
class slash_command:
    name: str
    description: str
    needs_param: bool
    param_label: str = ""
    param_placeholder: str = ""


ALL_COMMANDS: list[slash_command] = [
    # Network tools
    slash_command("/ping",       "Ping a host and show RTT",             True,  "Host",    "hostname or IP"),
    slash_command("/trace",      "Traceroute to a host",                 True,  "Host",    "hostname or IP"),
    slash_command("/dns",        "DNS lookup for a hostname",            True,  "Host",    "hostname"),
    slash_command("/cert",       "Inspect TLS certificate",              True,  "Host",    "hostname[:port]"),
    slash_command("/arp",        "Show ARP table",                       False),
    slash_command("/ports",      "Show listening ports",                 False),
    slash_command("/syslog",     "View system log (last N lines)",       True,  "Lines",   "50"),
    slash_command("/ssh",        "Open SSH session",                     True,  "Target",  "[user@]host"),
    # Navigation
    slash_command("/dashboard",  "Toggle right-side stats panel",        False),
    slash_command("/fullscreen", "Open full-screen dashboard",           False),
    slash_command("/logs",       "Open log viewer",                      False),
    slash_command("/plugins",    "Show loaded plugins",                  False),
    slash_command("/webdash",    "Open live browser dashboard",          False),
    # Terminal
    slash_command("/clear",      "Clear terminal output",                False),
    slash_command("/split",      "Toggle split terminal pane",           False),
    slash_command("/newtab",     "Open a new terminal tab",              False),
    slash_command("/closetab",   "Close current terminal tab",           False),
    slash_command("/history",    "Show command history",                 False),
    slash_command("/stats",      "Toggle right-side stats panel",        False),
    slash_command("/sidebar",    "Toggle right-side stats panel",        False),
    slash_command("/zoom",       "Toggle stats panel for more space",    False),
    slash_command("/reload",     "Reload all plugins",                   False),
    # App
    slash_command("/theme",      "Toggle dark/light theme",              False),
    slash_command("/help",       "Show keyboard shortcuts & commands",   False),
    slash_command("/quit",       "Quit Nextral",                         False),
]

_cmd_map: dict[str, slash_command] = {c.name: c for c in ALL_COMMANDS}


def get_command(name: str) -> slash_command | None:
    return _cmd_map.get(name)


def filter_commands(prefix: str) -> list[slash_command]:
    p = prefix.lower()
    return [c for c in ALL_COMMANDS if c.name.startswith(p) or p in c.description.lower()]


class CommandPaletteModal(ModalScreen[tuple[str, str] | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("up",     "move_up",   show=False),
        Binding("down",   "move_down", show=False),
    ]

    def __init__(self, initial: str = "") -> None:
        super().__init__()
        self._initial = initial
        self._filtered = filter_commands(initial) if initial else list(ALL_COMMANDS)
        self._selected = 0

    def compose(self) -> ComposeResult:
        with ListView(id="palette-container"):
            yield Input(value=self._initial, placeholder="/command...", id="palette-input")
            yield ListView(id="palette-list")

    def compose(self) -> ComposeResult:
        from textual.containers import Vertical
        with Vertical(id="palette-container"):
            yield Input(value=self._initial, placeholder="/command...", id="palette-input")
            lv = ListView(id="palette-list")
            yield lv

    def on_mount(self) -> None:
        self.query_one("#palette-container").border_title = "Command Palette"
        self.query_one("#palette-input", Input).focus()
        self._rebuild_list()

    def _rebuild_list(self) -> None:
        lv = self.query_one("#palette-list", ListView)
        lv.clear()
        for i, cmd in enumerate(self._filtered):
            item = ListItem(
                Label(f"[bold]{cmd.name}[/bold]  [dim]{cmd.description}[/dim]"),
                id=f"cmd-{i}",
            )
            lv.append(item)
        if self._filtered:
            lv.index = min(self._selected, len(self._filtered) - 1)

    def on_input_changed(self, event: Input.Changed) -> None:
        val = event.value
        self._filtered = filter_commands(val) if val.startswith("/") else list(ALL_COMMANDS)
        self._selected = 0
        self._rebuild_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._submit()

    def _submit(self) -> None:
        lv = self.query_one("#palette-list", ListView)
        idx = lv.index if lv.index is not None else 0
        if 0 <= idx < len(self._filtered):
            cmd = self._filtered[idx]
            inp = self.query_one("#palette-input", Input).value.strip()
            extra = ""
            parts = inp.split(None, 1)
            if len(parts) > 1:
                extra = parts[1]
            self.dismiss((cmd.name, extra))
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_move_up(self) -> None:
        lv = self.query_one("#palette-list", ListView)
        if lv.index and lv.index > 0:
            lv.index -= 1

    def action_move_down(self) -> None:
        lv = self.query_one("#palette-list", ListView)
        if lv.index is not None and lv.index < len(self._filtered) - 1:
            lv.index += 1


class ParamDialog(ModalScreen[str | None]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, cmd: slash_command, prefilled: str = "") -> None:
        super().__init__()
        self._cmd = cmd
        self._prefilled = prefilled

    def compose(self) -> ComposeResult:
        from textual.containers import Vertical, Horizontal
        with Vertical(id="param-box"):
            yield Label(f"[bold]{self._cmd.name}[/bold] — {self._cmd.description}")
            yield Input(
                value=self._prefilled,
                placeholder=self._cmd.param_placeholder,
                id="param-input",
            )
            with Horizontal(id="param-buttons"):
                from textual.widgets import Button
                yield Button("Run", variant="primary", id="btn-run")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#param-box").border_title = self._cmd.name
        inp = self.query_one("#param-input", Input)
        inp.focus()
        inp.cursor_position = len(self._prefilled)

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._submit()

    def on_button_pressed(self, event) -> None:
        if event.button.id == "btn-run":
            self._submit()
        else:
            self.dismiss(None)

    def _submit(self) -> None:
        val = self.query_one("#param-input", Input).value.strip()
        self.dismiss(val if val else None)

    def action_cancel(self) -> None:
        self.dismiss(None)
