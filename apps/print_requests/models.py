from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from apps.core.models import RequestNumberMixin
from apps.core.validators import (
    print_model_upload_path,
    print_photo_upload_path,
    validate_image_upload,
    validate_model_upload,
)

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-\(\)]{7,20}$",
    message="Введите корректный номер телефона.",
)


class Material(models.TextChoices):
    PLA = "PLA", "PLA"
    ABS = "ABS", "ABS"
    PETG = "PETG", "PETG"
    RESIN = "RESIN", "Фотополимер (Resin)"
    NYLON = "NYLON", "Нейлон"
    TPU = "TPU", "TPU (гибкий)"
    OTHER = "OTHER", "Другое / не знаю"


class CustomPrintRequest(RequestNumberMixin, models.Model):
    PREFIX = "PRINT"

    class Status(models.TextChoices):
        NEW = "NEW", "Новая"
        REVIEWING = "REVIEWING", "На рассмотрении"
        NEED_INFO = "NEED_INFO", "Нужна информация"
        QUOTED = "QUOTED", "Стоимость озвучена"
        CONFIRMED = "CONFIRMED", "Подтверждена"
        IN_PRODUCTION = "IN_PRODUCTION", "В производстве"
        COMPLETED = "COMPLETED", "Завершена"
        CANCELLED = "CANCELLED", "Отменена"

    name = models.CharField("Имя", max_length=150)
    phone = models.CharField("Телефон", max_length=32, validators=[phone_validator])
    email = models.EmailField("Email", blank=True)

    project_name = models.CharField("Название проекта", max_length=255, blank=True)
    description = models.TextField("Описание")
    quantity = models.PositiveIntegerField("Количество", default=1,
                                            validators=[MinValueValidator(1)])
    material = models.CharField("Материал", max_length=20, choices=Material.choices,
                                 default=Material.OTHER)
    color = models.CharField("Цвет", max_length=100, blank=True)
    deadline = models.DateField("Желаемый срок", null=True, blank=True)

    model_file = models.FileField(
        "3D-файл модели", upload_to=print_model_upload_path, blank=True, null=True,
        validators=[validate_model_upload],
    )
    model_url = models.URLField("Ссылка на модель", blank=True)

    comment = models.TextField("Комментарий", blank=True)

    status = models.CharField("Статус", max_length=20, choices=Status.choices,
                               default=Status.NEW, db_index=True)
    admin_comment = models.TextField("Комментарий администратора", blank=True)
    estimated_price = models.DecimalField("Ориентировочная цена", max_digits=10, decimal_places=2,
                                           null=True, blank=True, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Заявка на печать модели"
        verbose_name_plural = "Заявки на печать моделей"
        ordering = ["-created_at"]

    def __str__(self):
        return self.request_number

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.model_file and not self.model_url:
            raise ValidationError(
                "Прикрепите файл модели или укажите ссылку на модель (можно и то, и другое)."
            )


class PrintRequestPhoto(models.Model):
    """Optional additional reference photos for a custom print request
    (up to MAX_PRINT_PHOTOS, enforced in the form)."""

    request = models.ForeignKey(
        CustomPrintRequest, related_name="photos", verbose_name="Заявка",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        "Фото", upload_to=print_photo_upload_path, validators=[validate_image_upload],
    )
    created_at = models.DateTimeField("Загружено", auto_now_add=True)

    class Meta:
        verbose_name = "Фото к заявке на печать"
        verbose_name_plural = "Фото к заявкам на печать"

    def __str__(self):
        return f"Фото к {self.request.request_number}"
