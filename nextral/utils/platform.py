from __future__ import annotations

import os
import platform
import sys


def is_windows() -> bool:
    return sys.platform == "win32"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def is_macos() -> bool:
    return sys.platform == "darwin"


def platform_name() -> str:
    if is_windows():
        return f"Windows {platform.version()}"
    if is_macos():
        return f"macOS {platform.mac_ver()[0]}"
    return f"Linux {platform.release()}"


def has_winpty() -> bool:
    if not is_windows():
        return False
    try:
        import winpty  # type: ignore
        return True
    except ImportError:
        return False


def has_pty() -> bool:
    if is_windows():
        return has_winpty()
    return hasattr(os, "openpty")


def default_shell() -> str:
    if is_windows():
        return os.environ.get("COMSPEC", "cmd.exe")
    if is_macos():
        return os.environ.get("SHELL", "/bin/zsh")
    return os.environ.get("SHELL", "/bin/bash")


def hostname() -> str:
    try:
        import socket
        return socket.gethostname()
    except Exception:
        return "unknown"


def config_dir() -> str:
    if is_windows():
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "Nextral")
    if is_macos():
        return os.path.expanduser("~/Library/Application Support/Nextral")
    return os.path.expanduser("~/.nextral")
