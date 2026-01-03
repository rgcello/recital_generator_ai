# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['generate_recital.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('repertoire', 'repertoire'),
        ('ai/*.py', 'ai'),
        ('csv_loader.py', '.'),
        ('docx_generator.py', '.'),
        ('sort_students.py', '.'),
    ],
    hiddenimports=['openai', 'docx', 'pydantic', 'pydantic_core', 'csv_loader', 'docx_generator', 'sort_students'],
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
    name='RecitalProgramGenerator',
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
