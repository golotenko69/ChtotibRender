import apps.core.validators
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Название")),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True, verbose_name="Слаг")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="categories/",
                        validators=[apps.core.validators.validate_image_upload],
                        verbose_name="Изображение",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Активна")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
            ],
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                ("slug", models.SlugField(blank=True, max_length=280, unique=True, verbose_name="Слаг")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("short_description", models.CharField(blank=True, max_length=500, verbose_name="Краткое описание")),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Цена",
                    ),
                ),
                (
                    "old_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Старая цена",
                    ),
                ),
                (
                    "main_image",
                    models.ImageField(
                        blank=True, null=True,
                        upload_to=apps.core.validators.product_image_upload_path,
                        validators=[apps.core.validators.validate_image_upload],
                        verbose_name="Главное изображение",
                    ),
                ),
                ("sku", models.CharField(max_length=64, unique=True, verbose_name="Артикул")),
                ("stock", models.PositiveIntegerField(default=0, verbose_name="Остаток")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="Активен")),
                ("is_featured", models.BooleanField(default=False, verbose_name="Популярный")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
                (
                    "category",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products", to="products.category", verbose_name="Категория",
                    ),
                ),
            ],
            options={
                "verbose_name": "Товар",
                "verbose_name_plural": "Товары",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "image",
                    models.ImageField(
                        upload_to=apps.core.validators.product_image_upload_path,
                        validators=[apps.core.validators.validate_image_upload],
                        verbose_name="Изображение",
                    ),
                ),
                ("alt_text", models.CharField(blank=True, max_length=255, verbose_name="Alt-текст")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="images",
                        to="products.product", verbose_name="Товар",
                    ),
                ),
            ],
            options={
                "verbose_name": "Изображение товара",
                "verbose_name_plural": "Изображения товара",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["is_active", "is_featured"], name="products_pr_is_acti_2f0a4e_idx"),
        ),
    ]
