from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

import psutil
from textual.message import Message


@dataclass
class system_snapshot:
    cpu_pct: float = 0.0
    mem_pct: float = 0.0
    mem_used: int = 0
    mem_total: int = 0
    disk_partitions: list[dict] = field(default_factory=list)
    net_bytes_sent: int = 0
    net_bytes_recv: int = 0
    net_bytes_sent_delta: int = 0
    net_bytes_recv_delta: int = 0
    top_processes: list[dict] = field(default_factory=list)


class MetricsUpdate(Message):
    def __init__(self, snapshot: system_snapshot) -> None:
        super().__init__()
        self.snapshot = snapshot


class MetricsCollector:
    def __init__(self, target: object, interval: int = 2) -> None:
        self._target = target  # any MessagePump: App or Screen
        self._interval = interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._prev_sent = 0
        self._prev_recv = 0

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            try:
                snap = self._collect()
                self._target.call_from_thread(self._target.post_message, MetricsUpdate(snap))
            except Exception:
                pass
            time.sleep(self._interval)

    def _collect(self) -> system_snapshot:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        net = psutil.net_io_counters()

        sent_delta = max(0, net.bytes_sent - self._prev_sent)
        recv_delta = max(0, net.bytes_recv - self._prev_recv)
        self._prev_sent = net.bytes_sent
        self._prev_recv = net.bytes_recv

        partitions: list[dict] = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "mountpoint": part.mountpoint,
                    "device": part.device,
                    "pct": usage.percent,
                    "used": usage.used,
                    "total": usage.total,
                })
            except (PermissionError, OSError):
                pass

        procs: list[dict] = []
        for p in sorted(
            psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]),
            key=lambda x: x.info.get("cpu_percent") or 0,
            reverse=True,
        )[:10]:
            try:
                procs.append({
                    "pid": p.info["pid"],
                    "name": p.info["name"],
                    "cpu": p.info.get("cpu_percent") or 0.0,
                    "mem": p.info.get("memory_percent") or 0.0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return system_snapshot(
            cpu_pct=cpu,
            mem_pct=mem.percent,
            mem_used=mem.used,
            mem_total=mem.total,
            disk_partitions=partitions,
            net_bytes_sent=net.bytes_sent,
            net_bytes_recv=net.bytes_recv,
            net_bytes_sent_delta=sent_delta,
            net_bytes_recv_delta=recv_delta,
            top_processes=procs,
        )
