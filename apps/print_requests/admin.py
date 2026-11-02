from django.contrib import admin
from django.utils.html import format_html

from apps.core.models import STATUS_COLORS

from .models import CustomPrintRequest, PrintRequestPhoto


class PrintRequestPhotoInline(admin.TabularInline):
    model = PrintRequestPhoto
    extra = 0
    readonly_fields = ("preview",)
    fields = ("image", "preview")

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="max-height:80px;border-radius:6px;" />', obj.image.url)
        return "—"


@admin.register(CustomPrintRequest)
class CustomPrintRequestAdmin(admin.ModelAdmin):
    list_display = ("request_number", "name", "phone", "material", "quantity",
                     "status_badge", "estimated_price", "has_file", "created_at")
    list_filter = ("status", "material", "created_at")
    search_fields = ("request_number", "name", "phone", "email", "project_name")
    readonly_fields = ("request_number", "created_at", "updated_at", "model_file_link")
    inlines = [PrintRequestPhotoInline]
    date_hierarchy = "created_at"
    fieldsets = (
        ("Заявка", {"fields": ("request_number", "status", "estimated_price", "admin_comment")}),
        ("Клиент", {"fields": ("name", "phone", "email")}),
        ("Проект", {"fields": ("project_name", "description", "quantity", "material", "color", "deadline")}),
        ("Файлы", {"fields": ("model_file", "model_file_link", "model_url")}),
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

    @admin.display(description="Файл", boolean=True)
    def has_file(self, obj):
        return bool(obj.model_file)

    @admin.display(description="Ссылка на файл")
    def model_file_link(self, obj):
        if obj.model_file:
            return format_html('<a href="{}" target="_blank">Скачать файл</a>', obj.model_file.url)
        return "—"
