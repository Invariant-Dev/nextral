from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nextral.plugins.manager import PluginManager
    from nextral.shell.session import ShellSession
    from nextral.ui.widgets.terminal_pane import TerminalPane


class CommandRouter:
    def __init__(self, session: ShellSession, plugin_manager: PluginManager) -> None:
        self._session = session
        self._pm = plugin_manager

    def dispatch(self, raw: str, pane: TerminalPane) -> None:
        cmd = raw.strip()
        if not cmd:
            return

        if cmd.startswith("!"):
            parts = cmd[1:].split()
            alias = parts[0].lower() if parts else ""
            args = parts[1:]
            plugin = self._pm.get_by_alias(alias)
            if plugin:
                try:
                    plugin.run(args, pane)
                except Exception as exc:
                    pane.append_line(f"[plugin error] {exc}")
                return
            pane.append_line(f"[unknown plugin alias] !{alias}")
            return

        self._session.send(cmd)
