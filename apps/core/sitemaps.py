from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.products.models import Category, Product


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.active()

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["core:home", "core:about", "core:contact", "products:catalog",
                "print_requests:form", "scanning:form"]

    def location(self, item):
        return reverse(item)
