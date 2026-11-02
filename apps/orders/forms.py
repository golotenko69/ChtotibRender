from django import forms

from .models import OrderRequest


class OrderRequestForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = ["first_name", "last_name", "phone", "email", "city", "address", "comment"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ваше имя", "required": True}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Фамилия (необязательно)"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+7 900 000-00-00", "required": True}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "email@example.com"}),
            "city": forms.TextInput(attrs={"class": "form-input", "placeholder": "Город"}),
            "address": forms.TextInput(attrs={"class": "form-input", "placeholder": "Адрес доставки"}),
            "comment": forms.Textarea(attrs={"class": "form-textarea", "rows": 4, "placeholder": "Комментарий к заявке"}),
        }

    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()
        if not value:
            raise forms.ValidationError("Укажите имя.")
        return value
