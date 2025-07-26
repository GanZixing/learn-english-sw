# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('pyttsx3') + collect_submodules('sounddevice')
datas = collect_data_files('matplotlib') + collect_data_files('pyttsx3') + collect_data_files('sounddevice')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='learn_speech',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # 改为 True 需安装 strip 工具
    upx=True,     # 需系统有 upx.exe
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='learn_speech'
)
