import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestPublicPages:
    def test_home_page(self, client):
        response = client.get(reverse("core:home"))
        assert response.status_code == 200

    def test_about_page(self, client):
        response = client.get(reverse("core:about"))
        assert response.status_code == 200

    def test_contact_page(self, client):
        response = client.get(reverse("core:contact"))
        assert response.status_code == 200

    def test_robots_txt(self, client):
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert b"Disallow: /admin/" in response.content

    def test_sitemap_xml(self, client):
        response = client.get("/sitemap.xml")
        assert response.status_code == 200


class TestLegacyDashboardRedirect:
    def test_legacy_url_redirects_to_new_panel(self, client):
        response = client.get(reverse("core:admin_dashboard"))
        assert response.status_code == 302
        assert response.url == reverse("dashboard:home")


class TestRequestNumberGenerator:
    def test_numbers_do_not_collide_across_types(self, client, product, sample_stl, sample_image):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
        client.post(reverse("orders:checkout"), {"first_name": "A", "phone": "+79000000001"})

        client.post(reverse("print_requests:form"), {
            "name": "B", "phone": "+79000000002", "email": "", "project_name": "P",
            "description": "d", "quantity": 1, "material": "PLA", "color": "", "deadline": "",
            "model_url": "", "comment": "", "model_file": sample_stl,
        })

        client.post(reverse("scanning:form"), {
            "name": "C", "phone": "+79000000003", "email": "", "object_name": "O",
            "description": "", "dimensions": "", "quantity": 1, "city": "", "deadline": "",
            "scanning_only": "on", "post_processing": "", "output_format": "STL",
            "comment": "", "photos": [sample_image],
        })

        from apps.orders.models import OrderRequest
        from apps.print_requests.models import CustomPrintRequest
        from apps.scanning.models import ScanningRequest

        assert OrderRequest.objects.first().request_number.startswith("REQ-")
        assert CustomPrintRequest.objects.first().request_number.startswith("PRINT-")
        assert ScanningRequest.objects.first().request_number.startswith("SCAN-")


class TestNoClientAccounts:
    """Explicit checks that the site never grew a customer login/registration surface."""

    def test_no_register_url(self, client):
        response = client.get("/register/")
        assert response.status_code == 404

    def test_no_customer_login_url(self, client):
        response = client.get("/login/")
        assert response.status_code == 404

    def test_no_profile_url(self, client):
        response = client.get("/profile/")
        assert response.status_code == 404

    def test_admin_login_still_works_for_staff(self, client):
        response = client.get("/admin/login/")
        assert response.status_code == 200
