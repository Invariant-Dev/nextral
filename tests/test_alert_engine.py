from __future__ import annotations

import pytest

from nextral.monitoring.alert_engine import AlertEngine, severity
from nextral.monitoring.collector import system_snapshot


def _snap(**kwargs) -> system_snapshot:
    defaults = dict(
        cpu_pct=0.0, mem_pct=0.0, mem_used=0, mem_total=0,
        disk_partitions=[], net_bytes_sent=0, net_bytes_recv=0,
        net_bytes_sent_delta=0, net_bytes_recv_delta=0, top_processes=[],
    )
    defaults.update(kwargs)
    return system_snapshot(**defaults)


def test_cpu_alert_fires():
    received = []
    engine = AlertEngine(cpu_threshold=90.0, on_new_alert=received.append)
    engine.evaluate(_snap(cpu_pct=95.0))
    assert len(received) == 1
    assert received[0].sev == severity.critical


def test_cpu_alert_clears():
    engine = AlertEngine(cpu_threshold=90.0)
    engine.evaluate(_snap(cpu_pct=95.0))
    assert engine.count == 1
    engine.evaluate(_snap(cpu_pct=50.0))
    assert engine.count == 0


def test_disk_alert_fires():
    received = []
    engine = AlertEngine(disk_threshold=95.0, on_new_alert=received.append)
    snap = _snap(disk_partitions=[{"mountpoint": "/", "pct": 97.0, "used": 0, "total": 0}])
    engine.evaluate(snap)
    assert len(received) == 1


def test_no_duplicate_alerts():
    received = []
    engine = AlertEngine(cpu_threshold=90.0, on_new_alert=received.append)
    engine.evaluate(_snap(cpu_pct=95.0))
    engine.evaluate(_snap(cpu_pct=95.0))
    assert len(received) == 1


def test_cert_alert():
    engine = AlertEngine(cert_warn_days=14)
    engine.add_cert_alert("example.com", 5)
    assert engine.count == 1
    assert engine.active_alerts[0].sev == severity.warning


def test_cert_alert_critical():
    engine = AlertEngine(cert_warn_days=14)
    engine.add_cert_alert("example.com", 2)
    assert engine.active_alerts[0].sev == severity.critical


def test_dismiss():
    engine = AlertEngine(cpu_threshold=90.0)
    engine.evaluate(_snap(cpu_pct=95.0))
    assert engine.count == 1
    engine.dismiss("cpu_high")
    assert engine.count == 0
