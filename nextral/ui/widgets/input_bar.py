from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label, ListItem, ListView

from nextral.shell.completer import Completer
from nextral.shell.history import CommandHistory
from nextral.ui.widgets.command_palette import filter_commands, get_command


_MAX_INLINE_SUGGESTIONS = 6


class InputBar(Widget):
    BINDINGS = [
        Binding("up",     "history_prev",      "Prev",      show=False),
        Binding("down",   "history_next",       "Next",      show=False),
        Binding("tab",    "accept_suggestion",  "Accept",    show=False),
        Binding("ctrl+c", "interrupt",          "Interrupt", show=False),
        Binding("ctrl+k", "open_palette",       "Palette",   show=False),
        Binding("escape", "close_suggestions",  "Close",     show=False),
    ]

    ghost: reactive[str] = reactive("")
    _show_suggestions: reactive[bool] = reactive(False)

    class Submitted(Message):
        def __init__(self, value: str) -> None:
            super().__init__()
            self.value = value

    class Interrupt(Message):
        pass

    class OpenPalette(Message):
        def __init__(self, prefix: str = "") -> None:
            super().__init__()
            self.prefix = prefix

    class SlashExecute(Message):
        """Emitted when a slash command is ready to execute directly."""
        def __init__(self, raw: str) -> None:
            super().__init__()
            self.raw = raw

    def __init__(self, history: CommandHistory, completer: Completer, cwd: str) -> None:
        super().__init__()
        self._history = history
        self._completer = completer
        self._cwd = cwd
        self._suggestions: list[str] = []
        self._suggestion_idx: int = -1

    def compose(self) -> ComposeResult:
        # Suggestion list first so it renders above the input in the layout
        yield ListView(id="slash-suggestions")
        yield Label("", id="ghost-label", classes="ghost-suggestion")
        yield Input(placeholder="type a command or /slash...", id="cmd-input")

    def on_mount(self) -> None:
        self._update_prompt()
        self.query_one("#slash-suggestions", ListView).display = False

    def _update_prompt(self) -> None:
        cwd = self._cwd
        # Shorten long paths for display
        parts = cwd.replace("\\", "/").split("/")
        short = "/".join(parts[-2:]) if len(parts) > 2 else cwd
        try:
            self.query_one("#prompt-label", Label).update(f"[dim]{short}[/] [bold $accent]›[/]")
        except Exception:
            pass

    def on_input_changed(self, event: Input.Changed) -> None:
        val = event.value

        if val.startswith("/"):
            self._update_slash_suggestions(val)
            # Update ghost for single match
            matches = filter_commands(val)
            if matches:
                top = matches[0].name
                suffix = top[len(val):] if top.startswith(val) else ""
                self._set_ghost(suffix)
            else:
                self._set_ghost("")
            return

        # Hide slash suggestions for non-slash input
        self._hide_suggestions()

        if val:
            top = self._completer.top(val, self._cwd)
            self._set_ghost(top[len(val):] if top else "")
        else:
            self._set_ghost("")

    def _update_slash_suggestions(self, val: str) -> None:
        matches = filter_commands(val)
        lv = self.query_one("#slash-suggestions", ListView)
        lv.clear()
        if not matches:
            lv.display = False
            self._show_suggestions = False
            self._suggestions = []
            return

        self._suggestions = [c.name for c in matches[:_MAX_INLINE_SUGGESTIONS]]
        for i, cmd in enumerate(matches[:_MAX_INLINE_SUGGESTIONS]):
            param_hint = f" [dim]{cmd.param_placeholder}[/]" if cmd.needs_param and cmd.param_placeholder else ""
            lv.append(ListItem(
                Label(f"[bold]{cmd.name}[/bold]{param_hint}  [dim italic]{cmd.description}[/dim italic]"),
            ))
        lv.display = True
        self._show_suggestions = True
        self._suggestion_idx = -1

    def _hide_suggestions(self) -> None:
        try:
            lv = self.query_one("#slash-suggestions", ListView)
            lv.display = False
            lv.clear()
        except Exception:
            pass
        self._show_suggestions = False
        self._suggestions = []
        self._suggestion_idx = -1

    def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.value.strip()

        if val.startswith("/"):
            # If a suggestion is highlighted, use that command name
            if self._show_suggestions and self._suggestion_idx >= 0 and self._suggestion_idx < len(self._suggestions):
                cmd_name = self._suggestions[self._suggestion_idx]
                # Preserve any param typed after the command
                parts = val.split(None, 1)
                param = parts[1] if len(parts) > 1 else ""
                val = f"{cmd_name} {param}".strip()

            self._hide_suggestions()
            self.query_one("#cmd-input", Input).value = ""
            self._clear_ghost()

            # Execute directly if command is recognized, otherwise open palette
            parts = val.split(None, 1)
            cmd_name = parts[0] if parts else val
            cmd = get_command(cmd_name)

            if cmd is not None:
                # Command known — send SlashExecute so HomeScreen handles it inline
                self.post_message(self.SlashExecute(val))
            else:
                # Unknown prefix — open palette
                self.post_message(self.OpenPalette(val))
            return

        self._hide_suggestions()
        if val:
            self._history.push(val)
            self._history.reset_cursor()
            self.post_message(self.Submitted(val))
        self.query_one("#cmd-input", Input).value = ""
        self._clear_ghost()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """User clicked/entered a suggestion from the inline list."""
        if not self._suggestions:
            return
        idx = event.list_view.index
        if idx is not None and 0 <= idx < len(self._suggestions):
            cmd_name = self._suggestions[idx]
            inp = self.query_one("#cmd-input", Input)
            # Preserve any extra text already typed after command prefix
            current = inp.value.strip()
            parts = current.split(None, 1)
            param = parts[1] if len(parts) > 1 else ""
            inp.value = f"{cmd_name} {param}".strip() if param else cmd_name
            # Move cursor to end
            inp.cursor_position = len(inp.value)
            inp.focus()
            self._hide_suggestions()

    def action_history_prev(self) -> None:
        if self._show_suggestions:
            self._move_suggestion(-1)
            return
        prev = self._history.recall_prev()
        if prev is not None:
            self.query_one("#cmd-input", Input).value = prev

    def action_history_next(self) -> None:
        if self._show_suggestions:
            self._move_suggestion(1)
            return
        nxt = self._history.recall_next()
        if nxt is not None:
            self.query_one("#cmd-input", Input).value = nxt

    def _move_suggestion(self, delta: int) -> None:
        if not self._suggestions:
            return
        lv = self.query_one("#slash-suggestions", ListView)
        new_idx = max(0, min(len(self._suggestions) - 1, self._suggestion_idx + delta))
        self._suggestion_idx = new_idx
        lv.index = new_idx

    def action_accept_suggestion(self) -> None:
        inp = self.query_one("#cmd-input", Input)
        if self._show_suggestions and self._suggestion_idx >= 0:
            self._move_suggestion(0)  # confirm highlight
            return
        if self.ghost:
            inp.value = inp.value + self.ghost
            inp.cursor_position = len(inp.value)
            self._clear_ghost()

    def action_interrupt(self) -> None:
        self.post_message(self.Interrupt())

    def action_open_palette(self) -> None:
        self._hide_suggestions()
        self.post_message(self.OpenPalette())

    def action_close_suggestions(self) -> None:
        self._hide_suggestions()

    def _set_ghost(self, suffix: str) -> None:
        self.ghost = suffix
        lbl = self.query_one("#ghost-label", Label)
        if suffix:
            lbl.update(f"[dim]{suffix}[/dim]")
            lbl.add_class("visible")
        else:
            lbl.update("")
            lbl.remove_class("visible")

    def _clear_ghost(self) -> None:
        self._set_ghost("")

    def update_cwd(self, cwd: str) -> None:
        self._cwd = cwd
        self._update_prompt()

    def focus_input(self) -> None:
        self.query_one("#cmd-input", Input).focus()
