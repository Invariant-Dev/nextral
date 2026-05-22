from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from nextral.utils.platform import is_windows


@dataclass
class ping_result:
    host: str
    packets_sent: int
    packets_recv: int
    avg_ms: float | None
    raw: str


def ping(host: str, count: int = 4) -> ping_result:
    if is_windows():
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), host]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        raw = proc.stdout + proc.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return ping_result(host=host, packets_sent=count, packets_recv=0, avg_ms=None, raw=str(exc))

    avg_ms = _parse_avg(raw)
    recv = _parse_received(raw)
    return ping_result(host=host, packets_sent=count, packets_recv=recv, avg_ms=avg_ms, raw=raw)


def _parse_avg(raw: str) -> float | None:
    patterns = [
        r"Average\s*=\s*([\d.]+)\s*ms",
        r"rtt min/avg/max.*=\s*[\d.]+/([\d.]+)/",
        r"avg.*?([\d.]+)\s*ms",
    ]
    for pat in patterns:
        m = re.search(pat, raw, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    return None


def _parse_received(raw: str) -> int:
    m = re.search(r"Received\s*=\s*(\d+)", raw, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s+received", raw, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return 0


def traceroute(host: str) -> str:
    if is_windows():
        cmd = ["tracert", "-d", host]
    else:
        cmd = ["traceroute", "-n", host]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return proc.stdout + proc.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return str(exc)
