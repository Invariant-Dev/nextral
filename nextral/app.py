from __future__ import annotations

import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Label
from textual.containers import Horizontal

from nextral.config import load_config, app_config
from nextral.theme import get_css
from nextral.ui.screens.home import HomeScreen
from nextral.ui.screens.dashboard import DashboardScreen
from nextral.ui.screens.logs import LogScreen
from nextral.ui.screens.plugins import PluginScreen
from nextral.ui.screens.welcome import WelcomeScreen
from nextral.monitoring.audit_log import AuditLog
from nextral.plugins.manager import PluginManager
from nextral.utils.platform import hostname, config_dir

_LOGO = "NEXTRAL"
_VERSION = "v0.1.0"
_FIRST_RUN_FLAG = Path(config_dir()) / ".setup_complete"


class AppHeader(Horizontal):
    def __init__(self, theme: str) -> None:
        super().__init__(id="app-header")
        self._theme = theme

    def compose(self) -> ComposeResult:
        yield Label(f"◈ {_LOGO}", id="header-logo")
        yield Label("", id="header-spacer")
        yield Label("", id="header-stats")
        yield Label("", id="header-time")

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick)
        self._tick()

    def _tick(self) -> None:
        now = datetime.datetime.now().strftime("%a %d %b  %H:%M")
        try:
            self.query_one("#header-time", Label).update(f"[dim]{now}[/dim]")
        except Exception:
            pass

    def update_stats(self, cpu: float, mem: float) -> None:
        cpu_color = "red" if cpu >= 90 else "yellow" if cpu >= 70 else "green"
        mem_color = "red" if mem >= 90 else "yellow" if mem >= 70 else "green"
        try:
            self.query_one("#header-stats", Label).update(
                f"cpu [{cpu_color}]{cpu:.0f}%[/]  mem [{mem_color}]{mem:.0f}%[/]"
            )
        except Exception:
            pass


class NextralApp(App):
    BINDINGS = [
        Binding("ctrl+d", "push_screen('dashboard')", "Dashboard", show=True),
        Binding("ctrl+l", "push_screen('logs')",      "Logs",      show=True),
        Binding("ctrl+p", "push_screen('plugins')",   "Plugins",   show=True),
        Binding("ctrl+q", "request_quit",             "Quit",      show=True),
        Binding("ctrl+backslash", "toggle_split",     "Split",     show=False),
        Binding("ctrl+b",         "toggle_sidebar",   "Sidebar",   show=False),
        Binding("ctrl+k",         "open_palette",     "Palette",   show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.cfg = load_config()
        self.audit = AuditLog()
        self.plugin_manager = PluginManager(self.cfg)
        self._theme_name = self.cfg.general.theme
        self.CSS = get_css(self._theme_name)

    def compose(self) -> ComposeResult:
        yield AppHeader(self._theme_name)

    def on_mount(self) -> None:
        self.install_screen(
            HomeScreen(self.cfg, self.audit, self.plugin_manager), "home"
        )
        self.install_screen(DashboardScreen(self.cfg, self.audit), "dashboard")
        self.install_screen(LogScreen(self.cfg), "logs")
        self.install_screen(PluginScreen(self.plugin_manager), "plugins")

        first_run = not _FIRST_RUN_FLAG.exists()
        if first_run:
            def _after_welcome() -> None:
                _FIRST_RUN_FLAG.parent.mkdir(parents=True, exist_ok=True)
                _FIRST_RUN_FLAG.touch()
                self.push_screen("home")
            self.push_screen(WelcomeScreen(_after_welcome))
        else:
            self.push_screen("home")

        self.audit.record("app_start", {"version": _VERSION})

    def action_request_quit(self) -> None:
        from nextral.ui.widgets.confirm_modal import ConfirmModal
        def _do_quit(confirmed: bool) -> None:
            if confirmed:
                self.audit.record("app_quit", {})
                self.exit()
        self.push_screen(ConfirmModal("Quit Nextral?"), _do_quit)

    def action_toggle_split(self) -> None:
        home = self.get_screen("home")
        if isinstance(home, HomeScreen) and home.is_current:
            home.action_toggle_split()

    def action_toggle_sidebar(self) -> None:
        home = self.get_screen("home")
        if isinstance(home, HomeScreen) and home.is_current:
            home.action_toggle_sidebar()

    def action_open_palette(self) -> None:
        home = self.get_screen("home")
        if isinstance(home, HomeScreen) and home.is_current:
            home.action_open_palette()

    def action_toggle_theme(self) -> None:
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        self.CSS = get_css(self._theme_name)
        self.notify(f"Theme: {self._theme_name}", title="Theme")

    def notify(self, message: str, title: str = "", severity: str = "information") -> None:
        super().notify(message, title=title, severity=severity)


def main() -> None:
    NextralApp().run()
