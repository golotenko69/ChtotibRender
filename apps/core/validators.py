"""Reusable validators for user-uploaded files.

Applied to every FileField / ImageField that accepts client uploads
(product images excluded — those are managed by staff in the admin).
"""
import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

# Extensions that are explicitly forbidden, even if somehow whitelisted
# elsewhere. Defence in depth against executable / script uploads.
DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".ps1", ".msi", ".com", ".scr",
    ".js", ".jar", ".py", ".php", ".phtml", ".pl", ".rb", ".cgi",
    ".dll", ".apk", ".app", ".vbs", ".wsf", ".html", ".htm",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

MODEL_EXTENSIONS = {".stl", ".obj", ".3mf", ".step", ".stp"}
# MIME types are unreliable for CAD formats (many browsers send
# application/octet-stream), so model files are validated primarily by
# extension + magic-byte sniffing in validate_model_file_content below.
MODEL_MIME_TYPES = {
    "application/sla",
    "application/vnd.ms-pki.stl",
    "model/stl",
    "model/obj",
    "text/plain",
    "application/octet-stream",
    "application/step",
    "model/step",
}

MAX_IMAGE_SIZE_MB = getattr(settings, "MAX_IMAGE_UPLOAD_MB", 10)
MAX_MODEL_SIZE_MB = getattr(settings, "MAX_MODEL_UPLOAD_MB", 100)


def _ext(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


@deconstructible
class ExtensionAllowlistValidator:
    """Only allow a fixed set of extensions; always reject dangerous ones."""

    def __init__(self, allowed_extensions, max_size_mb):
        self.allowed_extensions = {e.lower() for e in allowed_extensions}
        self.max_size_mb = max_size_mb

    def __call__(self, value):
        ext = _ext(value.name)

        if ext in DANGEROUS_EXTENSIONS:
            raise ValidationError("Загрузка исполняемых или скриптовых файлов запрещена.")

        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"Недопустимый формат файла '{ext}'. "
                f"Разрешены: {', '.join(sorted(self.allowed_extensions))}."
            )

        max_bytes = self.max_size_mb * 1024 * 1024
        if value.size > max_bytes:
            raise ValidationError(f"Файл слишком большой. Максимум {self.max_size_mb} МБ.")

    def __eq__(self, other):
        return (
            isinstance(other, ExtensionAllowlistValidator)
            and self.allowed_extensions == other.allowed_extensions
            and self.max_size_mb == other.max_size_mb
        )


validate_image_upload = ExtensionAllowlistValidator(IMAGE_EXTENSIONS, MAX_IMAGE_SIZE_MB)
validate_model_upload = ExtensionAllowlistValidator(MODEL_EXTENSIONS, MAX_MODEL_SIZE_MB)


# Magic-byte signatures we can sanity-check without extra dependencies.
_IMAGE_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # WEBP starts with RIFF....WEBP
}


def validate_image_content(file_obj):
    """Sniff the first bytes to make sure the payload is really an image,
    not just a renamed file with an image extension."""
    try:
        file_obj.seek(0)
        header = file_obj.read(16)
    finally:
        file_obj.seek(0)

    if header.startswith(b"\xff\xd8\xff"):
        return
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return

    raise ValidationError("Файл не является допустимым изображением.")


def safe_upload_filename(instance, filename, subdir):
    """Generate a random, collision-free filename to avoid path traversal
    and to strip any client-supplied path or characters."""
    ext = _ext(filename)
    new_name = f"{uuid.uuid4().hex}{ext}"
    return os.path.join(subdir, new_name)


def product_image_upload_path(instance, filename):
    return safe_upload_filename(instance, filename, "product_images")


def print_model_upload_path(instance, filename):
    return safe_upload_filename(instance, filename, "print_requests/models")


def print_photo_upload_path(instance, filename):
    return safe_upload_filename(instance, filename, "print_requests/photos")


def scanning_photo_upload_path(instance, filename):
    return safe_upload_filename(instance, filename, "scanning_requests")
