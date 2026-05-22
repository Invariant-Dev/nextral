from __future__ import annotations

from typing import TYPE_CHECKING

from nextral.monitoring.network_probe import ping
from nextral.plugins.base import BasePlugin

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane


class PingPlugin(BasePlugin):
    name = "ping"
    aliases = ["ping"]
    description = "Ping a host. Usage: !ping <host> [count]"

    def run(self, args: list[str], pane: TerminalPane) -> None:
        if not args:
            pane.append_line("[red]usage: !ping <host> [count][/]")
            return
        host = args[0]
        count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 4
        pane.append_line(f"pinging {host} ({count} packets)...")
        result = ping(host, count)
        pane.append_line(result.raw)
        if result.avg_ms is not None:
            pane.append_line(f"avg: {result.avg_ms:.1f} ms  recv: {result.packets_recv}/{result.packets_sent}")
        else:
            pane.append_line(f"recv: {result.packets_recv}/{result.packets_sent}")
