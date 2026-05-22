from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, ProgressBar, RichLog, Static

_VERSION = "0.1.0"

_LOGO = """\
 ███╗   ██╗███████╗██╗  ██╗████████╗██████╗  █████╗ ██╗
 ████╗  ██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██║
 ██╔██╗ ██║█████╗   ╚███╔╝    ██║   ██████╔╝███████║██║
 ██║╚██╗██║██╔══╝   ██╔██╗    ██║   ██╔══██╗██╔══██║██║
 ██║ ╚████║███████╗██╔╝ ██╗   ██║   ██║  ██║██║  ██║███████╗
 ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"""

_CSS = """
Screen {
    background: #0a0e1a;
    color: #cdd6f4;
    align: center middle;
}

#installer-container {
    background: #0f1623;
    border: solid #89b4fa;
    border-title-color: #89b4fa;
    border-title-style: bold;
    width: 74;
    height: auto;
    padding: 2 4;
}

#install-logo {
    color: #89b4fa;
    text-style: bold;
    content-align: center middle;
    width: 100%;
    height: 7;
}

#install-subtitle {
    color: #7c8db5;
    content-align: center middle;
    width: 100%;
    margin-bottom: 2;
}

.install-step {
    height: 3;
    layout: horizontal;
    padding: 0 2;
    background: #161d2e;
    border: solid #1e2d47;
    margin-bottom: 1;
}

.install-step.active {
    border: solid #89b4fa;
}

.install-step.done {
    border: solid #a6e3a1;
}

.install-step.error {
    border: solid #f38ba8;
}

.step-icon { width: 4; content-align: left middle; }
.step-text { width: 1fr; content-align: left middle; color: #7c8db5; }
.step-status { width: 12; content-align: right middle; color: #3d4f6e; }

#install-log {
    background: #0a0e1a;
    border: solid #1e2d47;
    height: 12;
    padding: 0 1;
    margin-top: 1;
}

#install-actions {
    layout: horizontal;
    height: 3;
    align: center middle;
    margin-top: 2;
}

Button { min-width: 18; margin: 0 1; }

Button.primary {
    background: #89b4fa;
    color: #0a0e1a;
    border: none;
    text-style: bold;
}

Button.danger {
    background: #f38ba8;
    color: #0a0e1a;
    border: none;
}

Button.default {
    background: #161d2e;
    color: #7c8db5;
    border: solid #1e2d47;
}

#done-screen {
    background: #0f1623;
    border: solid #a6e3a1;
    border-title-color: #a6e3a1;
    border-title-style: bold;
    width: 74;
    height: auto;
    padding: 2 4;
    align: center middle;
}

#done-title {
    color: #a6e3a1;
    text-style: bold;
    content-align: center middle;
    width: 100%;
    margin-bottom: 1;
}

#done-info {
    color: #7c8db5;
    content-align: center middle;
    width: 100%;
    margin-bottom: 2;
}

#done-actions {
    layout: horizontal;
    height: 3;
    align: center middle;
}
"""


def _detect_install_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", str(Path.home()))
        return Path(base) / "Programs" / "Nextral"
    if sys.platform == "darwin":
        return Path.home() / "Applications" / "Nextral"
    return Path.home() / ".local" / "share" / "nextral"


def _config_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", str(Path.home()))
        return Path(base) / "Nextral"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Nextral"
    return Path.home() / ".nextral"


def _python_ok() -> tuple[bool, str]:
    vi = sys.version_info
    if vi >= (3, 11):
        return True, f"Python {vi.major}.{vi.minor}.{vi.micro}"
    return False, f"Python {vi.major}.{vi.minor} — need 3.11+"


def _check_pip() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, result.stdout.split()[1]
    except Exception:
        pass
    return False, "not found"


def _install_package(log_fn) -> bool:
    here = Path(__file__).parent
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "-e", str(here), "--quiet"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        if proc.stdout:
            for line in proc.stdout:
                log_fn(line.rstrip())
        proc.wait()
        return proc.returncode == 0
    except Exception as exc:
        log_fn(f"error: {exc}")
        return False


