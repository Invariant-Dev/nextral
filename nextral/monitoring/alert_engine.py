from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

from nextral.monitoring.collector import system_snapshot


class severity(Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


@dataclass
class alert:
    id: str
    message: str
    sev: severity
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    acked: bool = False


class AlertEngine:
    def __init__(
        self,
        cpu_threshold: float = 90.0,
        disk_threshold: float = 95.0,
        cert_warn_days: int = 14,
        on_new_alert: Callable[[alert], None] | None = None,
    ) -> None:
        self._cpu_thr = cpu_threshold
        self._disk_thr = disk_threshold
        self._cert_days = cert_warn_days
        self._on_new = on_new_alert
        self._active: dict[str, alert] = {}

    def evaluate(self, snap: system_snapshot) -> list[alert]:
        new_alerts: list[alert] = []

        new_alerts.extend(self._check_cpu(snap.cpu_pct))
        for part in snap.disk_partitions:
            new_alerts.extend(self._check_disk(part["mountpoint"], part["pct"]))

        return new_alerts

    def _check_cpu(self, pct: float) -> list[alert]:
        aid = "cpu_high"
        if pct >= self._cpu_thr:
            if aid not in self._active:
                a = alert(
                    id=aid,
                    message=f"CPU usage critical: {pct:.1f}%",
                    sev=severity.critical,
                )
                self._active[aid] = a
                if self._on_new:
                    self._on_new(a)
                return [a]
        else:
            self._active.pop(aid, None)
        return []

    def _check_disk(self, mountpoint: str, pct: float) -> list[alert]:
        aid = f"disk_{mountpoint}"
        if pct >= self._disk_thr:
            if aid not in self._active:
                a = alert(
                    id=aid,
                    message=f"Disk usage critical on {mountpoint}: {pct:.1f}%",
                    sev=severity.critical,
                )
                self._active[aid] = a
                if self._on_new:
                    self._on_new(a)
                return [a]
        else:
            self._active.pop(aid, None)
        return []

    def add_cert_alert(self, domain: str, days: int) -> None:
        aid = f"cert_{domain}"
        if days <= self._cert_days and aid not in self._active:
            sev = severity.critical if days <= 3 else severity.warning
            a = alert(
                id=aid,
                message=f"TLS cert for {domain} expires in {days} day(s)",
                sev=sev,
            )
            self._active[aid] = a
            if self._on_new:
                self._on_new(a)

    def ack(self, alert_id: str) -> None:
        if alert_id in self._active:
            self._active[alert_id].acked = True

    def dismiss(self, alert_id: str) -> None:
        self._active.pop(alert_id, None)

    @property
    def active_alerts(self) -> list[alert]:
        return sorted(
            self._active.values(),
            key=lambda a: (a.sev == severity.info, a.sev == severity.warning, a.ts),
        )

    @property
    def count(self) -> int:
        return len(self._active)
