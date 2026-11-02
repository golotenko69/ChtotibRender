from django.contrib import admin
from django.utils.html import format_html

from apps.core.models import STATUS_COLORS

from .models import OrderRequest, OrderRequestItem


class OrderRequestItemInline(admin.TabularInline):
    model = OrderRequestItem
    extra = 0
    readonly_fields = ("product_name", "price", "quantity", "subtotal_display")
    fields = ("product", "product_name", "price", "quantity", "subtotal_display")
    can_delete = False

    @admin.display(description="Сумма")
    def subtotal_display(self, obj):
        return f"{obj.subtotal} ₽" if obj.pk else "—"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ("request_number", "full_name", "phone", "email", "city",
                     "status_badge", "total_price_display", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("request_number", "first_name", "last_name", "phone", "email")
    readonly_fields = ("request_number", "created_at", "updated_at")
    inlines = [OrderRequestItemInline]
    fieldsets = (
        ("Заявка", {"fields": ("request_number", "status", "admin_comment")}),
        ("Клиент", {"fields": ("first_name", "last_name", "phone", "email", "city", "address")}),
        ("Комментарий клиента", {"fields": ("comment",)}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )
    date_hierarchy = "created_at"

    @admin.display(description="Статус")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:12px;">{}</span>',
            color, obj.get_status_display(),
        )

    @admin.display(description="Сумма")
    def total_price_display(self, obj):
        return f"{obj.total_price} ₽"
