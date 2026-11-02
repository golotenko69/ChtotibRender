import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import apps.orders.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "request_number",
                    models.CharField(blank=True, db_index=True, editable=False, max_length=32, unique=True),
                ),
                ("first_name", models.CharField(max_length=150, verbose_name="Имя")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="Фамилия")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Email")),
                (
                    "phone",
                    models.CharField(
                        max_length=32, validators=[apps.orders.models.phone_validator], verbose_name="Телефон",
                    ),
                ),
                ("city", models.CharField(blank=True, max_length=150, verbose_name="Город")),
                ("address", models.CharField(blank=True, max_length=500, verbose_name="Адрес")),
                ("comment", models.TextField(blank=True, verbose_name="Комментарий")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "Новая"),
                            ("CONTACTED", "Связались с клиентом"),
                            ("CONFIRMED", "Подтверждена"),
                            ("IN_PRODUCTION", "В производстве"),
                            ("READY", "Готова"),
                            ("COMPLETED", "Завершена"),
                            ("CANCELLED", "Отменена"),
                        ],
                        db_index=True, default="NEW", max_length=20, verbose_name="Статус",
                    ),
                ),
                ("admin_comment", models.TextField(blank=True, verbose_name="Комментарий администратора")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлена")),
            ],
            options={
                "verbose_name": "Заявка на товары",
                "verbose_name_plural": "Заявки на товары",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderRequestItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=255, verbose_name="Название товара")),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Цена на момент заказа",
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Количество",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                        related_name="order_items", to="products.product", verbose_name="Товар",
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="items",
                        to="orders.orderrequest", verbose_name="Заявка",
                    ),
                ),
            ],
            options={
                "verbose_name": "Позиция заявки",
                "verbose_name_plural": "Позиции заявки",
            },
        ),
    ]
