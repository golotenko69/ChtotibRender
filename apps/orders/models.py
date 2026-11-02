from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from apps.core.models import RequestNumberMixin
from apps.products.models import Product

phone_validator = RegexValidator(
    regex=r"^\+?[0-9\s\-\(\)]{7,20}$",
    message="Введите корректный номер телефона.",
)


class OrderRequest(RequestNumberMixin, models.Model):
    PREFIX = "REQ"

    class Status(models.TextChoices):
        NEW = "NEW", "Новая"
        CONTACTED = "CONTACTED", "Связались с клиентом"
        CONFIRMED = "CONFIRMED", "Подтверждена"
        IN_PRODUCTION = "IN_PRODUCTION", "В производстве"
        READY = "READY", "Готова"
        COMPLETED = "COMPLETED", "Завершена"
        CANCELLED = "CANCELLED", "Отменена"

    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Телефон", max_length=32, validators=[phone_validator])
    city = models.CharField("Город", max_length=150, blank=True)
    address = models.CharField("Адрес", max_length=500, blank=True)
    comment = models.TextField("Комментарий", blank=True)

    status = models.CharField("Статус", max_length=20, choices=Status.choices,
                               default=Status.NEW, db_index=True)
    admin_comment = models.TextField("Комментарий администратора", blank=True)

    created_at = models.DateTimeField("Создана", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Заявка на товары"
        verbose_name_plural = "Заявки на товары"
        ordering = ["-created_at"]

    def __str__(self):
        return self.request_number

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.all()), 0)


class OrderRequestItem(models.Model):
    request = models.ForeignKey(OrderRequest, related_name="items", verbose_name="Заявка",
                                 on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", verbose_name="Товар",
                                 on_delete=models.SET_NULL, null=True, blank=True)
    # Snapshot fields: kept even if the underlying Product is edited/removed later.
    product_name = models.CharField("Название товара", max_length=255)
    price = models.DecimalField("Цена на момент заказа", max_digits=10, decimal_places=2,
                                 validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField("Количество", default=1,
                                            validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Позиция заявки"
        verbose_name_plural = "Позиции заявки"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
