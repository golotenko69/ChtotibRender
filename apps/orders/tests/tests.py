import pytest
from django.urls import reverse

from apps.orders.models import OrderRequest, OrderRequestItem

pytestmark = pytest.mark.django_db


class TestCart:
    def test_add_to_cart(self, client, product):
        response = client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 2})
        assert response.status_code == 302
        session_cart = client.session["cart"]
        assert session_cart[str(product.id)]["quantity"] == 2

    def test_update_cart_quantity(self, client, product):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
        client.post(reverse("orders:cart_update", args=[product.id]), {"quantity": 5})
        assert client.session["cart"][str(product.id)]["quantity"] == 5

    def test_remove_from_cart(self, client, product):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": 1})
        client.post(reverse("orders:cart_remove", args=[product.id]))
        assert str(product.id) not in client.session.get("cart", {})

    def test_cannot_add_inactive_product(self, client, inactive_product):
        response = client.post(reverse("orders:cart_add", args=[inactive_product.id]), {"quantity": 1})
        assert response.status_code == 404

    def test_empty_checkout_redirects_to_catalog(self, client):
        response = client.get(reverse("orders:checkout"))
        assert response.status_code == 302
        assert response.url == reverse("products:catalog")


class TestCheckout:
    def _add_to_cart(self, client, product, qty=2):
        client.post(reverse("orders:cart_add", args=[product.id]), {"quantity": qty})

    def test_submit_order_request_creates_records(self, client, product):
        self._add_to_cart(client, product, qty=3)
        response = client.post(reverse("orders:checkout"), {
            "first_name": "Иван",
            "phone": "+7 900 123-45-67",
            "email": "",
            "city": "",
            "address": "",
            "comment": "",
        })
        assert response.status_code == 302
        assert OrderRequest.objects.count() == 1
        order = OrderRequest.objects.first()
        assert order.items.count() == 1
        item = order.items.first()
        assert item.quantity == 3
        assert item.product_name == product.name
        assert item.price == product.price

    def test_request_number_is_generated_and_unique(self, client, product):
        self._add_to_cart(client, product)
        client.post(reverse("orders:checkout"), {"first_name": "A", "phone": "+79001112233"})
        self._add_to_cart(client, product)
        client.post(reverse("orders:checkout"), {"first_name": "B", "phone": "+79001112234"})
        numbers = list(OrderRequest.objects.values_list("request_number", flat=True))
        assert len(numbers) == len(set(numbers))
        assert all(n.startswith("REQ-") for n in numbers)

    def test_cart_cleared_after_successful_submit(self, client, product):
        self._add_to_cart(client, product)
        client.post(reverse("orders:checkout"), {"first_name": "Иван", "phone": "+79001234567"})
        assert client.session.get("cart", {}) == {}

    def test_missing_required_fields_shows_errors(self, client, product):
        self._add_to_cart(client, product)
        response = client.post(reverse("orders:checkout"), {"first_name": "", "phone": ""})
        assert response.status_code == 200
        assert OrderRequest.objects.count() == 0

    def test_success_page_shows_request_number(self, client, product):
        self._add_to_cart(client, product)
        client.post(reverse("orders:checkout"), {"first_name": "Иван", "phone": "+79001234567"})
        order = OrderRequest.objects.first()
        response = client.get(reverse("orders:success", args=[order.request_number]))
        assert response.status_code == 200
        assert order.request_number in response.content.decode()

    def test_snapshot_survives_product_price_change(self, client, product):
        self._add_to_cart(client, product, qty=1)
        client.post(reverse("orders:checkout"), {"first_name": "Иван", "phone": "+79001234567"})
        item = OrderRequestItem.objects.first()
        original_price = item.price

        product.price = original_price + 500
        product.save()

        item.refresh_from_db()
        assert item.price == original_price


class TestOrderRequestAdminPermissions:
    def test_anonymous_cannot_access_admin(self, client):
        response = client.get("/admin/orders/orderrequest/")
        assert response.status_code in (302, 403)

    def test_staff_can_access_admin(self, staff_client):
        response = staff_client.get("/admin/orders/orderrequest/")
        assert response.status_code == 200
