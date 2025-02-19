# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['numpy.fft._pocketfft', 'numpy.core._dtype_ctypes', 'scipy._lib._uarray', 'scipy.fft._pocketfft', 'scipy.spatial.transform._rotation_groups']
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('PyQt5')
hiddenimports += collect_submodules('pynput')
hiddenimports += collect_submodules('pygame')
hiddenimports += collect_submodules('psutil')
hiddenimports += collect_submodules('gputil')


a = Analysis(
    ['TETR.py'],
    pathex=[],
    binaries=[],
    datas=[('render', '.'), ('instance', '.'), ('app', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TETR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\icon.ico'],
    hide_console='hide-early',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TETR',
)
