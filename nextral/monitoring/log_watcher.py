from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable


class LogWatcher:
    def __init__(self, path: str, on_line: Callable[[str], None], poll_interval: float = 0.5) -> None:
        self._path = Path(path)
        self._on_line = on_line
        self._interval = poll_interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._offset = 0

    def start(self) -> None:
        if self._running:
            return
        if self._path.exists():
            self._offset = self._path.stat().st_size
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            try:
                if self._path.exists():
                    size = self._path.stat().st_size
                    if size < self._offset:
                        self._offset = 0
                    if size > self._offset:
                        with self._path.open("r", encoding="utf-8", errors="replace") as f:
                            f.seek(self._offset)
                            for line in f:
                                self._on_line(line.rstrip("\r\n"))
                            self._offset = f.tell()
            except OSError:
                pass
            time.sleep(self._interval)
