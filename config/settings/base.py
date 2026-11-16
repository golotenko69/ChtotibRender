"""
Base settings shared by development and production.
Environment-specific overrides live in dev.py / prod.py.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-me-in-env")

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",

    "apps.core",
    "apps.products",
    "apps.orders",
    "apps.print_requests",
    "apps.scanning",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.cart",
                "apps.core.context_processors.shop_contacts",
                "apps.dashboard.context_processors.nav_counts",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "printshop"),
        "USER": os.environ.get("POSTGRES_USER", "printshop"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "printshop"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = os.environ.get("TIME_ZONE", "Europe/Moscow")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Cart / sessions — clients have no accounts, only anonymous sessions.
# ---------------------------------------------------------------------------
CART_SESSION_ID = "cart"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# ---------------------------------------------------------------------------
# File upload limits (also enforced in apps/core/validators.py)
# ---------------------------------------------------------------------------
MAX_IMAGE_UPLOAD_MB = int(os.environ.get("MAX_IMAGE_UPLOAD_MB", 10))
MAX_MODEL_UPLOAD_MB = int(os.environ.get("MAX_MODEL_UPLOAD_MB", 100))
# Caps the non-file part of a request body held in memory (file uploads
# are streamed to disk and limited per field by the validators).
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FILES = 20
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
FILE_UPLOAD_PERMISSIONS = 0o644

# ---------------------------------------------------------------------------
# Shop contacts shown to clients (success page, contacts page, footer,
# e-mails). Telegram is a username without @; if empty, the Telegram
# link opens a chat by phone number. WhatsApp defaults to SHOP_PHONE.
# The defaults are placeholders: set real values in .env before launch.
# ---------------------------------------------------------------------------
SHOP_PHONE = os.environ.get("SHOP_PHONE", "+7 (900) 000-00-00")
SHOP_EMAIL = os.environ.get("SHOP_EMAIL", "manager@chtotib-render.example")
SHOP_TELEGRAM = os.environ.get("SHOP_TELEGRAM", "chtotib_render_test_bot")
SHOP_WHATSAPP = os.environ.get("SHOP_WHATSAPP", "")
SHOP_ADDRESS = os.environ.get("SHOP_ADDRESS", "г. Москва, ул. Примерная, д. 1")
SHOP_HOURS = os.environ.get("SHOP_HOURS", "Пн–Пт: 10:00–19:00")

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@3dprint.example")

ADMINS = []
_admin_email = os.environ.get("ADMIN_EMAIL")
if _admin_email:
    ADMINS = [("Admin", _admin_email)]

# ---------------------------------------------------------------------------
# Logging — never log secrets (passwords / keys are excluded by design:
# only exception tracebacks and short messages are logged, no request
# bodies or settings dumps).
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "app.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console", "file"], "level": "ERROR", "propagate": False},
        "apps": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
    },
}

LOGIN_URL = "/manage/login/"
