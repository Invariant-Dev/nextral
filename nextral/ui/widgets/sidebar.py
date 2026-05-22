from __future__ import annotations

from textual.app import ComposeResult
from textual.events import Click
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Label, Static


class SidebarNav(Message):
    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target


class NavButton(Button):
    """A sidebar navigation button — styled entirely via app CSS (theme.py)."""


class Sidebar(Widget):
    def __init__(self) -> None:
        super().__init__(id="sidebar")
        self._cpu = 0.0
        self._mem = 0.0
        self._alert_count = 0

    def compose(self) -> ComposeResult:
        yield Label("◈ NEXTRAL", id="sb-logo", classes="label--accent")
        yield Static("", classes="sidebar-divider")

        yield Label("NAVIGATE", classes="sidebar-section-title")
        yield NavButton("⊞  Terminal",  id="nav-terminal",  classes="active")
        yield NavButton("◈  Dashboard", id="nav-dashboard")
        yield NavButton("≡  Logs",      id="nav-logs")
        yield NavButton("⊕  Plugins",   id="nav-plugins")

        yield Label("SYSTEM", classes="sidebar-section-title")
        yield Label("", id="sb-cpu",    classes="sidebar-stat")
        yield Label("", id="sb-mem",    classes="sidebar-stat")
        yield Label("", id="sb-alerts", classes="sidebar-stat")

        yield Label("SHORTCUTS", classes="sidebar-section-title")
        yield Label("  Ctrl+K   palette",    classes="sidebar-stat")
        yield Label("  /cmd     slash cmd",  classes="sidebar-stat")
        yield Label("  Ctrl+\\  split",      classes="sidebar-stat")
        yield Label("  Ctrl+B   sidebar",    classes="sidebar-stat")
        yield Label("  Ctrl+T   new tab",    classes="sidebar-stat")

    def on_mount(self) -> None:
        self._refresh_stats()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        nav_map = {
            "nav-terminal":  "terminal",
            "nav-dashboard": "dashboard",
            "nav-logs":      "logs",
            "nav-plugins":   "plugins",
        }
        btn_id = event.button.id
        if btn_id in nav_map:
            event.stop()
            self.post_message(SidebarNav(nav_map[btn_id]))
            self._set_active(btn_id)

    def _set_active(self, active_id: str) -> None:
        for nav_id in ("nav-terminal", "nav-dashboard", "nav-logs", "nav-plugins"):
            try:
                btn = self.query_one(f"#{nav_id}", NavButton)
                if nav_id == active_id:
                    btn.add_class("active")
                else:
                    btn.remove_class("active")
            except Exception:
                pass

    def update_stats(self, cpu: float, mem: float, alert_count: int) -> None:
        self._cpu = cpu
        self._mem = mem
        self._alert_count = alert_count
        self._refresh_stats()

    def _refresh_stats(self) -> None:
        cpu_color = "red" if self._cpu >= 90 else "yellow" if self._cpu >= 70 else "green"
        mem_color = "red" if self._mem >= 90 else "yellow" if self._mem >= 70 else "green"
        try:
            self.query_one("#sb-cpu", Label).update(
                f"  cpu  [{cpu_color}]{self._cpu:5.1f}%[/]"
            )
            self.query_one("#sb-mem", Label).update(
                f"  mem  [{mem_color}]{self._mem:5.1f}%[/]"
            )
            ac = self._alert_count
            a_color = "red" if ac else "dim"
            a_txt = str(ac) if ac else "none"
            self.query_one("#sb-alerts", Label).update(
                f"  alerts  [{a_color}]{a_txt}[/]"
            )
        except Exception:
            pass
