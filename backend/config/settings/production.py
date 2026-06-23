import os

from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=[])

# Azure SQL Database
AZURE_SQL_SERVER = env("AZURE_SQL_SERVER")
AZURE_SQL_DATABASE = env("AZURE_SQL_DATABASE")
AZURE_SQL_USER = env("AZURE_SQL_USER")
AZURE_SQL_PASSWORD = env("AZURE_SQL_PASSWORD")
AZURE_SQL_PORT = env("AZURE_SQL_PORT", default="1433")

DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": AZURE_SQL_DATABASE,
        "USER": AZURE_SQL_USER,
        "PASSWORD": AZURE_SQL_PASSWORD,
        "HOST": AZURE_SQL_SERVER,
        "PORT": AZURE_SQL_PORT,
        "OPTIONS": {
            "driver": "ODBC Driver 17 for SQL Server",
            "extra_params": "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
        },
    }
}

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "WARNING",
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
