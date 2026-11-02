from django.urls import path

from . import views

app_name = "print_requests"

urlpatterns = [
    path("", views.custom_print_request, name="form"),
    path("success/<str:request_number>/", views.success, name="success"),
]
