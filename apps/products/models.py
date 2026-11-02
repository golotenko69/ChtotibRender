from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.validators import product_image_upload_path, validate_image_upload


class Category(models.Model):
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", max_length=220, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField(
        "Изображение", upload_to="categories/", blank=True, null=True,
        validators=[validate_image_upload],
    )
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:catalog") + f"?category={self.slug}"


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def featured(self):
        return self.active().filter(is_featured=True)

    def in_stock(self):
        return self.filter(stock__gt=0)


class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Слаг", max_length=280, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    short_description = models.CharField("Краткое описание", max_length=500, blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2,
                                 validators=[MinValueValidator(0)])
    old_price = models.DecimalField("Старая цена", max_digits=10, decimal_places=2,
                                     null=True, blank=True, validators=[MinValueValidator(0)])
    category = models.ForeignKey(
        Category, verbose_name="Категория", related_name="products",
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    main_image = models.ImageField(
        "Главное изображение", upload_to=product_image_upload_path,
        blank=True, null=True, validators=[validate_image_upload],
    )
    sku = models.CharField("Артикул", max_length=64, unique=True)
    stock = models.PositiveIntegerField("Остаток", default=0)
    is_active = models.BooleanField("Активен", default=True, db_index=True)
    is_featured = models.BooleanField("Популярный", default=False)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["is_active", "is_featured"])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or "product"
            slug = base_slug
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base_slug}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", verbose_name="Товар",
                                 on_delete=models.CASCADE)
    image = models.ImageField("Изображение", upload_to=product_image_upload_path,
                               validators=[validate_image_upload])
    alt_text = models.CharField("Alt-текст", max_length=255, blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} — изображение {self.pk}"
