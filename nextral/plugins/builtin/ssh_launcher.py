from __future__ import annotations

from typing import TYPE_CHECKING

from nextral.plugins.base import BasePlugin

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane


class SshLauncherPlugin(BasePlugin):
    name = "ssh_launcher"
    aliases = ["ssh"]
    description = "Open SSH session. Usage: !ssh [user@]host [port]"

    def run(self, args: list[str], pane: TerminalPane) -> None:
        if not args:
            pane.append_line("[red]usage: !ssh [user@]host [port][/]")
            return
        target = args[0]
        port_args = ["-p", args[1]] if len(args) > 1 and args[1].isdigit() else []
        cmd = " ".join(["ssh"] + port_args + [target])
        pane.append_line(f"[dim]launching: {cmd}[/]")
        from nextral.shell.session import ShellSession
        session = pane._session
        session.send(cmd)
