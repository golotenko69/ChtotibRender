import pytest
from django.urls import reverse

from apps.products.models import Category, Product

pytestmark = pytest.mark.django_db


class TestDashboardAccess:
    def test_anonymous_redirected_to_login(self, client):
        response = client.get(reverse("dashboard:home"))
        assert response.status_code == 302
        assert reverse("dashboard:login") in response.url

    def test_non_staff_user_gets_403(self, client, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        User.objects.create_user(username="customer", password="pass12345!!", is_staff=False)
        client.login(username="customer", password="pass12345!!")
        response = client.get(reverse("dashboard:home"))
        assert response.status_code == 403

    def test_staff_user_can_view_dashboard(self, staff_client):
        response = staff_client.get(reverse("dashboard:home"))
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        response = client.get(reverse("dashboard:login"))
        assert response.status_code == 200

    def test_non_staff_cannot_log_in_via_dashboard_form(self, client, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        User.objects.create_user(username="customer2", password="pass12345!!", is_staff=False)
        response = client.post(reverse("dashboard:login"), {"username": "customer2", "password": "pass12345!!"})
        assert response.status_code == 200  # re-renders login page with an error
        assert not response.wsgi_request.user.is_authenticated

    def test_staff_can_log_in_and_reach_dashboard(self, client, admin_user):
        response = client.post(
            reverse("dashboard:login"), {"username": "admin", "password": "StrongPass123!"}
        )
        assert response.status_code == 302
        assert response.url == reverse("dashboard:home")

    def test_logout_redirects_to_login(self, staff_client):
        response = staff_client.get(reverse("dashboard:logout"))
        assert response.status_code == 302
        assert response.url == reverse("dashboard:login")


class TestProductManagement:
    def test_product_list_requires_staff(self, client):
        response = client.get(reverse("dashboard:product_list"))
        assert response.status_code == 302

    def test_staff_sees_product_list(self, staff_client, product):
        response = staff_client.get(reverse("dashboard:product_list"))
        assert response.status_code == 200
        assert product.name in response.content.decode()

    def test_staff_can_create_product(self, staff_client, category):
        response = staff_client.post(reverse("dashboard:product_create"), {
            "name": "Новый товар из панели",
            "category": category.id,
            "sku": "DASH-001",
            "short_description": "",
            "description": "",
            "price": "1500",
            "old_price": "",
            "stock": "5",
            "is_active": "on",
            "is_featured": "",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        })
        assert response.status_code == 302
        assert Product.objects.filter(sku="DASH-001").exists()

    def test_staff_can_edit_product(self, staff_client, product, category):
        url = reverse("dashboard:product_edit", args=[product.pk])
        response = staff_client.post(url, {
            "name": "Обновленное имя",
            "category": category.id,
            "sku": product.sku,
            "short_description": "",
            "description": "",
            "price": "2000",
            "old_price": "",
            "stock": "3",
            "is_active": "on",
            "is_featured": "",
            "images-TOTAL_FORMS": "0",
            "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0",
            "images-MAX_NUM_FORMS": "1000",
        })
        assert response.status_code == 302
        product.refresh_from_db()
        assert product.name == "Обновленное имя"
        assert product.stock == 3

    def test_staff_can_delete_product(self, staff_client, product):
        url = reverse("dashboard:product_delete", args=[product.pk])
        response = staff_client.post(url)
        assert response.status_code == 302
        assert not Product.objects.filter(pk=product.pk).exists()

    def test_toggle_active_flips_flag(self, staff_client, product):
        assert product.is_active is True
        staff_client.post(reverse("dashboard:product_toggle_active", args=[product.pk]))
        product.refresh_from_db()
        assert product.is_active is False


class TestCategoryManagement:
    def test_staff_can_create_category(self, staff_client):
        response = staff_client.post(reverse("dashboard:category_create"), {
            "name": "Новая категория", "description": "", "is_active": "on",
        })
        assert response.status_code == 302
        assert Category.objects.filter(name="Новая категория").exists()

    def test_staff_can_delete_category(self, staff_client, category):
        response = staff_client.post(reverse("dashboard:category_delete", args=[category.pk]))
        assert response.status_code == 302
        assert not Category.objects.filter(pk=category.pk).exists()


class TestRequestQueueManagement:
    def test_order_detail_requires_staff(self, client, product):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
        client.post(reverse("orders:checkout"), {"first_name": "Иван", "phone": "+79001234567"})
        from apps.orders.models import OrderRequest
        order = OrderRequest.objects.first()
        response = client.get(reverse("dashboard:order_detail", args=[order.pk]))
        assert response.status_code == 302

    def test_staff_can_update_order_status(self, staff_client, client, product):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
        client.post(reverse("orders:checkout"), {"first_name": "Иван", "phone": "+79001234567"})
        from apps.orders.models import OrderRequest
        order = OrderRequest.objects.first()

        response = staff_client.post(reverse("dashboard:order_detail", args=[order.pk]), {
            "status": "CONTACTED", "admin_comment": "Позвонили клиенту",
        })
        assert response.status_code == 302
        order.refresh_from_db()
        assert order.status == "CONTACTED"
        assert order.admin_comment == "Позвонили клиенту"

    def test_staff_can_set_estimated_price_on_print_request(self, staff_client, client, sample_stl):
        client.post(reverse("print_requests:form"), {
            "name": "Иван", "phone": "+79001234567", "email": "", "project_name": "P",
            "description": "d", "quantity": 1, "material": "PLA", "color": "", "deadline": "",
            "model_url": "", "comment": "", "model_file": sample_stl,
        })
        from apps.print_requests.models import CustomPrintRequest
        req = CustomPrintRequest.objects.first()

        response = staff_client.post(reverse("dashboard:print_detail", args=[req.pk]), {
            "status": "QUOTED", "estimated_price": "3500", "admin_comment": "",
        })
        assert response.status_code == 302
        req.refresh_from_db()
        assert req.status == "QUOTED"
        assert req.estimated_price == 3500

    def test_queue_filters_by_status(self, staff_client, client, product):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
        client.post(reverse("orders:checkout"), {"first_name": "Иван", "phone": "+79001234567"})
        response = staff_client.get(reverse("dashboard:order_list"), {"status": "NEW"})
        assert response.status_code == 200
        response_cancelled = staff_client.get(reverse("dashboard:order_list"), {"status": "CANCELLED"})
        assert response_cancelled.status_code == 200
