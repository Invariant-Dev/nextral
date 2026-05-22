import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

textual_datas = collect_data_files("textual")
rich_datas    = collect_data_files("rich")

hidden = (
    collect_submodules("textual")
    + collect_submodules("rich")
    + collect_submodules("nextral")
    + [
        "psutil",
        "paramiko",
        "cryptography",
        "cryptography.hazmat.backends.openssl",
        "cryptography.hazmat.primitives",
        "socket",
        "ssl",
        "select",
        "pty",
        "winpty",
    ]
)

a = Analysis(
    ["main.py"],
    pathex=[str(Path(".").resolve())],
    binaries=[],
    datas=textual_datas + rich_datas + [
        ("nextral", "nextral"),
    ],
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "test", "distutils"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="nextral",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="nextral",
)
