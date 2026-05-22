from __future__ import annotations

import platform
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label, Static

from nextral.utils.platform import platform_name, hostname, config_dir

_LOGO = """\
 ███╗   ██╗███████╗██╗  ██╗████████╗██████╗  █████╗ ██╗
 ████╗  ██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║
 ██╔██╗ ██║█████╗   ╚███╔╝    ██║   ██████╔╝███████║██║
 ██║╚██╗██║██╔══╝   ██╔██╗    ██║   ██╔══██╗██╔══██║██║
 ██║ ╚████║███████╗██╔╝ ██╗   ██║   ██║  ██║██║  ██║███████╗
 ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"""

_TAGLINE = "Professional command center for authorized system administration"


class WelcomeScreen(Screen):
    BINDINGS = [
        Binding("enter", "launch", "Launch", show=True),
        Binding("escape", "launch", "Skip",  show=False),
    ]

    def __init__(self, on_done) -> None:
        super().__init__()
        self._on_done = on_done
        self._steps: list[dict] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="welcome-container"):
            yield Static(_LOGO, id="welcome-logo")
            yield Label(_TAGLINE, id="welcome-tagline")
            yield Label("First-time setup", classes="section-title")
            with Vertical(id="welcome-steps"):
                for step_id, icon, label in [
                    ("step-config",    "○", "Creating config directory"),
                    ("step-history",   "○", "Initialising command history"),
                    ("step-plugins",   "○", "Loading built-in plugins"),
                    ("step-platform",  "○", f"Platform: {platform_name()}"),
                    ("step-host",      "○", f"Hostname: {hostname()}"),
                ]:
                    with Horizontal(classes="setup-step", id=step_id):
                        yield Label(icon, classes="step-icon", id=f"{step_id}-icon")
                        yield Label(label, classes="step-label")
                        yield Label("pending", classes="step-status", id=f"{step_id}-status")
            with Horizontal(id="welcome-actions"):
                yield Button("Launch Nextral", variant="primary", id="btn-launch")

    def on_mount(self) -> None:
        self.query_one("#welcome-container").border_title = "Welcome to Nextral"
        self.set_timer(0.2, self._run_setup)

    def _run_setup(self) -> None:
        self._complete_step("step-config",   self._setup_config)
        self._complete_step("step-history",  self._setup_history)
        self._complete_step("step-plugins",  self._setup_plugins)
        self._complete_step("step-platform", lambda: True)
        self._complete_step("step-host",     lambda: True)

    def _complete_step(self, step_id: str, fn) -> None:
        try:
            fn()
            ok = True
        except Exception:
            ok = False

        def _update():
            try:
                icon_lbl = self.query_one(f"#{step_id}-icon", Label)
                status_lbl = self.query_one(f"#{step_id}-status", Label)
                step_widget = self.query_one(f"#{step_id}")
                if ok:
                    icon_lbl.update("●")
                    status_lbl.update("[green]done[/green]")
                    status_lbl.add_class("done")
                    step_widget.add_class("done")
                else:
                    icon_lbl.update("✕")
                    status_lbl.update("[red]failed[/red]")
            except Exception:
                pass
        _update()

    def _setup_config(self) -> None:
        Path(config_dir()).mkdir(parents=True, exist_ok=True)

    def _setup_history(self) -> None:
        hist_path = Path(config_dir()) / "history.json"
        if not hist_path.exists():
            hist_path.write_text("[]", encoding="utf-8")

    def _setup_plugins(self) -> None:
        plugin_dir = Path(config_dir()) / "plugins"
        plugin_dir.mkdir(parents=True, exist_ok=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-launch":
            self.action_launch()

    def action_launch(self) -> None:
        self._on_done()
