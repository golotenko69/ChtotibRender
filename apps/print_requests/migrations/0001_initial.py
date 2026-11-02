import apps.core.validators
import apps.print_requests.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CustomPrintRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "request_number",
                    models.CharField(blank=True, db_index=True, editable=False, max_length=32, unique=True),
                ),
                ("name", models.CharField(max_length=150, verbose_name="Имя")),
                (
                    "phone",
                    models.CharField(
                        max_length=32, validators=[apps.print_requests.models.phone_validator], verbose_name="Телефон",
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Email")),
                ("project_name", models.CharField(blank=True, max_length=255, verbose_name="Название проекта")),
                ("description", models.TextField(verbose_name="Описание")),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Количество",
                    ),
                ),
                (
                    "material",
                    models.CharField(
                        choices=[
                            ("PLA", "PLA"), ("ABS", "ABS"), ("PETG", "PETG"),
                            ("RESIN", "Фотополимер (Resin)"), ("NYLON", "Нейлон"),
                            ("TPU", "TPU (гибкий)"), ("OTHER", "Другое / не знаю"),
                        ],
                        default="OTHER", max_length=20, verbose_name="Материал",
                    ),
                ),
                ("color", models.CharField(blank=True, max_length=100, verbose_name="Цвет")),
                ("deadline", models.DateField(blank=True, null=True, verbose_name="Желаемый срок")),
                (
                    "model_file",
                    models.FileField(
                        blank=True, null=True, upload_to=apps.core.validators.print_model_upload_path,
                        validators=[apps.core.validators.validate_model_upload], verbose_name="3D-файл модели",
                    ),
                ),
                ("model_url", models.URLField(blank=True, verbose_name="Ссылка на модель")),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "Новая"), ("REVIEWING", "На рассмотрении"),
                            ("NEED_INFO", "Нужна информация"), ("QUOTED", "Стоимость озвучена"),
                            ("CONFIRMED", "Подтверждена"), ("IN_PRODUCTION", "В производстве"),
                            ("COMPLETED", "Завершена"), ("CANCELLED", "Отменена"),
                        ],
                        db_index=True, default="NEW", max_length=20, verbose_name="Статус",
                    ),
                ),
                ("admin_comment", models.TextField(blank=True, verbose_name="Комментарий администратора")),
                (
                    "estimated_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Ориентировочная цена",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлена")),
            ],
            options={
                "verbose_name": "Заявка на печать модели",
                "verbose_name_plural": "Заявки на печать моделей",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PrintRequestPhoto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "image",
                    models.ImageField(
                        upload_to=apps.core.validators.print_photo_upload_path,
                        validators=[apps.core.validators.validate_image_upload], verbose_name="Фото",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Загружено")),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="photos",
                        to="print_requests.customprintrequest", verbose_name="Заявка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Фото к заявке на печать",
                "verbose_name_plural": "Фото к заявкам на печать",
            },
        ),
    ]
