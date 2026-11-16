import pytest
from django.urls import reverse

from apps.scanning.models import ScanningRequest

pytestmark = pytest.mark.django_db


def _base_payload():
    return {
        "name": "Мария",
        "phone": "+7 900 222-33-44",
        "email": "maria@example.com",
        "quantity": 1,
    }


class TestScanningRequestForm:
    def test_form_page_loads(self, client):
        response = client.get(reverse("scanning:form"))
        assert response.status_code == 200

    def test_form_has_only_short_field_set(self, client):
        response = client.get(reverse("scanning:form"))
        fields = set(response.context["form"].fields)
        for name in ("name", "phone", "email", "quantity", "photos"):
            assert name in fields
        for removed in ("object_name", "description", "dimensions", "city", "deadline",
                        "scanning_only", "post_processing", "output_format", "comment"):
            assert removed not in fields

    def test_submit_with_photo_creates_request(self, client, sample_image):
        response = client.post(reverse("scanning:form"), {**_base_payload(), "photos": [sample_image]})
        assert response.status_code == 302
        req = ScanningRequest.objects.get()
        assert req.request_number.startswith("SCAN-")
        assert req.images.count() == 1
        assert req.email == "maria@example.com"

    def test_submit_without_photo_is_invalid(self, client):
        response = client.post(reverse("scanning:form"), _base_payload())
        assert response.status_code == 200
        assert ScanningRequest.objects.count() == 0

    @pytest.mark.parametrize("field", ["name", "phone", "email"])
    def test_required_fields(self, client, sample_image, field):
        payload = _base_payload()
        payload[field] = ""
        response = client.post(reverse("scanning:form"), {**payload, "photos": [sample_image]})
        assert response.status_code == 200
        assert ScanningRequest.objects.count() == 0

    def test_multiple_photos_saved(self, client, sample_image):
        from django.core.files.uploadedfile import SimpleUploadedFile
        photo2 = SimpleUploadedFile("photo2.jpg", sample_image.read(), content_type="image/jpeg")
        sample_image.seek(0)
        response = client.post(reverse("scanning:form"), {**_base_payload(), "photos": [sample_image, photo2]})
        assert response.status_code == 302
        assert ScanningRequest.objects.get().images.count() == 2

    def test_success_page(self, client, sample_image):
        client.post(reverse("scanning:form"), {**_base_payload(), "photos": [sample_image]})
        req = ScanningRequest.objects.get()
        response = client.get(reverse("scanning:success", args=[req.request_number]))
        assert response.status_code == 200

    def test_anonymous_user_can_submit(self, client, sample_image):
        response = client.post(reverse("scanning:form"), {**_base_payload(), "photos": [sample_image]})
        assert response.status_code == 302
