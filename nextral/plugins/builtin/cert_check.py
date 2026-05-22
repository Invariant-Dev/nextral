from __future__ import annotations

from typing import TYPE_CHECKING

from nextral.monitoring.cert_monitor import check_cert
from nextral.plugins.base import BasePlugin

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane


class CertCheckPlugin(BasePlugin):
    name = "cert_check"
    aliases = ["cert"]
    description = "Inspect TLS cert. Usage: !cert <host> [port]"

    def run(self, args: list[str], pane: TerminalPane) -> None:
        if not args:
            pane.append_line("[red]usage: !cert <host> [port][/]")
            return
        host = args[0]
        port = int(args[1]) if len(args) > 1 and args[1].isdigit() else 443
        pane.append_line(f"checking TLS cert for {host}:{port}...")
        info = check_cert(host, port)
        if info.error:
            pane.append_line(f"[red]error: {info.error}[/]")
            return
        pane.append_line(f"subject: {info.subject}")
        if info.expiry:
            pane.append_line(f"expires: {info.expiry.strftime('%Y-%m-%d')}")
        if info.days_remaining is not None:
            color = "red" if info.days_remaining <= 3 else "yellow" if info.days_remaining <= 14 else "green"
            pane.append_line(f"days remaining: [{color}]{info.days_remaining}[/]")
