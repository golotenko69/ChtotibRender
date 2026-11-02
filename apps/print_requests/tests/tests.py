import pytest
from django.urls import reverse

from apps.print_requests.models import CustomPrintRequest

pytestmark = pytest.mark.django_db


def _base_payload():
    return {
        "name": "Иван",
        "phone": "+7 900 111-22-33",
        "email": "",
        "project_name": "Кронштейн",
        "description": "Нужна деталь по чертежу",
        "quantity": 1,
        "material": "PLA",
        "color": "",
        "deadline": "",
        "model_url": "",
        "comment": "",
    }


class TestCustomPrintRequestForm:
    def test_form_page_loads(self, client):
        response = client.get(reverse("print_requests:form"))
        assert response.status_code == 200

    def test_submit_with_file_creates_request(self, client, sample_stl):
        payload = _base_payload()
        response = client.post(reverse("print_requests:form"), {**payload, "model_file": sample_stl})
        assert response.status_code == 302
        assert CustomPrintRequest.objects.count() == 1
        req = CustomPrintRequest.objects.first()
        assert req.request_number.startswith("PRINT-")

    def test_submit_with_url_only_is_valid(self, client):
        payload = _base_payload()
        payload["model_url"] = "https://example.com/model.stl"
        response = client.post(reverse("print_requests:form"), payload)
        assert response.status_code == 302
        assert CustomPrintRequest.objects.count() == 1

    def test_submit_without_file_or_url_is_invalid(self, client):
        response = client.post(reverse("print_requests:form"), _base_payload())
        assert response.status_code == 200
        assert CustomPrintRequest.objects.count() == 0

    def test_executable_file_is_rejected(self, client, sample_exe):
        payload = _base_payload()
        response = client.post(reverse("print_requests:form"), {**payload, "model_file": sample_exe})
        assert response.status_code == 200
        assert CustomPrintRequest.objects.count() == 0

    def test_photos_are_optional(self, client, sample_stl):
        payload = _base_payload()
        response = client.post(reverse("print_requests:form"), {**payload, "model_file": sample_stl})
        assert response.status_code == 302

    def test_success_page(self, client, sample_stl):
        payload = _base_payload()
        client.post(reverse("print_requests:form"), {**payload, "model_file": sample_stl})
        req = CustomPrintRequest.objects.first()
        response = client.get(reverse("print_requests:success", args=[req.request_number]))
        assert response.status_code == 200

    def test_anonymous_user_can_submit(self, client, sample_stl):
        # No auth required — this is the core "no accounts" requirement.
        payload = _base_payload()
        response = client.post(reverse("print_requests:form"), {**payload, "model_file": sample_stl})
        assert response.status_code == 302
