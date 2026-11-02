"""Access control for the custom shop admin panel (/manage/).

This does NOT introduce a new authentication system: it reuses Django's
built-in auth (the same users created via `createsuperuser` / the old
Django Admin) and simply requires `is_staff`. Customers never touch
this — the public site has no login links pointing here.
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url="dashboard:login")
        if not request.user.is_staff:
            raise PermissionDenied("Доступ к панели управления есть только у сотрудников.")
        return view_func(request, *args, **kwargs)

    return _wrapped
