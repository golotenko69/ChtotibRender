"""Shop contact details (phone, e-mail, messengers) built from settings,
so the success page, contacts page, footer and e-mails share one source."""
import re
from urllib.parse import quote

from django.conf import settings


def _phone_digits(phone):
    digits = re.sub(r"\D", "", phone or "")
    # Russian numbers are often written with a leading 8 instead of +7.
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return digits


def shop_contacts(message=""):
    """Contact links; `message` is pre-filled in the messenger chat where
    the messenger supports it (Telegram by username, WhatsApp)."""
    phone = settings.SHOP_PHONE
    phone_digits = _phone_digits(phone)
    whatsapp_digits = _phone_digits(settings.SHOP_WHATSAPP) or phone_digits
    telegram = settings.SHOP_TELEGRAM.lstrip("@").strip()
    text = quote(message) if message else ""

    if telegram:
        telegram_url = f"https://t.me/{telegram}" + (f"?text={text}" if text else "")
    elif phone_digits:
        telegram_url = f"https://t.me/+{phone_digits}"
    else:
        telegram_url = ""

    whatsapp_url = ""
    if whatsapp_digits:
        whatsapp_url = f"https://wa.me/{whatsapp_digits}" + (f"?text={text}" if text else "")

    email = settings.SHOP_EMAIL
    mailto = ""
    if email:
        mailto = f"mailto:{email}" + (f"?subject={text}" if text else "")

    return {
        "phone": phone,
        "phone_href": f"tel:+{phone_digits}" if phone_digits else "",
        "email": email,
        "mailto": mailto,
        "telegram_url": telegram_url,
        "telegram_handle": f"@{telegram}" if telegram else "",
        "whatsapp_url": whatsapp_url,
        "address": settings.SHOP_ADDRESS,
        "hours": settings.SHOP_HOURS,
    }


def request_message(request_number):
    return f"Здравствуйте! Пишу по заявке № {request_number}."
