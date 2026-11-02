from django.urls import path

from . import views

app_name = "scanning"

urlpatterns = [
    path("", views.scanning_request, name="form"),
    path("success/<str:request_number>/", views.success, name="success"),
]
