# PyInstaller spec for the desktop Python sidecar.
#
# Build from this directory after installing PyInstaller:
#   pyinstaller pyinstaller.spec

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
SPEC_DIR = Path(SPECPATH)
PROJECT_ROOT = SPEC_DIR.parents[1]

datas = [
    (str(PROJECT_ROOT / "config"), "config"),
    (str(PROJECT_ROOT / ".ai" / "prompts"), ".ai/prompts"),
]

frontend_dist = PROJECT_ROOT / "knowledge_base" / "exports" / "app"
if frontend_dist.exists():
    datas.append((str(frontend_dist), "knowledge_base/exports/app"))

hiddenimports = (
    collect_submodules("src")
    + collect_submodules("uvicorn")
    + collect_submodules("fastapi")
    + collect_submodules("scrapling")
)

a = Analysis(
    ["desktop_server.py"],
    pathex=[str(PROJECT_ROOT), str(SPEC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="ai-knowledge-crawler-sidecar",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
