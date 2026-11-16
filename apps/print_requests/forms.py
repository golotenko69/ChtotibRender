from django import forms

from .models import CustomPrintRequest


class MultiFileInput(forms.ClearableFileInput):
    """Multi-file widget, reused by the scanning request form."""

    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, "getlist"):
            return files.getlist(name)
        return files.get(name)


class CustomPrintRequestForm(forms.ModelForm):
    """Short public form: contacts, quantity and a link to the model.
    Material, colour, deadline etc. are agreed with the manager later."""

    class Meta:
        model = CustomPrintRequest
        fields = ["name", "phone", "email", "quantity", "model_url"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ваше имя", "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+7 900 000-00-00", "autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "email@example.com", "autocomplete": "email"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": 1, "max": 1000}),
            "model_url": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://… (Thingiverse, Printables, Google Диск, Яндекс Диск)"}),
        }
        labels = {"email": "Почта", "model_url": "Ссылка на модель"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("name", "phone", "email", "model_url"):
            self.fields[name].required = True
        self.fields["model_url"].assume_scheme = "https"
