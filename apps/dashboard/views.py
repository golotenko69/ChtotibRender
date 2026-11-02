from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.orders.models import OrderRequest
from apps.print_requests.models import CustomPrintRequest
from apps.products.models import Category, Product
from apps.scanning.models import ScanningRequest

from .decorators import staff_required
from .forms import (
    CategoryForm,
    DashboardLoginForm,
    OrderRequestStatusForm,
    PrintRequestStatusForm,
    ProductForm,
    ProductImageFormSet,
    ScanningRequestStatusForm,
)

NEW_STATUSES = {"NEW"}
DONE_STATUSES = {"COMPLETED", "CANCELLED"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard:home")

    form = DashboardLoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                messages.error(request, "У этого аккаунта нет доступа к панели управления.")
            else:
                auth_login(request, user)
                next_url = request.POST.get("next") or request.GET.get("next") or reverse("dashboard:home")
                return redirect(next_url)
        else:
            messages.error(request, "Неверный логин или пароль.")
    return render(request, "dashboard/login.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    messages.info(request, "Вы вышли из панели управления.")
    return redirect("dashboard:login")


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

@staff_required
def home(request):
    queues = [
        ("order", "Заявки на товары", OrderRequest.objects.all(), "dashboard:order_detail"),
        ("print", "Заявки на печать", CustomPrintRequest.objects.all(), "dashboard:print_detail"),
        ("scan", "Заявки на сканирование", ScanningRequest.objects.all(), "dashboard:scan_detail"),
    ]

    stats = []
    new_total = in_progress_total = completed_total = 0
    recent_feed = []

    for key, label, qs, detail_url_name in queues:
        new_count = qs.filter(status="NEW").count()
        done_count = qs.filter(status__in=DONE_STATUSES).count()
        in_progress_count = qs.exclude(status__in=NEW_STATUSES | DONE_STATUSES).count()
        stats.append({
            "key": key, "label": label, "new": new_count,
            "in_progress": in_progress_count, "done": done_count, "total": qs.count(),
            "list_url": reverse(f"dashboard:{key}_list"),
        })
        new_total += new_count
        in_progress_total += in_progress_count
        completed_total += done_count

        for obj in qs.order_by("-created_at")[:5]:
            recent_feed.append({
                "number": obj.request_number,
                "who": getattr(obj, "full_name", None) or getattr(obj, "name", ""),
                "status": obj.get_status_display(),
                "status_code": obj.status,
                "created_at": obj.created_at,
                "url": reverse(detail_url_name, args=[obj.pk]),
                "kind": label,
            })

    recent_feed.sort(key=lambda x: x["created_at"], reverse=True)

    context = {
        "stats": stats,
        "new_total": new_total,
        "in_progress_total": in_progress_total,
        "completed_total": completed_total,
        "products_total": Product.objects.count(),
        "products_out_of_stock": Product.objects.filter(stock=0).count(),
        "categories_total": Category.objects.count(),
        "recent_feed": recent_feed[:10],
        "today": timezone.localdate(),
    }
    context["active"] = "home"
    return render(request, "dashboard/home.html", context)


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@staff_required
def product_list(request):
    products = Product.objects.select_related("category").all()

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    stock_filter = request.GET.get("stock")
    if stock_filter == "out":
        products = products.filter(stock=0)
    elif stock_filter == "low":
        products = products.filter(stock__gt=0, stock__lte=5)

    products = products.order_by("-created_at")
    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "query": query,
        "category_id": category_id,
        "stock_filter": stock_filter,
    }
    context["active"] = "products"
    return render(request, "dashboard/product_list.html", context)


@staff_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        formset = None
        with transaction.atomic():
            if form.is_valid():
                product = form.save()
                formset = ProductImageFormSet(request.POST, request.FILES, instance=product, prefix="images")
                if formset.is_valid():
                    formset.save()
                    messages.success(request, f"Товар «{product.name}» создан.")
                    return redirect("dashboard:product_list")
                # Roll back the product row too — nothing is saved unless both are valid.
                transaction.set_rollback(True)
            else:
                formset = ProductImageFormSet(request.POST, request.FILES, prefix="images")
    else:
        form = ProductForm()
        formset = ProductImageFormSet(prefix="images")

    return render(request, "dashboard/product_form.html", {"form": form, "formset": formset, "is_new": True, "active": "products"})


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product, prefix="images")
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"Товар «{product.name}» обновлен.")
            return redirect("dashboard:product_list")
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product, prefix="images")

    return render(request, "dashboard/product_form.html", {
        "form": form, "formset": formset, "product": product, "is_new": False, "active": "products",
    })


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Товар «{name}» удален.")
        return redirect("dashboard:product_list")
    return render(request, "dashboard/product_confirm_delete.html", {"product": product, "active": "products"})


