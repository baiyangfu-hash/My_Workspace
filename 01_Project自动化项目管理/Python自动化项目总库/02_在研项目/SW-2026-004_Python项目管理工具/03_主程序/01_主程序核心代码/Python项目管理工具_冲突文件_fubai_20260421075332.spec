# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('config', 'config'), ('src/plugins', 'src/plugins')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'flask', 'sqlalchemy', 'sqlalchemy.dialects.sqlite', 'sqlalchemy.orm', 'sqlalchemy.ext.declarative', 'click', 'markdown', 'dateutil', 'src', 'src.core', 'src.models', 'src.dao', 'src.services', 'src.ui', 'src.utils', 'src.api', 'src.plugins', 'src.plugins.code_check', 'src.plugins.document_generator'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'cv2', 'IPython', 'jupyter', 'notebook'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Python项目管理工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
