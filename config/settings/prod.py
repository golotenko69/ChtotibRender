import os

from .base import *  # noqa: F401,F403

DEBUG = False

if not SECRET_KEY or SECRET_KEY.startswith("django-insecure"):  # noqa: F405
    raise RuntimeError("SECRET_KEY must be set to a strong value in production (.env).")

if not ALLOWED_HOSTS or ALLOWED_HOSTS == ["localhost", "127.0.0.1"]:  # noqa: F405
    raise RuntimeError("ALLOWED_HOSTS must be configured in production (.env).")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# --- HTTPS / cookie / header hardening ---
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True") == "True"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]
