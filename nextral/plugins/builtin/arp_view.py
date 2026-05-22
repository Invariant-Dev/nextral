from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from nextral.plugins.base import BasePlugin
from nextral.utils.platform import is_windows

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane


class ArpViewPlugin(BasePlugin):
    name = "arp_view"
    aliases = ["arp"]
    description = "Show ARP table. Usage: !arp"

    def run(self, args: list[str], pane: TerminalPane) -> None:
        cmd = ["arp", "-a"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            for line in (result.stdout + result.stderr).splitlines():
                pane.append_line(line)
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            pane.append_line(f"[red]error: {exc}[/]")
