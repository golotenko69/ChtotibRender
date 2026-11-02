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
    photos = MultiImageField(
        required=True,
        label="Фотографии объекта",
        widget=MultiFileInput(attrs={"multiple": True, "accept": "image/jpeg,image/png,image/webp"}),
    )

    class Meta:
        model = ScanningRequest
        fields = [
            "name", "phone", "email", "object_name", "description", "dimensions",
            "quantity", "city", "deadline", "scanning_only", "post_processing",
            "output_format", "comment",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ваше имя"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+7 900 000-00-00"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "email@example.com"}),
            "object_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Например, статуэтка"}),
            "description": forms.Textarea(attrs={"class": "form-textarea", "rows": 4}),
            "dimensions": forms.TextInput(attrs={"class": "form-input", "placeholder": "например, 20×15×10 см"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": 1}),
            "city": forms.TextInput(attrs={"class": "form-input", "placeholder": "Город"}),
            "deadline": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "output_format": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-textarea", "rows": 3}),
        }
