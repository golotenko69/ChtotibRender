import pytest
from django.urls import reverse

from apps.scanning.models import ScanningRequest

pytestmark = pytest.mark.django_db


def _base_payload():
    return {
        "name": "Мария",
        "phone": "+7 900 222-33-44",
        "email": "",
        "object_name": "Статуэтка",
        "description": "",
        "dimensions": "20x15x10",
        "quantity": 1,
        "city": "Москва",
        "deadline": "",
        "scanning_only": "on",
        "post_processing": "",
        "output_format": "STL",
        "comment": "",
    }


class TestScanningRequestForm:
    def test_form_page_loads(self, client):
        response = client.get(reverse("scanning:form"))
        assert response.status_code == 200

    def test_submit_with_photo_creates_request(self, client, sample_image):
        payload = _base_payload()
        response = client.post(reverse("scanning:form"), {**payload, "photos": [sample_image]})
        assert response.status_code == 302
        assert ScanningRequest.objects.count() == 1
        req = ScanningRequest.objects.first()
        assert req.request_number.startswith("SCAN-")
        assert req.images.count() == 1

    def test_submit_without_photo_is_invalid(self, client):
        response = client.post(reverse("scanning:form"), _base_payload())
        assert response.status_code == 200
        assert ScanningRequest.objects.count() == 0

    def test_multiple_photos_saved(self, client, sample_image):
        from django.core.files.uploadedfile import SimpleUploadedFile
        photo2 = SimpleUploadedFile("photo2.jpg", sample_image.read(), content_type="image/jpeg")
        sample_image.seek(0)
        payload = _base_payload()
        response = client.post(reverse("scanning:form"), {**payload, "photos": [sample_image, photo2]})
        assert response.status_code == 302
        req = ScanningRequest.objects.first()
        assert req.images.count() == 2

    def test_success_page(self, client, sample_image):
        payload = _base_payload()
        client.post(reverse("scanning:form"), {**payload, "photos": [sample_image]})
        req = ScanningRequest.objects.first()
        response = client.get(reverse("scanning:success", args=[req.request_number]))
        assert response.status_code == 200

    def test_anonymous_user_can_submit(self, client, sample_image):
        payload = _base_payload()
        response = client.post(reverse("scanning:form"), {**payload, "photos": [sample_image]})
        assert response.status_code == 302
