from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core import views as core_views
from apps.core.sitemaps import CategorySitemap, ProductSitemap, StaticViewSitemap

sitemaps = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("manage/", include("apps.dashboard.urls")),

    path("", include("apps.core.urls")),
    path("products/", include("apps.products.urls")),
    path("", include("apps.orders.urls")),  # /orders/cart/, /request/
    path("custom-print/", include("apps.print_requests.urls")),
    path("3d-scanning/", include("apps.scanning.urls")),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", core_views.robots_txt, name="robots_txt"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

admin.site.site_header = "Чтотиб Render — администрирование"
admin.site.site_title = "Чтотиб Render Admin"
admin.site.index_title = "Панель управления"
