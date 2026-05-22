import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

textual_datas = collect_data_files("textual")
rich_datas    = collect_data_files("rich")

hidden = (
    collect_submodules("textual")
    + collect_submodules("rich")
    + collect_submodules("nextral")
    + ["psutil", "paramiko", "cryptography", "ssl"]
)

a = Analysis(
    ["installer.py"],
    pathex=[],
    binaries=[],
    datas=textual_datas + rich_datas + [("nextral", "nextral")],
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "unittest"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="nextral-installer",
    debug=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="nextral-installer",
)
