from __future__ import annotations

from collections import deque

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Static

from nextral.utils.formatting import bytes_to_human, pct_bar


def _c(pct: float) -> str:
    return "red" if pct >= 90 else "yellow" if pct >= 70 else "green"


def _spark(history: deque[float], width: int = 20) -> str:
    chars = "▁▂▃▄▅▆▇█"
    items = list(history)
    if not items:
        return " " * width
    result = []
    for v in items[-width:]:
        idx = min(int(v / 100 * len(chars)), len(chars) - 1)
        result.append(chars[idx])
    return "".join(result).rjust(width)


class StatsPanel(Widget):
    """Right-side monitoring panel — stats widgets only, no navigation."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cpu_history: deque[float] = deque(maxlen=20)

    def compose(self) -> ComposeResult:
        yield Label("◈ MONITOR", id="sp-title")
        yield Static("", classes="sp-rule")

        # CPU
        yield Label("CPU", classes="sp-section")
        yield Label("", id="sp-cpu-bar",   classes="sp-bar")
        yield Label("", id="sp-cpu-spark", classes="sp-spark")

        yield Static("", classes="sp-gap")

        # Memory
        yield Label("MEMORY", classes="sp-section")
        yield Label("", id="sp-mem-bar",    classes="sp-bar")
        yield Label("", id="sp-mem-detail", classes="sp-detail")

        yield Static("", classes="sp-gap")

        # Disk
        yield Label("DISK", classes="sp-section")
        yield Label("", id="sp-disk-0-bar",    classes="sp-bar")
        yield Label("", id="sp-disk-0-label",  classes="sp-detail")
        yield Label("", id="sp-disk-1-bar",    classes="sp-bar")
        yield Label("", id="sp-disk-1-label",  classes="sp-detail")

        yield Static("", classes="sp-gap")

        # Network
        yield Label("NETWORK", classes="sp-section")
        yield Label("", id="sp-net-up",   classes="sp-net")
        yield Label("", id="sp-net-down", classes="sp-net")

        yield Static("", classes="sp-rule")

        # Alerts
        yield Label("ALERTS", classes="sp-section")
        yield Label("  none", id="sp-alerts", classes="sp-alert")

        yield Static("", classes="sp-rule")

        # Processes
        yield Label("PROCESSES", classes="sp-section")
        for i in range(6):
            yield Label("", id=f"sp-proc-{i}", classes="sp-proc")

    def update_snapshot(self, snap: object, alert_count: int = 0) -> None:
        self._update_cpu(snap)
        self._update_mem(snap)
        self._update_disk(snap)
        self._update_net(snap)
        self._update_procs(snap)
        self._update_alerts(alert_count)

    def _update_cpu(self, snap: object) -> None:
        try:
            pct = snap.cpu_pct
            self._cpu_history.append(pct)
            c = _c(pct)
            bar = pct_bar(pct, width=18)
            self.query_one("#sp-cpu-bar", Label).update(
                f" [{c}]{bar}[/] [bold]{pct:5.1f}%[/]"
            )
            spark = _spark(self._cpu_history, width=20)
            self.query_one("#sp-cpu-spark", Label).update(
                f" [dim]{spark}[/]"
            )
        except Exception:
            pass

    def _update_mem(self, snap: object) -> None:
        try:
            pct = snap.mem_pct
            c = _c(pct)
            bar = pct_bar(pct, width=18)
            self.query_one("#sp-mem-bar", Label).update(
                f" [{c}]{bar}[/] [bold]{pct:5.1f}%[/]"
            )
            used = bytes_to_human(snap.mem_used)
            total = bytes_to_human(snap.mem_total)
            self.query_one("#sp-mem-detail", Label).update(
                f" [dim]{used} / {total}[/]"
            )
        except Exception:
            pass

    def _update_disk(self, snap: object) -> None:
        try:
            parts = snap.disk_partitions
            for i in range(2):
                bar_id = f"#sp-disk-{i}-bar"
                lbl_id = f"#sp-disk-{i}-label"
                if i < len(parts):
                    p = parts[i]
                    pct = p.get("pct", 0.0)
                    mp = p.get("mountpoint", "?")
                    mp_short = (mp[:10] + "…") if len(mp) > 11 else mp
                    used = bytes_to_human(p.get("used", 0))
                    total = bytes_to_human(p.get("total", 0))
                    c = _c(pct)
                    bar = pct_bar(pct, width=14)
                    self.query_one(bar_id, Label).update(
                        f" [{c}]{bar}[/] {pct:4.0f}%"
                    )
                    self.query_one(lbl_id, Label).update(
                        f" [dim]{mp_short}  {used}/{total}[/]"
                    )
                else:
                    self.query_one(bar_id, Label).update("")
                    self.query_one(lbl_id, Label).update("")
        except Exception:
            pass

    def _update_net(self, snap: object) -> None:
        try:
            up = snap.net_bytes_sent_delta
            dn = snap.net_bytes_recv_delta
            self.query_one("#sp-net-up", Label).update(
                f" [green]↑[/]  {bytes_to_human(up)}/s"
            )
            self.query_one("#sp-net-down", Label).update(
                f" [cyan]↓[/]  {bytes_to_human(dn)}/s"
            )
        except Exception:
            pass

    def _update_procs(self, snap: object) -> None:
        try:
            procs = snap.top_processes
            for i in range(6):
                lbl = self.query_one(f"#sp-proc-{i}", Label)
                if i < len(procs):
                    p = procs[i]
                    name = (p.get("name") or "")[:13]
                    cpu = p.get("cpu", 0.0)
                    c = _c(cpu)
                    lbl.update(f" [{c}]{cpu:5.1f}%[/]  [dim]{name}[/]")
                else:
                    lbl.update("")
        except Exception:
            pass

    def _update_alerts(self, count: int) -> None:
        try:
            if count:
                self.query_one("#sp-alerts", Label).update(
                    f" [red bold]{count} active[/]"
                )
            else:
                self.query_one("#sp-alerts", Label).update(
                    " [dim]none[/]"
                )
        except Exception:
            pass
