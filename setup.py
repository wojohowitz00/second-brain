"""
py2app build configuration for Second Brain menu bar app.

Build with: python setup.py py2app
Output: dist/Second Brain.app
"""
from setuptools import setup

APP = ['backend/_scripts/menu_bar_app.py']
DATA_FILES = []

OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'LSUIElement': True,  # Hide from dock (menu bar app)
        'CFBundleName': 'Second Brain',
        'CFBundleDisplayName': 'Second Brain',
        'CFBundleIdentifier': 'com.secondbrain.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'rumps',
        'ollama',
        'requests',
        'certifi',
        'urllib3',
        'httpx',
        'httpcore',
        'anyio',
    ],
    'includes': [
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
    ],
    'excludes': [
        'test',
        'tests',
        'pytest',
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
