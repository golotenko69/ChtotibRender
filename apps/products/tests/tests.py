import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestCatalog:
    def test_catalog_page_loads(self, client, product):
        response = client.get(reverse("products:catalog"))
        assert response.status_code == 200
        assert product.name in response.content.decode()

    def test_catalog_hides_inactive_products(self, client, inactive_product):
        response = client.get(reverse("products:catalog"))
        assert inactive_product.name not in response.content.decode()

    def test_catalog_search(self, client, product):
        response = client.get(reverse("products:catalog"), {"q": product.name[:5]})
        assert product.name in response.content.decode()

    def test_catalog_category_filter(self, client, product, category):
        response = client.get(reverse("products:catalog"), {"category": category.slug})
        assert product.name in response.content.decode()

    def test_anonymous_user_can_browse_catalog(self, client, product):
        # No auth required for browsing — this is the core "no accounts" requirement.
        response = client.get(reverse("products:catalog"))
        assert response.status_code == 200


class TestProductDetail:
    def test_product_detail_page(self, client, product):
        response = client.get(product.get_absolute_url())
        assert response.status_code == 200
        assert product.name in response.content.decode()

    def test_inactive_product_returns_404(self, client, inactive_product):
        response = client.get(reverse("products:product_detail", kwargs={"slug": inactive_product.slug}))
        assert response.status_code == 404

    def test_slug_auto_generated(self, category):
        from apps.products.models import Product
        p = Product.objects.create(name="Новый товар", category=category, price=100, sku="AUTO-1", stock=1)
        assert p.slug

    def test_discount_percent(self, category):
        from apps.products.models import Product
        p = Product.objects.create(
            name="Со скидкой", category=category, price=800, old_price=1000, sku="DISC-1", stock=1,
        )
        assert p.discount_percent == 20