def _create_shortcut_windows(install_dir: Path) -> bool:
    try:
        import winreg
        desktop = Path(os.environ.get("USERPROFILE", "~")) / "Desktop"
        shortcut_path = desktop / "Nextral.bat"
        shortcut_path.write_text(
            f'@echo off\n"{sys.executable}" -m nextral\n',
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def _create_shortcut_linux(install_dir: Path) -> bool:
    try:
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        entry = desktop_dir / "nextral.desktop"
        entry.write_text(
            f"[Desktop Entry]\n"
            f"Name=Nextral\n"
            f"Exec={sys.executable} -m nextral\n"
            f"Type=Application\n"
            f"Categories=System;TerminalEmulator;\n"
            f"Comment=Nextral Command Center\n",
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def _add_to_path_windows() -> bool:
    try:
        scripts_dir = str(Path(sys.prefix) / "Scripts")
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        )
        try:
            current, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current = ""
        if scripts_dir not in current:
            new_path = f"{current};{scripts_dir}" if current else scripts_dir
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


class InstallerScreen(Screen):
    BINDINGS = [Binding("ctrl+c", "cancel_install", "Cancel")]

    def __init__(self) -> None:
        super().__init__()
        self._steps_data = [
            ("step-python",   "⬡", "Checking Python version"),
            ("step-pip",      "⬡", "Checking pip"),
            ("step-config",   "⬡", "Creating configuration directory"),
            ("step-package",  "⬡", "Installing Nextral package"),
            ("step-shortcut", "⬡", "Creating desktop shortcut"),
            ("step-path",     "⬡", "Adding to PATH"),
        ]
        self._log_lines: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="installer-container"):
            yield Static(_LOGO, id="install-logo")
            yield Label(
                f"Command Center  ·  v{_VERSION}  ·  System Administration & Defense",
                id="install-subtitle"
            )
            with Vertical(id="step-list"):
                for step_id, icon, text in self._steps_data:
                    with Horizontal(classes="install-step", id=step_id):
                        yield Label(icon, classes="step-icon", id=f"{step_id}-icon")
                        yield Label(text, classes="step-text")
                        yield Label("waiting", classes="step-status", id=f"{step_id}-status")
            yield RichLog(id="install-log", highlight=False, markup=True)
            with Horizontal(id="install-actions"):
                yield Button("Install", variant="primary", id="btn-install", classes="primary")
                yield Button("Cancel",  variant="default", id="btn-cancel",  classes="default")

    def on_mount(self) -> None:
        self.query_one("#installer-container").border_title = "Nextral Installer"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-install":
            self._start_install()
        elif event.button.id == "btn-cancel":
            self.app.exit()

    def action_cancel_install(self) -> None:
        self.app.exit()

    def _log(self, msg: str) -> None:
        def _write() -> None:
            try:
                self.query_one("#install-log", RichLog).write(msg)
            except Exception:
                pass
        self.call_from_thread(_write)

    def _set_step(self, step_id: str, status: str, done: bool = False, error: bool = False) -> None:
        def _update() -> None:
            try:
                icon = self.query_one(f"#{step_id}-icon", Label)
                stat = self.query_one(f"#{step_id}-status", Label)
                step = self.query_one(f"#{step_id}")
                step.remove_class("active", "done", "error")
                if done:
                    icon.update("●")
                    stat.update(f"[green]{status}[/green]")
                    step.add_class("done")
                elif error:
                    icon.update("✕")
                    stat.update(f"[red]{status}[/red]")
                    step.add_class("error")
                else:
                    icon.update("◌")
                    stat.update(f"[yellow]{status}[/yellow]")
                    step.add_class("active")
            except Exception:
                pass
        self.call_from_thread(_update)

    def _start_install(self) -> None:
        try:
            self.query_one("#btn-install", Button).disabled = True
        except Exception:
            pass
        threading.Thread(target=self._run_install, daemon=True).start()

    def _run_install(self) -> None:
        ok, info = _python_ok()
        self._set_step("step-python", info, done=ok, error=not ok)
        self._log(f"Python: {info}")
        if not ok:
            self._set_step("step-package", "skipped", error=True)
            return

        ok, info = _check_pip()
        self._set_step("step-pip", info, done=ok, error=not ok)
        self._log(f"pip: {info}")

        cfg = _config_dir()
        self._set_step("step-config", "creating...", done=False)
        try:
            cfg.mkdir(parents=True, exist_ok=True)
            (cfg / "plugins").mkdir(exist_ok=True)
            self._set_step("step-config", str(cfg), done=True)
            self._log(f"config dir: {cfg}")
        except Exception as exc:
            self._set_step("step-config", "failed", error=True)
            self._log(f"config error: {exc}")

        self._set_step("step-package", "installing...", done=False)
        self._log("installing package...")
        pkg_ok = _install_package(self._log)
        self._set_step("step-package", "installed" if pkg_ok else "failed", done=pkg_ok, error=not pkg_ok)

        self._set_step("step-shortcut", "creating...", done=False)
        if sys.platform == "win32":
            sc_ok = _create_shortcut_windows(_detect_install_dir())
        else:
            sc_ok = _create_shortcut_linux(_detect_install_dir())
        self._set_step("step-shortcut", "created" if sc_ok else "skipped", done=sc_ok)
        self._log(f"shortcut: {'ok' if sc_ok else 'skipped'}")

        self._set_step("step-path", "updating...", done=False)
        if sys.platform == "win32":
            path_ok = _add_to_path_windows()
        else:
            path_ok = True
        self._set_step("step-path", "updated" if path_ok else "skipped", done=path_ok)
        self._log(f"PATH: {'updated' if path_ok else 'skipped'}")

        self._log("\n[green]Installation complete.[/green]")
        self.call_from_thread(self._show_done, pkg_ok)

    def _show_done(self, success: bool) -> None:
        self.app.push_screen(DoneScreen(success))


class DoneScreen(Screen):
    BINDINGS = [Binding("escape", "exit_app", "Exit")]

    def __init__(self, success: bool) -> None:
        super().__init__()
        self._success = success

    def compose(self) -> ComposeResult:
        with Vertical(id="done-screen"):
            if self._success:
                yield Label("✓  Installation Complete", id="done-title")
                yield Label(
                    "Nextral has been installed.\n\n"
                    "Run it with:  python -m nextral\n"
                    "Or use the desktop shortcut.",
                    id="done-info"
                )
            else:
                yield Label("⚠  Installation Incomplete", id="done-title")
                yield Label(
                    "Some steps failed. Check the log above.\n"
                    "You can still run:  python -m nextral",
                    id="done-info"
                )
            with Horizontal(id="done-actions"):
                yield Button("Launch Nextral", variant="primary", id="btn-launch", classes="primary")
                yield Button("Exit",           variant="default", id="btn-exit",   classes="default")

    def on_mount(self) -> None:
        title = "Installation Complete" if self._success else "Installation Incomplete"
        self.query_one("#done-screen").border_title = title

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-launch":
            subprocess.Popen([sys.executable, "-m", "nextral"])
            self.app.exit()
        else:
            self.app.exit()

    def action_exit_app(self) -> None:
        self.app.exit()


class InstallerApp(App):
    CSS = _CSS

    def on_mount(self) -> None:
        self.push_screen(InstallerScreen())


if __name__ == "__main__":
    InstallerApp().run()
