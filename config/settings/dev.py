from .base import *  # noqa: F401,F403

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Manifest storage (from base) needs `collectstatic` first; in dev and tests
# serve files straight from static/ so templates render without it.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

INSTALLED_APPS += []  # noqa: F405

INTERNAL_IPS = ["127.0.0.1"]
