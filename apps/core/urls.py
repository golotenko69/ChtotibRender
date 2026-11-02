from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    # Legacy URL — the real staff panel now lives at /manage/.
    path("dashboard/", RedirectView.as_view(pattern_name="dashboard:home", permanent=False), name="admin_dashboard"),
]
