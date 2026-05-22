from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

_audit_path = Path.home() / ".nextral" / "audit.log"
_REDACTED = "[redacted]"
_SECRET_KEYS = {"password", "secret", "token", "key", "credential", "passwd"}


def _sanitize(data: dict) -> dict:
    out: dict = {}
    for k, v in data.items():
        if k.lower() in _SECRET_KEYS:
            out[k] = _REDACTED
        elif isinstance(v, dict):
            out[k] = _sanitize(v)
        else:
            out[k] = v
    return out


class AuditLog:
    def __init__(self) -> None:
        _audit_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def record(self, action: str, data: dict) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "data": _sanitize(data),
        }
        line = json.dumps(entry, ensure_ascii=False)
        with self._lock:
            try:
                with _audit_path.open("a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except OSError:
                pass

    def read_recent(self, n: int = 200) -> list[dict]:
        results: list[dict] = []
        try:
            lines = _audit_path.read_text(encoding="utf-8").splitlines()
            for line in lines[-n:]:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        except OSError:
            pass
        return results
