from django import forms
from django.core.exceptions import ValidationError

from apps.core.validators import validate_image_content, validate_image_upload, validate_model_upload

from .models import CustomPrintRequest

MAX_PRINT_PHOTOS = 5


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, "getlist"):
            return files.getlist(name)
        return files.get(name)


class MultiFileField(forms.FileField):
    widget = MultiFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        if len(data) > MAX_PRINT_PHOTOS:
            raise ValidationError(f"Можно загрузить не более {MAX_PRINT_PHOTOS} фотографий.")
        cleaned = []
        for f in data:
            validate_image_upload(f)
            validate_image_content(f.file)
            cleaned.append(f)
        return cleaned


class CustomPrintRequestForm(forms.ModelForm):
    photos = MultiFileField(
        required=False,
        label="Дополнительные фотографии",
        widget=MultiFileInput(attrs={"multiple": True, "accept": "image/jpeg,image/png,image/webp"}),
    )

    class Meta:
        model = CustomPrintRequest
        fields = [
            "name", "phone", "email", "project_name", "description", "quantity",
            "material", "color", "deadline", "model_url", "model_file", "comment",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ваше имя"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+7 900 000-00-00"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "email@example.com"}),
            "project_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Название проекта"}),
            "description": forms.Textarea(attrs={"class": "form-textarea", "rows": 4}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": 1}),
            "material": forms.Select(attrs={"class": "form-select"}),
            "color": forms.TextInput(attrs={"class": "form-input", "placeholder": "Например, черный"}),
            "deadline": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "model_url": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://..."}),
            "model_file": forms.ClearableFileInput(attrs={"accept": ".stl,.obj,.3mf,.step,.stp"}),
            "comment": forms.Textarea(attrs={"class": "form-textarea", "rows": 3}),
        }

    def clean_model_file(self):
        model_file = self.cleaned_data.get("model_file")
        if model_file:
            validate_model_upload(model_file)
        return model_file

    def clean(self):
        cleaned_data = super().clean()
        model_file = cleaned_data.get("model_file")
        model_url = cleaned_data.get("model_url")
        if not model_file and not model_url:
            raise ValidationError(
                "Прикрепите файл модели или укажите ссылку на модель (можно и то, и другое)."
            )
        return cleaned_data
