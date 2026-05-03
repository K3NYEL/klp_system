# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['programa_de_facturacion.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'reportlab',
        'reportlab.lib',
        'reportlab.platypus',
        'reportlab_mods',
        'reportlab.platypus.cleanBlockQuotedText',
        'reportlab.platypus.XPreformatted',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
app_icon = 'facturacion_ico.ico'

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='facturacion',
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
    icon=[app_icon],
)
