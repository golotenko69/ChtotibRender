from .base import *  # noqa: F401,F403

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += []  # noqa: F405

INTERNAL_IPS = ["127.0.0.1"]
