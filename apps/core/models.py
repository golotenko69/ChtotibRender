from django.db import models, transaction


class RequestNumberMixin(models.Model):
    """Abstract mixin providing a unique, human-readable request number,
    e.g. REQ-000123, PRINT-000045, SCAN-000007.

    The number is generated server-side inside a transaction using a
    row-locked counter row, so it stays correct under concurrent writes
    without relying on the database's autoincrement id (which could
    leave gaps or be guessed/enumerated).
    """

    PREFIX = "REQ"

    request_number = models.CharField(
        max_length=32, unique=True, editable=False, blank=True, db_index=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.request_number:
            self.request_number = self._generate_request_number()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_request_number(cls):
        from apps.core.models import RequestCounter

        with transaction.atomic():
            counter, _ = RequestCounter.objects.select_for_update().get_or_create(
                prefix=cls.PREFIX, defaults={"last_value": 0}
            )
            counter.last_value += 1
            counter.save(update_fields=["last_value"])
            return f"{cls.PREFIX}-{counter.last_value:06d}"


class RequestCounter(models.Model):
    """One row per prefix (REQ / PRINT / SCAN), locked on write to hand
    out sequential, gap-free numbers."""

    prefix = models.CharField(max_length=16, unique=True)
    last_value = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Счетчик номеров заявок"
        verbose_name_plural = "Счетчики номеров заявок"

    def __str__(self):
        return f"{self.prefix}: {self.last_value}"


STATUS_COLORS = {
    "NEW": "#2563eb",
    "REVIEWING": "#7c3aed",
    "CONTACTED": "#7c3aed",
    "NEED_INFO": "#d97706",
    "QUOTED": "#0891b2",
    "CONFIRMED": "#059669",
    "IN_PRODUCTION": "#ea580c",
    "IN_PROGRESS": "#ea580c",
    "READY": "#16a34a",
    "COMPLETED": "#15803d",
    "CANCELLED": "#dc2626",
}
