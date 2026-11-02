from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("<str:slug>/", views.product_detail, name="product_detail"),
]
