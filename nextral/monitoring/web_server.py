from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Nextral — Live Dashboard</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #080c14; color: #c8d8f0; font-family: 'Cascadia Code', 'Fira Code', monospace; padding: 24px; }
h1 { color: #4d9fff; margin-bottom: 24px; font-size: 1.4rem; letter-spacing: 2px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 24px; }
.card { background: #0c1220; border: 1px solid #1a2840; border-radius: 6px; padding: 16px; }
.card h2 { color: #6a84a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
.stat { font-size: 2rem; font-weight: bold; margin-bottom: 8px; }
.bar-bg { background: #1a2840; border-radius: 3px; height: 6px; width: 100%; }
.bar-fill { height: 6px; border-radius: 3px; transition: width 0.5s ease; }
.green { color: #4ecf7e; } .yellow { color: #f0c040; } .red { color: #f05060; }
.bg-green { background: #4ecf7e; } .bg-yellow { background: #f0c040; } .bg-red { background: #f05060; }
.sub { color: #6a84a8; font-size: 0.8rem; margin-top: 6px; }
.procs { background: #0c1220; border: 1px solid #1a2840; border-radius: 6px; padding: 16px; }
.procs h2 { color: #6a84a8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th { color: #4d9fff; text-align: left; padding: 4px 8px; border-bottom: 1px solid #1a2840; }
td { padding: 4px 8px; color: #c8d8f0; }
tr:hover td { background: #121b2e; }
.ts { color: #2e4060; font-size: 0.75rem; text-align: right; margin-top: 16px; }
.net-row { display: flex; gap: 16px; }
.net-row .card { flex: 1; }
</style>
</head>
<body>
<h1>◈ NEXTRAL — Live Dashboard</h1>
<div class="grid">
  <div class="card">
    <h2>CPU</h2>
    <div class="stat" id="cpu-val">—</div>
    <div class="bar-bg"><div class="bar-fill bg-green" id="cpu-bar" style="width:0%"></div></div>
    <div class="sub" id="cpu-sub"></div>
  </div>
  <div class="card">
    <h2>Memory</h2>
    <div class="stat" id="mem-val">—</div>
    <div class="bar-bg"><div class="bar-fill bg-green" id="mem-bar" style="width:0%"></div></div>
    <div class="sub" id="mem-sub"></div>
  </div>
  <div class="card">
    <h2>Disk</h2>
    <div class="stat" id="disk-val">—</div>
    <div class="bar-bg"><div class="bar-fill bg-green" id="disk-bar" style="width:0%"></div></div>
    <div class="sub" id="disk-sub"></div>
  </div>
  <div class="card">
    <h2>Network</h2>
    <div class="stat" id="net-val">—</div>
    <div class="sub" id="net-sub"></div>
  </div>
</div>
<div class="procs">
  <h2>Top Processes</h2>
  <table id="proc-table">
    <thead><tr><th>PID</th><th>Name</th><th>CPU%</th><th>Mem%</th></tr></thead>
    <tbody id="proc-body"></tbody>
  </table>
</div>
<div class="ts" id="ts">Waiting for data...</div>
<script>
function color(pct) {
  return pct >= 90 ? 'red' : pct >= 70 ? 'yellow' : 'green';
}
function barColor(pct) {
  return pct >= 90 ? 'bg-red' : pct >= 70 ? 'bg-yellow' : 'bg-green';
}
function setBar(barId, valId, pct, label, sub) {
  const bar = document.getElementById(barId);
  const val = document.getElementById(valId);
  const c = color(pct);
  bar.style.width = pct + '%';
  bar.className = 'bar-fill ' + barColor(pct);
  val.textContent = label;
  val.className = 'stat ' + c;
  if (sub) document.getElementById(barId.replace('-bar','-sub')).textContent = sub;
}
function fmt(bytes) {
  if (bytes > 1e9) return (bytes/1e9).toFixed(1) + ' GB/s';
  if (bytes > 1e6) return (bytes/1e6).toFixed(1) + ' MB/s';
  if (bytes > 1e3) return (bytes/1e3).toFixed(1) + ' KB/s';
  return bytes + ' B/s';
}
async function refresh() {
  try {
    const r = await fetch('/api/stats');
    const d = await r.json();
    setBar('cpu-bar','cpu-val', d.cpu_pct, d.cpu_pct.toFixed(1)+'%', '');
    setBar('mem-bar','mem-val', d.mem_pct, d.mem_pct.toFixed(1)+'%',
      d.mem_used+' / '+d.mem_total);
    const dp = d.disk && d.disk.length ? d.disk[0].pct : 0;
    const dm = d.disk && d.disk.length ? d.disk[0].mountpoint : '';
    setBar('disk-bar','disk-val', dp, dp.toFixed(1)+'%', dm);
    const nv = document.getElementById('net-val');
    nv.textContent = '↑ '+fmt(d.net_sent_delta)+'  ↓ '+fmt(d.net_recv_delta);
    nv.className = 'stat';
    document.getElementById('net-sub').textContent =
      'Total sent: '+d.net_sent+'  recv: '+d.net_recv;
    const tbody = document.getElementById('proc-body');
    tbody.innerHTML = '';
    (d.processes||[]).forEach(p => {
      const tr = document.createElement('tr');
      tr.innerHTML = '<td>'+p.pid+'</td><td>'+p.name+'</td><td class="'+color(p.cpu)+'">'+p.cpu.toFixed(1)+'%</td><td>'+p.mem.toFixed(1)+'%</td>';
      tbody.appendChild(tr);
    });
    document.getElementById('ts').textContent = 'Updated ' + new Date().toLocaleTimeString();
  } catch(e) {}
}
refresh();
setInterval(refresh, 2000);
</script>
</body>
</html>"""


class _Handler(BaseHTTPRequestHandler):
    server: WebDashServer  # type: ignore[assignment]

    def log_message(self, *args: Any) -> None:
        pass  # silence access log

    def do_GET(self) -> None:
        if self.path == "/api/stats":
            data = self.server._snapshot_json()
            body = data.encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        else:
            body = _HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


class WebDashServer(HTTPServer):
    def __init__(self, port: int = 8787) -> None:
        super().__init__(("127.0.0.1", port), _Handler)
        self._port = port
        self._snap: dict = {}
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.shutdown()

    def update(self, snap: object) -> None:
        try:
            def _fmt(b: int) -> str:
                for unit, div in (("GB", 1_073_741_824), ("MB", 1_048_576), ("KB", 1024)):
                    if b >= div:
                        return f"{b/div:.1f} {unit}"
                return f"{b} B"

            disk = [
                {"mountpoint": p.get("mountpoint", ""), "pct": p.get("pct", 0.0)}
                for p in getattr(snap, "disk_partitions", [])
            ]
            procs = [
                {
                    "pid": p.get("pid", 0),
                    "name": p.get("name", ""),
                    "cpu": p.get("cpu", 0.0),
                    "mem": p.get("mem", 0.0),
                }
                for p in getattr(snap, "top_processes", [])
            ]
            data = {
                "cpu_pct": snap.cpu_pct,
                "mem_pct": snap.mem_pct,
                "mem_used": _fmt(snap.mem_used),
                "mem_total": _fmt(snap.mem_total),
                "net_sent_delta": snap.net_bytes_sent_delta,
                "net_recv_delta": snap.net_bytes_recv_delta,
                "net_sent": _fmt(snap.net_bytes_sent),
                "net_recv": _fmt(snap.net_bytes_recv),
                "disk": disk,
                "processes": procs,
            }
            with self._lock:
                self._snap = data
        except Exception:
            pass

    def _snapshot_json(self) -> str:
        with self._lock:
            return json.dumps(self._snap)

    @property
    def url(self) -> str:
        return f"http://localhost:{self._port}"
