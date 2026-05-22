from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from nextral.plugins.base import BasePlugin
from nextral.utils.platform import is_windows

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane


class PortStatusPlugin(BasePlugin):
    name = "port_status"
    aliases = ["ports"]
    description = "Show listening ports on this machine. Usage: !ports"

    def run(self, args: list[str], pane: TerminalPane) -> None:
        if is_windows():
            cmd = ["netstat", "-ano"]
        else:
            cmd = ["ss", "-tlnp"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            output = result.stdout or result.stderr
            for line in output.splitlines():
                pane.append_line(line)
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            pane.append_line(f"[red]error: {exc}[/]")
