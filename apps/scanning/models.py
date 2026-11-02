from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from apps.core.models import RequestNumberMixin
from apps.core.validators import scanning_photo_upload_path, validate_image_upload

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-\(\)]{7,20}$",
    message="Введите корректный номер телефона.",
)


class OutputFormat(models.TextChoices):
    STL = "STL", "STL"
    OBJ = "OBJ", "OBJ"
    STEP = "STEP", "STEP"
    PLY = "PLY", "PLY"
    OTHER = "OTHER", "Другое / не знаю"


class ScanningRequest(RequestNumberMixin, models.Model):
    PREFIX = "SCAN"

    class Status(models.TextChoices):
        NEW = "NEW", "Новая"
        REVIEWING = "REVIEWING", "На рассмотрении"
        NEED_INFO = "NEED_INFO", "Нужна информация"
        QUOTED = "QUOTED", "Стоимость озвучена"
        CONFIRMED = "CONFIRMED", "Подтверждена"
        IN_PROGRESS = "IN_PROGRESS", "В работе"
        COMPLETED = "COMPLETED", "Завершена"
        CANCELLED = "CANCELLED", "Отменена"

    name = models.CharField("Имя", max_length=150)
    phone = models.CharField("Телефон", max_length=32, validators=[phone_validator])
    email = models.EmailField("Email", blank=True)

    object_name = models.CharField("Название объекта", max_length=255)
    description = models.TextField("Описание", blank=True)
    dimensions = models.CharField("Примерные размеры", max_length=255, blank=True)
    quantity = models.PositiveIntegerField("Количество объектов", default=1,
                                            validators=[MinValueValidator(1)])
    city = models.CharField("Город", max_length=150, blank=True)
    deadline = models.DateField("Желаемый срок", null=True, blank=True)

    scanning_only = models.BooleanField("Нужен только скан", default=False)
    post_processing = models.BooleanField("Нужна постобработка", default=False)
    output_format = models.CharField("Формат результата", max_length=20,
                                      choices=OutputFormat.choices, default=OutputFormat.STL)

    comment = models.TextField("Комментарий", blank=True)

    status = models.CharField("Статус", max_length=20, choices=Status.choices,
                               default=Status.NEW, db_index=True)
    admin_comment = models.TextField("Комментарий администратора", blank=True)
    estimated_price = models.DecimalField("Ориентировочная цена", max_digits=10, decimal_places=2,
                                           null=True, blank=True, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Заявка на 3D-сканирование"
        verbose_name_plural = "Заявки на 3D-сканирование"
        ordering = ["-created_at"]

    def __str__(self):
        return self.request_number


class ScanningRequestImage(models.Model):
    request = models.ForeignKey(ScanningRequest, related_name="images", verbose_name="Заявка",
                                 on_delete=models.CASCADE)
    image = models.ImageField("Фото", upload_to=scanning_photo_upload_path,
                               validators=[validate_image_upload])
    created_at = models.DateTimeField("Загружено", auto_now_add=True)

    class Meta:
        verbose_name = "Фото к заявке на сканирование"
        verbose_name_plural = "Фото к заявкам на сканирование"

    def __str__(self):
        return f"Фото к {self.request.request_number}"
