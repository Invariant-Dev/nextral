from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class cert_info:
    host: str
    port: int
    subject: str
    expiry: datetime | None
    days_remaining: int | None
    error: str | None


def check_cert(host: str, port: int = 443, timeout: int = 10) -> cert_info:
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
    except Exception as exc:
        return cert_info(host=host, port=port, subject="", expiry=None, days_remaining=None, error=str(exc))

    subject = dict(x[0] for x in cert.get("subject", []))
    cn = subject.get("commonName", host)

    not_after = cert.get("notAfter", "")
    try:
        expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days = (expiry - datetime.now(timezone.utc)).days
    except (ValueError, TypeError):
        expiry = None
        days = None

    return cert_info(host=host, port=port, subject=cn, expiry=expiry, days_remaining=days, error=None)
