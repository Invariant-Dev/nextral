from __future__ import annotations

import os
import subprocess
import threading
from pathlib import Path
from typing import Callable

from nextral.utils.platform import is_windows, is_macos, has_winpty, has_pty, default_shell


class ShellSession:
    def __init__(
        self,
        on_output: Callable[[str], None],
        on_cwd_change: Callable[[str], None],
        cwd: str | None = None,
    ) -> None:
        self._on_output = on_output
        self._on_cwd_change = on_cwd_change
        self._cwd = cwd or str(Path.home())
        self._proc: subprocess.Popen | None = None
        self._winpty_proc = None
        self._lock = threading.Lock()
        self._alive = False
        self._reader: threading.Thread | None = None
        self._use_winpty = is_windows() and has_winpty()
        self._start()

    def _start(self) -> None:
        if self._use_winpty:
            self._start_winpty()
        else:
            self._start_subprocess()

    def _start_winpty(self) -> None:
        try:
            import winpty  # type: ignore
            shell = default_shell()
            self._winpty_proc = winpty.PtyProcess.spawn(
                [shell],
                cwd=self._cwd,
            )
            self._alive = True
            self._reader = threading.Thread(target=self._read_winpty, daemon=True)
            self._reader.start()
        except Exception as exc:
            self._on_output(f"[winpty error: {exc}] falling back to subprocess")
            self._use_winpty = False
            self._start_subprocess()

    def _read_winpty(self) -> None:
        try:
            while self._alive and self._winpty_proc:
                data = self._winpty_proc.read(4096)
                if not data:
                    break
                for line in data.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
                    if line:
                        self._on_output(line)
        except Exception:
            pass
        finally:
            self._alive = False
            self._on_output("[session ended]")

    def _start_subprocess(self) -> None:
        shell = default_shell()
        env = os.environ.copy()

        if is_windows():
            args = [shell, "/Q", "/K"]
            extra = {}
        elif is_macos() and "zsh" in shell:
            args = [shell, "--no-rcs"]
            extra = {}
        else:
            args = [shell, "--norc", "--noprofile"] if "bash" in shell else [shell]
            extra = {}

        if not is_windows() and has_pty():
            import pty
            master_fd, slave_fd = pty.openpty()
            self._proc = subprocess.Popen(
                args,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                cwd=self._cwd,
                env=env,
                close_fds=True,
                **extra,
            )
            os.close(slave_fd)
            self._master_fd = master_fd
            self._alive = True
            self._reader = threading.Thread(target=self._read_pty, daemon=True)
            self._reader.start()
        else:
            self._proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self._cwd,
                env=env,
                text=False,
                **extra,
            )
            self._master_fd = None
            self._alive = True
            self._reader = threading.Thread(target=self._read_pipe, daemon=True)
            self._reader.start()

    def _read_pty(self) -> None:
        import select
        try:
            buf = b""
            while self._alive:
                rlist, _, _ = select.select([self._master_fd], [], [], 0.1)
                if rlist:
                    try:
                        chunk = os.read(self._master_fd, 4096)
                        if not chunk:
                            break
                        buf += chunk
                        while b"\n" in buf:
                            line, buf = buf.split(b"\n", 1)
                            decoded = line.decode("utf-8", errors="replace").rstrip("\r")
                            self._on_output(decoded)
                    except OSError:
                        break
        except Exception:
            pass
        finally:
            self._alive = False
            self._on_output("[session ended]")

    def _read_pipe(self) -> None:
        assert self._proc and self._proc.stdout
        try:
            for raw in iter(self._proc.stdout.readline, b""):
                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                self._on_output(line)
        except (OSError, ValueError):
            pass
        finally:
            self._alive = False
            self._on_output("[session ended]")

    def send(self, cmd: str) -> None:
        if not self._alive:
            self._on_output("[no active shell session]")
            return

        line = cmd.strip() + "\n"

        if self._use_winpty and self._winpty_proc:
            with self._lock:
                try:
                    self._winpty_proc.write(line)
                except Exception:
                    self._alive = False
        elif self._proc:
            if self._master_fd is not None:
                with self._lock:
                    try:
                        os.write(self._master_fd, line.encode("utf-8"))
                    except OSError:
                        self._alive = False
            elif self._proc.stdin:
                with self._lock:
                    try:
                        self._proc.stdin.write(line.encode("utf-8"))
                        self._proc.stdin.flush()
                    except (OSError, BrokenPipeError):
                        self._alive = False

        if cmd.strip().lower().startswith("cd "):
            self._update_cwd(cmd.strip()[3:].strip())

    def _update_cwd(self, target: str) -> None:
        try:
            resolved = (Path(self._cwd) / target).resolve()
            if resolved.is_dir():
                self._cwd = str(resolved)
                self._on_cwd_change(self._cwd)
        except (OSError, ValueError):
            pass

    def interrupt(self) -> None:
        import signal
        if self._use_winpty and self._winpty_proc:
            try:
                self._winpty_proc.write("\x03")
            except Exception:
                pass
            return

        if self._proc and self._alive:
            try:
                if is_windows():
                    self._proc.send_signal(signal.CTRL_C_EVENT)
                else:
                    self._proc.send_signal(signal.SIGINT)
            except (OSError, ProcessLookupError):
                pass

    def close(self) -> None:
        self._alive = False
        if self._use_winpty and self._winpty_proc:
            try:
                self._winpty_proc.close()
            except Exception:
                pass
            return
        if hasattr(self, "_master_fd") and self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    self._proc.kill()
                except OSError:
                    pass
            self._proc = None

    @property
    def cwd(self) -> str:
        return self._cwd

    @property
    def is_alive(self) -> bool:
        return self._alive
