from urllib.parse import quote

import pytest
from django.core import mail
from django.urls import reverse

from apps.core.contacts import request_message, shop_contacts
from apps.print_requests.models import CustomPrintRequest

pytestmark = pytest.mark.django_db

SHOP = {
    "SHOP_PHONE": "8 (912) 345-67-89",
    "SHOP_EMAIL": "manager@shop.example",
    "SHOP_TELEGRAM": "@chtotib_manager",
    "SHOP_WHATSAPP": "",
}


@pytest.fixture
def shop_settings(settings):
    for key, value in SHOP.items():
        setattr(settings, key, value)
    return settings


class TestShopContacts:
    def test_links_from_settings(self, shop_settings):
        c = shop_contacts(request_message("PRINT-000007"))
        text = quote("Здравствуйте! Пишу по заявке № PRINT-000007.")
        assert c["phone_href"] == "tel:+79123456789"
        assert c["telegram_url"] == f"https://t.me/chtotib_manager?text={text}"
        # WhatsApp falls back to the shop phone, 8 -> 7.
        assert c["whatsapp_url"] == f"https://wa.me/79123456789?text={text}"
        assert c["mailto"] == f"mailto:manager@shop.example?subject={text}"

    def test_telegram_by_phone_when_no_username(self, shop_settings):
        shop_settings.SHOP_TELEGRAM = ""
        assert shop_contacts()["telegram_url"] == "https://t.me/+79123456789"


class TestSuccessPageContacts:
    def _submit(self, client):
        client.post(reverse("print_requests:form"), {
            "name": "Иван", "phone": "+79001234567", "email": "ivan@example.com",
            "quantity": 1, "model_url": "https://example.com/m.stl",
        })
        return CustomPrintRequest.objects.get()

    def test_success_page_shows_number_and_ways_to_reach_manager(self, client, shop_settings):
        req = self._submit(client)
        html = client.get(reverse("print_requests:success", args=[req.request_number])).content.decode()
        assert req.request_number in html
        assert 'href="tel:+79123456789"' in html
        assert "https://t.me/chtotib_manager?text=" in html
        assert "https://wa.me/79123456789?text=" in html
        assert quote(req.request_number) in html
        assert 'data-copy="%s"' % req.request_number in html

    def test_client_email_lists_contacts(self, client, shop_settings):
        req = self._submit(client)
        client_mail = next(m for m in mail.outbox if "ivan@example.com" in m.to)
        assert req.request_number in client_mail.body
        assert "8 (912) 345-67-89" in client_mail.body
        assert "https://t.me/chtotib_manager" in client_mail.body

    def test_contacts_page_uses_settings(self, client, shop_settings):
        html = client.get(reverse("core:contact")).content.decode()
        assert "8 (912) 345-67-89" in html
        assert "manager@shop.example" in html
