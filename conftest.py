import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.products.models import Category, Product


@pytest.fixture
def category(db):
    return Category.objects.create(name="Фигурки", slug="figures")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Тестовая фигурка",
        category=category,
        price=1000,
        sku="TEST-001",
        stock=10,
        is_active=True,
    )


@pytest.fixture
def inactive_product(db, category):
    return Product.objects.create(
        name="Скрытый товар",
        category=category,
        price=500,
        sku="TEST-HIDDEN",
        stock=5,
        is_active=False,
    )


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_superuser(username="admin", email="admin@example.com", password="StrongPass123!")


@pytest.fixture
def staff_client(client, admin_user):
    client.force_login(admin_user)
    return client


def _tiny_jpeg_bytes():
    # Minimal valid-looking JPEG header + payload, enough to pass our
    # magic-byte sniffing without pulling in Pillow-generated fixtures.
    return b"\xff\xd8\xff\xe0" + b"\x00" * 64


@pytest.fixture
def sample_image():
    return SimpleUploadedFile("photo.jpg", _tiny_jpeg_bytes(), content_type="image/jpeg")


@pytest.fixture
def sample_stl():
    content = b"solid test\nfacet normal 0 0 0\nendsolid test\n"
    return SimpleUploadedFile("model.stl", content, content_type="application/sla")


@pytest.fixture
def sample_exe():
    return SimpleUploadedFile("virus.exe", b"MZ\x90\x00" + b"\x00" * 32, content_type="application/octet-stream")
