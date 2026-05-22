from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmModal(ModalScreen[bool]):
    BINDINGS = [
        Binding("escape", "cancel",  "Cancel"),
        Binding("y",      "confirm", "Confirm"),
        Binding("enter",  "confirm", "Confirm"),
    ]

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-box"):
            yield Label(self._message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("Confirm  [y]", variant="error",   id="btn-confirm")
                yield Button("Cancel  [Esc]", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#confirm-box").border_title = "Confirm Action"
        self.query_one("#btn-confirm", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-confirm")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
