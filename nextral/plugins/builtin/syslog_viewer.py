from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from nextral.plugins.base import BasePlugin
from nextral.utils.platform import is_windows

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane

_LINUX_LOG_PATHS = ["/var/log/syslog", "/var/log/messages", "/var/log/kern.log"]
_WINDOWS_LOG_PATHS: list[str] = []


class SyslogViewerPlugin(BasePlugin):
    name = "syslog_viewer"
    aliases = ["syslog"]
    description = "View last N lines of system log. Usage: !syslog [n]"

    def run(self, args: list[str], pane: TerminalPane) -> None:
        n = int(args[0]) if args and args[0].isdigit() else 50

        if is_windows():
            pane.append_line("[dim]use Windows Event Viewer or 'wevtutil' for event logs[/]")
            return

        for log_path in _LINUX_LOG_PATHS:
            p = Path(log_path)
            if p.exists():
                try:
                    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
                    pane.append_line(f"[dim]{log_path} (last {n} lines):[/]")
                    for line in lines[-n:]:
                        pane.append_line(line)
                    return
                except (PermissionError, OSError) as exc:
                    pane.append_line(f"[red]{log_path}: {exc}[/]")
                    return

        pane.append_line("[yellow]no readable syslog found[/]")
