# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec para empacotar o Acai Stock em .exe.

Build: pyinstaller acai_stock.spec
Saida: dist/AcaiStock/AcaiStock.exe
"""

import os

block_cipher = None

# Set DJANGO_SETTINGS_MODULE para o hook do PyInstaller
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.portable"

# Diretorio base absoluto
base_dir = r"C:\Users\irisp\OneDrive\Documentos\Breno\ProjetoAcai"
backend_dir = os.path.join(base_dir, "backend")

# Adicionar backend ao path para import do Django
import sys
sys.path.insert(0, backend_dir)

a = Analysis(
    ["backend/launcher.py"],
    pathex=[backend_dir],
    binaries=[],
    datas=[
        # Templates
        (os.path.join(backend_dir, "templates"), "templates"),
        # Static
        (os.path.join(backend_dir, "static"), "static"),
        # Migrations de todos os apps
        (os.path.join(backend_dir, "tenants/migrations"), "tenants/migrations"),
        (os.path.join(backend_dir, "accounts/migrations"), "accounts/migrations"),
        (os.path.join(backend_dir, "inventory/migrations"), "inventory/migrations"),
        (os.path.join(backend_dir, "subscriptions/migrations"), "subscriptions/migrations"),
        (os.path.join(backend_dir, "reports/migrations"), "reports/migrations"),
        (os.path.join(backend_dir, "ai_engine/migrations"), "ai_engine/migrations"),
        (os.path.join(backend_dir, "billing/migrations"), "billing/migrations"),
        (os.path.join(backend_dir, "notifications/migrations"), "notifications/migrations"),
        (os.path.join(backend_dir, "api/migrations"), "api/migrations"),
    ],
    hiddenimports=[
        # Apps Django
        "tenants",
        "accounts",
        "inventory",
        "subscriptions",
        "reports",
        "ai_engine",
        "ai_engine.engine",
        "ai_engine.nlg",
        "ai_engine.chatbot",
        "ai_engine.knowledge_base",
        "ai_engine.graph",
        "ai_engine.tasks",
        "billing",
        "billing.services",
        "billing.tasks",
        "notifications",
        "notifications.services",
        "notifications.tasks",
        "api",
        "api.serializers",
        "api.views",
        # Settings
        "config.settings.base",
        "config.settings.portable",
        # Third-party
        "rest_framework",
        "rest_framework_simplejwt",
        "drf_spectacular",
        "corsheaders",
        "widget_tweaks",
        "django_celery_beat",
        "django_celery_results",
        "langgraph",
        "reportlab",
        "openpyxl",
        "PIL",
        "PIL._tkinter_finder",
    ],
    hookspath=[],
    hooksconfig={
        "django": {"collect_all": False},
    },
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "pytest",
        "factory",
        "IPython",
        "jedi",
    ],
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
    name="AcaiStock",
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
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AcaiStock",
)
