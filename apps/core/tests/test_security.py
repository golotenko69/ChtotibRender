"""Regression tests for the issues fixed in the security review."""
import pytest
from django.contrib.sessions.models import Session
from django.urls import reverse

from apps.orders.models import OrderRequest
from apps.print_requests.models import CustomPrintRequest
from apps.scanning.models import ScanningRequest

pytestmark = pytest.mark.django_db


def _place_order(client, product):
    client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
    client.post(reverse("orders:checkout"), {"first_name": "Иван", "phone": "+79001234567"})
    return OrderRequest.objects.latest("pk")


class TestSuccessPagesArePrivate:
    def test_order_success_hidden_from_other_visitors(self, client, product):
        order = _place_order(client, product)
        from django.test import Client

        stranger = Client()
        response = stranger.get(reverse("orders:success", args=[order.request_number]))
        assert response.status_code == 404
        assert "+79001234567" not in response.content.decode()

    def test_order_success_visible_to_submitter(self, client, product):
        order = _place_order(client, product)
        response = client.get(reverse("orders:success", args=[order.request_number]))
        assert response.status_code == 200

    def test_print_and_scan_success_not_enumerable(self, client):
        print_req = CustomPrintRequest.objects.create(
            name="Пётр", phone="+79005556677", description="x", model_url="https://example.com/m.stl"
        )
        scan_req = ScanningRequest.objects.create(name="Анна", phone="+79004443322", object_name="Ваза", description="x")
        assert client.get(reverse("print_requests:success", args=[print_req.request_number])).status_code == 404
        assert client.get(reverse("scanning:success", args=[scan_req.request_number])).status_code == 404


class TestOpenRedirects:
    def test_cart_add_ignores_external_next(self, client, product):
        response = client.post(
            reverse("orders:cart_add", args=[product.id]), {"quantity": 1, "next": "https://evil.example/phish"}
        )
        assert response.status_code == 302
        assert response.url == reverse("orders:cart_detail")

    def test_cart_add_keeps_local_next(self, client, product):
        response = client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1, "next": "/products/"})
        assert response.url == "/products/"

    def test_dashboard_login_ignores_external_next(self, client, admin_user):
        response = client.post(
            reverse("dashboard:login") + "?next=//evil.example/",
            {"username": "admin", "password": "StrongPass123!"},
        )
        assert response.status_code == 302
        assert response.url == reverse("dashboard:home")


class TestDashboardCsrfSafeMethods:
    def test_toggle_active_rejects_get(self, staff_client, product):
        response = staff_client.get(reverse("dashboard:product_toggle_active", args=[product.pk]))
        assert response.status_code == 405
        product.refresh_from_db()
        assert product.is_active is True

    def test_logout_rejects_get(self, staff_client):
        response = staff_client.get(reverse("dashboard:logout"))
        assert response.status_code == 405

    def test_non_staff_login_message_is_generic(self, client, db):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_user(username="client", password="StrongPass123!")
        response = client.post(reverse("dashboard:login"), {"username": "client", "password": "StrongPass123!"})
        assert "нет доступа" not in response.content.decode()


class TestCart:
    def test_anonymous_page_view_creates_no_session(self, client, product):
        client.get(reverse("core:home"))
        client.get(reverse("products:catalog"))
        assert Session.objects.count() == 0

    def test_non_numeric_quantity_does_not_crash(self, client, product):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
        response = client.post(reverse("orders:cart_update", args=[product.id]), {"quantity": "abc"})
        assert response.status_code == 302

    def test_hidden_product_cannot_be_ordered(self, client, product):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
        product.is_active = False
        product.save()
        response = client.get(reverse("orders:checkout"))
        assert response.status_code == 302  # empty cart -> back to catalog
        assert OrderRequest.objects.count() == 0


class TestSecurityHeaders:
    def test_csp_and_permissions_policy_present(self, client):
        response = client.get(reverse("core:home"))
        csp = response.headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in csp
        assert "object-src 'none'" in csp
        assert "camera=()" in response.headers["Permissions-Policy"]
        assert response.headers["X-Frame-Options"] == "DENY"
