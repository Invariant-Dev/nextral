from __future__ import annotations

import os
from pathlib import Path

from nextral.shell.history import CommandHistory


class Completer:
    def __init__(self, history: CommandHistory, max_results: int = 10) -> None:
        self._history = history
        self._max = max_results

    def suggest(self, partial: str, cwd: str) -> list[str]:
        if not partial:
            return []

        results: list[str] = []
        seen: set[str] = set()

        for entry in self._history.search(partial, self._max):
            if entry not in seen:
                seen.add(entry)
                results.append(entry)

        if len(results) < self._max:
            results.extend(self._fs_suggest(partial, cwd, seen))

        return results[: self._max]

    def _fs_suggest(self, partial: str, cwd: str, seen: set[str]) -> list[str]:
        results: list[str] = []
        try:
            parts = partial.rsplit(" ", 1)
            token = parts[-1] if len(parts) > 1 else partial
            prefix = parts[0] + " " if len(parts) > 1 else ""

            base_dir = Path(cwd)
            if "/" in token or "\\" in token:
                candidate_dir = Path(token).parent
                stem = Path(token).name
                search_dir = (base_dir / candidate_dir).resolve()
            else:
                search_dir = base_dir
                stem = token

            if search_dir.is_dir():
                for entry in search_dir.iterdir():
                    if entry.name.startswith(stem):
                        suggestion = prefix + str(
                            entry if token and ("/" in token or "\\" in token)
                            else entry.name
                        )
                        if suggestion not in seen:
                            seen.add(suggestion)
                            results.append(suggestion)
                        if len(results) >= self._max:
                            break
        except (OSError, ValueError):
            pass
        return results

    def top(self, partial: str, cwd: str) -> str | None:
        suggestions = self.suggest(partial, cwd)
        if suggestions and suggestions[0] != partial:
            return suggestions[0]
        return None
