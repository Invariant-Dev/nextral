from __future__ import annotations

import webbrowser

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import TabbedContent, TabPane

from nextral.config import app_config
from nextral.monitoring.audit_log import AuditLog
from nextral.monitoring.collector import MetricsCollector, MetricsUpdate
from nextral.monitoring.alert_engine import AlertEngine
from nextral.monitoring.web_server import WebDashServer
from nextral.plugins.manager import PluginManager
from nextral.shell.completer import Completer
from nextral.shell.history import CommandHistory
from nextral.shell.router import CommandRouter
from nextral.shell.session import ShellSession
from nextral.ui.widgets.stats_panel import StatsPanel
from nextral.ui.widgets.status_bar import StatusBar
from nextral.ui.widgets.terminal_pane import TerminalPane
from nextral.ui.widgets.command_palette import (
    CommandPaletteModal,
    ParamDialog,
    get_command,
    ALL_COMMANDS,
)


class HomeScreen(Screen):
    BINDINGS = [
        Binding("ctrl+t",         "new_tab",        "New Tab",    show=False),
        Binding("ctrl+w",         "close_tab",      "Close Tab",  show=False),
        Binding("ctrl+backslash", "toggle_split",   "Split",      show=False),
        Binding("ctrl+b",         "toggle_panel",   "Panel",      show=False),
        Binding("ctrl+d",         "toggle_panel",   "Panel",      show=False),
        Binding("ctrl+k",         "open_palette",   "Palette",    show=False),
    ]

    def __init__(self, cfg: app_config, audit: AuditLog, pm: PluginManager) -> None:
        super().__init__()
        self._cfg = cfg
        self._audit = audit
        self._pm = pm
        self._panel_visible = True
        self._tab_counter = 1
        self._sessions: dict[str, ShellSession] = {}
        self._collector: MetricsCollector | None = None
        self._alert_engine = AlertEngine(
            cpu_threshold=cfg.monitoring.cpu_alert_threshold,
            disk_threshold=cfg.monitoring.disk_alert_threshold,
            cert_warn_days=cfg.monitoring.cert_expiry_warn_days,
        )
        self._web_server: WebDashServer | None = None
        self._history = CommandHistory(cfg.shell.history_file, cfg.general.history_limit)
        self._completer = Completer(self._history, cfg.shell.max_suggestions)

    def compose(self) -> ComposeResult:
        with Vertical(id="main-content"):
            with TabbedContent(id="session-tabs"):
                with TabPane("Terminal 1", id="tab-1"):
                    yield self._make_pane("tab-1")
            yield StatusBar()
        yield StatsPanel(id="stats-panel")

    def on_mount(self) -> None:
        session = self._sessions.get("tab-1")
        if session:
            self.query_one(StatusBar).cwd = session.cwd
        # Pass self (Screen) so MetricsUpdate posts to this screen's queue
        self._collector = MetricsCollector(
            self,
            interval=self._cfg.monitoring.poll_interval_seconds,
        )
        self._collector.start()

    def on_unmount(self) -> None:
        if self._collector:
            self._collector.stop()
        if self._web_server:
            self._web_server.stop()
        for session in self._sessions.values():
            session.close()

    def on_metrics_update(self, event: MetricsUpdate) -> None:
        snap = event.snapshot
        new_alerts = self._alert_engine.evaluate(snap)
        alert_count = len(self._alert_engine.active_alerts)
        try:
            self.query_one(StatsPanel).update_snapshot(snap, alert_count)
        except Exception:
            pass
        # Update the app header stats
        try:
            from nextral.app import AppHeader
            self.app.query_one(AppHeader).update_stats(snap.cpu_pct, snap.mem_pct)
        except Exception:
            pass
        # Feed web server
        if self._web_server:
            self._web_server.update(snap)

    def _make_pane(self, tab_id: str) -> TerminalPane:
        session = ShellSession(
            on_output=lambda _: None,
            on_cwd_change=lambda _: None,
        )
        self._sessions[tab_id] = session
        router = CommandRouter(session, self._pm)
        return TerminalPane(
            self._history,
            self._completer,
            router,
            session,
            self._audit,
            pane_id=hash(tab_id) % 10000,
        )

    def on_terminal_pane_cwd_changed(self, event: TerminalPane.CwdChanged) -> None:
        self.query_one(StatusBar).cwd = event.cwd

    def on_terminal_pane_slash_command(self, event: TerminalPane.SlashCommand) -> None:
        self._handle_slash(event.raw)

    def on_input_bar_open_palette(self, event) -> None:
        self._handle_slash(getattr(event, "prefix", ""))

    def _handle_slash(self, raw: str) -> None:
        parts = raw.strip().split(None, 1)
        cmd_name = parts[0] if parts else ""
        extra = parts[1] if len(parts) > 1 else ""
        cmd = get_command(cmd_name)

        if cmd is None:
            def _after_palette(result: tuple[str, str] | None) -> None:
                if result:
                    self._execute_slash(result[0], result[1])
            self.app.push_screen(CommandPaletteModal(raw), _after_palette)
            return

        if cmd.needs_param and not extra:
            def _after_param(val: str | None) -> None:
                if val:
                    self._execute_slash(cmd.name, val)
            self.app.push_screen(ParamDialog(cmd, extra), _after_param)
        else:
            self._execute_slash(cmd.name, extra)

    def _execute_slash(self, cmd_name: str, param: str) -> None:
        self._audit.record("slash_command", {"cmd": cmd_name, "param": param})
        pane = self._active_pane()

        match cmd_name:
            # ── Network tools ──────────────────────────────────────────────
            case "/ping":
                if pane:
                    self._route_plugin("ping", param.split(), pane)
            case "/trace":
                if pane:
                    from nextral.monitoring.network_probe import traceroute
                    import threading
                    def _run() -> None:
                        pane.append_line(f"[dim]traceroute {param}...[/dim]")
                        for line in traceroute(param).splitlines():
                            pane.append_line(line)
                    threading.Thread(target=_run, daemon=True).start()
            case "/dns":
                if pane:
                    self._route_plugin("dns", [param], pane)
            case "/cert":
                if pane:
                    parts = param.split(":")
                    args = [parts[0], parts[1]] if len(parts) > 1 else [param]
                    self._route_plugin("cert", args, pane)
            case "/arp":
                if pane:
                    self._route_plugin("arp", [], pane)
            case "/ports":
                if pane:
                    self._route_plugin("ports", [], pane)
            case "/syslog":
                if pane:
                    self._route_plugin("syslog", [param] if param else [], pane)
            case "/ssh":
                if pane:
                    self._route_plugin("ssh", param.split(), pane)
            # ── Navigation ─────────────────────────────────────────────────
            case "/dashboard" | "/stats" | "/sidebar":
                self.action_toggle_panel()
            case "/fullscreen":
                self.app.push_screen("dashboard")
            case "/logs":
                self.app.push_screen("logs")
            case "/plugins":
                self.app.push_screen("plugins")
            case "/webdash":
                self._open_webdash(pane)
            # ── Terminal ───────────────────────────────────────────────────
            case "/clear":
                if pane:
                    pane.clear_output()
            case "/split":
                self.action_toggle_split()
            case "/newtab":
                self.action_new_tab()
            case "/closetab":
                self.action_close_tab()
            case "/history":
                if pane:
                    self._show_history(pane)
            case "/zoom":
                self._zoom_pane(pane)
            # ── Plugins ────────────────────────────────────────────────────
            case "/reload":
                self._reload_plugins(pane)
            # ── App ────────────────────────────────────────────────────────
            case "/theme":
                self.app.action_toggle_theme()
            case "/help":
                if pane:
                    self._show_help(pane)
            case "/quit":
                self.app.action_request_quit()

    def _open_webdash(self, pane: TerminalPane | None) -> None:
        if not self._web_server:
            self._web_server = WebDashServer(port=8787)
            self._web_server.start()
        webbrowser.open(self._web_server.url)
        if pane:
            pane.append_line(f"[green]◈ Browser dashboard → {self._web_server.url}[/green]")
            pane.append_line("[dim]Refreshes every 2s. Run /webdash again to reopen.[/dim]")

    def _route_plugin(self, alias: str, args: list[str], pane: TerminalPane) -> None:
        plugin = self._pm.get_by_alias(alias)
        if plugin:
            import threading
            threading.Thread(target=plugin.run, args=(args, pane), daemon=True).start()
        else:
            pane.append_line(f"[red]plugin '{alias}' not found[/red]")

    def _zoom_pane(self, pane: TerminalPane | None) -> None:
        """Toggle the stats panel to give the terminal more room."""
        self.action_toggle_panel()

    def _reload_plugins(self, pane: TerminalPane | None) -> None:
        try:
            # Re-run discovery by calling internal loader
            self._pm._load_all()
            if pane:
                count = len(self._pm.all_plugins())
                pane.append_line(f"[green]Plugins reloaded — {count} loaded.[/green]")
        except Exception as exc:
            if pane:
                pane.append_line(f"[red]Reload failed: {exc}[/red]")

    def _show_help(self, pane: TerminalPane) -> None:
        pane.append_line("[bold]─── Nextral Help ───────────────────────────────[/bold]")
        pane.append_line("")
        pane.append_line("[bold]Keyboard shortcuts:[/bold]")
        shortcuts = [
            ("Ctrl+K",    "open command palette"),
            ("Ctrl+T",    "new terminal tab"),
            ("Ctrl+W",    "close current tab"),
            ("Ctrl+\\",   "toggle split pane"),
            ("Ctrl+B/D",  "toggle stats panel"),
            ("Ctrl+Q",    "quit"),
            ("↑ / ↓",     "command history"),
            ("Tab",       "accept autocomplete"),
            ("Ctrl+C",    "interrupt shell"),
        ]
        for key, desc in shortcuts:
            pane.append_line(f"  [dim cyan]{key:<14}[/]  {desc}")
        pane.append_line("")
        pane.append_line("[bold]Slash commands:[/bold]")
        for cmd in ALL_COMMANDS:
            param = f" [dim]<{cmd.param_label}>[/]" if cmd.needs_param else ""
            pane.append_line(f"  [bold cyan]{cmd.name:<16}[/]{param}  [dim]{cmd.description}[/]")
        pane.append_line("")

    def _show_history(self, pane: TerminalPane) -> None:
        items = list(self._history._items) if hasattr(self._history, "_items") else []
        if not items:
            pane.append_line("[dim]No history yet.[/dim]")
            return
        pane.append_line("[bold]Command history (most recent first):[/bold]")
        for i, cmd in enumerate(reversed(items[-50:]), 1):
            pane.append_line(f"  [dim]{i:3}.[/]  {cmd}")

    def _active_pane(self) -> TerminalPane | None:
        try:
            panes = list(self.query(TerminalPane))
            for p in panes:
                if p.has_focus or any(True for _ in p.query("#cmd-input")):
                    return p
            return panes[0] if panes else None
        except Exception:
            return None

    # ── Actions ────────────────────────────────────────────────────────────

    def action_new_tab(self) -> None:
        self._tab_counter += 1
        tab_id = f"tab-{self._tab_counter}"
        pane = self._make_pane(tab_id)
        tabbed = self.query_one("#session-tabs", TabbedContent)
        tabbed.add_pane(TabPane(f"Terminal {self._tab_counter}", pane, id=tab_id))

    def action_close_tab(self) -> None:
        tabbed = self.query_one("#session-tabs", TabbedContent)
        active = tabbed.active
        if active and active in self._sessions:
            self._sessions[active].close()
            del self._sessions[active]
        if len(list(tabbed.query(TabPane))) > 1:
            tabbed.remove_pane(active)

    def action_toggle_split(self) -> None:
        tabbed = self.query_one("#session-tabs", TabbedContent)
        active = tabbed.active
        if not active:
            return
        pane_container = tabbed.query_one(f"#{active}", TabPane)
        existing = list(pane_container.query(TerminalPane))
        if len(existing) == 1:
            split_id = f"{active}-split"
            new_pane = self._make_pane(split_id)
            pane_container.mount(new_pane)
            existing[0].styles.width = "1fr"
            new_pane.styles.width = "1fr"
        elif len(existing) == 2:
            split_id = f"{active}-split"
            if split_id in self._sessions:
                self._sessions[split_id].close()
                del self._sessions[split_id]
            existing[1].remove()
            existing[0].styles.width = "100%"

    def action_toggle_panel(self) -> None:
        panel = self.query_one(StatsPanel)
        self._panel_visible = not self._panel_visible
        if self._panel_visible:
            panel.remove_class("hidden")
        else:
            panel.add_class("hidden")

    def action_open_palette(self) -> None:
        self._handle_slash("/")
