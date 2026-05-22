from __future__ import annotations

import time
import pytest

from nextral.shell.session import ShellSession


@pytest.fixture
def session(tmp_path):
    outputs = []
    cwd_changes = []
    s = ShellSession(
        on_output=outputs.append,
        on_cwd_change=cwd_changes.append,
        cwd=str(tmp_path),
    )
    yield s, outputs, cwd_changes
    s.close()


def test_session_starts(session):
    s, outputs, _ = session
    assert s.is_alive


def test_session_close(session):
    s, _, _ = session
    s.close()
    assert not s.is_alive


def test_cwd_tracks_cd(session, tmp_path):
    s, _, cwd_changes = session
    sub = tmp_path / "subdir"
    sub.mkdir()
    s.send(f"cd {sub}")
    time.sleep(0.3)
    assert str(sub) in s.cwd or sub.name in s.cwd


def test_send_after_close(session):
    s, outputs, _ = session
    s.close()
    s.send("echo hello")
    assert any("no active shell" in o for o in outputs)
