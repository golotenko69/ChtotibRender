"""Transactional emails for the three request types.

Failures are logged, never raised — a broken SMTP connection must not
prevent a client's request from being saved.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("apps.core.emails")


def _safe_send(subject, message, recipient_list):
    if not recipient_list:
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception:
        logger.exception("Не удалось отправить email на %s", recipient_list)


def _admin_recipients():
    return [email for _, email in getattr(settings, "ADMINS", [])] or \
        ([settings.EMAIL_HOST_USER] if getattr(settings, "EMAIL_HOST_USER", "") else [])


def send_order_request_emails(order_request):
    subject_client = f"Заявка {order_request.request_number} принята"
    message_client = (
        f"Здравствуйте, {order_request.first_name}!\n\n"
        f"Ваша заявка №{order_request.request_number} успешно принята.\n"
        f"Мы свяжемся с вами по телефону {order_request.phone} для уточнения деталей и стоимости.\n\n"
        f"Спасибо, что выбрали нас!"
    )
    if order_request.email:
        _safe_send(subject_client, message_client, [order_request.email])

    subject_admin = f"Новая заявка на товары {order_request.request_number}"
    message_admin = (
        f"Новая заявка на товары: {order_request.request_number}\n"
        f"Клиент: {order_request.full_name}, тел. {order_request.phone}\n"
        f"Позиций: {order_request.items.count() if order_request.pk else 0}\n"
        f"Откройте Django Admin для подробностей."
    )
    _safe_send(subject_admin, message_admin, _admin_recipients())


def send_print_request_emails(print_request):
    subject_client = f"Заявка {print_request.request_number} на печать принята"
    message_client = (
        f"Здравствуйте, {print_request.name}!\n\n"
        f"Ваша заявка №{print_request.request_number} на печать 3D-модели принята.\n"
        f"Мы изучим модель и свяжемся с вами по телефону {print_request.phone}.\n\n"
        f"Спасибо!"
    )
    if print_request.email:
        _safe_send(subject_client, message_client, [print_request.email])

    subject_admin = f"Новая заявка на печать {print_request.request_number}"
    message_admin = (
        f"Новая заявка на печать модели: {print_request.request_number}\n"
        f"Клиент: {print_request.name}, тел. {print_request.phone}\n"
        f"Проект: {print_request.project_name or '—'}\n"
        f"Откройте Django Admin для подробностей."
    )
    _safe_send(subject_admin, message_admin, _admin_recipients())


def send_scanning_request_emails(scan_request):
    subject_client = f"Заявка {scan_request.request_number} на сканирование принята"
    message_client = (
        f"Здравствуйте, {scan_request.name}!\n\n"
        f"Ваша заявка №{scan_request.request_number} на 3D-сканирование принята.\n"
        f"Мы свяжемся с вами по телефону {scan_request.phone}.\n\n"
        f"Спасибо!"
    )
    if scan_request.email:
        _safe_send(subject_client, message_client, [scan_request.email])

    subject_admin = f"Новая заявка на сканирование {scan_request.request_number}"
    message_admin = (
        f"Новая заявка на 3D-сканирование: {scan_request.request_number}\n"
        f"Клиент: {scan_request.name}, тел. {scan_request.phone}\n"
        f"Объект: {scan_request.object_name}\n"
        f"Откройте Django Admin для подробностей."
    )
    _safe_send(subject_admin, message_admin, _admin_recipients())
