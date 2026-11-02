from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.emails import send_order_request_emails
from apps.products.models import Product

from .cart import Cart
from .forms import OrderRequestForm
from .models import OrderRequest, OrderRequestItem


def cart_detail(request):
    cart = Cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product.objects.active(), id=product_id)
    quantity = request.POST.get("quantity", 1)
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1
    cart = Cart(request)
    cart.add(product=product, quantity=quantity)
    messages.success(request, f"«{product.name}» добавлен в заявку.")
    next_url = request.POST.get("next") or "orders:cart_detail"
    return redirect(next_url)


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    quantity = request.POST.get("quantity", 1)
    cart.update(product_id, quantity)
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.info(request, "Товар удален из заявки.")
    return redirect("orders:cart_detail")


def checkout(request):
    cart = Cart(request)
    if cart.is_empty():
        messages.warning(request, "Ваша заявка пуста. Добавьте товары из каталога.")
        return redirect("products:catalog")

    if request.method == "POST":
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order_request = form.save(commit=False)
                order_request.save()
                items = list(cart)
                OrderRequestItem.objects.bulk_create([
                    OrderRequestItem(
                        request=order_request,
                        product=entry["product"],
                        product_name=entry["product"].name,
                        price=entry["product"].price,
                        quantity=entry["quantity"],
                    )
                    for entry in items
                ])
            cart.clear()
            send_order_request_emails(order_request)
            return redirect("orders:success", request_number=order_request.request_number)
    else:
        form = OrderRequestForm()

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


def success(request, request_number):
    order_request = get_object_or_404(OrderRequest, request_number=request_number)
    return render(request, "orders/success.html", {"object": order_request, "kind": "товары"})
