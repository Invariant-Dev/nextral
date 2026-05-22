from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane


class BasePlugin(ABC):
    name: str = ""
    aliases: list[str] = []
    description: str = ""

    @abstractmethod
    def run(self, args: list[str], pane: TerminalPane) -> None:
        ...
