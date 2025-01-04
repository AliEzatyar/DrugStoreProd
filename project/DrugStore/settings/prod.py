from DrugStore.settings.base import *
import logging
from os import environ as env


DEBUG = False

ALLOWED_HOSTS = ["*"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.get("DB_NAME"),
        "USER": env.get("DB_USER"),
        "PASSWORD": env.get("DB_PASSWORD"),
        "PORT": 5432,
        "HOST": env.get("DB_HOST"),
    }
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True # redirecting http requests  to https
# logging
import os


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "sim": {
            "format": "{asctime}:{levelname}- {name} {module}.py (line {lineno:d}). {message} ",
            "style": "{",
        }
    },
    "handlers": {
        "info": {
            "level": "INFO",
            "filename": os.path.join(BASE_DIR, "logging", "info.log"),
            "formatter": "sim",
            "class": "logging.FileHandler",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["info"],
            "level": "INFO",
            "propagate": True,
        },
        "print_logger": {
            "handlers": ["info"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
SESSION_COOKIE_AGE = 3 * 30 * 86400 # 3 months no login needed