@staff_required
def product_toggle_active(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    return redirect(request.META.get("HTTP_REFERER") or "dashboard:product_list")


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "dashboard/category_list.html", {"categories": categories, "active": "categories"})


@staff_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Категория «{category.name}» создана.")
            return redirect("dashboard:category_list")
    else:
        form = CategoryForm()
    return render(request, "dashboard/category_form.html", {"form": form, "is_new": True, "active": "categories"})


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Категория «{category.name}» обновлена.")
            return redirect("dashboard:category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "dashboard/category_form.html", {"form": form, "category": category, "is_new": False, "active": "categories"})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        name = category.name
        category.delete()
        messages.success(request, f"Категория «{name}» удалена.")
        return redirect("dashboard:category_list")
    return render(request, "dashboard/category_confirm_delete.html", {"category": category, "active": "categories"})


# ---------------------------------------------------------------------------
# Request queues — shared list/filter helper
# ---------------------------------------------------------------------------

def _filtered_queue(request, queryset, status_choices):
    status = request.GET.get("status", "")
    query = request.GET.get("q", "").strip()
    if status:
        queryset = queryset.filter(status=status)
    if query:
        queryset = queryset.filter(
            Q(request_number__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query)
        )
    paginator = Paginator(queryset.order_by("-created_at"), 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return page_obj, status, query


@staff_required
def order_list(request):
    page_obj, status, query = _filtered_queue(request, OrderRequest.objects.all(), OrderRequest.Status.choices)
    context = {
        "page_obj": page_obj, "status": status, "query": query,
        "status_choices": OrderRequest.Status.choices, "title": "Заявки на товары",
        "list_url": "dashboard:order_list", "detail_url": "dashboard:order_detail",
    }
    context["active"] = "orders"
    return render(request, "dashboard/queue_list.html", context)


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(OrderRequest.objects.prefetch_related("items"), pk=pk)
    if request.method == "POST":
        form = OrderRequestStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Заявка {order.request_number} обновлена.")
            return redirect("dashboard:order_detail", pk=order.pk)
    else:
        form = OrderRequestStatusForm(instance=order)
    return render(request, "dashboard/order_detail.html", {"order": order, "form": form, "active": "orders"})


@staff_required
def print_list(request):
    page_obj, status, query = _filtered_queue(
        request, CustomPrintRequest.objects.all(), CustomPrintRequest.Status.choices
    )
    context = {
        "page_obj": page_obj, "status": status, "query": query,
        "status_choices": CustomPrintRequest.Status.choices, "title": "Заявки на печать моделей",
        "list_url": "dashboard:print_list", "detail_url": "dashboard:print_detail",
    }
    context["active"] = "print"
    return render(request, "dashboard/queue_list.html", context)


@staff_required
def print_detail(request, pk):
    print_request = get_object_or_404(CustomPrintRequest.objects.prefetch_related("photos"), pk=pk)
    if request.method == "POST":
        form = PrintRequestStatusForm(request.POST, instance=print_request)
        if form.is_valid():
            form.save()
            messages.success(request, f"Заявка {print_request.request_number} обновлена.")
            return redirect("dashboard:print_detail", pk=print_request.pk)
    else:
        form = PrintRequestStatusForm(instance=print_request)
    return render(request, "dashboard/print_detail.html", {"print_request": print_request, "form": form, "active": "print"})


@staff_required
def scan_list(request):
    page_obj, status, query = _filtered_queue(
        request, ScanningRequest.objects.all(), ScanningRequest.Status.choices
    )
    context = {
        "page_obj": page_obj, "status": status, "query": query,
        "status_choices": ScanningRequest.Status.choices, "title": "Заявки на 3D-сканирование",
        "list_url": "dashboard:scan_list", "detail_url": "dashboard:scan_detail",
    }
    context["active"] = "scan"
    return render(request, "dashboard/queue_list.html", context)


@staff_required
def scan_detail(request, pk):
    scan_request = get_object_or_404(ScanningRequest.objects.prefetch_related("images"), pk=pk)
    if request.method == "POST":
        form = ScanningRequestStatusForm(request.POST, instance=scan_request)
        if form.is_valid():
            form.save()
            messages.success(request, f"Заявка {scan_request.request_number} обновлена.")
            return redirect("dashboard:scan_detail", pk=scan_request.pk)
    else:
        form = ScanningRequestStatusForm(instance=scan_request)
    return render(request, "dashboard/scan_detail.html", {"scan_request": scan_request, "form": form, "active": "scan"})
