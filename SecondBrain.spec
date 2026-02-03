# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Second Brain menu bar app.

Build with: pyinstaller SecondBrain.spec
"""

import os
import sys

# Add _scripts to path
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'backend', '_scripts')
sys.path.insert(0, scripts_dir)

block_cipher = None

a = Analysis(
    ['backend/_scripts/menu_bar_app.py'],
    pathex=[scripts_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Local modules
        'menu_bar_app',
        'notifications',
        'process_inbox',
        'message_classifier',
        'ollama_client',
        'vault_scanner',
        'slack_client',
        'file_writer',
        'state',
        'schema',
        'wikilinks',
        'fix_handler',
        'status_handler',
        'task_parser',
        'domain_classifier',
        'veritas_client',
        'youtube_ingest',
        'yt_dlp',
        'whisper',
        # External packages
        'rumps',
        'objc',
        'Foundation',
        'AppKit',
        'ollama',
        'requests',
        'httpx',
        'httpcore',
        'anyio',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'tests', 'pytest'],
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
    name='Second Brain',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
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
    name='Second Brain',
)

app = BUNDLE(
    coll,
    name='Second Brain.app',
    icon=None,
    bundle_identifier='com.secondbrain.app',
    info_plist={
        'LSUIElement': True,  # Hide from dock
        'CFBundleName': 'Second Brain',
        'CFBundleDisplayName': 'Second Brain',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
)
