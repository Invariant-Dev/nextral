from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from nextral.monitoring.audit_log import AuditLog, _sanitize, _REDACTED


def test_sanitize_removes_secrets():
    data = {"user": "admin", "password": "hunter2", "host": "10.0.0.1"}
    result = _sanitize(data)
    assert result["password"] == _REDACTED
    assert result["user"] == "admin"
    assert result["host"] == "10.0.0.1"


def test_sanitize_nested():
    data = {"credentials": {"token": "abc123", "name": "svc"}}
    result = _sanitize(data)
    assert result["credentials"]["token"] == _REDACTED
    assert result["credentials"]["name"] == "svc"


def test_record_writes_to_file(tmp_path):
    log_path = tmp_path / "audit.log"
    with patch("nextral.monitoring.audit_log._audit_path", log_path):
        audit = AuditLog()
        audit.record("test_action", {"host": "10.0.0.1"})
    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["action"] == "test_action"
    assert entry["data"]["host"] == "10.0.0.1"


def test_record_does_not_log_secrets(tmp_path):
    log_path = tmp_path / "audit.log"
    with patch("nextral.monitoring.audit_log._audit_path", log_path):
        audit = AuditLog()
        audit.record("login", {"user": "admin", "password": "s3cr3t"})
    content = log_path.read_text()
    assert "s3cr3t" not in content
    assert _REDACTED in content


def test_read_recent(tmp_path):
    log_path = tmp_path / "audit.log"
    with patch("nextral.monitoring.audit_log._audit_path", log_path):
        audit = AuditLog()
        for i in range(5):
            audit.record(f"action_{i}", {})
        entries = audit.read_recent(3)
    assert len(entries) == 3
    assert entries[-1]["action"] == "action_4"
