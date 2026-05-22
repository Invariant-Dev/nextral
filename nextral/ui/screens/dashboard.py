from __future__ import annotations

import psutil
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen

from nextral.config import app_config
from nextral.monitoring.alert_engine import AlertEngine
from nextral.monitoring.audit_log import AuditLog
from nextral.monitoring.collector import MetricsUpdate
from nextral.ui.widgets.alert_panel import AlertPanel
from nextral.ui.widgets.confirm_modal import ConfirmModal
from nextral.ui.widgets.cpu_widget import CpuWidget
from nextral.ui.widgets.disk_widget import DiskWidget
from nextral.ui.widgets.memory_widget import MemoryWidget
from nextral.ui.widgets.network_widget import NetworkWidget
from nextral.ui.widgets.process_widget import ProcessWidget


class DashboardScreen(Screen):
    BINDINGS = [Binding("escape", "pop_screen", "Back")]

    def __init__(self, cfg: app_config, audit: AuditLog) -> None:
        super().__init__()
        self._cfg = cfg
        self._audit = audit
        self._alert_engine = AlertEngine(
            cpu_threshold=cfg.monitoring.cpu_alert_threshold,
            disk_threshold=cfg.monitoring.disk_alert_threshold,
            cert_warn_days=cfg.monitoring.cert_expiry_warn_days,
        )

    def compose(self) -> ComposeResult:
        with Horizontal(id="dash-main"):
            with Vertical(id="dash-left"):
                with Horizontal(id="dash-metrics"):
                    yield CpuWidget(id="w-cpu")
                    yield MemoryWidget(id="w-mem")
                    yield DiskWidget(id="w-disk")
                    yield NetworkWidget(id="w-net")
                with Vertical(id="dash-procs"):
                    yield ProcessWidget(id="w-procs")
            with Vertical(id="dash-right"):
                yield AlertPanel(id="w-alerts")

    def on_mount(self) -> None:
        pass  # MetricsCollector runs in HomeScreen; we receive MetricsUpdate from the app

    def on_unmount(self) -> None:
        pass

    def on_metrics_update(self, event: MetricsUpdate) -> None:
        snap = event.snapshot
        try:
            self.query_one("#w-cpu",   CpuWidget).update(snap.cpu_pct)
            self.query_one("#w-mem",   MemoryWidget).update(snap.mem_pct, snap.mem_used, snap.mem_total)
            self.query_one("#w-net",   NetworkWidget).update(
                snap.net_bytes_sent_delta, snap.net_bytes_recv_delta,
                snap.net_bytes_sent, snap.net_bytes_recv,
            )
            self.query_one("#w-disk",  DiskWidget).update(snap.disk_partitions)
            self.query_one("#w-procs", ProcessWidget).update(snap.top_processes)
        except Exception:
            pass

        new_alerts = self._alert_engine.evaluate(snap)
        if new_alerts:
            try:
                self.query_one("#w-alerts", AlertPanel).refresh_alerts(
                    self._alert_engine.active_alerts
                )
            except Exception:
                pass

    def on_process_widget_kill_request(self, event: ProcessWidget.KillRequest) -> None:
        def _do_kill(confirmed: bool) -> None:
            if confirmed:
                try:
                    proc = psutil.Process(event.pid)
                    proc.terminate()
                    self._audit.record("kill_process", {"pid": event.pid, "name": event.name})
                except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
                    self.app.notify(str(exc), severity="error")
        self.app.push_screen(ConfirmModal(f"Kill '{event.name}' (PID {event.pid})?"), _do_kill)

    def on_alert_panel_dismissed(self, event: AlertPanel.Dismissed) -> None:
        self._alert_engine.dismiss(event.alert_id)
        try:
            self.query_one("#w-alerts", AlertPanel).refresh_alerts(self._alert_engine.active_alerts)
        except Exception:
            pass
