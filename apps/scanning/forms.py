from django import forms
from django.core.exceptions import ValidationError

from apps.core.validators import validate_image_content, validate_image_upload
from apps.print_requests.forms import MultiFileInput

from .models import ScanningRequest

MAX_SCAN_PHOTOS = 10
MIN_SCAN_PHOTOS = 1


class MultiImageField(forms.FileField):
    widget = MultiFileInput

    def clean(self, data, initial=None):
        if not data:
            raise ValidationError("Загрузите хотя бы одну фотографию объекта.")
        if not isinstance(data, (list, tuple)):
            data = [data]
        if len(data) < MIN_SCAN_PHOTOS:
            raise ValidationError("Загрузите хотя бы одну фотографию объекта.")
        if len(data) > MAX_SCAN_PHOTOS:
            raise ValidationError(f"Можно загрузить не более {MAX_SCAN_PHOTOS} фотографий.")
        cleaned = []
        for f in data:
            validate_image_upload(f)
            validate_image_content(f.file)
            cleaned.append(f)
        return cleaned


class ScanningRequestForm(forms.ModelForm):
    """Short public form: contacts, quantity and photos of the object.
    Size, format and post-processing are agreed with the manager later."""

    photos = MultiImageField(
        required=True,
        label="Фотографии объекта",
        widget=MultiFileInput(attrs={"multiple": True, "accept": "image/jpeg,image/png,image/webp"}),
    )

    class Meta:
        model = ScanningRequest
        fields = ["name", "phone", "email", "quantity"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ваше имя", "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+7 900 000-00-00", "autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "email@example.com", "autocomplete": "email"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": 1, "max": 1000}),
        }
        labels = {"email": "Почта", "quantity": "Количество объектов"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("name", "phone", "email"):
            self.fields[name].required = True
