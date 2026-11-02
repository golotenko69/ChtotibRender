from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory

from apps.orders.models import OrderRequest
from apps.print_requests.models import CustomPrintRequest
from apps.products.models import Category, Product, ProductImage
from apps.scanning.models import ScanningRequest

INPUT = "dash-input"
SELECT = "dash-input dash-select"
TEXTAREA = "dash-input dash-textarea"


class DashboardLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": INPUT, "placeholder": "Логин", "autofocus": True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": INPUT, "placeholder": "Пароль"}))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "image", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT, "placeholder": "Название категории"}),
            "description": forms.Textarea(attrs={"class": TEXTAREA, "rows": 3}),
            "image": forms.ClearableFileInput(attrs={"class": INPUT}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "category", "sku", "short_description", "description",
            "price", "old_price", "stock", "main_image", "is_active", "is_featured",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT, "placeholder": "Название товара"}),
            "category": forms.Select(attrs={"class": SELECT}),
            "sku": forms.TextInput(attrs={"class": INPUT, "placeholder": "Артикул"}),
            "short_description": forms.TextInput(attrs={"class": INPUT, "placeholder": "Краткое описание для карточки"}),
            "description": forms.Textarea(attrs={"class": TEXTAREA, "rows": 5}),
            "price": forms.NumberInput(attrs={"class": INPUT, "step": "0.01", "min": 0}),
            "old_price": forms.NumberInput(attrs={"class": INPUT, "step": "0.01", "min": 0}),
            "stock": forms.NumberInput(attrs={"class": INPUT, "min": 0}),
            "main_image": forms.ClearableFileInput(attrs={"class": INPUT}),
        }


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=["image", "alt_text", "sort_order"],
    extra=3,
    can_delete=True,
    widgets={
        "image": forms.ClearableFileInput(attrs={"class": INPUT}),
        "alt_text": forms.TextInput(attrs={"class": INPUT, "placeholder": "Alt-текст"}),
        "sort_order": forms.NumberInput(attrs={"class": INPUT, "style": "width:70px"}),
    },
)


class OrderRequestStatusForm(forms.ModelForm):
    class Meta:
        model = OrderRequest
        fields = ["status", "admin_comment"]
        widgets = {
            "status": forms.Select(attrs={"class": SELECT}),
            "admin_comment": forms.Textarea(attrs={"class": TEXTAREA, "rows": 4, "placeholder": "Заметка для команды / клиента"}),
        }


class PrintRequestStatusForm(forms.ModelForm):
    class Meta:
        model = CustomPrintRequest
        fields = ["status", "estimated_price", "admin_comment"]
        widgets = {
            "status": forms.Select(attrs={"class": SELECT}),
            "estimated_price": forms.NumberInput(attrs={"class": INPUT, "step": "0.01", "min": 0, "placeholder": "Ориентировочная цена, ₽"}),
            "admin_comment": forms.Textarea(attrs={"class": TEXTAREA, "rows": 4, "placeholder": "Заметка для команды / клиента"}),
        }


class ScanningRequestStatusForm(forms.ModelForm):
    class Meta:
        model = ScanningRequest
        fields = ["status", "estimated_price", "admin_comment"]
        widgets = {
            "status": forms.Select(attrs={"class": SELECT}),
            "estimated_price": forms.NumberInput(attrs={"class": INPUT, "step": "0.01", "min": 0, "placeholder": "Ориентировочная цена, ₽"}),
            "admin_comment": forms.Textarea(attrs={"class": TEXTAREA, "rows": 4, "placeholder": "Заметка для команды / клиента"}),
        }
