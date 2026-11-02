from django.contrib import admin
from django.utils.html import format_html

from apps.core.models import STATUS_COLORS

from .models import ScanningRequest, ScanningRequestImage


class ScanningRequestImageInline(admin.TabularInline):
    model = ScanningRequestImage
    extra = 0
    readonly_fields = ("preview",)
    fields = ("image", "preview")

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="max-height:80px;border-radius:6px;" />', obj.image.url)
        return "—"


@admin.register(ScanningRequest)
class ScanningRequestAdmin(admin.ModelAdmin):
    list_display = ("request_number", "name", "phone", "object_name", "quantity",
                     "status_badge", "estimated_price", "photo_count", "created_at")
    list_filter = ("status", "scanning_only", "post_processing", "created_at")
    search_fields = ("request_number", "name", "phone", "email", "object_name")
    readonly_fields = ("request_number", "created_at", "updated_at")
    inlines = [ScanningRequestImageInline]
    date_hierarchy = "created_at"
    fieldsets = (
        ("Заявка", {"fields": ("request_number", "status", "estimated_price", "admin_comment")}),
        ("Клиент", {"fields": ("name", "phone", "email", "city")}),
        ("Объект", {"fields": ("object_name", "description", "dimensions", "quantity", "deadline")}),
        ("Требования", {"fields": ("scanning_only", "post_processing", "output_format")}),
        ("Комментарий клиента", {"fields": ("comment",)}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Статус")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:12px;">{}</span>',
            color, obj.get_status_display(),
        )

    @admin.display(description="Фото")
    def photo_count(self, obj):
        return obj.images.count()
