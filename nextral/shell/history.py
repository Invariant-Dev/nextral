from __future__ import annotations

import json
from collections import deque
from pathlib import Path


class CommandHistory:
    def __init__(self, path: str, limit: int = 5000) -> None:
        self._path = Path(path).expanduser()
        self._limit = limit
        self._entries: deque[str] = deque(maxlen=limit)
        self._cursor: int = -1
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for entry in data[-self._limit:]:
                        self._entries.append(str(entry))
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(list(self._entries), ensure_ascii=False, indent=None),
            encoding="utf-8",
        )

    def push(self, cmd: str) -> None:
        cmd = cmd.strip()
        if not cmd:
            return
        if self._entries and self._entries[-1] == cmd:
            self._cursor = -1
            return
        self._entries.append(cmd)
        self._cursor = -1
        self.save()

    def recall_prev(self) -> str | None:
        if not self._entries:
            return None
        if self._cursor == -1:
            self._cursor = len(self._entries) - 1
        elif self._cursor > 0:
            self._cursor -= 1
        return self._entries[self._cursor]

    def recall_next(self) -> str | None:
        if self._cursor == -1:
            return None
        self._cursor += 1
        if self._cursor >= len(self._entries):
            self._cursor = -1
            return ""
        return self._entries[self._cursor]

    def reset_cursor(self) -> None:
        self._cursor = -1

    def search(self, prefix: str, limit: int = 10) -> list[str]:
        seen: set[str] = set()
        results: list[str] = []
        for entry in reversed(self._entries):
            if entry.startswith(prefix) and entry not in seen:
                seen.add(entry)
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def all_entries(self) -> list[str]:
        return list(self._entries)
