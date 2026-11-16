import pytest
from django.urls import reverse

from apps.print_requests.models import CustomPrintRequest

pytestmark = pytest.mark.django_db


def _base_payload():
    return {
        "name": "Иван",
        "phone": "+7 900 111-22-33",
        "email": "ivan@example.com",
        "quantity": 1,
        "model_url": "https://example.com/model.stl",
    }


class TestCustomPrintRequestForm:
    def test_form_page_loads(self, client):
        response = client.get(reverse("print_requests:form"))
        assert response.status_code == 200

    def test_form_has_only_short_field_set(self, client):
        response = client.get(reverse("print_requests:form"))
        fields = set(response.context["form"].fields)
        for name in ("name", "phone", "email", "quantity", "model_url"):
            assert name in fields
        for removed in ("project_name", "description", "material", "color", "deadline", "model_file", "photos", "comment"):
            assert removed not in fields

    def test_submit_creates_request(self, client):
        response = client.post(reverse("print_requests:form"), _base_payload())
        assert response.status_code == 302
        req = CustomPrintRequest.objects.get()
        assert req.request_number.startswith("PRINT-")
        assert req.model_url == "https://example.com/model.stl"
        assert req.email == "ivan@example.com"

    @pytest.mark.parametrize("field", ["name", "phone", "email", "model_url"])
    def test_required_fields(self, client, field):
        payload = _base_payload()
        payload[field] = ""
        response = client.post(reverse("print_requests:form"), payload)
        assert response.status_code == 200
        assert CustomPrintRequest.objects.count() == 0

    def test_link_without_scheme_gets_https(self, client):
        payload = _base_payload()
        payload["model_url"] = "example.com/model.stl"
        client.post(reverse("print_requests:form"), payload)
        assert CustomPrintRequest.objects.get().model_url == "https://example.com/model.stl"

    def test_javascript_link_rejected(self, client):
        payload = _base_payload()
        payload["model_url"] = "javascript:alert(1)"
        response = client.post(reverse("print_requests:form"), payload)
        assert response.status_code == 200
        assert CustomPrintRequest.objects.count() == 0

    def test_success_page(self, client):
        client.post(reverse("print_requests:form"), _base_payload())
        req = CustomPrintRequest.objects.get()
        response = client.get(reverse("print_requests:success", args=[req.request_number]))
        assert response.status_code == 200

    def test_anonymous_user_can_submit(self, client):
        # No auth required — this is the core "no accounts" requirement.
        response = client.post(reverse("print_requests:form"), _base_payload())
        assert response.status_code == 302
