from __future__ import annotations

import threading

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import RichLog

from nextral.shell.completer import Completer
from nextral.shell.history import CommandHistory
from nextral.shell.session import ShellSession
from nextral.shell.router import CommandRouter
from nextral.ui.widgets.input_bar import InputBar
from nextral.monitoring.audit_log import AuditLog


def _on_main_thread() -> bool:
    return threading.current_thread() is threading.main_thread()


class TerminalPane(Widget):
    class CwdChanged(Message):
        def __init__(self, cwd: str, pane: TerminalPane) -> None:
            super().__init__()
            self.cwd = cwd
            self.pane = pane

    class SlashCommand(Message):
        def __init__(self, raw: str) -> None:
            super().__init__()
            self.raw = raw

    def __init__(
        self,
        history: CommandHistory,
        completer: Completer,
        router: CommandRouter,
        session: ShellSession,
        audit: AuditLog,
        pane_id: int = 1,
    ) -> None:
        super().__init__()
        self._history = history
        self._completer = completer
        self._router = router
        self._session = session
        self._audit = audit
        self._pane_id = pane_id

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, id=f"output-{self._pane_id}", wrap=True)
        yield InputBar(self._history, self._completer, self._session.cwd)

    def on_mount(self) -> None:
        self._session._on_output = self._receive_output
        self._session._on_cwd_change = self._receive_cwd
        self.query_one(InputBar).focus_input()

    def _receive_output(self, line: str) -> None:
        if _on_main_thread():
            self.append_line(line)
        else:
            try:
                self.app.call_from_thread(self.append_line, line)
            except Exception:
                pass

    def _receive_cwd(self, cwd: str) -> None:
        def _update() -> None:
            try:
                self.query_one(InputBar).update_cwd(cwd)
                self.post_message(self.CwdChanged(cwd, self))
            except Exception:
                pass
        if _on_main_thread():
            _update()
        else:
            self.app.call_from_thread(_update)

    def append_line(self, line: str) -> None:
        try:
            self.query_one(f"#output-{self._pane_id}", RichLog).write(line)
        except Exception:
            pass

    def clear_output(self) -> None:
        try:
            self.query_one(f"#output-{self._pane_id}", RichLog).clear()
        except Exception:
            pass

    def on_input_bar_submitted(self, event: InputBar.Submitted) -> None:
        self._audit.record("shell_command", {"cmd": event.value, "pane": self._pane_id})
        self.append_line(f"[bold dim]> {event.value}[/bold dim]")
        self._router.dispatch(event.value, self)

    def on_input_bar_open_palette(self, event: InputBar.OpenPalette) -> None:
        self.post_message(self.SlashCommand(event.prefix))

    def on_input_bar_slash_execute(self, event: InputBar.SlashExecute) -> None:
        self.post_message(self.SlashCommand(event.raw))

    def on_input_bar_interrupt(self, _: InputBar.Interrupt) -> None:
        self._session.interrupt()
