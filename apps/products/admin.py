from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "product_count", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Товаров")
    def product_count(self, obj):
        return obj.products.count()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "preview", "alt_text", "sort_order")
    readonly_fields = ("preview",)

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="max-height:60px;border-radius:6px;" />', obj.image.url)
        return "—"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "stock", "is_active",
                     "is_featured", "preview", "created_at")
    list_filter = ("is_active", "is_featured", "category")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "stock", "is_active", "is_featured")
    inlines = [ProductImageInline]
    fieldsets = (
        ("Основное", {"fields": ("name", "slug", "category", "sku")}),
        ("Описание", {"fields": ("short_description", "description")}),
        ("Цена и наличие", {"fields": ("price", "old_price", "stock")}),
        ("Изображение", {"fields": ("main_image",)}),
        ("Публикация", {"fields": ("is_active", "is_featured")}),
    )

    @admin.display(description="Фото")
    def preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height:40px;border-radius:4px;" />', obj.main_image.url)
        return "—"
