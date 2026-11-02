import apps.core.validators
import apps.scanning.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ScanningRequest",
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
                        max_length=32, validators=[apps.scanning.models.phone_validator], verbose_name="Телефон",
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Email")),
                ("object_name", models.CharField(max_length=255, verbose_name="Название объекта")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("dimensions", models.CharField(blank=True, max_length=255, verbose_name="Примерные размеры")),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Количество объектов",
                    ),
                ),
                ("city", models.CharField(blank=True, max_length=150, verbose_name="Город")),
                ("deadline", models.DateField(blank=True, null=True, verbose_name="Желаемый срок")),
                ("scanning_only", models.BooleanField(default=False, verbose_name="Нужен только скан")),
                ("post_processing", models.BooleanField(default=False, verbose_name="Нужна постобработка")),
                (
                    "output_format",
                    models.CharField(
                        choices=[
                            ("STL", "STL"), ("OBJ", "OBJ"), ("STEP", "STEP"),
                            ("PLY", "PLY"), ("OTHER", "Другое / не знаю"),
                        ],
                        default="STL", max_length=20, verbose_name="Формат результата",
                    ),
                ),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "Новая"), ("REVIEWING", "На рассмотрении"),
                            ("NEED_INFO", "Нужна информация"), ("QUOTED", "Стоимость озвучена"),
                            ("CONFIRMED", "Подтверждена"), ("IN_PROGRESS", "В работе"),
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
                "verbose_name": "Заявка на 3D-сканирование",
                "verbose_name_plural": "Заявки на 3D-сканирование",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ScanningRequestImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "image",
                    models.ImageField(
                        upload_to=apps.core.validators.scanning_photo_upload_path,
                        validators=[apps.core.validators.validate_image_upload], verbose_name="Фото",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Загружено")),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="images",
                        to="scanning.scanningrequest", verbose_name="Заявка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Фото к заявке на сканирование",
                "verbose_name_plural": "Фото к заявкам на сканирование",
            },
        ),
    ]
