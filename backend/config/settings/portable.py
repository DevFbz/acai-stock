"""
Settings para a versao .exe (portavel).

- Usa SQLite local (nao precisa Azure SQL)
- Sem Redis/Celery (tarefas rodam sincronas)
- DEBUG=True para servir arquivos estaticos
- Banco de dados criado ao lado do .exe
"""
import os
import sys

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Detectar diretorio do executavel
if getattr(sys, "frozen", False):
    # Rodando como .exe (PyInstaller)
    BASE_DIR_EXE = os.path.dirname(sys.executable)
else:
    BASE_DIR_EXE = BASE_DIR  # noqa: F405

# SQLite ao lado do .exe
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR_EXE, "acai_stock.db"),
    }
}

# Sem Celery/Redis - tarefas sincronas
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email em console (para dev) ou arquivo
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Static files servidos pelo Django
STATIC_URL = "static/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    },
}
