from __future__ import annotations

import socket
from typing import TYPE_CHECKING

from nextral.plugins.base import BasePlugin

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane


class DnsLookupPlugin(BasePlugin):
    name = "dns_lookup"
    aliases = ["dns"]
    description = "DNS lookup. Usage: !dns <hostname>"

    def run(self, args: list[str], pane: TerminalPane) -> None:
        if not args:
            pane.append_line("[red]usage: !dns <hostname>[/]")
            return
        host = args[0]
        try:
            results = socket.getaddrinfo(host, None)
            seen: set[str] = set()
            for r in results:
                addr = r[4][0]
                if addr not in seen:
                    seen.add(addr)
                    family = "IPv6" if r[0].name == "AF_INET6" else "IPv4"
                    pane.append_line(f"{host}  {family}  {addr}")
        except socket.gaierror as exc:
            pane.append_line(f"[red]lookup failed: {exc}[/]")
