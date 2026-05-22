from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from nextral.config import app_config
from nextral.plugins.base import BasePlugin

if TYPE_CHECKING:
    from nextral.ui.widgets.terminal_pane import TerminalPane

_log = logging.getLogger(__name__)


class PluginManager:
    def __init__(self, cfg: app_config) -> None:
        self._cfg = cfg
        self._plugins: dict[str, BasePlugin] = {}
        self._alias_map: dict[str, BasePlugin] = {}
        self._load_all()

    def _load_all(self) -> None:
        builtin_dir = Path(__file__).parent / "builtin"
        self._load_dir(builtin_dir, source="builtin")

        user_dir = Path(self._cfg.plugins.user_plugin_dir).expanduser()
        if user_dir.exists():
            self._load_dir(user_dir, source="user")

    def _load_dir(self, directory: Path, source: str) -> None:
        for path in sorted(directory.glob("*.py")):
            if path.name.startswith("_"):
                continue
            self._load_file(path, source)

    def _load_file(self, path: Path, source: str) -> None:
        module_name = f"_nextral_plugin_{source}_{path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                _log.warning("could not load plugin spec: %s", path)
                return
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:
            _log.warning("plugin load error %s: %s", path.name, exc)
            return

        for attr in vars(mod).values():
            if (
                isinstance(attr, type)
                and issubclass(attr, BasePlugin)
                and attr is not BasePlugin
            ):
                self._register(attr, path)

    def _register(self, cls: type[BasePlugin], path: Path) -> None:
        if not cls.name:
            _log.warning("plugin in %s has no name, skipping", path.name)
            return
        if not cls.aliases:
            _log.warning("plugin %s has no aliases, skipping", cls.name)
            return

        for alias in cls.aliases:
            if alias in self._alias_map:
                _log.warning("duplicate alias %r from %s, skipping", alias, path.name)
                return

        try:
            instance = cls()
        except Exception as exc:
            _log.warning("plugin %s init error: %s", cls.name, exc)
            return

        self._plugins[cls.name] = instance
        for alias in cls.aliases:
            self._alias_map[alias] = instance
        _log.info("loaded plugin: %s (aliases: %s)", cls.name, cls.aliases)

    def get_by_alias(self, alias: str) -> BasePlugin | None:
        return self._alias_map.get(alias)

    def all_plugins(self) -> list[BasePlugin]:
        return list(self._plugins.values())
